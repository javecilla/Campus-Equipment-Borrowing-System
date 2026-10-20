"""Atomic per-unit returns, including damaged-return maintenance and final closure."""

from dataclasses import dataclass
from datetime import datetime

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.access import require_active_admin
from accounts.models import User
from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestStatus,
    ReturnRecord,
    UnitAllocation,
)
from borrowing.services import WorkflowConflict
from inventory.models import (
    EquipmentUnit,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitCondition,
    UnitStatus,
)
from operations.audit import write_audit
from operations.locking import LockedRequest, lock_request, lock_units
from operations.models import AuditAction, AuditTarget


@dataclass(frozen=True)
class ReturnInput:
    loan_unit_id: int
    returned_condition: str
    notes: str
    maintenance_problem: str


def validate_returns(rows: tuple[ReturnInput, ...]) -> tuple[ReturnInput, ...]:
    """Validate every selected row before persistence; never alter caller-owned inputs."""
    if not rows:
        raise ValidationError("Select at least one issued unit to return.")
    identifiers: tuple[int, ...] = tuple(row.loan_unit_id for row in rows)
    if any(type(identifier) is not int or identifier < 1 for identifier in identifiers):
        raise ValidationError("Select valid issued units.")
    if len(set(identifiers)) != len(identifiers):
        raise ValidationError("Select each issued unit only once.")
    for row in rows:
        if row.returned_condition not in UnitCondition.values:
            raise ValidationError("Choose Good, Fair or Damaged for each selected unit.")
        if row.returned_condition == UnitCondition.DAMAGED and not row.maintenance_problem.strip():
            raise ValidationError("Describe the maintenance problem for every damaged return.")
    return tuple(
        ReturnInput(
            row.loan_unit_id,
            row.returned_condition,
            row.notes.strip(),
            row.maintenance_problem.strip(),
        )
        for row in rows
    )


