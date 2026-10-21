# T20 main integration review and documentation

- Date: October 21, 2026, Asia/Manila.
- Owner: Jerome Avecilla with Codex review/documentation assistance. T20 implementation belongs to Ralph Andre F. Giga; preserve his source commit and Codex co-author credit, plus earlier Alex/Kiro contributions.
- Scope: review the user-merged T20 delivery and reconcile current documentation. No application changes, new implementation, commit, push, PR, main merge, teammate message or diagram work.

## Integration and outcome

Ralph's source `b43fb999ee571bbb90a1d5be32245c2d7f638b1c` is integrated through [PR #51](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/51) at `6f18116da83859aa6b4e2d2c982104cfae4e62b6`, with Git merge time October 21, 16:20:19 Asia/Manila. Freshly fetched `origin/main` equals local `jerome` HEAD. Source ancestry and exact source/merge tree equality are verified: `1502ca5fb81a9f2887bebac7090c2fbd67f2b6de`. The earlier T20 readiness documentation is also integrated through PR #50 at `f8b1c5b`.

**T20 meets the reviewed functional contract; no blocking runtime defect found.** Review covered the [task acceptance](../docs/tasks.md#administrator-operations), [HTTP behavior](../docs/api_spec.md#basic-user-portal), [coding standards](../docs/coding-standards.md) and actual source:

- [Portal home view](../accounts/views.py) retains safe-method and active-BASIC_USER enforcement, derives identity from the session and supplies the campus date explicitly.
- [Workspace query](../borrowing/queries.py) returns an immutable owner-scoped summary, full counts and bounded previews. It reuses return-aware loan progress; due today is not overdue, partial returns stay active and final returns leave the preview. Recent requests sort newest first; active loans sort earliest due first.
- [Borrower home](../templates/accounts/portal/home.html) uses real named destinations and shared role navigation. Shared fields, statuses, pagination, messages and empty states replace repeated markup across the affected portal/management pages. Pagination retains filters; invalid filters have distinct recovery content. Confirmations retain native CSRF-protected workflows and back-out actions.
- [Seven workspace integration tests](../accounts/tests/test_workspace.py) exercise empty/read-only home, owner tampering, foreign-record isolation, active-role/method boundaries, real approval/release/partial/final damaged-return progression, due-date boundaries, full counts versus bounded previews, pagination and cancellation/CSRF messages. Existing workflow/report tests remain intact.

## Checks run for this review

- Complete PostgreSQL suite: **322 tests passed in 127.102s**, including all seven T20 workspace tests. Django created and destroyed its separate test database; system check found no issues.
- Django database check, migration drift (`makemigrations --check --dry-run --noinput`) and applied-migration check: passed; no model changes detected.
- Full Ruff lint: passed. All three T20 Python files pass Ruff formatting; all 21 affected templates pass djLint.
- Full formatting checks retain three unrelated findings: `inventory/tests/test_portal_equipment.py` line endings, the Python example in archived `handoffs/borrower-portal-ui-improvements-10-20-2026.md`, and attribute wrapping in `templates/inventory/portal/equipment_list.html`. These were preserved. The earlier `accounts/views.py` formatting finding no longer reproduces after T20.
- npm source formatting and build: passed; all nine theme text-role pairs meet 4.5:1 contrast. npm audit: zero vulnerabilities. `pip check`: no broken requirements.
- Documentation: 873 relative targets and 223 heading anchors across 12 changed documents resolve; current integration labels, code references, paired fences, conflict markers and diff whitespace checked after the documentation edits.

The [implementation handoff](ralph-t20-role-workspace-integration-10-21-2026.md) and [Module 19](../docs/manual-test-guide.md#module-19--integrated-role-workspaces-t20) preserve Ralph's earlier 322-test/87.253s run, 17-route/five-width Edge/Chromium browser execution, keyboard/table scrolling, workflow progression, CSV downloads and JavaScript-disabled checks. **Those browser checks were not rerun in this review.** Exact source/merge equality establishes that the reviewed integration preserves that source; it does not invent a new browser run.

## Documentation and next action

Updated [current handoff](../HANDOFF.md), [backlog](../docs/tasks.md#verified-task-evidence), [developer consumer guidance](../DEV.md#t20-readiness-and-consumer-handoff), README, AGENTS, SRS, architecture, HTTP contracts, folder guide, shared-component guidance and manual guide. Removed stale current claims that T20 was local/uncommitted or awaiting main integration; preserved historical handoffs and attributed results.

T01-T20 are accepted and integrated. **Jerome / T21 remains Not started and is ready with T17 integrated.** Its coherent fictional demonstration dataset remains the outstanding prerequisite for T22 system verification and T23 actual user acceptance. No seed command or demonstration rows were created by this review. Live business data and private configuration were not changed.

Screen-reader evaluation, Firefox/Safari, spreadsheet-application checks, complete maintenance-repair browser coverage, historical manual follow-ups and actual system/user acceptance remain open. Diagram work still requires Jerome's explicit go signal and T25 prerequisites. Documentation changes remain uncommitted for review.
