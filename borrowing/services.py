"""Atomic borrowing workflow: request submission, cancellation and audited admin decisions."""

from datetime import date, datetime

from django.core.exceptions import (
    ImproperlyConfigured,
    PermissionDenied,
    ValidationError,
)
from django.db import transaction
from django.utils import timezone

from accounts.access import require_active_basic_user
from accounts.models import User, UserRole
from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestItem,
    RequestStatus,
    UnitAllocation,
)
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitStatus
from operations.audit import write_audit
from operations.locking import (
    lock_available_units,
    lock_borrower,
    lock_catalog,
    lock_request,
    lock_units,
)
from operations.models import AuditAction, AuditTarget, SystemSetting
from operations.validation import (
    LoanLimits,
    RequestedItem,
    validate_loan_limits,
    validate_requested_due_date,
    validate_requested_items,
)


class WorkflowConflict(Exception):
    """The request cannot change because of its state or the available inventory (HTTP 409)."""


class RequestCancellationConflict(Exception):
    """The request or its reservation state no longer permits borrower cancellation."""


def submit_request(
    owner_id: int,
    purpose: str,
    desired_due_date: date,
    items: tuple[RequestedItem, ...],
) -> BorrowRequest:
    """Create a Pending request and all its rows under authoritative shared locks."""
    clean_purpose: str = purpose.strip()
    if not clean_purpose:
        raise ValidationError({"purpose": "Purpose cannot be blank."})

    with transaction.atomic():
        try:
            borrower: User = lock_borrower(owner_id)
        except User.DoesNotExist as error:
            raise PermissionDenied("The submitting borrower account does not exist.") from error
        require_active_basic_user(borrower)

        try:
            setting: SystemSetting = SystemSetting.objects.select_for_update().get(pk=1)
        except SystemSetting.DoesNotExist as error:
            raise ImproperlyConfigured(
                "SystemSetting row 1 is missing; request submission cannot continue."
            ) from error
        limits: LoanLimits = validate_loan_limits(
            setting.max_loan_days, setting.max_quantity_per_item
        )
        validated_items: tuple[RequestedItem, ...] = validate_requested_items(items, limits)

        submitted_at: datetime = timezone.now()
        submitted_on: date = timezone.localdate(submitted_at)
        validated_due_date: date = validate_requested_due_date(
            submitted_on, desired_due_date, limits
        )

        catalog_item_ids: tuple[int, ...] = tuple(item.catalog_item_id for item in validated_items)
        try:
            locked_catalog = lock_catalog(catalog_item_ids)
        except CatalogItem.DoesNotExist as error:
            raise ValidationError(
                "One or more selected equipment items no longer exist."
            ) from error

        categories_by_id: dict[int, Category] = {
            category.pk: category for category in locked_catalog.categories
        }
        items_by_id: dict[int, CatalogItem] = {item.pk: item for item in locked_catalog.items}
        for requested_item in validated_items:
            catalog_item: CatalogItem = items_by_id[requested_item.catalog_item_id]
            category: Category = categories_by_id[catalog_item.category_id]
            if catalog_item.is_archived or category.is_archived:
                raise ValidationError(
                    "Archived equipment or categories cannot be included in a new request."
                )

        borrow_request: BorrowRequest = BorrowRequest.objects.create(
            owner=borrower,
            purpose=clean_purpose,
            submitted_at=submitted_at,
            submitted_on=submitted_on,
            desired_due_date=validated_due_date,
            agreed_due_date=validated_due_date,
            max_loan_days_applied=limits.max_loan_days,
            max_quantity_applied=limits.max_quantity_per_item,
            status=RequestStatus.PENDING,
            decision_reason="",
        )
        RequestItem.objects.bulk_create(
            [
                RequestItem(
                    request=borrow_request,
                    catalog_item=items_by_id[item.catalog_item_id],
                    quantity=item.quantity,
                )
                for item in validated_items
            ]
        )
        return borrow_request


