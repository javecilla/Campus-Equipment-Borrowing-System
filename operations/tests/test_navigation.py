"""Role navigation and read-only module destinations through real Django requests."""

from html.parser import HTMLParser

from django.contrib.auth import SESSION_KEY
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from operations.tests.records import CatalogRecords, create_catalog_records

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
    "portal:profile",
    "portal:equipment-list",
    "portal:request-list",
    "portal:loan-list",
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
            *(reverse(name) for name in PORTAL_READ_ONLY),
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
            (self.records.admin, PORTAL_READ_ONLY, ADMIN_READ_ONLY),
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
        for name in (*ADMIN_READ_ONLY, *PORTAL_READ_ONLY):
            with self.subTest(anonymous=name):
                response = anonymous.get(reverse(name))
                self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse(name)}")

    def test_deactivated_sessions_cannot_open_read_only_pages(self) -> None:
        for user, routes in (
            (self.records.admin, ADMIN_READ_ONLY),
            (self.records.borrower, PORTAL_READ_ONLY),
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
        for user, other, route in (
            (self.records.admin, self.records.borrower, "operations:profile"),
            (self.records.borrower, self.records.admin, "portal:profile"),
        ):
            with self.subTest(role=user.role):
                self.client.force_login(user)
                response = self.client.get(reverse(route), {"user_id": other.pk})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["profile"].user_id, user.pk)
                self.assertNotContains(response, other.email)
                self.assertNotContains(response, other.username)
                self.assertEqual(
                    self.client.post(reverse(route), {"first_name": "Changed"}).status_code, 405
                )
                user.refresh_from_db()
                self.assertEqual(user.first_name, "Fictional")
