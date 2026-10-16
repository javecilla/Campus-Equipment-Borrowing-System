"""Pure request-limit and campus-calendar validation shared by feature owners."""

from dataclasses import dataclass
from datetime import date

from django.core.exceptions import ValidationError


@dataclass(frozen=True)
class LoanLimits:
    max_loan_days: int
    max_quantity_per_item: int


@dataclass(frozen=True)
class RequestedItem:
    catalog_item_id: int
    quantity: int


def validate_loan_limits(max_loan_days: int, max_quantity_per_item: int) -> LoanLimits:
    for field, value in (
        ("max_loan_days", max_loan_days),
        ("max_quantity_per_item", max_quantity_per_item),
    ):
        if type(value) is not int or not 1 <= value <= 2147483647:
            raise ValidationError({field: "Enter a positive integer no greater than 2147483647."})
    return LoanLimits(max_loan_days=max_loan_days, max_quantity_per_item=max_quantity_per_item)


def validate_requested_items(
    items: tuple[RequestedItem, ...], limits: LoanLimits
) -> tuple[RequestedItem, ...]:
    validate_loan_limits(limits.max_loan_days, limits.max_quantity_per_item)
    if not 1 <= len(items) <= 3:
        raise ValidationError("A request must contain one to three distinct catalog items.")
    if any(type(item.catalog_item_id) is not int or item.catalog_item_id < 1 for item in items):
        raise ValidationError("Every catalog item ID must be a positive integer.")
    if len({item.catalog_item_id for item in items}) != len(items):
        raise ValidationError("A catalog item can appear only once in a request.")
    for item in items:
        if type(item.quantity) is not int or not 1 <= item.quantity <= limits.max_quantity_per_item:
            raise ValidationError(
                f"Catalog item {item.catalog_item_id} requires a positive quantity within the snapshotted limit of {limits.max_quantity_per_item}."
            )
    return items


def validate_requested_due_date(
    submitted_on: date, desired_due_date: date, limits: LoanLimits
) -> date:
    validate_loan_limits(limits.max_loan_days, limits.max_quantity_per_item)
    duration: int = (desired_due_date - submitted_on).days
    if not 1 <= duration <= limits.max_loan_days:
        raise ValidationError(
            {
                "desired_due_date": f"Choose a date after submission and within {limits.max_loan_days} calendar days."
            }
        )
    return desired_due_date


def validate_revised_due_date(
    submitted_on: date, proposed_due_date: date, today: date, limits: LoanLimits
) -> date:
    validate_requested_due_date(submitted_on, proposed_due_date, limits)
    if proposed_due_date < today:
        raise ValidationError(
            {"agreed_due_date": "The revised due date cannot be before today's campus date."}
        )
    return proposed_due_date
