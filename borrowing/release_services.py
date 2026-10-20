"""Audited pre-issue due-date revision and one-time release of reserved units."""

from datetime import date, datetime

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.access import require_active_admin
from accounts.models import User, UserRole
from borrowing.models import BorrowRequest, Loan, LoanUnit, RequestStatus
from borrowing.reservations import ReservationConflict, ReservedUnits, lock_reserved_units
from borrowing.services import WorkflowConflict
from inventory.models import UnitStatus
from operations.audit import write_audit
from operations.locking import lock_request
from operations.models import AuditAction, AuditTarget
from operations.validation import LoanLimits, validate_revised_due_date


def _approved_request(actor_id: int, request_id: int) -> BorrowRequest:
    """Recheck authority and the locked pre-issue state inside the caller's transaction."""
    try:
        actor: User = User.objects.get(pk=actor_id)
    except User.DoesNotExist as error:
        raise PermissionDenied("The performing administrator account does not exist.") from error
    require_active_admin(actor)
    owner_id: int = BorrowRequest.objects.values_list("owner_id", flat=True).get(pk=request_id)
    locked = lock_request(owner_id, request_id)
    if locked.request.status != RequestStatus.APPROVED or locked.loan is not None:
        raise WorkflowConflict("Only an Approved request without an existing loan can be changed.")
    if not locked.borrower.is_active or locked.borrower.role != UserRole.BASIC_USER:
        raise WorkflowConflict("The borrower must be an active basic-user account.")
    return locked.request


def revise_due_date(
    actor_id: int, request_id: int, agreed_due_date: date, reason: str
) -> BorrowRequest:
    """Keep the original requested date and validate against the submission snapshots."""
    clean_reason: str = reason.strip()
    if not clean_reason or len(clean_reason) > 500:
        raise ValidationError({"reason": "Enter a nonblank reason of at most 500 characters."})
    with transaction.atomic():
        borrow_request: BorrowRequest = _approved_request(actor_id, request_id)
        revised: date = validate_revised_due_date(
            borrow_request.submitted_on,
            agreed_due_date,
            timezone.localdate(),
            LoanLimits(borrow_request.max_loan_days_applied, borrow_request.max_quantity_applied),
        )
        if revised == borrow_request.agreed_due_date:
            raise ValidationError({"agreed_due_date": "Choose a different agreed due date."})
        previous: date = borrow_request.agreed_due_date
        borrow_request.agreed_due_date = revised
        borrow_request.save(update_fields=["agreed_due_date"])
        write_audit(
            actor_id,
            AuditAction.DUE_DATE_REVISED,
            AuditTarget.BORROW_REQUEST,
            request_id,
            f"Request #{request_id} due date revised from {previous} to {revised}: {clean_reason}",
        )
        return borrow_request


def release_request(actor_id: int, request_id: int) -> Loan:
    """Issue every reserved unit and its audit together; keep allocations active until return."""
    with transaction.atomic():
        borrow_request: BorrowRequest = _approved_request(actor_id, request_id)
        try:
            reserved: ReservedUnits = lock_reserved_units(request_id)
        except ReservationConflict as error:
            raise WorkflowConflict(str(error)) from error
        issued_at: datetime = timezone.now()
        issued_on: date = timezone.localdate(issued_at)
        if issued_on > borrow_request.agreed_due_date:
            raise WorkflowConflict(
                "The agreed due date has passed. Revise it within the submission limit, "
                "or ask the borrower to cancel and submit a new request."
            )
        loan: Loan = Loan.objects.create(
            request=borrow_request,
            issued_by_id=actor_id,
            issued_at=issued_at,
            issued_on=issued_on,
            due_date=borrow_request.agreed_due_date,
        )
        LoanUnit.objects.bulk_create(
            [LoanUnit(loan=loan, allocation=allocation) for allocation in reserved.allocations]
        )
        for allocation in reserved.allocations:
            allocation.released_at = issued_at
            allocation.save(update_fields=["released_at"])
        for unit in reserved.units:
            unit.status = UnitStatus.ISSUED
            unit.save(update_fields=["status", "updated_at"])
        borrow_request.status = RequestStatus.ISSUED
        borrow_request.save(update_fields=["status"])
        write_audit(
            actor_id,
            AuditAction.LOAN_RELEASED,
            AuditTarget.LOAN,
            loan.pk,
            f"Released request #{request_id} as loan #{loan.pk}; "
            f"{len(reserved.units)} unit(s), due {loan.due_date}.",
        )
        return loan