def _active_admin(actor_id: int) -> User:
    actor = User.objects.get(pk=actor_id)
    if not actor.is_active or actor.role != UserRole.ADMIN:
        raise PermissionDenied("This action requires an active ADMIN account.")
    return actor


def _clean_reason(reason: str) -> str:
    reason = reason.strip()
    if not reason:
        raise ValidationError("A reason is required for this decision.")
    return reason


def approve_request(actor_id: int, request_id: int, reason: str) -> BorrowRequest:
    """Reserve every requested unit atomically, or change nothing."""
    reason = _clean_reason(reason)
    owner_id = BorrowRequest.objects.values_list("owner_id", flat=True).get(pk=request_id)
    with transaction.atomic():
        _active_admin(actor_id)
        locked = lock_request(owner_id, request_id)
        borrow_request = locked.request
        if borrow_request.status != RequestStatus.PENDING:
            raise WorkflowConflict(
                f"Request #{borrow_request.pk} is {borrow_request.get_status_display().lower()}, "
                "so it can no longer be approved."
            )
        if not locked.borrower.is_active:
            raise WorkflowConflict("The borrower's account is inactive.")
        lines = list(borrow_request.items.select_related("catalog_item").order_by("pk"))
        if not lines:
            raise WorkflowConflict("The request has no items.")
        item_ids = tuple(line.catalog_item_id for line in lines)
        catalog = lock_catalog(item_ids)
        if any(item.is_archived for item in catalog.items) or any(
            category.is_archived for category in catalog.categories
        ):
            raise WorkflowConflict("The request includes an archived item or category.")
        available: dict[int, list] = {}
        for unit in lock_available_units(item_ids):
            available.setdefault(unit.catalog_item_id, []).append(unit)
        plan = []
        shortages = []
        for line in lines:
            chosen = available.get(line.catalog_item_id, [])[: line.quantity]
            if len(chosen) < line.quantity:
                shortages.append(
                    f"{line.catalog_item.name}: requested {line.quantity}, available {len(chosen)}"
                )
            plan.append((line, chosen))
        if shortages:
            # Raising inside atomic() rolls back everything: nothing is reserved.
            raise WorkflowConflict(
                "Not enough available units. " + "; ".join(shortages) + ". Nothing was reserved."
            )
        now = timezone.now()
        for line, chosen in plan:
            for unit in chosen:
                UnitAllocation.objects.create(
                    request_item=line, unit=unit, allocated_at=now, allocated_by_id=actor_id
                )
                unit.status = UnitStatus.RESERVED
                unit.save(update_fields=["status", "updated_at"])
        borrow_request.status = RequestStatus.APPROVED
        borrow_request.decided_by_id = actor_id
        borrow_request.decided_at = now
        borrow_request.decision_reason = reason
        borrow_request.save(update_fields=["status", "decided_by", "decided_at", "decision_reason"])
        write_audit(
            actor_id,
            AuditAction.REQUEST_APPROVED,
            AuditTarget.BORROW_REQUEST,
            borrow_request.pk,
            f"Approved request #{borrow_request.pk}: {reason}",
        )
        return borrow_request


def reject_request(actor_id: int, request_id: int, reason: str) -> BorrowRequest:
    """Reject a pending request. No units are touched."""
    reason = _clean_reason(reason)
    owner_id = BorrowRequest.objects.values_list("owner_id", flat=True).get(pk=request_id)
    with transaction.atomic():
        _active_admin(actor_id)
        borrow_request = lock_request(owner_id, request_id).request
        if borrow_request.status != RequestStatus.PENDING:
            raise WorkflowConflict(
                f"Request #{borrow_request.pk} is {borrow_request.get_status_display().lower()}, "
                "so it can no longer be rejected."
            )
        now = timezone.now()
        borrow_request.status = RequestStatus.REJECTED
        borrow_request.decided_by_id = actor_id
        borrow_request.decided_at = now
        borrow_request.decision_reason = reason
        borrow_request.save(update_fields=["status", "decided_by", "decided_at", "decision_reason"])
        write_audit(
            actor_id,
            AuditAction.REQUEST_REJECTED,
            AuditTarget.BORROW_REQUEST,
            borrow_request.pk,
            f"Rejected request #{borrow_request.pk}: {reason}",
        )
        return borrow_request


