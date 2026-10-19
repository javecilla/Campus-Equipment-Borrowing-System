# Work Handoff: T16 Equipment Maintenance and Inventory Reconciliation

- **Date**: October 19, 2026
- **Time Zone**: Asia/Manila (UTC+08:00)
- **Author**: Kenneth T. Cortez (`@corkenneth`) with Antigravity AI assistance
- **Branch**: `kenneth`
- **Delivery State**: Uncommitted on `kenneth`; **Not integrated into main**

---

## 1. Scope and Outcome

Implemented **T16** ([docs/tasks.md#administrator-operations](file:///C:/Users/acer/Documents/000%204th%20Year%20Kenneth/1st%20Semester/5.%20Web%20Programming%20and%20Frameworks/Project/Campus-Equipment-Borrowing-System/docs/tasks.md#administrator-operations)) in full compliance with [docs/api_spec.md](file:///C:/Users/acer/Documents/000%204th%20Year%20Kenneth/1st%20Semester/5.%20Web%20Programming%20and%20Frameworks/Project/Campus-Equipment-Borrowing-System/docs/api_spec.md#custom-administration-accounts-and-inventory), [docs/SRS.md](file:///C:/Users/acer/Documents/000%204th%20Year%20Kenneth/1st%20Semester/5.%20Web%20Programming%20and%20Frameworks/Project/Campus-Equipment-Borrowing-System/docs/SRS.md) (BR-12, BR-13, BR-15, FR-38 to FR-44), [docs/db_design.md](file:///C:/Users/acer/Documents/000%204th%20Year%20Kenneth/1st%20Semester/5.%20Web%20Programming%20and%20Frameworks/Project/Campus-Equipment-Borrowing-System/docs/db_design.md), and [docs/coding-standards.md](file:///C:/Users/acer/Documents/000%204th%20Year%20Kenneth/1st%20Semester/5.%20Web%20Programming%20and%20Frameworks/Project/Campus-Equipment-Borrowing-System/docs/coding-standards.md):

* **Maintenance Workflow Services (`inventory/services.py`)**:
  * `open_maintenance`: Acquires a row lock on `Unit` with `select_for_update()`. Validates that the unit is in `AVAILABLE` status, strictly rejecting `RESERVED`, `ISSUED`, `MAINTENANCE`, or `RETIRED` units. Verifies no duplicate open maintenance records exist for the unit. Atomically transitions unit status to `MAINTENANCE`, creates a `MaintenanceRecord` (type `SCHEDULED` or `UNSCHEDULED`), and writes an `AuditLog` entry with `AuditAction.MAINTENANCE_OPENED`.
  * `close_maintenance`: Acquires row locks on `MaintenanceRecord` and `Unit` with `select_for_update()`. Validates that the maintenance record is currently `OPEN`. Accepts required servicing `action` and `outcome` (`AVAILABLE` or `RETIRED`). Enforces condition repair rules: when returning a unit to `AVAILABLE` that was previously in `DAMAGED` condition, its condition is transitioned to `GOOD` (or chosen repaired condition), strictly adhering to PostgreSQL check constraint `unit_damaged_unavailable` (`~Q(condition=DAMAGED) | Q(status__in=[MAINTENANCE, RETIRED])`). Updates the maintenance record to `CLOSED`, sets `completed_at`, records `action_taken`, `resolution_outcome`, and `serviced_by`, and writes an `AuditLog` entry with `AuditAction.MAINTENANCE_CLOSED`.

* **Read-Only Query Helpers (`inventory/queries.py`)**:
  * `list_maintenance_records`: Provides a filtered query for maintenance records across search text `q` (matching unit asset code, maintenance problem, action taken, and catalog item name) and `status` (`OPEN` or `CLOSED`). Orders chronologically with most recent records first (`-created_at`).
  * `get_maintenance_or_404`: Retrieves a `MaintenanceRecord` by ID with related `unit` and `unit__catalog_item` pre-selected, raising `Http404` when not found.

* **Forms and Validation (`inventory/forms.py`)**:
  * `MaintenanceSearchForm`: Clean, allowlisted GET form supporting search query (`q`) and status choices (`ALL`, `OPEN`, `CLOSED`).
  * `MaintenanceCreateForm`: Restricts unit selection to `AVAILABLE` units without an open maintenance record. Collects maintenance type (`SCHEDULED` / `UNSCHEDULED`) and required problem description.
  * `MaintenanceCloseForm`: Collects required `action_taken`, resolution outcome (`AVAILABLE` / `RETIRED`), and repaired condition selector when returning a unit to service.

* **Administrator HTTP Views (`inventory/views.py`)**:
  * Replaced the pending module placeholder with active, production-grade views protected by `@admin_required`:
    * `maintenance_list` (`/manage/maintenance/`): 25-row paginated list with search and status filters, top-level inventory KPI cards (Total registered, Serviceable, Available, Reserved, Issued, Maintenance, Retired), and empty states.
    * `maintenance_detail` (`/manage/maintenance/<int:record_id>/`): Displays complete maintenance record attributes, servicing dates, action taken, resolution outcome, servicing admin, and direct links to the physical unit and catalog item.
    * `maintenance_create` (`/manage/maintenance/new/`): Allows administrators to schedule or log maintenance on available physical units with optional pre-selection via `?unit=<id>`.
    * `maintenance_close` (`/manage/maintenance/<int:record_id>/close/`): Allows administrators to resolve open maintenance, update unit condition, return the unit to service or mark it retired, and reconciles inventory counts.

* **URL Routing (`inventory/manage_urls.py`)**:
  * Registered routes: `maintenance-list` (`maintenance/`), `maintenance-create` (`maintenance/new/`), `maintenance-detail` (`maintenance/<int:record_id>/`), and `maintenance-close` (`maintenance/<int:record_id>/close/`).
  * Preserved `unit-update` route (`units/<int:unit_id>/edit/`).

* **Templates**:
  * Created `templates/inventory/manage/maintenance_list.html`: Responsive table, KPI cards, filter bar, status badges, pagination controls, and action links.
  * Created `templates/inventory/manage/maintenance_detail.html`: Detailed view of maintenance attributes, audit details, unit metadata card, and close action button.
  * Created `templates/inventory/manage/maintenance_form.html`: Clean creation form with available unit dropdown, maintenance type selector, and problem description.
  * Created `templates/inventory/manage/maintenance_close.html`: Resolution form with outcome choices, action taken textarea, and repaired condition options.
  * Updated `templates/inventory/manage/unit_detail.html`: Added "Open maintenance" button for available units, linkified maintenance records in the history table to their detail and close views, and resolved a pre-existing whitespace issue reported by djLint.

* **Manual Test Guide Documentation (`docs/manual-test-guide.md`)**:
  * Added **Module 11 — Equipment Maintenance and Inventory Reconciliation (T16)** with 7 concrete, field-by-field test cases (T16-01 through T16-07) based on a dated read-only PostgreSQL snapshot (`October 19, 2026, 12:00 Asia/Manila`).
  * Documented exact read-only database records, inputs, and expected vs executed outcomes.
  * Removed T16 from the pending modules list and updated automated test suite instructions.

---

## 2. Shared Interfaces and Files Created/Modified

| Path | Responsibility |
| :--- | :--- |
| [`inventory/services.py`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/inventory/services.py) | Workflow mutation services: `open_maintenance` (row-locking, availability check, duplicate rejection, status change, audit log) and `close_maintenance` (row-locking, resolution outcome, condition repair enforcement adhering to PostgreSQL check constraint, audit log). |
| [`inventory/queries.py`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/inventory/queries.py) | Read-only ORM query helpers: `list_maintenance_records` and `get_maintenance_or_404`. |
| [`inventory/forms.py`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/inventory/forms.py) | Allowlisted forms: `MaintenanceSearchForm`, `MaintenanceCreateForm` (bounded to available units without open maintenance), and `MaintenanceCloseForm`. |
| [`inventory/views.py`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/inventory/views.py) | Replaced pending maintenance placeholder with `maintenance_list`, `maintenance_detail`, `maintenance_create`, and `maintenance_close`. |
| [`inventory/manage_urls.py`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/inventory/manage_urls.py) | URL routing for maintenance list, create, detail, and close endpoints. |
| [`templates/inventory/manage/maintenance_list.html`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/templates/inventory/manage/maintenance_list.html) | Maintenance queue list view with summary KPI cards, search and status filters, and 25-row pagination. |
| [`templates/inventory/manage/maintenance_detail.html`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/templates/inventory/manage/maintenance_detail.html) | Maintenance record detail view with metadata cards, unit link, and close maintenance action. |
| [`templates/inventory/manage/maintenance_form.html`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/templates/inventory/manage/maintenance_form.html) | Maintenance creation form for scheduling or opening maintenance on available physical units. |
| [`templates/inventory/manage/maintenance_close.html`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/templates/inventory/manage/maintenance_close.html) | Close maintenance resolution form with outcome selection, action description, and repaired condition options. |
| [`templates/inventory/manage/unit_detail.html`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/templates/inventory/manage/unit_detail.html) | Added "Open maintenance" action button for available units, linkified maintenance records in unit history, and resolved djLint whitespace issue. |
| [`inventory/tests/test_maintenance.py`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/inventory/tests/test_maintenance.py) | 26 comprehensive integration tests covering service mutations, error cases, row locks, audit logs, inventory reconciliation, access control, CSRF, forms, queries, and pagination. |
| [`inventory/tests/test_catalog_management.py`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/inventory/tests/test_catalog_management.py) | Updated navigation assertion from placeholder text to active "Maintenance". |
| [`docs/manual-test-guide.md`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/docs/manual-test-guide.md) | Added Module 11 test cases (T16-01 through T16-07) with exact read-only database snapshot inputs, expected vs executed checks, and updated execution status. |
| [`docs/tasks.md`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/docs/tasks.md) | Marked T16 as `Done` and added verified task evidence row. |
| [`HANDOFF.md`](file:///C:/Users/acer/Documents/000 4th Year Kenneth/1st Semester/5. Web Programming and Frameworks/Project/Campus-Equipment-Borrowing-System/HANDOFF.md) | Updated current project state, work at handover table, and dated handoff index. |

---

## 3. Verification and Checks

All verification checks were executed locally against PostgreSQL 17:

| Check | Command | Result |
| :--- | :--- | :--- |
| **Maintenance Feature Tests** | `python manage.py test inventory.tests.test_maintenance` | **26 passed** in 3.963s (0 failures, 0 errors) |
| **Combined Inventory Suite** | `python manage.py test inventory.tests` | **90 passed** in 11.233s (0 failures, 0 errors) |
| **Full Regression Suite** | `python manage.py test` | **217 passed** in 37.464s (0 failures, 0 errors) |
| **Django System Check** | `python manage.py check` | 0 silenced issues |
| **Django Database Check** | `python manage.py check --database default` | 0 issues |
| **Migration Drift Check** | `python manage.py makemigrations --check --dry-run` | No changes detected |
| **Unapplied Migrations** | `python manage.py migrate --check` | 0 unapplied migrations |
| **Ruff Lint** | `python -m ruff check .` | All checks passed |
| **Ruff Format Check** | `python -m ruff format --check .` | 166 files cleanly formatted |
| **djLint Template Check** | `djlint.exe templates --check` | 64/64 files checked, 0 errors (pre-existing `unit_detail.html` whitespace resolved) |
| **Prettier Format Check** | `npm.cmd run format:check` | All matched files use Prettier code style |
| **Frontend Assets Build** | `npm.cmd run build` | Tailwind CSS and JS assets built cleanly |
| **npm Security Audit** | `npm.cmd audit` | 0 vulnerabilities (113 scanned packages) |
| **Dependency Integrity** | `python -m pip check` | No broken requirements found |
| **Git Whitespace** | `git diff --check` | Clean |

---

## 4. Manual Testing Status and Limitations

* **Automated Coverage**: 26 new automated tests in `inventory/tests/test_maintenance.py` comprehensively exercise service validation, row locking, error branches, audit log emissions, condition transitions, PostgreSQL check constraints, role authorization (`@admin_required`), CSRF protection, and pagination.
* **Manual Browser Testing**: Detailed step-by-step test cases are documented in [docs/manual-test-guide.md#module-11--equipment-maintenance-and-inventory-reconciliation-t16](file:///C:/Users/acer/Documents/000%204th%20Year%20Kenneth/1st%20Semester/5.%20Web%20Programming%20and%20Frameworks/Project/Campus-Equipment-Borrowing-System/docs/manual-test-guide.md#module-11--equipment-maintenance-and-inventory-reconciliation-t16). Browser execution has not yet been conducted and remains pending user manual testing.
* **Concurrency and Browser Multi-tab Testing**: Concurrent open/close and loan approval races are verified via unit tests with simulated locks, but interactive multi-tab browser concurrency awaits demonstration execution.

---

## 5. Unresolved Issues and Next Actions

1. Changes remain **uncommitted on branch `kenneth`** per project guidelines.
2. Await user manual testing of the scenarios in Module 11 of the manual testing guide.
3. Once reviewed and authorized by Kenneth, commit changes on `kenneth` with Codex co-authorship, push to `origin/kenneth`, and open a Pull Request into `main`.
4. **Next Task Readiness**:
   * **T16** is complete locally on `kenneth` and verified; awaiting Kenneth's review and main integration.
   * **T17** (Return processing, damage assessment, maintenance workflow · Margareth with Kenneth) depends on T15 and T16. Once T15 (Margareth) and T16 are integrated into `main`, T17 will consume `open_maintenance` and `close_maintenance` for damaged returns.
   * **T13** (Administrator request review and approval queue · Margareth) is independently ready and not blocked by T16.
