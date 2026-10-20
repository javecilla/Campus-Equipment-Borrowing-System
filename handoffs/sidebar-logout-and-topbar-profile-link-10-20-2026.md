# Sidebar Logout and Top-Bar Profile Link

- **Owner:** Jerome Avecilla with Codex assistance.
- **Date/time zone:** October 20, 2026, Asia/Manila.
- **Task:** UI-09 navigation refinement requested from the annotated screenshot.
- **Outcome:** Done locally on `jerome`, uncommitted and **not integrated into main**. No commit, push, PR or downstream workflow implementation.

## Delivered behavior

[The workspace](../templates/components/workspace.html) places the native [logout form](../templates/components/logout.html) at the bottom of the desktop sidebar. Its red icon/text uses the same 20px icon, 48px row height, padding and gap as the other navigation links. At compact widths it sits beside the brand above scrolling navigation. The small-screen brand gap was tightened to fit at 320px while preserving uniform logout spacing.

[The profile link](../templates/components/account_link.html) replaces the top bar's system-description text with the existing avatar, surname/first initial and role, linked directly to the signed-in account's profile. Both [management](../templates/operations/manage/base.html) and [portal](../templates/accounts/portal/base.html) layouts supply their existing named profile route. The workspace label is hidden below 640px so profile identity stays visible. The old account-menu template, dropdown JavaScript and unused generated menu bundle were removed; no dropdown behavior remains.

The change affects presentation only. Existing profile access/editing permissions, server-derived identity, POST-only logout, CSRF protection, models, services and routes are unchanged. Existing JPG logo/avatar and favicon changes present at task start were preserved. Historical handoffs were not rewritten; archived dropdown snapshots retain links to their now-retired source files.

Current styling/build/HTTP guidance and [Module 14 manual cases](../docs/manual-test-guide.md#module-14--shared-m3-layout-and-controls-ui-09) describe the new flow. The earlier settings/fixture snapshot remains dated October 20 at 08:42 Asia/Manila; this task loaded existing active fictional accounts for temporary browser sessions without a new settings/stock inspection or seed.

## Actual checks

- **254 PostgreSQL tests passed in 43.842s** in the separate test database, which was removed afterward.
- Chrome **155.0.8059.84** passed **32 layout checks**: both roles' home/profile pages at 320, 375, 640, 768, 1023, 1024, 1440 and 1702px. Checked loaded profile images/name visibility, top-bar containment, no dropdown, no page overflow, matching navigation/logout spacing/height, red logout, bottom-sidebar alignment and compact brand/logout row alignment.
- **12 interaction checks passed** across both roles: direct profile click, current-profile state, keyboard profile navigation, logout reachability at 1024 × 500, native CSRF POST logout and protected-profile redirects after logout. Desktop/mobile screenshots were visually inspected and remain ignored under `output/playwright/`.
- npm build/format/audit (zero vulnerabilities), nine theme contrast pairs, djLint (70 templates), Ruff lint/format, Django database/migration checks and pip check passed. Current document link targets, code fences and diff whitespace were checked. No new permanent styling tests or dependencies were added.
- Existing fictional `auth_demo_admin` / `auth_demo_user` sessions were used and logged out. No account/profile/inventory/request/settings business mutation was submitted. Temporary browser/server processes and private state files were cleaned up.

## Limits and next action

Full screen-reader acceptance and Firefox/Safari remain unrun. Prior broad UI route/form results are preserved in the [reference-design handoff](minimal-dashboard-reference-and-ui-review-10-20-2026.md); dropdown-specific cases there are superseded by this request.

Jerome/user reviews the local UI before separately authorizing publication. Margareth / T15 remains ready on integrated T13/T14, Not started; T20 retains its original dependencies. See [HANDOFF.md](../HANDOFF.md) and the [canonical backlog](../docs/tasks.md).
