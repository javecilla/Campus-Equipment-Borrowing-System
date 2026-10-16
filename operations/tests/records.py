"""Fictional records for schema and shared-service integration checks."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.utils import timezone

from accounts.models import Profile, User, UserRole
from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestItem,
    RequestStatus,
    UnitAllocation,
)
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitCondition, UnitStatus


@dataclass(frozen=True)
class CatalogRecords:
    admin: User
    borrower: User
    category: Category
    item: CatalogItem
    unit: EquipmentUnit


@dataclass(frozen=True)
class IssuedRecords:
    catalog: CatalogRecords
    request: BorrowRequest
    request_item: RequestItem
    allocation: UnitAllocation
    loan: Loan
    loan_unit: LoanUnit


def create_catalog_records() -> CatalogRecords:
    admin: User = User.objects.create_user(
        username="fictional_admin",
        email="admin@example.invalid",
        password=None,
        first_name="Fictional",
        last_name="Admin",
        role=UserRole.ADMIN,
    )
    borrower: User = User.objects.create_user(
        username="fictional_borrower",
        email="borrower@example.invalid",
        password=None,
        first_name="Fictional",
        last_name="Borrower",
        role=UserRole.BASIC_USER,
    )
    Profile.objects.create(user=admin, contact_number="")
    Profile.objects.create(user=borrower, contact_number="")
    category: Category = Category.objects.create(name="Test cameras", description="")
    item: CatalogItem = CatalogItem.objects.create(
        category=category, name="Test camera", description="Camera for integration checks."
    )
    unit: EquipmentUnit = EquipmentUnit.objects.create(
        catalog_item=item,
        asset_code="TEST-CAM-001",
        condition=UnitCondition.GOOD,
        acquired_on=timezone.localdate(),
        status=UnitStatus.AVAILABLE,
        internal_notes="",
    )
    return CatalogRecords(admin=admin, borrower=borrower, category=category, item=item, unit=unit)


def create_request(owner_id: int, catalog_item_id: int, submitted_at: datetime) -> RequestItem:
    submitted_on = timezone.localdate(submitted_at)
    request: BorrowRequest = BorrowRequest.objects.create(
        owner_id=owner_id,
        purpose="Fictional classroom activity",
        submitted_at=submitted_at,
        submitted_on=submitted_on,
        desired_due_date=submitted_on + timedelta(days=3),
        agreed_due_date=submitted_on + timedelta(days=3),
        max_loan_days_applied=7,
        max_quantity_applied=3,
        status=RequestStatus.PENDING,
        decision_reason="",
    )
    return RequestItem.objects.create(request=request, catalog_item_id=catalog_item_id, quantity=1)


def create_issued_records() -> IssuedRecords:
    catalog: CatalogRecords = create_catalog_records()
    issued_at: datetime = timezone.now()
    request_item: RequestItem = create_request(
        catalog.borrower.pk, catalog.item.pk, issued_at - timedelta(days=1)
    )
    request: BorrowRequest = request_item.request
    request.status = RequestStatus.ISSUED
    request.decided_by = catalog.admin
    request.decided_at = issued_at
    request.decision_reason = "Fictional approved request"
    request.save(update_fields=["status", "decided_by", "decided_at", "decision_reason"])
    EquipmentUnit.objects.filter(pk=catalog.unit.pk).update(status=UnitStatus.ISSUED)
    allocation: UnitAllocation = UnitAllocation.objects.create(
        request_item=request_item,
        unit=catalog.unit,
        allocated_at=issued_at,
        allocated_by=catalog.admin,
        released_at=issued_at,
    )
    loan: Loan = Loan.objects.create(
        request=request,
        issued_by=catalog.admin,
        issued_at=issued_at,
        issued_on=timezone.localdate(issued_at),
        due_date=request.agreed_due_date,
    )
    loan_unit: LoanUnit = LoanUnit.objects.create(loan=loan, allocation=allocation)
    return IssuedRecords(
        catalog=catalog,
        request=request,
        request_item=request_item,
        allocation=allocation,
        loan=loan,
        loan_unit=loan_unit,
    )
