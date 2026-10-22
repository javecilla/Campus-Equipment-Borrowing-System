"""Import fictional historical events through the accepted workflow services.

Services perform every state transition using server time. Only records created
in this transaction are then given their original historical event dates. Master
record entry timestamps remain the real database registration/import times.
"""

from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from accounts.access import require_active_admin, require_active_basic_user
from accounts.models import User
from borrowing.models import BorrowRequest, Loan, LoanUnit, ReturnRecord, UnitAllocation
from borrowing.release_services import release_request
from borrowing.return_services import ReturnInput, return_units
from borrowing.services import approve_request, cancel_request, reject_request, submit_request
from inventory.models import (
    CatalogItem,
    EquipmentUnit,
    MaintenanceOutcome,
    MaintenanceRecord,
    UnitCondition,
)
from inventory.services import close_maintenance
from operations.audit import ACTION_TARGETS
from operations.demo_seed import DEMO_ADMIN, DEMO_BORROWERS
from operations.demo_transaction_plan import (
    APPROVED,
    APPROVED_CANCELLATIONS,
    CANCELLED,
    LOANS,
    PENDING,
    REJECTED,
    LoanPlan,
    RequestPlan,
)
from operations.models import AuditAction, AuditLog
from operations.validation import RequestedItem

HISTORY_START = date(2026, 8, 1)
HISTORY_AS_OF = date(2026, 10, 22)


def _date_audit(action: AuditAction, target_id: int, occurred_at: datetime) -> None:
    event: AuditLog = AuditLog.objects.get(
        action=action, target_model=ACTION_TARGETS[action], target_id=target_id
    )
    event.occurred_at = occurred_at
    event.full_clean()
    event.save(update_fields=["occurred_at"])


def _submit(plan: RequestPlan, today: date) -> BorrowRequest:
    """Resolve the existing named equipment and capture real configured limits."""
    owner: User = User.objects.get(username=plan.borrower)
    items: list[RequestedItem] = []
    for name in plan.items:
        try:
            item: CatalogItem = CatalogItem.objects.get(name=name)
        except CatalogItem.DoesNotExist as error:
            raise ValidationError(
                f'History requires the existing equipment "{name}". Register its catalog record and physical stock before importing.'
            ) from error
        except CatalogItem.MultipleObjectsReturned as error:
            raise ValidationError(
                f'Equipment name "{name}" is ambiguous. Resolve duplicate catalog names before importing this fixed history.'
            ) from error
        items.append(RequestedItem(item.pk, 1))
    duration: timedelta = plan.due_date - timezone.localdate(plan.submitted_at)
    if not HISTORY_START <= timezone.localdate(plan.submitted_at) <= HISTORY_AS_OF:
        raise ValidationError(f"Request date is outside the demonstration period: {plan.purpose}.")
    if plan.due_date > date(2026, 10, 31):
        raise ValidationError(f"Due date is outside August-October 2026: {plan.purpose}.")
    return submit_request(owner.pk, plan.purpose, today + duration, tuple(items))


def _date_request(request_id: int, plan: RequestPlan) -> None:
    request: BorrowRequest = BorrowRequest.objects.get(pk=request_id)
    decision_at: datetime = plan.submitted_at + timedelta(minutes=30)
    cancelled_at: datetime = plan.submitted_at + timedelta(hours=3)
    BorrowRequest.objects.filter(pk=request_id).update(
        submitted_at=plan.submitted_at,
        submitted_on=timezone.localdate(plan.submitted_at),
        desired_due_date=plan.due_date,
        agreed_due_date=plan.due_date,
        decided_at=decision_at if request.decided_at is not None else None,
        cancelled_at=cancelled_at if request.cancelled_at is not None else None,
    )
    if request.decided_at is not None:
        event: AuditLog = AuditLog.objects.get(
            target_model=ACTION_TARGETS[AuditAction.REQUEST_APPROVED],
            target_id=request_id,
            action__in=(AuditAction.REQUEST_APPROVED, AuditAction.REQUEST_REJECTED),
        )
        _date_audit(AuditAction(event.action), request_id, decision_at)
    if request.cancelled_at is not None:
        _date_audit(AuditAction.REQUEST_CANCELLED, request_id, cancelled_at)
    # Only reservations without a loan belong here; issue/return dates are mapped below.
    if not Loan.objects.filter(request_id=request_id).exists():
        UnitAllocation.objects.filter(request_item__request_id=request_id).update(
            allocated_at=decision_at,
            cancelled_at=cancelled_at if request.cancelled_at is not None else None,
            ended_at=cancelled_at if request.cancelled_at is not None else None,
        )


