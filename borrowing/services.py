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
    RequestItem,
    RequestStatus,
    UnitAllocation,
)
from borrowing.reservations import ReservationConflict, ReservedUnits, lock_reserved_units
from inventory.models import CatalogItem, Category, UnitStatus
from operations.audit import write_audit
from operations.locking import (
    lock_available_units,
    lock_borrower,
    lock_catalog,
    lock_request,
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

        if borrow_request.status == RequestStatus.PENDING:
            if UnitAllocation.objects.filter(request_item__request_id=borrow_request.pk).exists():
                raise RequestCancellationConflict(
                    "The Pending request has unexpected reservation history and cannot be cancelled."
                )
        else:
            if locked_request.loan is not None:
                raise RequestCancellationConflict(
                    "The Approved request no longer has a cancellable reservation."
                )
            try:
                reserved: ReservedUnits = lock_reserved_units(borrow_request.pk)
            except ReservationConflict as error:
                raise RequestCancellationConflict(str(error)) from error
            for allocation in reserved.allocations:
                allocation.cancelled_at = cancelled_at
                allocation.ended_at = cancelled_at
                allocation.save(update_fields=["cancelled_at", "ended_at"])
            for unit in reserved.units:
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
