"""Audited approval and rejection of borrow requests."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.models import User, UserRole
from borrowing.models import BorrowRequest, RequestStatus, UnitAllocation
from inventory.models import UnitStatus
from operations.audit import write_audit
from operations.locking import lock_available_units, lock_catalog, lock_request
from operations.models import AuditAction, AuditTarget


class WorkflowConflict(Exception):
    """The request cannot change because of its state or the available inventory (HTTP 409)."""


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
            raise WorkflowConflict("Not enough available units. " + "; ".join(shortages) + ". Nothing was reserved.")
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
            actor_id, AuditAction.REQUEST_APPROVED, AuditTarget.BORROW_REQUEST, borrow_request.pk,
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
            actor_id, AuditAction.REQUEST_REJECTED, AuditTarget.BORROW_REQUEST, borrow_request.pk,
            f"Rejected request #{borrow_request.pk}: {reason}",
        )
        return borrow_request