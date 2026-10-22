"""Build T24's fictional workload through services in its dedicated local database."""

from dataclasses import dataclass
from datetime import timedelta
from secrets import token_urlsafe

from django.conf import settings
from django.db import connection
from django.utils import timezone

from accounts.models import User
from accounts.services import create_admin_account, register_basic_user
from borrowing.models import BorrowRequest, Loan, RequestStatus, UnitAllocation
from borrowing.release_services import release_request
from borrowing.return_services import ReturnInput, return_units
from borrowing.services import approve_request, cancel_request, reject_request, submit_request
from inventory.models import EquipmentUnit, UnitCondition
from inventory.services import create_catalog_item, create_category, create_equipment_unit
from operations.models import AuditLog, AuditTarget
from operations.validation import RequestedItem


@dataclass(frozen=True)
class SessionWorkload:
    user_id: int
    username: str
    routes: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkFixture:
    password: str
    sessions: tuple[SessionWorkload, ...]


def require_benchmark_database() -> None:
    """Reject populated development databases and every non-loopback target."""
    connection.ensure_connection()
    if (
        connection.settings_dict["NAME"] != "campus_t24_benchmark"
        or connection.settings_dict["HOST"] != "127.0.0.1"
        or settings.STORAGES["default"]["BACKEND"] != "django.core.files.storage.FileSystemStorage"
    ):
        raise RuntimeError("T24 requires local 127.0.0.1/campus_t24_benchmark; no data changed.")


def seed_benchmark() -> BenchmarkFixture:
    """Create exactly 1,000 units/5,000 requests; reject reruns instead of clearing data."""
    require_benchmark_database()
    if User.objects.exists() or EquipmentUnit.objects.exists() or BorrowRequest.objects.exists():
        raise RuntimeError("T24 fixture requires a fresh migrated benchmark database, not a rerun.")
    password: str = token_urlsafe(32)
    admins: tuple[User, ...] = tuple(
        create_admin_account(
            f"t24_admin_{index}",
            "Fictional",
            f"Admin {index}",
            f"t24.admin.{index}@example.invalid",
            password,
        )
        for index in range(5)
    )
    borrowers: tuple[User, ...] = tuple(
        register_basic_user(
            f"t24_borrower_{index}",
            "Fictional",
            f"Borrower {index}",
            f"t24.borrower.{index}@example.invalid",
            "",
            password,
        )
        for index in range(5)
    )
    categories = tuple(
        create_category(admins[0].pk, f"T24 category {index}", "Fictional benchmark category")
        for index in range(5)
    )
    items = tuple(
        create_catalog_item(
            admins[0].pk,
            categories[index % 5].pk,
            f"T24 equipment {index:02d}",
            "Fictional performance fixture",
        )
        for index in range(20)
    )
    today = timezone.localdate()
    for index in range(1000):
        create_equipment_unit(
            admins[0].pk,
            items[index % 20].pk,
            f"T24-{index:04d}",
            UnitCondition.GOOD,
            today - timedelta(days=90),
            "T24 fixture only",
            None,
        )
    for index in range(5000):
        request = submit_request(
            borrowers[index % 5].pk,
            f"Fictional T24 classroom request {index}",
            today + timedelta(days=2),
            (RequestedItem(items[index % 20].pk, 1),),
        )
        # Spread the action distribution over every item rather than exhausting one item.
        action: int = (index // 20) % 20
        if action == 0:
            reject_request(admins[0].pk, request.pk, "Fictional benchmark rejection")
        elif action == 1:
            cancel_request(borrowers[index % 5].pk, request.pk)
        elif action in {2, 3, 4, 5, 6}:
            approve_request(admins[0].pk, request.pk, "Fictional benchmark approval")
            if action != 6:
                loan: Loan = release_request(admins[0].pk, request.pk)
                if action in {2, 3, 4}:
                    return_units(
                        admins[0].pk,
                        loan.pk,
                        (ReturnInput(loan.units.get().pk, UnitCondition.GOOD, "T24 return", ""),),
                    )
        if (index + 1) % 1000 == 0:
            print(f"T24 fixture: {index + 1}/5000 requests", flush=True)
    backdate_active_fixture_loans()
    if EquipmentUnit.objects.count() != 1000 or BorrowRequest.objects.count() != 5000:
        raise RuntimeError("T24 fixture count mismatch; retain database for inspection.")
    admin_routes: tuple[str, ...] = (
        "/manage/",
        "/manage/items/",
        f"/manage/items/{items[0].pk}/",
        "/manage/units/",
        "/manage/units/1/",
        "/manage/requests/",
        "/manage/requests/?status=PENDING",
        "/manage/requests/1/",
        "/manage/loans/",
        "/manage/loans/1/",
        "/manage/reports/loans/",
        "/manage/reports/overdue/",
        "/manage/audit/",
    )
    sessions: list[SessionWorkload] = [
        SessionWorkload(user.pk, user.username, admin_routes) for user in admins
    ]
    for user in borrowers:
        request_id: int = BorrowRequest.objects.filter(owner=user).earliest("pk").pk
        loan_id: int = Loan.objects.filter(request__owner=user).earliest("pk").pk
        sessions.append(
            SessionWorkload(
                user.pk,
                user.username,
                (
                    "/portal/",
                    "/portal/equipment/",
                    f"/portal/equipment/{items[0].pk}/",
                    "/portal/requests/",
                    f"/portal/requests/{request_id}/",
                    "/portal/loans/",
                    f"/portal/loans/{loan_id}/",
                ),
            )
        )
    print(
        "T24 request states:",
        tuple(
            (status, BorrowRequest.objects.filter(status=status).count())
            for status in RequestStatus.values
        ),
        flush=True,
    )
    return BenchmarkFixture(password, tuple(sessions))


def backdate_active_fixture_loans() -> None:
    """Date half of this new fixture's active loans five days earlier, preserving event order."""
    require_benchmark_database()
    for loan in Loan.objects.filter(closed_at__isnull=True).select_related("request"):
        if loan.pk % 2 == 0:
            request: BorrowRequest = loan.request
            shift: timedelta = timedelta(days=5)
            BorrowRequest.objects.filter(pk=request.pk).update(
                submitted_at=request.submitted_at - shift,
                submitted_on=request.submitted_on - shift,
                desired_due_date=request.desired_due_date - shift,
                agreed_due_date=request.agreed_due_date - shift,
                decided_at=request.decided_at - shift,
            )
            Loan.objects.filter(pk=loan.pk).update(
                issued_at=loan.issued_at - shift,
                issued_on=loan.issued_on - shift,
                due_date=loan.due_date - shift,
            )
            for allocation in UnitAllocation.objects.filter(loan_unit__loan=loan):
                UnitAllocation.objects.filter(pk=allocation.pk).update(
                    allocated_at=allocation.allocated_at - shift,
                    released_at=allocation.released_at - shift,
                )
            for target, identifier in (
                (AuditTarget.BORROW_REQUEST, request.pk),
                (AuditTarget.LOAN, loan.pk),
            ):
                for audit in AuditLog.objects.filter(target_model=target, target_id=identifier):
                    AuditLog.objects.filter(pk=audit.pk).update(
                        occurred_at=audit.occurred_at - shift
                    )
