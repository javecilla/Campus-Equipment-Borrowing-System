# Minimal branded login

- Owner: Jerome Avecilla, with Codex assistance.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00), around 11:56.
- Task: UI-04, explicitly requested login presentation refresh. Scope is the existing login template and input styling; no authentication feature or other member's page was added.
- Delivery: local, uncommitted on `jerome`, based on `cb96319`; **Not integrated**. Earlier uncommitted work and dated handoffs preserved. No commit, push, PR, or merge performed.

## Outcome and files

The user supplied [Notion's login page](https://app.notion.com/login?from=marketing&pathname=%2F) as the visual reference. The page was inspected in Chrome: a small logo, centered narrow column, open white background, compact headings, and simple form controls informed this layout. No reference-site assets or code were copied.

- [Login template](../templates/accounts/login.html): removes the outer card/border/shadow, displays the existing [logo](../static/images/logo.jpg) at 48px, adds a centered heading/subtitle, and keeps a 384px maximum content column with mobile gutters. Form labels, associated errors, generic-error alert, CSRF, hidden `next`, named action, and stable test IDs remain present.
- [LoginForm](../accounts/forms.py): only the two widget class strings change, adding compact 44px controls with neutral borders and emerald focus treatment. Username/email/password validation and session behavior are unchanged from AUTH-02.
- Existing shared shell, local DM Sans/Poppins fonts, green `accent` token, and Tailwind build are reused. Source logo bytes and shared CSS are unchanged; no new library, generated image, script, or nonfunctional login option was added.
- [Backlog](../docs/tasks.md#shared-frontend-tooling) records UI-04 acceptance; [HANDOFF.md](../HANDOFF.md) records readiness and indexes this snapshot.

## Verification performed

| Check                 | Actual result                                                                                                                                                                                                                                                     |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Desktop browser       | Chrome at 1704×803: logo loaded; content column 384px; no section border or shadow; page width equals viewport; button computes to existing accent `rgb(4, 120, 87)`; focused input has the emerald border/ring                                                   |
| Mobile browser        | Temporary viewport 375×812: form width 327px; page width 375px with no horizontal overflow; labels remain associated and password input remains masked. Default viewport restored afterward                                                                       |
| Keyboard/error UI     | Username → password → sign-in tab order verified; button keyboard focus uses a visible solid outline. Incorrect credentials render the generic error within `role="alert"`; screenshots inspected for clean and error states                                      |
| Live authentication   | Basic-user email reached `/portal/` from the mobile layout and signed out; administrator email reached `/manage/` in a fresh desktop preview and signed out. Both flows used existing accounts/passwords. Final preview remains signed out                        |
| PostgreSQL suite      | 44 tests passed in 16.441 seconds; separate test database created and destroyed. No new tests added for reversible styling                                                                                                                                        |
| Django/schema         | Database check: no issues; migration drift: no changes; applied-migration check: passed                                                                                                                                                                           |
| Python/templates      | Ruff lint passed; Ruff format: 105 files already formatted; djLint: seven templates checked, zero updates                                                                                                                                                         |
| Assets/dependencies   | npm build and source formatting passed; pip check: no broken requirements; approved npm audit: zero vulnerabilities                                                                                                                                               |
| Documentation/privacy | 418 relative links/anchors across 15 documents, fences, handoff naming, unchanged application feature statuses, preserved Alex snapshot, unchanged source logo/shared CSS, private seed-value exclusion from shared files, and diff whitespace passed after edits |

Browser control briefly timed out during navigation in one preview; a fresh tab on the same browser completed the administrator check. No application error was inferred from that control timeout. Chrome is the only browser tested; no full accessibility audit or other-device certification is claimed. No database records were deleted or reseeded, and no password was changed or saved to the browser.

## Next action

Jerome reviews the signed-out local login preview and the uncommitted changes. Existing username/email sign-in uses the same private seed credentials. Feature owners keep their current task scopes; T20's complete application UI integration remains pending its own prerequisites. Publication requires a separate request.
