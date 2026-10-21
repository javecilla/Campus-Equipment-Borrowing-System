# Alex T19 Administrator Loan and Overdue Reporting

## Work and owner

- **Task:** T19 — administrator loan and overdue reporting with CSV exports
- **Owner:** Alex Enrico Cayanan (`@AlexCayanan`) with Codex implementation assistance
- **Branch:** local `alex`
- **Date:** October 20, 2026, 23:27 Asia/Manila
- **Base:** implemented and initially verified on fetched `origin/main` `0e05ed6ea7bbd8f2994cd4e793ca2717a6c534ab`; restored and verified atop fetched `origin/main` `c0529009cacd3e234f04cc07b4fc5c4c70261522`
- **Dependencies:** T17 source `bd62ed7b93db965ed5b4442af84e8186ccf45065` and T18 source `54380fd912b6cb684c11a8c2e79fa4cac00f856a` are ancestors of the base; T18 reached main through PR #45 merge `26b1ee555ae5b98e9d744bd7a11b3bfb74153b60`
- **Publication state:** Done on the authorized `alex` publication candidate; not integrated into main
- **Publication preparation:** October 21, 2026, 01:15 Asia/Manila

## Current outcome

T19 implements four active-administrator-only GET endpoints:

- `/manage/reports/loans/`
- `/manage/reports/loans/export/`
- `/manage/reports/overdue/`
- `/manage/reports/overdue/export/`

Both reports use optional inclusive `date_from` and `date_to` filters against the stored Asia/Manila issue date. Invalid or reversed ranges render bound errors without exposing unfiltered rows; malformed or nonexistent pages return 404. Loan rows are ordered newest issue date/time/ID first and paginate at 25 rows while preserving filters. The overdue report includes only loans whose due date is before the current campus date and which still have outstanding LoanUnits.

Each HTML row and CSV row identifies the loan, request, borrower, purpose, issue/due dates, request/derived loan statuses and exact issued/returned/outstanding quantities. The overdue version also includes overdue days. Query helpers aggregate each loan once and count physical LoanUnits directly so return joins cannot multiply rows or totals. Empty results show report-specific messages.

CSV exports apply the identical filters, ordering and totals to every matching row rather than only the current page. Responses use `text/csv; charset=utf-8`, a UTF-8 BOM, stable attachment filenames and explicit headers. Any string cell beginning with `=`, `+`, `-`, `@`, tab or carriage return receives an apostrophe prefix before CSV encoding. Unicode, commas, double quotes and embedded newlines remain valid CSV fields.

All page/export endpoints reuse T04's active-administrator guard and reject unsupported methods with 405. Anonymous GET requests redirect safely to login; BASIC_USER and inactive administrators are denied. The implementation performs only SELECT queries and adds no service, transaction mutation, model, migration, dependency, demonstration data, T20 work or unrelated dashboard change.

## T19-only boundary

Whole implementation/test/template files:

- `operations/forms.py` — `ReportDateFilterForm` addition only
- `operations/queries.py` — T19 result type and report query/total helpers only
- `operations/workspace_views.py` — report presentation, page, CSV and four endpoint additions only
- `operations/urls.py` — four T19 report/export route entries only
- `operations/tests/test_reports.py` — complete new T19 PostgreSQL regression module
- `templates/operations/manage/report.html` — complete new shared report template

Mixed implementation/template files with T19-only hunks:

- `operations/tests/test_navigation.py` — replaces the old loan-report placeholder expectations with GET-only implemented-report expectations
- `templates/operations/manage/base.html` — keeps Reports active across the loan and overdue report pages

T19 documentation boundary:

- `docs/tasks.md` — current phase, T19 status/evidence and T18 consumer wording only
- `docs/manual-test-guide.md` — T19 scope references, Module 18, result example and unavailable-feature list only
- `HANDOFF.md` — T19 current state, phase/dependency wording, dated index, verification row and next action only
- `handoffs/alex-t19-administrator-loan-and-overdue-reporting-10-20-2026.md` — this complete file

No authentication file or inactive-account follow-up content was changed. The inactive-login work is already integrated through PR #46 at main `c052900`; T19 does not alter that source or evidence.

## Verification