def _seed_loan(admin_id: int, plan: LoanPlan, today: date) -> None:
    request: BorrowRequest = _submit(plan.request, today)
    approve_request(
        admin_id, request.pk, "Equipment reserved for the scheduled class or campus activity."
    )
    loan: Loan = release_request(admin_id, request.pk)
    returned_times: dict[int, datetime] = {}
    repair_times: dict[int, datetime] = {}
    for batch in plan.returns:
        rows: tuple[ReturnInput, ...] = tuple(
            ReturnInput(
                LoanUnit.objects.get(loan=loan, allocation__unit__catalog_item__name=name).pk,
                batch.condition,
                batch.notes,
                batch.maintenance_problem,
            )
            for name in batch.items
        )
        return_units(admin_id, loan.pk, rows)
        for row in rows:
            returned: ReturnRecord = ReturnRecord.objects.get(loan_unit_id=row.loan_unit_id)
            returned_times[returned.pk] = batch.returned_at
    for repair in plan.repairs:
        maintenance: MaintenanceRecord = MaintenanceRecord.objects.get(
            source_return__loan_unit__loan=loan, unit__catalog_item__name=repair.item
        )
        close_maintenance(
            admin_id,
            maintenance.pk,
            repair.action,
            MaintenanceOutcome.AVAILABLE,
            UnitCondition.GOOD,
        )
        repair_times[maintenance.pk] = repair.closed_at

    _date_request(request.pk, plan.request)
    loan.refresh_from_db()
    original_due: date = loan.due_date
    Loan.objects.filter(pk=loan.pk).update(
        issued_at=plan.issued_at,
        issued_on=timezone.localdate(plan.issued_at),
        due_date=plan.request.due_date,
        closed_at=max(returned_times.values()) if loan.closed_at is not None else None,
    )
    for row in loan.units.select_related("allocation", "return_record"):
        ended_at: datetime | None = (
            returned_times[row.return_record.pk] if hasattr(row, "return_record") else None
        )
        UnitAllocation.objects.filter(pk=row.allocation_id).update(
            allocated_at=plan.request.submitted_at + timedelta(minutes=30),
            released_at=plan.issued_at,
            ended_at=ended_at,
        )
    for returned_id, at in returned_times.items():
        ReturnRecord.objects.filter(pk=returned_id).update(returned_at=at)
        _date_audit(AuditAction.UNIT_RETURNED, returned_id, at)
        for maintenance in MaintenanceRecord.objects.filter(source_return_id=returned_id):
            MaintenanceRecord.objects.filter(pk=maintenance.pk).update(
                opened_at=at, closed_at=repair_times.get(maintenance.pk)
            )
            _date_audit(AuditAction.MAINTENANCE_OPENED, maintenance.pk, at)
            if maintenance.pk in repair_times:
                _date_audit(
                    AuditAction.MAINTENANCE_CLOSED, maintenance.pk, repair_times[maintenance.pk]
                )
    event: AuditLog = AuditLog.objects.get(action=AuditAction.LOAN_RELEASED, target_id=loan.pk)
    due_text: str = f"due {original_due}"
    if due_text not in event.summary:
        raise ValidationError(f"Loan {loan.pk} release audit is missing its original due date.")
    event.summary = event.summary.replace(due_text, f"due {plan.request.due_date}")
    event.save(update_fields=["summary"])
    _date_audit(AuditAction.LOAN_RELEASED, loan.pk, plan.issued_at)


