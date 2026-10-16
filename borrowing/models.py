"""Request, reservation, issue, and per-unit return persistence contracts."""

from django.conf import settings
from django.db import models
from django.db.models.lookups import LessThanOrEqual

from inventory.models import UnitCondition


class RequestStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"
    ISSUED = "ISSUED", "Issued"
    PARTIALLY_RETURNED = "PARTIALLY_RETURNED", "Partially returned"
    RETURNED = "RETURNED", "Returned"


def days_since_submission(date_field: str) -> models.Func:
    """PostgreSQL date subtraction avoids overflow from adding an integer limit."""
    return models.Func(
        models.F(date_field),
        models.F("submitted_on"),
        arg_joiner=" - ",
        output_field=models.IntegerField(),
        template="(%(expressions)s)",
    )


class BorrowRequest(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="borrow_requests"
    )
    purpose = models.TextField()
    submitted_at = models.DateTimeField()
    submitted_on = models.DateField()
    desired_due_date = models.DateField()
    agreed_due_date = models.DateField()
    max_loan_days_applied = models.PositiveIntegerField()
    max_quantity_applied = models.PositiveIntegerField()
    status = models.CharField(max_length=18, choices=RequestStatus.choices)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requests_decided",
        null=True,
        blank=True,
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requests_cancelled",
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes: list[models.Index] = [
            models.Index(fields=["owner", "submitted_at"], name="request_owner_submitted_idx"),
            models.Index(fields=["status", "submitted_at"], name="request_status_submitted_idx"),
        ]
        constraints: list[models.BaseConstraint] = [
            models.CheckConstraint(
                condition=models.Q(purpose__regex=r"\S"), name="request_nonblank_purpose"
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=RequestStatus.values), name="request_valid_status"
            ),
            models.CheckConstraint(
                condition=models.Q(max_loan_days_applied__gt=0, max_quantity_applied__gt=0),
                name="request_positive_limits",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    desired_due_date__gt=models.F("submitted_on"),
                    agreed_due_date__gt=models.F("submitted_on"),
                ),
                name="request_due_after_submission",
            ),
            models.CheckConstraint(
                condition=LessThanOrEqual(
                    days_since_submission("desired_due_date"), models.F("max_loan_days_applied")
                )
                & LessThanOrEqual(
                    days_since_submission("agreed_due_date"), models.F("max_loan_days_applied")
                ),
                name="request_due_within_limit",
            ),
            models.CheckConstraint(
                condition=models.Q(decided_by__isnull=True, decided_at__isnull=True)
                | models.Q(decided_by__isnull=False, decided_at__isnull=False),
                name="request_decision_actor_time",
            ),
            models.CheckConstraint(
                condition=models.Q(decided_by__isnull=True)
                | models.Q(decision_reason__regex=r"\S"),
                name="request_decision_has_reason",
            ),
            models.CheckConstraint(
                condition=models.Q(cancelled_by__isnull=True, cancelled_at__isnull=True)
                | models.Q(cancelled_by__isnull=False, cancelled_at__isnull=False),
                name="request_cancel_actor_time",
            ),
        ]


class RequestItem(models.Model):
    request = models.ForeignKey(BorrowRequest, on_delete=models.PROTECT, related_name="items")
    catalog_item = models.ForeignKey(
        "inventory.CatalogItem", on_delete=models.PROTECT, related_name="request_items"
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.UniqueConstraint(
                fields=["request", "catalog_item"], name="request_item_unique_catalog"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0), name="request_item_positive_quantity"
            ),
        ]


class UnitAllocation(models.Model):
    request_item = models.ForeignKey(
        RequestItem, on_delete=models.PROTECT, related_name="allocations"
    )
    unit = models.ForeignKey(
        "inventory.EquipmentUnit", on_delete=models.PROTECT, related_name="allocations"
    )
    allocated_at = models.DateTimeField()
    allocated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="allocations_approved"
    )
    released_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.UniqueConstraint(
                fields=["request_item", "unit"], name="allocation_unique_request_unit"
            ),
            models.UniqueConstraint(
                fields=["unit"],
                condition=models.Q(ended_at__isnull=True),
                name="allocation_one_active_unit",
            ),
            models.CheckConstraint(
                condition=models.Q(released_at__isnull=True)
                | models.Q(released_at__gte=models.F("allocated_at")),
                name="allocation_release_after_start",
            ),
            models.CheckConstraint(
                condition=models.Q(cancelled_at__isnull=True)
                | models.Q(cancelled_at__gte=models.F("allocated_at")),
                name="allocation_cancel_after_start",
            ),
            models.CheckConstraint(
                condition=models.Q(ended_at__isnull=True)
                | models.Q(ended_at__gte=models.F("allocated_at")),
                name="allocation_end_after_start",
            ),
            models.CheckConstraint(
                condition=models.Q(released_at__isnull=True) | models.Q(cancelled_at__isnull=True),
                name="allocation_not_released_cancelled",
            ),
            models.CheckConstraint(
                condition=models.Q(cancelled_at__isnull=True)
                | models.Q(ended_at__isnull=False, ended_at=models.F("cancelled_at")),
                name="allocation_cancel_ends_reservation",
            ),
            models.CheckConstraint(
                condition=models.Q(released_at__isnull=True)
                | models.Q(ended_at__isnull=True)
                | models.Q(ended_at__gte=models.F("released_at")),
                name="allocation_end_after_release",
            ),
        ]


class Loan(models.Model):
    request = models.OneToOneField(BorrowRequest, on_delete=models.PROTECT, related_name="loan")
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="loans_issued"
    )
    issued_at = models.DateTimeField()
    issued_on = models.DateField()
    due_date = models.DateField()
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes: list[models.Index] = [
            models.Index(fields=["issued_at"], name="loan_issued_at_idx"),
            models.Index(fields=["due_date"], name="loan_due_date_idx"),
        ]
        constraints: list[models.BaseConstraint] = [
            models.CheckConstraint(
                condition=models.Q(due_date__gte=models.F("issued_on")),
                name="loan_due_on_or_after_issue",
            ),
            models.CheckConstraint(
                condition=models.Q(closed_at__isnull=True)
                | models.Q(closed_at__gte=models.F("issued_at")),
                name="loan_closure_after_issue",
            ),
        ]


class LoanUnit(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT, related_name="units")
    allocation = models.OneToOneField(
        UnitAllocation, on_delete=models.PROTECT, related_name="loan_unit"
    )


class ReturnRecord(models.Model):
    loan_unit = models.OneToOneField(
        LoanUnit, on_delete=models.PROTECT, related_name="return_record"
    )
    returned_at = models.DateTimeField()
    returned_condition = models.CharField(max_length=10, choices=UnitCondition.choices)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="returns_received"
    )
    notes = models.TextField(blank=True)

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.CheckConstraint(
                condition=models.Q(returned_condition__in=UnitCondition.values),
                name="return_valid_condition",
            ),
        ]
