# Operational settings, audit history, and evidence collection guide

- Owner: Jerome Avecilla with Codex assistance; Alex's authentication/account work preserved.
- Date: October 17, 2026, Asia/Manila (UTC+08:00).
- Tasks: T06 Done locally; T26 In progress (requested guide only; actual research pending).
- Delivery: local uncommitted changes on `jerome`, based on fetched main `c2ff921` (PR #16). **Not integrated**; no new commit, push, PR, or main update.

## Accepted scope and interfaces

T03 `d122518`, T04 `cb96319`, T05 source `22fb720`/merge `7a80257`, and shared UI `a444de9` were verified as ancestors of fetched main. The clean member branch fast-forwarded from `d4f10ca` to `c2ff921` before edits.

- [SettingsForm and AuditSearchForm](../operations/forms.py) allowlist the two positive integer limits and documented audit filters. Invalid settings render bound errors without writes. Audit filters reject unknown actions, invalid actor IDs, invalid/reversed dates, and overlong search text.
- [Custom views](../operations/views.py) replace the T06 placeholders through existing [named URLs](../operations/urls.py). Settings accepts GET/HEAD/POST and uses server-derived actor identity with the existing `update_settings(actor_id, max_loan_days, max_quantity_per_item)` transaction. Audit accepts GET/HEAD only, requires active ADMIN access, and has no edit/delete interface.
- [Read-only queries](../operations/queries.py) expose `get_system_setting()` and preserve `get_loan_limits() -> LoanLimits`. `audit_history(search_query, action, actor_id, date_from, date_to)` returns related-actor-loaded entries ordered newest first; reference search matches `target_model#target_id`, and occurrence-date filters use inclusive Asia/Manila dates. Pagination is 25 rows with strict 404 handling and preserved filters.
- [Settings template](../templates/operations/manage/settings.html), [audit template](../templates/operations/manage/audit_list.html), and [field fragment](../templates/operations/manage/form_field.html) reuse the shared admin layout, labels, native forms/CSRF, escaping, accessible feedback, and stable IDs. [HTTP contracts](../docs/api_spec.md) record the implemented behavior.
- [T26 guide](../docs/user-needs-evidence-guide.md) lists collection needs, interview/usability questions, recording worksheets, option comparison, tool/reuse evidence, and an emerging-technology evaluation process. It links existing technical sources instead of duplicating package/architecture claims. README links the guide. The user confirmed that real feedback/interviews/evaluation are unavailable; none was fabricated.

No dependency, model, or migration changes were required. No other member's workflow was implemented.

## Verification performed

| Check | Actual result |
| --- | --- |
| `python manage.py test operations.tests.test_settings_audit operations.tests.test_navigation --noinput` using `.venv` | 11 tests passed |
| `python manage.py test --noinput` using `.venv` | All 68 tests passed against PostgreSQL, including seven new T06 integration tests and the existing real audit-failure rollback check |
| Settings acceptance | GET/HEAD read without writes; valid POST audits correct before/after limits and server actor; forged metadata ignored; invalid/missing/out-of-range inputs do not write; existing snapshots retained; new limits used by shared date/item validation |
| Audit acceptance | Combined reference/action/actor/date filters; inclusive Manila midnight boundaries; system actor; errors and empty state; stable two-page ordering and preserved filters; malformed/nonexistent pages 404; escaped summaries |
| Authorization/protocol | Anonymous redirects, BASIC_USER denial despite staff/superuser flags, inactive-session invalidation, CSRF denial, and method restrictions passed through real Django client requests |
| Django database/system check, migration dry run, migration check | Pass; no model changes detected or unapplied migrations |
| Ruff lint and format check; template djLint check | Pass; all Python files formatted, all 31 templates formatted |
| npm build, format check, audit; pip check | Pass; zero npm vulnerabilities, no broken Python requirements |
| Documentation and final diff | 373 local links/anchors across six changed documents and code fences checked successfully; final Ruff/djLint and `git diff --check` pass. Original requirement/member files and archived handoffs preserved |
| Chrome browser flow | Existing local admin session at port 8000: saved 4 days / 2 units, observed success, restored 7 days / 3 units, and verified both audit entries. Filtered actual history, exercised reversed-date errors and reset, and checked keyboard field order |
| Responsive DOM/layout checks | At 375px, controls fit a 327px content width and audit table scrolling stays inside its region; no document horizontal overflow. Settings also has no document overflow at 1440px. Temporary viewport override reset |
| Screenshot review | Browser capture repeatedly timed out. No screenshot artifact or pixel-level visual acceptance is claimed |

The browser checks leave the initialized local limits at **7 calendar days / 3 units per item** and retain the two genuine audit events. The existing local runserver/session was used and left running. No audit events were deleted.

## Limitations and next actions

- T11 submission does not exist yet. Shared limit reading/validation and existing snapshot preservation are verified; an end-to-end newly submitted request must be checked by Ralph after T08/T09 are integrated. Use `get_loan_limits()` once per submission and persist both snapshots within the request transaction.
- Jerome reviews the uncommitted T06/T26 diff. Commit/push/PR/main integration require a separate explicit request. No task depends directly on T06 in the current backlog; other members keep their own prerequisite gates.
- T26 remains In progress. Alex/Jerome coordinate actual borrower/admin needs, reviewed options/recommendation, tool/reuse justification, and an emerging-technology adopt/defer evaluation with all members. Fill the guide with real findings and link later T23/T25/T27/T28/T29 records.
- Jerome's T14 needs integrated T13; T21 needs T17; T24 needs T22; T25 needs T22/T23/T24; technical T29 needs T22/T24. The current tests/guide do not complete these later tasks or the team-wide acceptance/delivery tasks.
- Pixel-level desktop/mobile visual review remains open because browser screenshot capture failed; DOM behavior, dimensions, labels, and keyboard checks passed.
