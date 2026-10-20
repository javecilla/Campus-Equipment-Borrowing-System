# Alex T18 Live Administration Dashboard

## Work and owner

- **Task:** T18 — live administration dashboard cards and charts
- **Owner:** Alex Enrico Cayanan (`@AlexCayanan`) with Codex implementation assistance
- **Branch:** `alex`
- **Date:** October 20, 2026, 19:14 Asia/Manila
- **Base:** `2258364c81c8ff15120792a1e5c867b279298651`, matching fetched `origin/main` when work began
- **Publication state:** Completed source on `alex`; scoped commit/push/PR authorized; no merge or main integration evidence

## Current outcome

T18 is **Done locally and awaiting review/integration**. The protected `/manage/` destination now reads committed database state and displays:

- Available physical units
- Pending borrow requests
- Active loans with at least one outstanding unit
- Overdue active loans using the explicit campus date
- Issued loans grouped by issue month, counting each `Loan` once
- Issued physical units grouped by category, counting every `LoanUnit` including returned units

The page preserves the shared administrator shell, active-ADMIN enforcement, GET/HEAD-only behavior, stable test IDs, useful empty states and accessible data tables. Django `json_script` embeds chart data safely; `static/js/dashboard-charts.js` progressively renders dependency-free bars without changing the server-rendered disclosure tables.

## Relevant files and interfaces

- `operations/queries.py` — immutable dashboard result types and `dashboard_snapshot(today)` read model
- `operations/views.py` — campus-date orchestration and JSON-safe presentation conversion
- `templates/operations/manage/dashboard.html` — four cards, two chart panels, disclosure tables, shortcuts and workspace tools
- `static/js/dashboard-charts.js` — validated progressive bar rendering using text-only DOM writes
- `operations/tests/test_dashboard.py` — live workflow, aggregation, access, method, empty-state and JSON-safety coverage
- `docs/manual-test-guide.md` — Module 17 inputs, expected results, read-only snapshot and actual automated checks
- `docs/tasks.md`, `DEV.md`, `HANDOFF.md` — local completion evidence and integration gate

No model, migration, endpoint name or repository dependency changed. The local environment was refreshed from the existing `requirements-dev.txt`; this installed the already-pinned Pillow 13.0.0 package that was missing from `.venv`, without changing repository dependency declarations.

## Verification

| Check | Actual result |
| --- | --- |
| Focused T18 tests | 4 passed in 0.304s |
| `operations.tests` | 32 passed in 3.864s |
| Full Django PostgreSQL suite | 298 passed in 54.443s; system check found no issues |
| `manage.py check --database default` | Passed; no issues |
| `makemigrations --check --dry-run --noinput` | Passed; no changes detected |
| `migrate --check` | Passed; no unapplied migrations |
| `ruff check .` | Passed |
| Ruff format check for the three changed Python files | Passed |
| djLint check for the changed dashboard template | Passed; zero files would be updated |
| `npm.cmd run format:check` | Passed |
| `npm.cmd run build` | Passed; all nine theme pairs pass and `dashboard-charts.js` builds |
| `npm.cmd audit` | Passed; zero vulnerabilities |
| `python -m pip check` | Passed; no broken requirements |
| `git --no-pager diff --check` | Passed |
| Read-only `dashboard_snapshot()` against the development database | Four card values were `0`; monthly/category series were empty; no writes |

Repository-wide formatting still reports two pre-existing findings outside T18: Ruff would reformat a Python example in `handoffs/borrower-portal-ui-improvements-10-20-2026.md`, and djLint would split one long tag in `templates/inventory/portal/equipment_list.html`. The changed T18 Python files pass Ruff formatting; the dashboard template was formatted separately. These unrelated files were not modified.

## Unresolved items and decisions

- Manual browser workflow, keyboard, 390/320-pixel viewport, JavaScript-disabled, screen-reader and cross-browser checks remain **Not run**. Module 17 records exact cases without claiming passes.
- The local development database currently has no business records, so its real snapshot correctly produces zero cards and empty charts. Automated tests create disposable committed workflow data instead of modifying live records to manufacture demonstration totals.
- The monthly series includes every stored issue month in chronological order because the T18 contract specifies monthly issued-loan counts but no reporting date window. T19 owns explicit date-filtered reporting.
- No chart library was added; the small page module is sufficient for the required bar presentation and keeps disclosure tables available without JavaScript.
- T19 is **blocked** until T18 is accepted and integrated into `main`. Local completion is not an integrated prerequisite under `PLAN.md`.

## Next action

Publish the authorized scoped T18 commit to `origin/alex` and open the authorized PR into `main`. Jerome's review and main integration remain separate and are not authorized by this handoff. After integration evidence is recorded, Alex may re-evaluate T19 readiness. T20 continues to wait for integrated T18 and T19.
