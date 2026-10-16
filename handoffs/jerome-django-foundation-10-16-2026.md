# Jerome Django foundation

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date: October 16, 2026, Asia/Manila (UTC+08:00).
- Scope: T01–T03; requested README quick start and detailed DEV migration/team guidance.
- Authorization: the user explicitly allowed these three foundation tasks as one local, uncommitted batch before main integration. Other members' feature dependencies remain required.
- Delivery: `jerome`, uncommitted; no new commit, push, PR, or merge. HEAD and fetched `origin/main` remain `5b0d6302383ad7194bb9cc2ca4272b142fb011f0`. **Not integrated**.

## Outcome and actual interfaces

T01–T03 meet their local acceptance criteria. The [backlog](../docs/tasks.md#verified-task-evidence) separates this result from main integration. No login, management/portal pages, borrowing workflows, or demonstration seed is delivered.

| Area | Implemented source/interface |
| --- | --- |
| Bootstrap/configuration | [manage.py](../manage.py), [config/settings.py](../config/settings.py), WSGI/ASGI entry points, and [read_environment(path, process_environment)](../config/environment.py). Required private configuration, literal dotenv values, explicit process overrides, malformed/duplicate-key errors, typed settings, no secret values in configuration error messages |
| Shared schema | [accounts](../accounts/models.py), [inventory](../inventory/models.py), [borrowing](../borrowing/models.py), and [operations](../operations/models.py) define all 14 shared models. `accounts.User` is selected before the initial migration. Django migrations own constraints/indexes; cross-table workflow responsibilities remain with their feature services |
| Settings initialization | [operations/migrations/0002_initial_settings.py](../operations/migrations/0002_initial_settings.py) atomically creates row 1 with limits 7/3 and a SYSTEM/SETTINGS_INITIALIZED audit. The initializer is deliberately irreversible |
| Shared locks | [operations/locking.py](../operations/locking.py): `lock_borrower(owner_id)`, `lock_request(owner_id, request_id)`, `lock_catalog(catalog_item_ids)`, `lock_units(unit_ids)`, `lock_available_units(catalog_item_ids)`. All require an explicit transaction; typed return records and the canonical ordering are documented in source. These helpers never approve or change statuses |
| Audit | [write_audit(actor_id, action, target_model, target_id, summary)](../operations/audit.py) requires the caller's business transaction, an active actor, compatible enum action/target, existing target, and nonblank sanitized summary. The caller enforces the business action's authorization and excludes secrets/unnecessary contact data |
| Settings services | [get_loan_limits()](../operations/queries.py) reads both limits in one statement into immutable `LoanLimits`; a missing singleton raises explicitly. [update_settings(actor_id, max_loan_days, max_quantity_per_item)](../operations/services.py) rechecks a locked active ADMIN, updates the locked singleton, and writes its audit in the same transaction |
| Pure validation | [operations/validation.py](../operations/validation.py): explicit typed limits and requested items, positive per-item limits, one to three distinct rows, submission-date limits, and pre-issue revised-date checks. Feature owners must still validate catalog eligibility and workflow state |
| Setup and checks | [README](../README.md#run-locally) has startup steps. [DEV](../DEV.md#application-migrations-checks-and-local-server) covers migration inspection/application/creation, local tests/Ruff, dependencies, and team synchronization. Runtime/dev requirements and [Ruff configuration](../pyproject.toml) are shareable; the environment remains ignored |

## Verification performed

All results below were executed for this work, including verification after the interrupted turn resumed.

| Check | Actual result |
| --- | --- |
| Existing branch/baseline | Clean `jerome` was already selected; fetched main matched HEAD before edits. No branch reset, history rewrite, or unrelated work was performed |
| Runtime installation | Existing Python 3.13.12 used to create local `.venv`; declared pins installed with uv. Pip was bootstrapped locally, then `python -m pip install -r requirements-dev.txt` and `python -m pip check` passed |
| Fresh PostgreSQL migration | PostgreSQL 17.5 public schema had zero tables before migration. All 22 migrations applied successfully, including seven project migrations. A subsequent `migrate --plan` reported no planned operations and `migrate --noinput` reported no migrations to apply |
| Schema/data inspection | 22 public tables, 22 migration records; singleton row `(1, 7, 3, null updater)`, one SYSTEM initialization audit, zero User records. Test fixtures stayed in the separate test database |
| Django tests | `python manage.py test --noinput`: **23 passed**. Seven bootstrap/configuration tests and sixteen real PostgreSQL schema/service/locking tests. Includes active-allocation exclusivity after release, duplicate issue/return constraints, date/quantity/enum/maintenance rules, real database audit-insert failure rolling back settings, unchanged existing request snapshots, missing-singleton failure, and separate-connection row blocking (`55P03`) followed by successful lock acquisition after commit |
| Django checks | `check --database default`, `makemigrations --check --dry-run --noinput`, and `migrate --check` pass with no issues/drift/pending migrations |
| Ruff | `ruff check .` and `ruff format --check .` pass |
| Local HTTP smoke | `runserver 127.0.0.1:8000 --noreload` booted without system errors or unapplied migrations. With DEBUG=False, /, /admin/, /manage/, /portal/ returned 404 HTML as expected for empty routes. Debugging mode displayed Django's native welcome screen. Server processes were stopped after inspection |
| Read-only MCP | Connected execute_sql returned `transaction_read_only=on` and 22 public tables. Shared/private MCP configuration was not changed |
| Scope/private files | `.env.local`, `.venv`, Ruff cache, and collected static output remain ignored. Source requirement/member TXT files, MCP configuration, skills, and prior dated handoffs are preserved. All 327 local links/anchors across 24 Markdown files resolved, code fences and handoff naming passed, no private credential values appeared across 77 shareable paths, and Git whitespace checks passed |

The date-limit constraint compares a calendar-day difference rather than adding a potentially large positive duration to a date, avoiding database date overflow. The expression's keyword order matches Django's migration serialization, so the model does not repeatedly generate equivalent constraint migrations.

## Remaining work and next owner

- Jerome reviews this uncommitted diff. Publication/main integration needs a separate user instruction. Update the backlog/current handoff with the actual merge identity and checks after integration; this snapshot does not claim a merge.
- Alex / T04: local T02 acceptance exists, but main integration is still missing. After integration, implement shared login/logout, role/active/ownership checks, and authorized admin-account provisioning using the actual custom user schema.
- Jerome / T06: T03 is locally accepted; T04 and main integration remain missing. Add settings/audit forms, queries, views, and templates only once that access contract exists.
- Jerome with Margareth / T14 still requires the real T13 approval service. A foundation lock test is not the last-unit competing-approval scenario.
- T21, T24, T25, technical T29 and shared acceptance/course work still need their backlog prerequisites and actual evidence. No meetings, user feedback, benchmark, backup/restore, seed dataset, or teammate contribution was fabricated.
- Not run: clean-machine installation, macOS/Linux, complete browser/product workflows, T14 competing approvals, performance measurements, backup/restore, or GitHub Actions CI. These remain distinct later tasks.
