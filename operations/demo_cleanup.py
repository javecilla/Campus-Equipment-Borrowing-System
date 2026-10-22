"""Explicit local data purges, separate from ordinary audited workflow actions.

Stop application/database writers before invoking these destructive CLI tools.
Each purge is atomic; uploaded files and account/settings records are preserved.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestItem,
    ReturnRecord,
    UnitAllocation,
)
from inventory.models import EquipmentUnit, MaintenanceRecord, UnitCondition, UnitStatus
from operations.models import AuditLog, AuditTarget


@transaction.atomic
def clear_borrowing_data() -> None:
    """Purge all borrowing history; retain stock and maintenance, detaching return links."""
    busy_units: QuerySet[EquipmentUnit] = EquipmentUnit.objects.filter(
        status__in=(UnitStatus.RESERVED, UnitStatus.ISSUED)
    )
    if busy_units.filter(condition=UnitCondition.DAMAGED).exists():
        raise ValidationError(
            "Cannot clear borrowing: damaged stock is Reserved/Issued. Correct the inconsistent stock record first."
        )
    MaintenanceRecord.objects.filter(source_return__isnull=False).update(source_return=None)
    ReturnRecord.objects.all().delete()
    LoanUnit.objects.all().delete()
    Loan.objects.all().delete()
    UnitAllocation.objects.all().delete()
    RequestItem.objects.all().delete()
    BorrowRequest.objects.all().delete()
    busy_units.update(status=UnitStatus.AVAILABLE, updated_at=timezone.now())
    AuditLog.objects.filter(
        target_model__in=(AuditTarget.BORROW_REQUEST, AuditTarget.LOAN, AuditTarget.RETURN_RECORD)
    ).delete()


@transaction.atomic
def clear_equipment_units() -> None:
    """Remove all physical stock and maintenance while retaining catalog/photo references."""
    if BorrowRequest.objects.exists():
        raise ValidationError(
            "Borrowing history exists. Run clear_borrowing_data before clear_equipment_units."
        )
    MaintenanceRecord.objects.all().delete()
    EquipmentUnit.objects.all().delete()
    AuditLog.objects.filter(
        target_model__in=(AuditTarget.EQUIPMENT_UNIT, AuditTarget.MAINTENANCE_RECORD)
    ).delete()
