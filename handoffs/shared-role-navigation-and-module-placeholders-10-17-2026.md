# Shared role navigation and module placeholders

- Date: October 17, 2026, Asia/Manila.
- Work: UI-07, requested by Jerome; Codex implementation assistance. Alex's T05 account-management implementation and credit are preserved.
- Branch/base: `jerome`, based on `7a80257`. This follow-up is uncommitted and **Not integrated**; no commit, push, PR, or merge performed.

## Outcome and integration review

Alex's T05 source commit `22fb720` is included in PR #15's merge `7a80257` (October 17, 18:05:03 +08:00). Local `origin/main` points to that merge; source ancestry and merge parents were inspected. The old T05 snapshot remains unchanged. Current backlog/handoff records now reflect this integration.

Admin pages share Dashboard, User accounts, Equipment, Borrowing, Reports, Settings, and Audit history tabs. Portal pages share Home, Equipment, My requests, My loans, and Profile. Navigation wraps on small screens and remains sticky while scrolling. The current section has `aria-current="page"`; account details and confirmations retain the User accounts selection. Both layouts preserve the shared POST/CSRF logout, light branding, and messages.

T05 list/detail/status-confirmation templates now use the admin layout with restrained dividers in place of outer cards. Existing search/pagination, history tables, forms, services, audits, conflicts, and authorization remain intact.

Twelve pending destinations use the existing contracted paths/names and active-role checks. GET/HEAD displays a clearly labeled pending module with assigned owner/task and next steps; POST returns 405. These pages do not read domain records or implement workflows. Equipment offers catalog/units/maintenance links; Borrowing offers requests/approvals and releases/returns links. The dashboard remains pending T18. T06–T19 and full T20 acceptance retain their owners/dependencies/statuses.

## Interfaces and developer entry points

- [Shared workspace](../templates/components/workspace.html), [admin base](../templates/operations/manage/base.html), [portal base](../templates/accounts/portal/base.html): feature pages extend their role base and fill `workspace_content`. Preserve shared navigation, stable IDs, skip link, active state, messages, and POST logout.
- [Account templates](../templates/accounts/manage/): presentation integration only; Alex's account query/service/view code is unchanged.
- [Inventory views](../inventory/views.py) and [routes](../inventory/manage_urls.py): pending `inventory_manage:item-list`, `unit-list`, and `maintenance-list`.
- [Borrowing views](../borrowing/views.py) and [routes](../borrowing/manage_urls.py): pending `borrowing_manage:request-list` and `loan-list`.
- [Operations placeholders](../operations/workspace_views.py): pending `operations:settings`, `audit-list`, and `loan-report`.
- [Portal placeholders](../accounts/portal_views.py) and [portal routes](../accounts/portal_urls.py): pending `portal:profile`, `equipment-list`, `request-list`, and `loan-list`. Feature owners move real equipment/borrowing handlers into their owning apps when implementing them, preserving the `portal` namespace.
- [HTTP contract](../docs/api_spec.md#status-and-interface-choice) distinguishes current placeholder behavior from eventual feature contracts. [Coding standards](../docs/coding-standards.md#tailwind-styling-pattern), [architecture](../docs/architecture.md), and [folder map](../docs/project-folder-architecture.md) identify the implemented layouts.
- [Navigation integration tests](../operations/tests/test_navigation.py) exercise real rendered links, active parent selection, roles, anonymous redirects, inactive-session invalidation, safe methods, and POST rejection.

## Verification

- Full Django suite on PostgreSQL: **60 tests passed**, 18.823 seconds, including Alex's 13 T05 tests and three new navigation/access integration tests; separate test database created/destroyed.
- Django database check: no issues. Migration drift: no changes. Applied-migration check: passed. No schema changes.
- Tailwind/esbuild build and npm format check: passed. npm audit: **0 vulnerabilities** after retrying the sandbox-blocked registry call with approved network access. No dependency changes.
- Ruff lint/format: passed (final check: 126 Python files). djLint: 22 templates checked, zero pending formatting changes. pip check: no broken requirements. Whitespace check: passed.
- Chrome fresh preview on `127.0.0.1:8012`: administrator sign-in, account list/detail/confirmation and cancel, module/subsection links, sticky header after scrolling, active section, both-role logout, borrower sign-in and pending requests page checked. Desktop 1704px and mobile 375px layouts have no page-level horizontal overflow; all main tabs remain visible and wrap. Keyboard skip link focuses main content; light scheme verified.
- The existing localhost tab retained stale CSS despite the correct rebuilt bytes being served. A fresh preview address rendered the rebuilt stylesheet correctly (sticky header and 1152px desktop content width). No private environment changes or edits to the user's running server were needed. Browser viewport override reset; temporary preview closed/stopped.
- All 308 relative links/anchors across seven changed documents and their Markdown fences passed validation. T05 forms/views/queries/services and existing authentication/account tests have zero source diff. No CI, populated-history browser workflow, performance, or full T20 acceptance claimed. Existing real ORM history/preservation tests pass.

## Next action

Jerome reviews this uncommitted diff. After separately authorized publication/main integration, each owner extends the existing role layout and replaces their pending handler only when their backlog prerequisites are satisfied. Keep the pending warning until actual feature acceptance passes; do not mark a workflow complete because its navigation destination exists.