def cancel_request(owner_id: int, request_id: int) -> BorrowRequest:
    """Cancel an eligible owner request and release its reservations atomically."""
    with transaction.atomic():
        try:
            locked_request = lock_request(owner_id, request_id)
        except User.DoesNotExist as error:
            raise PermissionDenied("The cancelling borrower account does not exist.") from error
        require_active_basic_user(locked_request.borrower)

        borrow_request: BorrowRequest = locked_request.request
        if borrow_request.status not in (RequestStatus.PENDING, RequestStatus.APPROVED):
            raise RequestCancellationConflict("Only Pending or Approved requests can be cancelled.")
        cancelled_at = timezone.now()

        request_items: tuple[RequestItem, ...] = tuple(
            RequestItem.objects.select_for_update()
            .filter(request_id=borrow_request.pk)
            .order_by("pk")
        )
        allocations: tuple[UnitAllocation, ...] = tuple(
            UnitAllocation.objects.filter(request_item__request_id=borrow_request.pk).order_by("pk")
        )

        if borrow_request.status == RequestStatus.PENDING:
            if allocations:
                raise RequestCancellationConflict(
                    "The Pending request has unexpected reservation history and cannot be cancelled."
                )
        else:
            if locked_request.loan is not None or not request_items:
                raise RequestCancellationConflict(
                    "The Approved request no longer has a cancellable reservation."
                )
            if not allocations:
                raise RequestCancellationConflict(
                    "The Approved request has no reservation to release."
                )

            catalog_item_ids: tuple[int, ...] = tuple(
                item.catalog_item_id for item in request_items
            )
            try:
                locked_catalog = lock_catalog(catalog_item_ids)
            except (CatalogItem.DoesNotExist, ValidationError) as error:
                raise RequestCancellationConflict(
                    "The reserved equipment changed; refresh the request before retrying."
                ) from error

            request_item_by_id: dict[int, RequestItem] = {item.pk: item for item in request_items}
            catalog_ids: set[int] = {item.pk for item in locked_catalog.items}
            if len(catalog_ids) != len(catalog_item_ids) or not set(catalog_item_ids).issubset(
                catalog_ids
            ):
                raise RequestCancellationConflict(
                    "The Approved request's equipment items are inconsistent."
                )

            allocation_counts: dict[int, int] = {}
            unit_ids: list[int] = []
            for allocation in allocations:
                allocation_counts[allocation.request_item_id] = (
                    allocation_counts.get(allocation.request_item_id, 0) + 1
                )
                unit_ids.append(allocation.unit_id)
                if (
                    allocation.released_at is not None
                    or allocation.cancelled_at is not None
                    or allocation.ended_at is not None
                    or allocation.request_item_id not in request_item_by_id
                ):
                    raise RequestCancellationConflict(
                        "A reservation has already been released or ended."
                    )

            if len(unit_ids) != len(set(unit_ids)) or any(
                allocation_counts.get(item.pk, 0) != item.quantity for item in request_items
            ):
                raise RequestCancellationConflict(
                    "The Approved request does not have its complete reservation."
                )

            try:
                locked_units: tuple[EquipmentUnit, ...] = lock_units(tuple(unit_ids))
            except (EquipmentUnit.DoesNotExist, ValidationError) as error:
                raise RequestCancellationConflict(
                    "A reserved equipment unit changed; refresh the request before retrying."
                ) from error
            units_by_id: dict[int, EquipmentUnit] = {unit.pk: unit for unit in locked_units}
            for allocation in allocations:
                unit: EquipmentUnit = units_by_id[allocation.unit_id]
                request_item: RequestItem = request_item_by_id[allocation.request_item_id]
                if (
                    unit.status != UnitStatus.RESERVED
                    or unit.catalog_item_id != request_item.catalog_item_id
                ):
                    raise RequestCancellationConflict(
                        "A reserved equipment unit is no longer available for release."
                    )

            locked_allocations: tuple[UnitAllocation, ...] = tuple(
                UnitAllocation.objects.select_for_update()
                .filter(pk__in=[allocation.pk for allocation in allocations])
                .order_by("pk")
            )
            allocations_by_id: dict[int, UnitAllocation] = {
                allocation.pk: allocation for allocation in allocations
            }
            if len(locked_allocations) != len(allocations) or any(
                allocation.ended_at is not None
                or allocation.cancelled_at is not None
                or allocation.released_at is not None
                or allocation.unit_id != allocations_by_id[allocation.pk].unit_id
                or allocation.request_item_id != allocations_by_id[allocation.pk].request_item_id
                for allocation in locked_allocations
            ):
                raise RequestCancellationConflict(
                    "A reservation changed while cancellation was in progress."
                )

            for allocation in locked_allocations:
                allocation.cancelled_at = cancelled_at
                allocation.ended_at = cancelled_at
                allocation.save(update_fields=["cancelled_at", "ended_at"])
            for unit in locked_units:
                unit.status = UnitStatus.AVAILABLE
                unit.save(update_fields=["status", "updated_at"])

        borrow_request.status = RequestStatus.CANCELLED
        borrow_request.cancelled_by_id = owner_id
        borrow_request.cancelled_at = cancelled_at
        borrow_request.save(update_fields=["status", "cancelled_by", "cancelled_at"])
        write_audit(
            actor_id=owner_id,
            action=AuditAction.REQUEST_CANCELLED,
            target_model=AuditTarget.BORROW_REQUEST,
            target_id=borrow_request.pk,
            summary=f"Request #{borrow_request.pk} cancelled by its borrower.",
        )
        return borrow_request