| Check | Actual result |
| --- | --- |
| Focused `operations.tests.test_reports` stress runs | 11 passed with seed `1919` in 1.801s, seed `20261020` in 1.601s and reverse order in 1.662s; after strengthening method/field assertions, seed `20261020` passed in 1.576s |
| Reversed `operations borrowing` suites | 130 passed in 26.833s |
| Fresh shuffled complete PostgreSQL suite | 309 passed in 71.614s with seed `20261020`; system check found no issues |
| Post-sync report/navigation/dashboard regression | 22 passed in 5.791s on `c052900`; system check found no issues |
| Post-sync complete PostgreSQL suite | 315 passed in 73.795s on `c052900`; system check found no issues |
| Exact publication-candidate regression | 22 report/navigation/dashboard tests passed in 3.425s; system check found no issues |
| `manage.py check --database default` | Passed; no issues |
| `makemigrations --check --dry-run --noinput` | Passed; no changes detected |
| `migrate --check` and `showmigrations --plan` | Passed; no pending migrations and every listed migration is applied |
| `ruff check .` | Passed |
| Ruff format check for six affected Python files | Passed; all six already formatted |
| djLint for the two affected templates | Passed; zero files would be updated |
| `npm.cmd run format:check` | Passed |
| `npm.cmd run build` | Passed; all nine theme pairs pass and frontend assets build |
| `npm.cmd audit` | Passed; zero vulnerabilities |
| `python -m pip check` | Passed; no broken requirements |
| `git --no-pager diff --check` | Passed |
| Staged boundary and sensitive-value scan | Exactly the 12 authorized paths; no staged AUTH-02 hunk, private path, credential-like value or unexpected unstaged implementation |
| Affected documentation links | 463 relative targets and 67 heading anchors passed against the staged tree |
| Read-only regression assertion | HTML and both exports execute only SELECT queries and preserve model row counts |

After the main synchronization, `manage.py check --database default`, migration drift/applied checks, affected-file Ruff lint/format, affected-template djLint, pip and whitespace checks passed. The first asset build correctly exposed stale local dependencies missing main's new Chart.js package; `npm.cmd ci` synchronized `node_modules` from the committed lockfile, after which npm format, theme/build and audit passed with zero vulnerabilities. The npm `min-release-age` configuration warning is non-blocking and did not change repository files.

The first complete run reused a stale kept test database and failed with 49 errors plus one failure because the required `SystemSetting` row was absent. Recreating the PostgreSQL test database with the ordinary no-input test command resolved the environmental fixture state; both subsequent fresh 309-test runs passed, including the final shuffled exact-tree run. This was not fixed in T19 source.

Repository-wide formatting has two unrelated findings outside T19: Ruff would reformat a Python example in `handoffs/borrower-portal-ui-improvements-10-20-2026.md`, and djLint would split one long tag in `templates/inventory/portal/equipment_list.html`. Affected T19 Python/templates pass targeted formatting; neither unrelated file was modified.

## Manual and isolated evidence

Browser verification is **Not run**. The computer-use runtime exposed no browser surface, so no administrator/BASIC_USER workflow, downloaded-spreadsheet, desktop/390/320 viewport or keyboard-focus result is claimed.

A temporary PostgreSQL database with fictional records was created only for an isolated read check. It produced 27 loan rows totaling 31 issued, 3 returned and 28 outstanding units, plus one overdue row totaling 3 issued, 1 returned and 2 outstanding. The temporary server, database and generated clipboard password were removed afterward; no development records were changed.

A later manual-test preparation session created `T19-DEMO-*` records in the ignored local development database through the existing workflow services. Those records are not part of Git or this publication. No populated report browser, responsive, keyboard, downloaded-spreadsheet or spreadsheet-opening check was run.

[Module 18](../docs/manual-test-guide.md#module-18--administrator-loan-and-overdue-reporting-t19) records the exact pending steps for:

- administrator access and both issue-date filters
- BASIC_USER/inactive-administrator denial
- invalid and reversed ranges
- filter-preserving pagination
- HTML totals versus downloaded CSV rows/totals
- Unicode/quoted/newline and formula-prefixed CSV cells in a spreadsheet
- desktop, 390px and 320px layouts
- visible keyboard focus and navigation

## Unresolved items and decisions

- Manual browser, responsive, keyboard, populated local-data report and spreadsheet-opening evidence remains Not run until a browser surface is available.
- Cross-browser, screen-reader, performance and system-wide acceptance remain outside this implementation result.
- Repository-wide formatting findings remain separate cleanup work and do not belong in T19.
- T19 is locally complete but is not an integrated prerequisite. Ralph must not start T20 from this worktree evidence alone.
- Commit, normal push to `origin/alex` and an `alex`-to-`main` review PR are authorized; merge, main modification, T20 and teammate messages are not.

## Next action

Publish only the verified T19 boundary on `alex`, leave the review PR open for Jerome and wait for verified main integration before declaring T20 ready.
