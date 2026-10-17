# Login screen and auth development guide

- Owner: Jerome Avecilla, with Codex assistance; builds on Alex Enrico Cayanan's integrated T04 authentication work.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00).
- Scope: user-supplied login screenshot and local seed/error-preview guidance; verification of the authorized auth/UI/documentation publication batch.
- State at verification: local on `jerome`, based on `847a8c0`; **Not integrated**. User authorized commit/push with Alex and Codex co-author credit. No new PR or main merge requested.

## Outcome and relevant files

[DEV.md](../DEV.md#expected-startup-screen) now displays [login-screen.png](../static/images/login-screen.png) as the current anonymous startup screen; earlier setup images remain in a historical disclosure. The supplied screenshot was visually inspected and contains no entered credentials. T04's existing main integration through PR #9 and PR #10 is reflected in the guide.

The canonical [seed setup](../DEV.md#seed-authentication-test-accounts) lists both fictional role identities, using the private environment password without publishing its value. [Reset guidance](../DEV.md#delete-only-the-two-authentication-seed-accounts) includes the requested narrowly scoped deletion/reseed command and explains Profile cascading and protected-history refusal. [Error preview steps](../DEV.md#preview-custom-error-pages) explain DEBUG=False, local-only `--insecure`, real 403/404 paths, process overrides, and restoration of ordinary debugging. These instructions were documented without deleting/reseeding accounts or editing private settings.

## Verification performed

- Full real PostgreSQL suite: 44 tests passed in 16.006 seconds, with a separate test database created/destroyed.
- Django database check: no issues; migration drift: no changes; applied-migration check passed.
- Ruff lint passed; Ruff format reported 110 files already formatted; djLint checked 11 templates with zero updates.
- Full npm build and source formatting passed; pip check passed; approved npm audit found zero vulnerabilities.
- Supplied screenshot inspected visually; existing UI-04/UI-05 snapshots retain the actual browser checks. No redundant browser run was needed for this documentation update.
- 490 relative links/anchors across 20 changed or new documents passed, with Markdown fences checked. All 18 original T04–T21 task rows and source briefs are unchanged. Private seed/database passwords and Django secret are absent from publishable files; Git ancestry, empty index, unchanged LF policy, retained stash, and diff whitespace passed. The batch contains 39 reviewed files. No seed-deletion command was executed.

## Attribution and next action

Alex's original T04 commit `7ae5e87` and LF correction `5f42ac0` remain in ancestry with their authors unchanged. Git history confirms Alex's identity as `Alex Enrico Cayanan <AlexCayanan@users.noreply.github.com>`. The requested follow-up commit uses that co-author trailer plus `Codex <codex@openai.com>`; Jerome remains the submitting member.

Commit and push the verified batch to `origin/jerome` using ordinary history, preserve the existing stash backup, and record actual publication evidence in the current handoff/backlog. Registration, borrowing workflows, live reporting, full T20 layouts, and T21 demonstration data retain their existing status and owners. Main integration requires a separately requested PR/merge.
