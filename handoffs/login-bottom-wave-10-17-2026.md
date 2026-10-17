# Login bottom wave

- Owner: Jerome Avecilla, with Codex assistance.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00), around 12:07.
- Scope: UI-04 presentation follow-up explicitly requested by the user. Add the supplied SVG shape below the existing login form.
- Delivery: local, uncommitted on `jerome`, based on `cb96319`; **Not integrated**. Earlier changes and completed handoffs preserved. No commit, push, PR, or merge performed.

## Outcome and files

[The login template](../templates/accounts/login.html) uses the supplied path and `#047857` fill in a full-width bottom decoration. The page is now a vertical flex layout with an auto top margin and explicit spacing before the wave. The decoration stays in document flow, so short viewports scroll rather than placing it over form controls. SVG height is responsive; the shape stretches across the available width.

The SVG is `aria-hidden`, nonfocusable, and inside a pointer-events-disabled wrapper. No animation, script, new asset file, CSS dependency, or authentication change was introduced. [UI-04 evidence](../docs/tasks.md#shared-frontend-tooling) and [HANDOFF.md](../HANDOFF.md) link this follow-up; the [minimal-login snapshot](minimal-branded-login-10-17-2026.md) preserves earlier presentation and authentication checks.

## Verification performed

| Check | Actual result |
| --- | --- |
| Desktop Chrome | 1704×803: form section ends at y=500, SVG begins at y=611 and ends at the page bottom y=803; no horizontal overflow |
| Mobile Chrome | 375×812: section ends at y=468; SVG begins at y=684 and ends at y=812; page width 375px. Screenshot inspected |
| Short viewport | 375×400: content grows to 644px and scrolls; SVG begins at y=516, below the section ending at y=468; no form overlap. Default viewport restored |
| Decoration/accessibility | `aria-hidden="true"`, `focusable="false"`, and disabled pointer events keep the wave outside the interaction/accessibility flow |
| Assets | npm build passed. Local HTTP CSS bytes match the generated file. An existing `127.0.0.1` tab retained old CSS during initial preview; the fresh `localhost` preview loaded the rebuilt styles and displayed the expected layout |
| Django/PostgreSQL | Database check: no issues; migration drift: no changes; applied-migration check passed; full suite: 44 tests passed in 16.470 seconds |
| Python/templates/dependencies | Ruff lint passed; Ruff format: 106 files already formatted; djLint: seven templates checked, zero updates; npm source formatting and pip check passed; approved npm audit: zero vulnerabilities |
| Documentation/privacy | 183 relative links/anchors, fences, filename/date, unchanged downstream statuses, preserved Alex snapshot, private seed-value exclusion, and diff whitespace passed after edits |

No new tests were added for this reversible decoration. No sign-in logic, model, schema, private environment value, account, or workflow record changed. The previous UI-04 handoff contains the both-role browser authentication checks; this follow-up verifies layout and reruns the full integration suite.

## Next action

Jerome reviews the updated signed-out preview. Refresh cached styles when revisiting an older tab; the verified preview is available at `http://localhost:8000/accounts/login/`. Review the uncommitted changes before separately requesting publication. Other members' tasks and T20/T21 readiness are unchanged.