def _validate_history() -> None:
    """Check imported event ordering, acquisition dates and exclusive physical stock."""
    now: datetime = timezone.now()
    for request in BorrowRequest.objects.all():
        request.full_clean()
        if request.submitted_at > now:
            raise ValidationError(f"Request {request.pk} has a future submission timestamp.")
    for unit in EquipmentUnit.objects.all():
        unit.full_clean()
        previous: UnitAllocation | None = None
        for allocation in unit.allocations.select_related("request_item__request").order_by(
            "allocated_at", "pk"
        ):
            allocation.full_clean()
            if unit.acquired_on > timezone.localdate(allocation.allocated_at):
                raise ValidationError(
                    f"Unit {unit.asset_code} was allocated before acquisition on {unit.acquired_on}."
                )
            if allocation.request_item.catalog_item_id != unit.catalog_item_id:
                raise ValidationError(
                    f"Allocation {allocation.pk} references the wrong catalog item."
                )
            if previous is not None and (
                previous.ended_at is None or previous.ended_at > allocation.allocated_at
            ):
                raise ValidationError(f"Historical allocations overlap for unit {unit.asset_code}.")
            end: datetime = allocation.ended_at if allocation.ended_at is not None else now
            if (
                MaintenanceRecord.objects.filter(unit=unit, opened_at__lt=end)
                .filter(Q(closed_at__isnull=True) | Q(closed_at__gt=allocation.allocated_at))
                .exists()
            ):
                raise ValidationError(f"Unit {unit.asset_code} was allocated during maintenance.")
            previous = allocation
    for loan in Loan.objects.select_related("request"):
        loan.full_clean()
        if not loan.request.decided_at <= loan.issued_at <= now:
            raise ValidationError(f"Loan {loan.pk} has inconsistent issue/approval dates.")
        for row in loan.units.select_related("allocation", "return_record"):
            if row.allocation.released_at != loan.issued_at:
                raise ValidationError(f"Loan unit {row.pk} release date differs from issue.")
            if hasattr(row, "return_record"):
                returned: ReturnRecord = row.return_record
                returned.full_clean()
                if (
                    not loan.issued_at <= returned.returned_at <= now
                    or row.allocation.ended_at != returned.returned_at
                ):
                    raise ValidationError(f"Loan unit {row.pk} has inconsistent return dates.")


@transaction.atomic
def seed_demo_transactions(today: date) -> None:
    """Import the fixed 2026 history once into existing equipment and account records."""
    if today != timezone.localdate() or today < HISTORY_AS_OF:
        raise ValidationError(
            "Use the actual campus date, on or after October 22, 2026, for this history import."
        )
    actors: tuple[User, ...] = tuple(
        User.objects.select_for_update()
        .filter(
            username__in=(DEMO_ADMIN.username, *(identity.username for identity in DEMO_BORROWERS))
        )
        .order_by("pk")
    )
    if len(actors) != 9:
        raise ValidationError(
            "Create the documented one-admin/eight-borrower accounts before importing history."
        )
    admin: User = next(user for user in actors if user.username == DEMO_ADMIN.username)
    require_active_admin(admin)
    for user in actors:
        if user.pk != admin.pk:
            require_active_basic_user(user)
    if BorrowRequest.objects.exists() or Loan.objects.exists():
        raise ValidationError(
            "Borrowing history already exists. No records changed; this import requires an empty borrowing history and never overwrites transactions."
        )
    for plan in LOANS:
        _seed_loan(admin.pk, plan, today)
    for plan, reason in REJECTED:
        request: BorrowRequest = _submit(plan, today)
        reject_request(admin.pk, request.pk, reason)
        _date_request(request.pk, plan)
    for plan in CANCELLED:
        request = _submit(plan, today)
        cancel_request(request.owner_id, request.pk)
        _date_request(request.pk, plan)
    for plan in APPROVED_CANCELLATIONS:
        request = _submit(plan, today)
        approve_request(admin.pk, request.pk, "Reserved for the confirmed activity schedule.")
        cancel_request(request.owner_id, request.pk)
        _date_request(request.pk, plan)
    for plan in APPROVED:
        request = _submit(plan, today)
        approve_request(
            admin.pk, request.pk, "Approved for the scheduled activity; awaiting collection."
        )
        _date_request(request.pk, plan)
    for plan in PENDING:
        request = _submit(plan, today)
        _date_request(request.pk, plan)
    _validate_history()