def revise_due_date(
    actor_id: int,
    request_id: int,
    agreed_due_date: date,
    reason: str,
) -> BorrowRequest:
    """Revise an approved request's agreed due date before equipment release."""
    reason = _clean_reason(reason)
    owner_id = BorrowRequest.objects.values_list("owner_id", flat=True).get(pk=request_id)
    with transaction.atomic():
        _active_admin(actor_id)
        locked = lock_request(owner_id, request_id)
        borrow_request = locked.request

        if borrow_request.status != RequestStatus.APPROVED:
            raise WorkflowConflict(
                f"Request #{borrow_request.pk} is {borrow_request.get_status_display().lower()}, "
                "so its due date cannot be revised."
            )
        if locked.loan is not None:
            raise WorkflowConflict("The request has already been released as a loan.")
        if not locked.borrower.is_active:
            raise WorkflowConflict("The borrower's account is inactive.")

        if agreed_due_date < borrow_request.submitted_on:
            raise ValidationError(
                {"agreed_due_date": "Agreed due date cannot precede the submission date."}
            )

        duration_days = (agreed_due_date - borrow_request.submitted_on).days
        if duration_days > borrow_request.max_loan_days_applied:
            raise ValidationError(
                {
                    "agreed_due_date": (
                        f"Agreed loan duration of {duration_days} day(s) exceeds the "
                        f"applied limit of {borrow_request.max_loan_days_applied} day(s)."
                    )
                }
            )

        previous_due_date = borrow_request.agreed_due_date
        borrow_request.agreed_due_date = agreed_due_date
        borrow_request.save(update_fields=["agreed_due_date"])

        write_audit(
            actor_id=actor_id,
            action=AuditAction.DUE_DATE_REVISED,
            target_model=AuditTarget.BORROW_REQUEST,
            target_id=borrow_request.pk,
            summary=(
                f"Revised agreed due date for request #{borrow_request.pk} "
                f"from {previous_due_date.isoformat()} to {agreed_due_date.isoformat()}: {reason}"
            ),
        )
        return borrow_request


