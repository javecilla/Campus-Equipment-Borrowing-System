"""Atomic borrower request-submission workflow."""

from datetime import date, datetime

from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.access import require_active_basic_user
from accounts.models import User
from borrowing.models import BorrowRequest, RequestItem, RequestStatus
from inventory.models import CatalogItem, Category
from operations.locking import lock_borrower, lock_catalog
from operations.models import SystemSetting
from operations.validation import (
    LoanLimits,
    RequestedItem,
    validate_loan_limits,
    validate_requested_due_date,
    validate_requested_items,
)


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
