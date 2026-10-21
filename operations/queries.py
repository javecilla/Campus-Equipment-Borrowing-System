"""Read operational settings, audit history, dashboards, and loan reports."""

from dataclasses import dataclass
from datetime import date

from django.core.exceptions import ImproperlyConfigured
from django.db.models import CharField, Count, F, Q, QuerySet, Value
from django.db.models.functions import Cast, Concat, TruncMonth

from borrowing.models import BorrowRequest, Loan, LoanUnit, RequestStatus
from borrowing.queries import with_loan_progress
from inventory.models import EquipmentUnit, UnitStatus
from operations.models import AuditLog, SystemSetting
from operations.validation import LoanLimits, validate_loan_limits


@dataclass(frozen=True)
class DashboardCards:
    available_units: int
    pending_requests: int
    active_loans: int
    overdue_loans: int


@dataclass(frozen=True)
class ChartPoint:
    label: str
    value: int


@dataclass(frozen=True)
class DashboardSnapshot:
    cards: DashboardCards
    monthly_issued_loans: tuple[ChartPoint, ...]
    category_issued_units: tuple[ChartPoint, ...]


@dataclass(frozen=True)
class ReportTotals:
    loan_count: int
    issued_quantity: int
    returned_quantity: int
    outstanding_quantity: int


def monthly_issued_loans(today: date) -> tuple[ChartPoint, ...]:
    """Include zero-issue months from the first stored release through the current month."""
    counts: dict[date, int] = {
        row["month"]: row["value"]
        for row in Loan.objects.annotate(month=TruncMonth("issued_on"))
        .values("month")
        .annotate(value=Count("pk"))
        .order_by("month")
    }
    if not counts:
        return ()
    month: date = min(counts)
    last_month: date = max(today.replace(day=1), max(counts))
    points: list[ChartPoint] = []
    while month <= last_month:
        points.append(ChartPoint(label=month.strftime("%b %Y"), value=counts.get(month, 0)))
        month = date(month.year + month.month // 12, month.month % 12 + 1, 1)
    return tuple(points)


def pending_request_count() -> int:
    """Count the current administrator decision queue for dashboard and navigation."""
    return BorrowRequest.objects.filter(status=RequestStatus.PENDING).count()


def dashboard_snapshot(today: date) -> DashboardSnapshot:
    """Return current cards and all-history issue charts from committed records."""
    active_loans: QuerySet[Loan] = with_loan_progress(Loan.objects.all(), today).filter(
        outstanding_quantity__gt=0
    )
    category_issued_units: tuple[ChartPoint, ...] = tuple(
        ChartPoint(label=row["category"], value=row["value"])
        for row in LoanUnit.objects.values(
            category=F("allocation__unit__catalog_item__category__name")
        )
        .annotate(value=Count("pk"))
        .order_by("-value", "category")
    )
    return DashboardSnapshot(
        cards=DashboardCards(
            available_units=EquipmentUnit.objects.filter(status=UnitStatus.AVAILABLE).count(),
            pending_requests=pending_request_count(),
            active_loans=active_loans.count(),
            overdue_loans=active_loans.filter(due_date__lt=today).count(),
        ),
        monthly_issued_loans=monthly_issued_loans(today),
        category_issued_units=category_issued_units,
    )


def loan_report_rows(
    date_from: date | None,
    date_to: date | None,
    today: date,
) -> QuerySet[Loan]:
    """Return date-filtered loans once each with nonmultiplying unit totals."""
    loans: QuerySet[Loan] = with_loan_progress(
        Loan.objects.select_related("request__owner", "issued_by"), today
    )
    if date_from is not None:
        loans = loans.filter(issued_on__gte=date_from)
    if date_to is not None:
        loans = loans.filter(issued_on__lte=date_to)
    return loans.order_by("-issued_on", "-issued_at", "-pk")


def overdue_report_rows(
    date_from: date | None,
    date_to: date | None,
    today: date,
) -> QuerySet[Loan]:
    """Return currently outstanding overdue loans within the issue-date range."""
    return loan_report_rows(date_from, date_to, today).filter(
        outstanding_quantity__gt=0,
        due_date__lt=today,
    )


def report_totals(loans: QuerySet[Loan]) -> ReportTotals:
    """Aggregate the exact filtered report rows without repeating loan-unit joins."""
    unit_values: dict[str, int] = LoanUnit.objects.filter(loan_id__in=loans.values("pk")).aggregate(
        issued_quantity=Count("pk"),
        returned_quantity=Count("pk", filter=Q(return_record__isnull=False)),
        outstanding_quantity=Count("pk", filter=Q(return_record__isnull=True)),
    )
    return ReportTotals(
        loan_count=loans.count(),
        issued_quantity=unit_values["issued_quantity"],
        returned_quantity=unit_values["returned_quantity"],
        outstanding_quantity=unit_values["outstanding_quantity"],
    )


def get_system_setting() -> SystemSetting:
    """Require the initialized singleton; never repair configuration during a read."""
    try:
        return SystemSetting.objects.get(pk=1)
    except SystemSetting.DoesNotExist as error:
        raise ImproperlyConfigured(
            "SystemSetting row 1 is missing. Apply the settings initialization migration on a fresh database or restore the missing row from a verified backup; request submission cannot continue."
        ) from error


def get_loan_limits() -> LoanLimits:
    """A single SELECT captures both limits consistently for a new request."""
    setting: SystemSetting = get_system_setting()
    return validate_loan_limits(setting.max_loan_days, setting.max_quantity_per_item)


def audit_history(
    search_query: str,
    action: str,
    actor_id: int | None,
    date_from: date | None,
    date_to: date | None,
) -> QuerySet[AuditLog]:
    """Search historical references with inclusive campus dates, newest event first."""
    entries: QuerySet[AuditLog] = AuditLog.objects.select_related("actor")
    if search_query:
        entries = entries.annotate(
            reference=Concat("target_model", Value("#"), Cast("target_id", CharField()))
        ).filter(reference__icontains=search_query)
    if action:
        entries = entries.filter(action=action)
    if actor_id is not None:
        entries = entries.filter(actor_id=actor_id)
    if date_from is not None:
        entries = entries.filter(occurred_at__date__gte=date_from)
    if date_to is not None:
        entries = entries.filter(occurred_at__date__lte=date_to)
    return entries.order_by("-occurred_at", "-pk")