def issue_request(actor_id: int, request_id: int) -> Loan:
    """Transition an approved request to ISSUED, creating Loan and LoanUnit records."""
    owner_id = BorrowRequest.objects.values_list("owner_id", flat=True).get(pk=request_id)
    with transaction.atomic():
        admin = _active_admin(actor_id)
        locked = lock_request(owner_id, request_id)
        borrow_request = locked.request

        if borrow_request.status != RequestStatus.APPROVED:
            raise WorkflowConflict(
                f"Request #{borrow_request.pk} is {borrow_request.get_status_display().lower()}, "
                "so it cannot be released."
            )
        if locked.loan is not None:
            raise WorkflowConflict("The request has already been released.")
        if not locked.borrower.is_active:
            raise WorkflowConflict("The borrower's account is inactive.")

        request_items = tuple(
            RequestItem.objects.select_for_update()
            .filter(request_id=borrow_request.pk)
            .order_by("pk")
        )
        if not request_items:
            raise WorkflowConflict("The request has no items.")

        allocations = tuple(
            UnitAllocation.objects.filter(request_item__request_id=borrow_request.pk).order_by("pk")
        )
        if not allocations:
            raise WorkflowConflict("The request has no allocated equipment units.")

        item_counts: dict[int, int] = {}
        for line in request_items:
            item_counts[line.pk] = line.quantity

        unit_ids: list[int] = []
        alloc_counts: dict[int, int] = {}
        for alloc in allocations:
            if alloc.released_at is not None or alloc.cancelled_at is not None or alloc.ended_at is not None:
                raise WorkflowConflict("One or more allocations have already been released or cancelled.")
            alloc_counts[alloc.request_item_id] = alloc_counts.get(alloc.request_item_id, 0) + 1
            unit_ids.append(alloc.unit_id)

        if len(unit_ids) != len(set(unit_ids)) or any(
            alloc_counts.get(item_id, 0) != count for item_id, count in item_counts.items()
        ):
            raise WorkflowConflict("The request is insufficiently or inconsistently allocated.")

        locked_units = lock_units(tuple(unit_ids))
        for unit in locked_units:
            if unit.status != UnitStatus.RESERVED:
                raise WorkflowConflict(
                    f"Unit '{unit.asset_code}' is {unit.get_status_display().lower()}, not reserved."
                )

        now = timezone.now()
        today = timezone.localdate(now)

        locked_allocations = tuple(
            UnitAllocation.objects.select_for_update()
            .filter(pk__in=[alloc.pk for alloc in allocations])
            .order_by("pk")
        )
        for alloc in locked_allocations:
            alloc.released_at = now
            alloc.save(update_fields=["released_at"])

        for unit in locked_units:
            unit.status = UnitStatus.ON_LOAN
            unit.save(update_fields=["status", "updated_at"])

        borrow_request.status = RequestStatus.ISSUED
        borrow_request.save(update_fields=["status"])

        loan = Loan.objects.create(
            request=borrow_request,
            issued_by=admin,
            issued_at=now,
            issued_on=today,
            due_date=borrow_request.agreed_due_date,
        )

        for alloc in locked_allocations:
            LoanUnit.objects.create(
                loan=loan,
                allocation=alloc,
            )

        write_audit(
            actor_id=actor_id,
            action=AuditAction.LOAN_RELEASED,
            target_model=AuditTarget.LOAN,
            target_id=loan.pk,
            summary=(
                f"Released loan #{loan.pk} for request #{borrow_request.pk} "
                f"({len(locked_allocations)} unit(s) on loan)."
            ),
        )
        return loan