def return_units(actor_id: int, loan_id: int, rows: tuple[ReturnInput, ...]) -> Loan:
    """Return the complete selection or nothing, using the shared parent/unit lock order.

    Existing loans remain returnable after borrower deactivation or catalog archival.
    Released allocations stay exclusive until their individual return commits.
    """
    clean_rows: tuple[ReturnInput, ...] = validate_returns(rows)
    with transaction.atomic():
        try:
            actor: User = User.objects.select_for_update().get(pk=actor_id)
        except User.DoesNotExist as error:
            raise PermissionDenied(
                "The performing administrator account does not exist."
            ) from error
        require_active_admin(actor)
        parent_ids: tuple[int, int] = Loan.objects.values_list(
            "request_id", "request__owner_id"
        ).get(pk=loan_id)
        request_id: int = parent_ids[0]
        owner_id: int = parent_ids[1]
        locked: LockedRequest = lock_request(owner_id, request_id)
        loan: Loan | None = locked.loan
        borrow_request: BorrowRequest = locked.request
        if (
            loan is None
            or loan.pk != loan_id
            or loan.closed_at is not None
            or borrow_request.status not in (RequestStatus.ISSUED, RequestStatus.PARTIALLY_RETURNED)
        ):
            raise WorkflowConflict("Only an active issued loan can receive returns.")

        identifiers: tuple[int, ...] = tuple(sorted(row.loan_unit_id for row in clean_rows))
        membership: tuple[tuple[int, int, int], ...] = tuple(
            LoanUnit.objects.filter(loan_id=loan_id, pk__in=identifiers)
            .order_by("pk")
            .values_list("pk", "allocation_id", "allocation__unit_id")
        )
        if tuple(row[0] for row in membership) != identifiers:
            raise WorkflowConflict("Every selected unit must belong to this loan.")
        units: tuple[EquipmentUnit, ...] = lock_units(tuple(row[2] for row in membership))
        allocations: dict[int, UnitAllocation] = {
            allocation.pk: allocation
            for allocation in UnitAllocation.objects.select_related("request_item")
            .select_for_update(of=("self",))
            .filter(pk__in=[row[1] for row in membership])
            .order_by("pk")
        }
        loan_units: tuple[LoanUnit, ...] = tuple(
            LoanUnit.objects.select_for_update()
            .filter(loan_id=loan_id, pk__in=identifiers)
            .order_by("pk")
        )
        if (
            tuple(
                (row.pk, row.allocation_id, allocations[row.allocation_id].unit_id)
                for row in loan_units
            )
            != membership
        ):
            raise WorkflowConflict("Issued unit relationships changed; refresh before retrying.")
        if ReturnRecord.objects.filter(loan_unit_id__in=identifiers).exists():
            raise WorkflowConflict("A selected unit has already been returned. Refresh the loan.")
        if MaintenanceRecord.objects.filter(
            unit_id__in=[unit.pk for unit in units], status=MaintenanceStatus.OPEN
        ).exists():
            raise WorkflowConflict("A selected issued unit already has open maintenance.")

        returned_at: datetime = timezone.now()
        if returned_at < loan.issued_at:
            raise WorkflowConflict("A return cannot occur before the loan was issued.")
        units_by_id: dict[int, EquipmentUnit] = {unit.pk: unit for unit in units}
        rows_by_id: dict[int, ReturnInput] = {row.loan_unit_id: row for row in clean_rows}
        for loan_unit in loan_units:
            allocation: UnitAllocation = allocations[loan_unit.allocation_id]
            unit: EquipmentUnit = units_by_id[allocation.unit_id]
            if (
                allocation.request_item.request_id != request_id
                or allocation.request_item.catalog_item_id != unit.catalog_item_id
                or allocation.released_at is None
                or allocation.released_at > returned_at
                or allocation.ended_at is not None
                or allocation.cancelled_at is not None
                or unit.status != UnitStatus.ISSUED
            ):
                raise WorkflowConflict("A selected unit is no longer an outstanding issued unit.")
            row: ReturnInput = rows_by_id[loan_unit.pk]
            returned: ReturnRecord = ReturnRecord.objects.create(
                loan_unit=loan_unit,
                returned_at=returned_at,
                returned_condition=row.returned_condition,
                received_by_id=actor_id,
                notes=row.notes,
            )
            allocation.ended_at = returned_at
            allocation.save(update_fields=["ended_at"])
            unit.condition = row.returned_condition
            unit.status = (
                UnitStatus.MAINTENANCE
                if row.returned_condition == UnitCondition.DAMAGED
                else UnitStatus.AVAILABLE
            )
            unit.save(update_fields=["condition", "status", "updated_at"])
            write_audit(
                actor_id,
                AuditAction.UNIT_RETURNED,
                AuditTarget.RETURN_RECORD,
                returned.pk,
                f"Returned {unit.asset_code} on loan #{loan_id}: {row.returned_condition}.",
            )
            if row.returned_condition == UnitCondition.DAMAGED:
                maintenance: MaintenanceRecord = MaintenanceRecord.objects.create(
                    unit=unit,
                    source_return=returned,
                    problem=row.maintenance_problem,
                    opened_at=returned_at,
                    opened_by_id=actor_id,
                    status=MaintenanceStatus.OPEN,
                )
                write_audit(
                    actor_id,
                    AuditAction.MAINTENANCE_OPENED,
                    AuditTarget.MAINTENANCE_RECORD,
                    maintenance.pk,
                    f"Opened maintenance for damaged return #{returned.pk}, "
                    f"physical unit {unit.asset_code}: {row.maintenance_problem}.",
                )

        if LoanUnit.objects.filter(loan_id=loan_id, return_record__isnull=True).exists():
            borrow_request.status = RequestStatus.PARTIALLY_RETURNED
        else:
            borrow_request.status = RequestStatus.RETURNED
            loan.closed_at = returned_at
            loan.save(update_fields=["closed_at"])
        borrow_request.save(update_fields=["status"])
        return loan
