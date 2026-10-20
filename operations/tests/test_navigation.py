"""Role navigation and read-only module destinations through real Django requests."""

from html.parser import HTMLParser

from django.contrib.auth import SESSION_KEY
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from borrowing.services import approve_request, reject_request
from operations.tests.records import CatalogRecords, create_catalog_records, create_request

ADMIN_READ_ONLY: tuple[str, ...] = (
    "inventory_manage:item-list",
    "inventory_manage:unit-list",
    "inventory_manage:maintenance-list",
    "borrowing_manage:request-list",
    "borrowing_manage:loan-list",
    "operations:loan-report",
    "operations:audit-list",
    "operations:profile",
)
PORTAL_READ_ONLY: tuple[str, ...] = (
    "portal:equipment-list",
    "portal:request-list",
    "portal:loan-list",
)
PORTAL_MODULE_DESTINATIONS: tuple[str, ...] = (
    "portal:profile",
    *PORTAL_READ_ONLY,
)


class NavigationLinks(HTMLParser):
    """Collect the rendered navigation targets and active state, independent of wording."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, bool]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes: dict[str, str | None] = dict(attrs)
        test_id: str = attributes.get("data-testid") or ""
        if tag == "a" and test_id.startswith("nav-"):
            target: str | None = attributes.get("href")
            if target is None:
                raise ValueError(f"Navigation link {test_id} has no target.")
            self.links.append((target, attributes.get("aria-current") == "page"))


class WorkspaceNavigationTests(TestCase):
    records: CatalogRecords

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()

    def test_role_navigation_targets_resolve_and_one_parent_stays_active(self) -> None:
        account_id: int = self.records.borrower.pk
        admin_paths: tuple[str, ...] = (
            reverse("operations:dashboard"),
            reverse("accounts:manage-list"),
            reverse("accounts:manage-detail", args=[account_id]),
            reverse("accounts:manage-activate", args=[account_id]),
            reverse("accounts:manage-deactivate", args=[account_id]),
            reverse("operations:settings"),
            *(reverse(name) for name in ADMIN_READ_ONLY),
        )
        portal_paths: tuple[str, ...] = (
            reverse("portal:home"),
            *(reverse(name) for name in PORTAL_MODULE_DESTINATIONS),
        )
        for user, paths, count in (
            (self.records.admin, admin_paths, 8),
            (self.records.borrower, portal_paths, 5),
        ):
            self.client.force_login(user)
            for path in paths:
                with self.subTest(path=path):
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 200)
                    navigation = NavigationLinks()
                    navigation.feed(response.content.decode())
                    self.assertEqual(len(navigation.links), count)
                    self.assertEqual(sum(active for _, active in navigation.links), 1)
                    for target, _ in navigation.links:
                        self.assertEqual(self.client.get(target).status_code, 200)

    def test_read_only_pages_enforce_role_authentication_and_safe_methods(self) -> None:
        for user, forbidden, permitted in (
            (self.records.admin, PORTAL_MODULE_DESTINATIONS, ADMIN_READ_ONLY),
            (self.records.borrower, ADMIN_READ_ONLY, PORTAL_READ_ONLY),
        ):
            self.client.force_login(user)
            for name in forbidden:
                with self.subTest(role=user.role, name=name):
                    self.assertEqual(self.client.get(reverse(name)).status_code, 403)
            for name in permitted:
                with self.subTest(role=user.role, name=name):
                    self.assertEqual(self.client.head(reverse(name)).status_code, 200)
                    self.assertEqual(
                        self.client.post(reverse(name), {"is_active": False}).status_code, 405
                    )
        anonymous = Client()
        for name in (*ADMIN_READ_ONLY, *PORTAL_MODULE_DESTINATIONS):
            with self.subTest(anonymous=name):
                response = anonymous.get(reverse(name))
                self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse(name)}")

    def test_deactivated_sessions_cannot_open_read_only_pages(self) -> None:
        for user, routes in (
            (self.records.admin, ADMIN_READ_ONLY),
            (self.records.borrower, PORTAL_MODULE_DESTINATIONS),
        ):
            for name in routes:
                with self.subTest(role=user.role, name=name):
                    User.objects.filter(pk=user.pk).update(is_active=True)
                    user.refresh_from_db()
                    self.client.force_login(user)
                    User.objects.filter(pk=user.pk).update(is_active=False)
                    self.assertEqual(self.client.get(reverse(name)).status_code, 403)
                    self.assertNotIn(SESSION_KEY, self.client.session)

    def test_my_profile_ignores_supplied_account_ids_and_cannot_update_accounts(self) -> None:
        self.client.force_login(self.records.admin)
        response = self.client.get(
            reverse("operations:profile"), {"user_id": self.records.borrower.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"].user_id, self.records.admin.pk)
        self.assertNotContains(response, self.records.borrower.email)
        self.assertNotContains(response, self.records.borrower.username)
        self.assertEqual(
            self.client.post(reverse("operations:profile"), {"first_name": "Changed"}).status_code,
            405,
        )
        self.records.admin.refresh_from_db()
        self.assertEqual(self.records.admin.first_name, "Fictional")

        self.client.force_login(self.records.borrower)
        portal_response = self.client.get(
            reverse("portal:profile"), {"user_id": self.records.admin.pk}
        )
        self.assertEqual(portal_response.status_code, 200)
        self.assertEqual(portal_response.context["profile"].user_id, self.records.borrower.pk)
        self.assertNotContains(portal_response, self.records.admin.email)
        self.assertNotContains(portal_response, self.records.admin.username)

    def test_pending_badge_tracks_committed_decisions_and_hides_when_queue_is_empty(self) -> None:
        self.client.force_login(self.records.admin)
        url: str = reverse("operations:dashboard")
        empty = self.client.get(url)
        self.assertEqual(empty.context["nav_pending_requests"], 0)
        self.assertNotContains(empty, 'data-testid="nav-manage-borrowing-badge"')
        first = create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
        second = create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())

        pending = self.client.get(url)
        self.assertEqual(pending.context["nav_pending_requests"], 2)
        self.assertEqual(pending.context["snapshot"].cards.pending_requests, 2)
        self.assertContains(pending, 'data-testid="nav-manage-borrowing-badge"')

        approve_request(self.records.admin.pk, first.request_id, "Fictional badge approval")
        approved = self.client.get(url)
        self.assertEqual(approved.context["nav_pending_requests"], 1)
        reject_request(self.records.admin.pk, second.request_id, "Fictional badge rejection")
        decided = self.client.get(url)
        self.assertEqual(decided.context["nav_pending_requests"], 0)
        self.assertNotContains(decided, 'data-testid="nav-manage-borrowing-badge"')

    def test_pending_badge_caps_display_and_is_not_supplied_to_other_roles(self) -> None:
        for _ in range(100):
            create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
        self.client.force_login(self.records.admin)
        administrator = self.client.get(reverse("operations:dashboard"))
        self.assertEqual(administrator.context["nav_pending_requests"], 100)
        self.assertContains(administrator, "99+")
        self.assertContains(administrator, 'aria-label="100 pending requests"')

        self.client.force_login(self.records.borrower)
        borrower = self.client.get(reverse("portal:home"))
        self.assertIsNone(borrower.context.get("nav_pending_requests"))
        self.assertNotContains(borrower, 'data-testid="nav-manage-borrowing-badge"')
        anonymous = Client().get(reverse("accounts:login"))
        self.assertIsNone(anonymous.context.get("nav_pending_requests"))
        self.client.force_login(self.records.admin)
        User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
        inactive = self.client.get(reverse("operations:dashboard"))
        self.assertEqual(inactive.status_code, 403)
        self.assertIsNone(inactive.context.get("nav_pending_requests"))
