"""T18 live dashboard query, access, and rendered dataset integration checks."""

from datetime import timedelta

from django.contrib.auth import SESSION_KEY
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from borrowing.models import Loan
from borrowing.release_services import release_request
from borrowing.return_services import ReturnInput, return_units
from borrowing.services import approve_request
from inventory.models import EquipmentUnit, UnitCondition, UnitStatus
from operations.queries import ChartPoint, DashboardCards, dashboard_snapshot
from operations.tests.records import CatalogRecords, create_catalog_records, create_request


class DashboardIntegrationTests(TestCase):
    records: CatalogRecords
    loan: Loan
    today = timezone.localdate()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        EquipmentUnit.objects.create(
            catalog_item=cls.records.item,
            asset_code="T18-CAM-002",
            condition=UnitCondition.GOOD,
            acquired_on=cls.today,
            status=UnitStatus.AVAILABLE,
        )
        request_line = create_request(cls.records.borrower.pk, cls.records.item.pk, timezone.now())
        request_line.quantity = 2
        request_line.save(update_fields=["quantity"])
        approve_request(cls.records.admin.pk, request_line.request_id, "T18 dashboard approval")
        cls.loan = release_request(cls.records.admin.pk, request_line.request_id)
        Loan.objects.filter(pk=cls.loan.pk).update(
            issued_at=timezone.now() - timedelta(days=5),
            issued_on=cls.today - timedelta(days=5),
            due_date=cls.today - timedelta(days=1),
        )
        cls.loan.refresh_from_db()
        create_request(cls.records.borrower.pk, cls.records.item.pk, timezone.now())

    def test_cards_and_charts_follow_partial_and_final_returns(self) -> None:
        first, second = tuple(self.loan.units.order_by("pk"))
        initial = dashboard_snapshot(self.today)
        self.assertEqual(initial.cards, DashboardCards(0, 1, 1, 1))
        self.assertEqual(
            initial.monthly_issued_loans,
            (ChartPoint((self.today - timedelta(days=5)).strftime("%b %Y"), 1),),
        )
        self.assertEqual(initial.category_issued_units, (ChartPoint("Test cameras", 2),))

        return_units(
            self.records.admin.pk,
            self.loan.pk,
            (ReturnInput(first.pk, UnitCondition.FAIR, "Dashboard partial return", ""),),
        )
        partial = dashboard_snapshot(self.today)
        self.assertEqual(partial.cards, DashboardCards(1, 1, 1, 1))
        self.assertEqual(partial.category_issued_units, (ChartPoint("Test cameras", 2),))

        return_units(
            self.records.admin.pk,
            self.loan.pk,
            (
                ReturnInput(
                    second.pk,
                    UnitCondition.DAMAGED,
                    "Dashboard final return",
                    "Fictional cracked housing",
                ),
            ),
        )
        final = dashboard_snapshot(self.today)
        self.assertEqual(final.cards, DashboardCards(1, 1, 0, 0))
        self.assertEqual(final.category_issued_units, (ChartPoint("Test cameras", 2),))

    def test_dashboard_renders_live_values_and_json_safe_chart_data(self) -> None:
        self.records.category.name = "Lab </script><script>alert(1)</script>"
        self.records.category.save(update_fields=["name", "updated_at"])
        self.client.force_login(self.records.admin)

        response = self.client.get(reverse("operations:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "operations/manage/dashboard.html")
        self.assertEqual(response.context["snapshot"].cards, DashboardCards(0, 1, 1, 1))
        self.assertEqual(response.context["monthly_chart_data"][0]["value"], 1)
        self.assertEqual(response.context["category_chart_data"][0]["value"], 2)
        self.assertContains(response, 'data-testid="dashboard-available-units"')
        self.assertContains(response, 'data-testid="monthly-issued-loans-chart"')
        self.assertContains(response, 'data-testid="category-issued-units-chart"')
        self.assertNotContains(response, "</script><script>alert(1)</script>")
        self.assertContains(response, "\\u003C/script\\u003E")

    def test_dashboard_enforces_active_admin_and_safe_methods(self) -> None:
        url = reverse("operations:dashboard")
        anonymous = Client()
        self.assertRedirects(anonymous.get(url), f"{reverse('accounts:login')}?next={url}")

        self.client.force_login(self.records.borrower)
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_login(self.records.admin)
        self.assertEqual(self.client.head(url).status_code, 200)
        self.assertEqual(self.client.post(url, {"available_units": 999}).status_code, 405)
        User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertNotIn(SESSION_KEY, self.client.session)


class DashboardEmptyStateTests(TestCase):
    def test_empty_loan_charts_keep_real_inventory_card_and_useful_empty_states(self) -> None:
        records = create_catalog_records()
        self.client.force_login(records.admin)

        response = self.client.get(reverse("operations:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["snapshot"].cards, DashboardCards(1, 0, 0, 0))
        self.assertEqual(response.context["monthly_chart_data"], [])
        self.assertEqual(response.context["category_chart_data"], [])
        self.assertContains(response, "No issued loans yet.")
        self.assertContains(response, "No issued equipment usage yet.")
        self.assertFalse(
            response.context["snapshot"].monthly_issued_loans
            or response.context["snapshot"].category_issued_units
        )
