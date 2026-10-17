# Minimal role and error pages

- Owner: Jerome Avecilla, with Codex assistance; user-authorized UI-05 presentation work on existing T04 destinations.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00), around 12:30.
- Delivery: local, uncommitted on `jerome`, based on main merge `847a8c0`; **Not integrated**. No commit, push, PR, merge, seed, or database reset performed.

## Current outcome

The [administrator destination](../templates/operations/manage/dashboard.html) and [borrower destination](../templates/accounts/portal/home.html) use white surfaces, existing green branding, generous spacing, and thin dividers. They show honest pending-feature summaries without dashboard numbers or unimplemented links. Both use the shared [brand](../templates/components/brand.html) and [logout form](../templates/components/logout.html); logout retains the existing named POST action, CSRF token, and stable test ID.

Developer comments in each role template identify ready work, prerequisites, and owners while linking the canonical [backlog](../docs/tasks.md). The [coding guide](../docs/coding-standards.md#tailwind-styling-pattern) records the requested minimal light design as the default unless an explicit requirement calls for another theme. The course brief does not require dark mode. The [shared CSS](../static/css/app.css) declares the light color scheme, and the [document shell](../templates/base.html) supplies matching metadata.

The [403](../templates/403.html) and new [404](../templates/404.html) templates share a minimal [error layout](../templates/errors/base.html), readable explanation, logo, and a named home link. Home uses the existing stored-role redirect or anonymous sign-in flow. Errors disclose no requested path, internal exception, owner details, or record data. Django's native handlers retain HTTP 403/404; no custom error view or URL was added. With `DJANGO_DEBUG=True`, Django still displays its technical 404; verify the custom page with debug disabled.

The existing [bootstrap checks](../config/tests.py) now verify native custom-404 rendering. The [authentication tests](../accounts/tests/test_authentication.py) verify custom 403 and owner-isolation 404 rendering; the isolated ownership test URL configuration includes the existing account routes so shared recovery links resolve. No business logic, schema, permission, or endpoint contract changed. Prior local seed/email-login/login-wave work and the stash backup remain intact.

## Verification performed

| Check | Actual result |
| --- | --- |
| PostgreSQL suite | 44 tests passed in 17.891 seconds; separate test database created and destroyed |
| Django/schema | Database system check: no issues; migration drift: no changes; applied-migration check passed |
| Python/templates | Ruff lint passed; 109 Python files already formatted; djLint checked 11 templates with zero updates |
| Frontend/dependencies | Full npm build passed; CSS rebuilt after the explicit light-scheme declaration; npm source formatting passed; pip check passed; npm audit passed with zero vulnerabilities after approved network retry |
| Chrome role flow | Both seeded email identities reached their correct homes; both logout buttons returned to sign-in and protected destinations required sign-in afterward |
| Chrome layout/accessibility | Admin and borrower inspected at desktop 1704px and mobile 375px, without horizontal overflow; local logo/fonts loaded; keyboard reached logout with visible outline; computed borrower surface white and document color scheme light |
| Chrome errors | Real admin-to-portal 403 inspected on mobile; real missing-route 404 inspected on mobile and desktop with debug disabled; return-home actions reached the correct signed-in workspace; errors had no horizontal overflow |
| Documentation/privacy/Git | 474 relative links/anchors across 19 changed or new documents passed; Markdown fences and table continuity checked; all 18 original T04–T21 task rows unchanged; historical handoffs, source briefs, private settings, LF policy, stash, branch/base, and empty index preserved; diff whitespace passed |

Browser verification used a temporary local server on port 8001 with debug disabled and insecure static serving solely for inspection; private configuration was not edited. Temporary viewport overrides were reset, both accounts signed out, and the temporary tab/server closed. No dark-mode operating-system emulation was performed; CSS explicitly declares the light scheme.

## Next action and remaining scope

Jerome reviews UI-05 alongside the existing uncommitted authentication/login work. This task does not complete the full T20 role layouts/navigation or any future workflow feature. Preserve the shared components and light design when feature owners introduce role base templates.

- Admin: Alex T05 account management, Jerome T06 settings/audit, and Kenneth T07 catalog are ready under their existing prerequisites. Kenneth T08/T16 units/maintenance and Margareth T13/T15/T17 approval/release/returns follow their exact backlog gates. Alex T18 live dashboard and T19 reports require real issued/returned loan data.
- Basic user: Ellyssa T09 registration/profile and portal base is ready. T10 browsing requires T08/T09; Ralph T11 requests requires T03/T08/T09, then T12 tracking/cancellation follows. Preserve owner-scoped reads and hide internal management data.
- Ralph, Ellyssa, and admin owners retain T20 integration after its prerequisites. T21 full demonstration data remains pending. All existing feature statuses are unchanged.

Keep all work uncommitted and retain the stash backup until Jerome finishes reviewing the combined diff.
