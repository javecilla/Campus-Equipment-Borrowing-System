# Minimal Dashboard Reference and UI Review

- **Owner:** Jerome Avecilla with Codex assistance; existing feature-owner work preserved.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** UI-09 reference-design refinement and review of the existing uncommitted UI changes.
- **Outcome:** Done locally on `jerome`; uncommitted, **not integrated into main**. No commit, push, PR or workflow implementation. Earlier UI-09 work remains in the [initial handoff](shared-m3-layout-and-template-consistency-10-20-2026.md).

## Current result

[Shared CSS](../static/css/app.css) now uses the supplied dashboard's white panels, `#f8f9fa` canvas, `#1b5a5a` accent, neutral slate utilities, subtle borders/shadows and compact rounded controls. DM Sans, Poppins and existing branding are retained. [The generator](../scripts/build-theme.mjs) applies explicit reference overrides to the semantic roles before contrast validation; campus-seed status colors remain. [The base asset loader](../templates/base.html) already loads generated theme CSS before compiled app CSS and remains correct.

[The workspace](../templates/components/workspace.html) uses a 240px sticky desktop sidebar from 1024px, decorative line icons, bottom account disclosure and a separate main header. Smaller screens retain horizontal navigation and the current-destination enhancement. The profile panel opens upward within the sidebar and downward on compact screens. [The administrator home](../templates/operations/manage/dashboard.html) has a responsive 1.8:1 panel split with real equipment/request/account/maintenance shortcuts and existing settings/audit tools. Pending summaries remain explicit; no sample financial metrics, charts, search or notification controls were added.

Review confirmed that existing Python form edits only replace widget classes; backend validation, models, services, routes and access rules are unchanged. The review corrected a dangling `sm:` utility in [equipment detail](../templates/inventory/portal/equipment_detail.html), restored the danger button for [cancellation confirmation](../templates/accounts/portal/request_cancel.html), and corrected sidebar profile-menu width after browser checks exposed clipping. Existing dependencies and lock versions were preserved. No additional dependency was installed for this follow-up.

[Canonical styling guidance](../docs/coding-standards.md#shared-m3-roles-and-components-ui-09), [build setup](../DEV.md#frontend-assets-tailwind-and-page-scripts), [Module 14](../docs/manual-test-guide.md#module-14--shared-m3-layout-and-controls-ui-09), current readiness and the affected backlog entry reflect the latest reference. Original requirements/member files and completed handoffs are preserved.

## Verification

- **254 PostgreSQL tests passed in 37.813s**, creating/removing a separate test database.
- Chrome **155.0.8059.84** passed **168 route/viewport checks**: 24 existing ADMIN/BASIC_USER pages at 320, 375, 768, 1023, 1024, 1440 and 1920px. Checked response/destination, whole-page bounds, sidebar-aware main width, labels, unique IDs and 48px controls.
- **36 interaction assertions passed:** exact teal/white/gray colors, local font families, keyboard skip, account-menu containment/Escape/focus at four widths, short-desktop menu reachability, compact active destination, keyboard table scrolling, real shortcuts, reduced motion, invalid request errors/IDs, cancellation emphasis, wrong-role 403 and both-role POST logout.
- Dashboard, catalog, desktop menu, invalid request and compact portal screenshots were visually inspected. Local artifacts are ignored under `output/playwright/`.
- npm build and formatting, nine final text-role contrast pairs, audit (zero vulnerabilities), djLint (70 templates), Ruff lint/format (211 files), Django database/migration checks and pip check passed. Checked 659 local documentation link targets across 11 documents, balanced code fences and diff whitespace.
- Existing active fictional `auth_demo_admin` / `auth_demo_user` accounts were loaded for temporary UI sessions and existing GET routes. No valid business mutation or seed creation was performed; both sessions were logged out. The earlier settings/fixture snapshot remains explicitly dated October 20 at 08:42 Asia/Manila in Module 14; it was not represented as a new settings inspection.

## Limits and next action

This is reference-inspired presentation for the equipment application, not a pixel-identical financial dashboard or completed T18/T20. Full screen-reader conformance, Firefox/Safari, populated issue/return flows and outstanding lifecycle acceptance remain unverified. No new permanent tests were added for styling.

Jerome/user reviews the uncommitted design before separately authorizing publication. Margareth / T15 remains ready on integrated T13/T14 with its original scope; T17/T18/T19 and full T20 gates remain unchanged. See [current readiness](../HANDOFF.md) and [canonical backlog](../docs/tasks.md).
