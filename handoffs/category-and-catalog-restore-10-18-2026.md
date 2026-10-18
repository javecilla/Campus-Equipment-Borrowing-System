# Category and catalog item restoration

- Date/time zone: October 18, 2026, 14:42 Asia/Manila (UTC+08:00).
- Work/owner: T07 optional enhancement, explicitly requested by the user; Jerome Avecilla with Codex assistance continuing Kenneth Cortez's catalog work.
- Branch/base: `jerome`, HEAD/local `origin/main` `20c4452`, Kenneth baseline PR #19. T03 `d122518` and T04 `cb96319` are recorded integrated prerequisites. This enhancement and preceding T07 follow-ups remain **uncommitted / Not integrated**. No commit, push, PR, merge, or remote refresh performed.

## Current outcome

Archived category and catalog item detail pages expose **Restore category** or **Restore item**. Find archived records using the list's Status filter and open View. A GET confirmation explains the effects; a CSRF-protected POST restores the record and redirects to its detail page. Active ADMIN is enforced by both the view and the locked service. A repeated restoration returns 409 without another audit entry.

- [Distinct restore services](../inventory/services.py) clear only the selected master record's archive flag. Category restoration keeps individually archived children archived. Item restoration under an archived category is allowed, with a confirmation warning; active-category eligibility still blocks new requests/approvals. Physical-unit statuses, including RETIRED, photos and transaction references remain unchanged.
- The existing actor/category/item lock order is reused. Each restore and its audit entry commit or roll back together. [Audit actions](../operations/models.py) `CATEGORY_RESTORED` and `ITEM_RESTORED` have matching [target validation](../operations/audit.py) and appear in the existing audit filters.
- [Migration operations.0003](../operations/migrations/0003_catalog_restore_audit_actions.py) expands the audit action field/constraint, preserving existing records; applied successfully to the local development database. Teammates must run `manage.py migrate --noinput` after integrating this batch.
- [Restore views](../inventory/restore_views.py), allowlisted empty confirmation [forms](../inventory/forms.py), and [named routes](../inventory/manage_urls.py) implement `/manage/categories/<id>/restore/` (`category-restore`) and `/manage/items/<id>/restore/` (`item-restore`).
- [Category](../templates/inventory/manage/category_restore.html) and [item](../templates/inventory/manage/item_restore.html) confirmations use the shared management shell, visible accent buttons, stable test IDs and cancel links. Existing detail pages show Restore only for individually archived records.
- [HTTP contract](../docs/api_spec.md#custom-administration-accounts-and-inventory), [SRS BR-13](../docs/SRS.md#business-rules-and-calculations) and [audit design](../docs/db_design.md#auditlog) describe this optional enhancement. The original course brief and member assignments are unchanged. This is restoration of catalog master records; it does not reopen terminal requests or reactivate retired physical units.

## Actual verification

| Check | Result |
| --- | --- |
| Full PostgreSQL suite | **110 tests passed** in 22.698s, including 41 inventory tests. No SQLite substitution |
| Restore integration | Six [new integration tests](../inventory/tests/test_catalog_restore.py) pass: real issued-loan/reference preservation, independent category/item flags, photo path and unit statuses, server-derived actor/ignored submitted fields, anonymous/basic/inactive access, service recheck, CSRF, wrong methods, missing targets, repeat conflicts, and audit failure rollback through a real database constraint |
| Final test refinement | The same six tests passed again after adding a valid CSRF-enforced restoration and filtering actual new audit actions; no application changes after the full run |
| Build/dependencies | npm build and format check passed; npm audit reports zero vulnerabilities; pip check passed. No dependency added |
| Python/templates | Final Ruff lint/format checks passed (160 files); all 48 templates passed djLint. Modified test file formatting passed again after final refinements |
| Django/schema | Database check passed; no migration drift or unapplied migrations; local operations.0003 applied successfully |
| Chrome localhost:8000 | Archived category 7 and item 19 expose Restore; both confirmation pages inspected visually. Confirm button is green with white text; category Tab order reaches Back to category, cancel returns to the still-archived detail; no console warnings/errors. No live catalog mutation submitted |
| Documentation/Git | 326 local links in changed canonical documents/current handoff/new snapshot resolved; code fences balanced and Git whitespace checked before transfer; no Git publication |

Initial new-test failures concerned deferred PostgreSQL trigger checks during test-only constraint creation and the existing middleware logging inactive sessions out. Tests now flush deferred checks before test DDL and authenticate separately for each inactive request. Final checks pass without changing the authentication or database error behavior.

## Transfer and remaining scope

Review the full uncommitted T07 batch before separately authorized publication/integration. Kenneth / T08 remains Not started and should consume the integrated corrected forms, lock helpers and migrations. T10/T11 retain their T08/T09 prerequisites. No unit, borrower-request, approval, issue or return workflow was implemented by this enhancement.

Restore POST behavior is verified through real Django/PostgreSQL integration; live Chrome review deliberately exercised GET/cancel only to preserve the user's catalog state. The previous photo-selection browser coverage limitation remains documented in the [layout/preview handoff](catalog-layout-preview-and-asset-refresh-10-18-2026.md); it is unrelated to restoration. No CI, T14 competing approvals, performance or backup/recovery evidence is claimed.
