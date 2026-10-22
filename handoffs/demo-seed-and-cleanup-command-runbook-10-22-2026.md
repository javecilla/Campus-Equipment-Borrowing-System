# Demo seed and cleanup command runbook

- Date: October 22, 2026, Asia/Manila.
- Owner: Jerome Avecilla with Codex implementation/verification assistance; existing team contributions preserved.
- Scope: runnable developer instructions for preparing and clearing a local professor demonstration. Current populated data retained; no commit, push, PR/main integration, teammate message or unrelated feature work.

## Outcome and interfaces

**T21 remains Done locally on `jerome`, uncommitted and Not integrated**, over integrated main `4f285cb`. T17 remains an accepted integrated prerequisite. [DEV.md](../DEV.md#demo-command-runbook) owns the commands, private environment password source, execution order, preservation scopes, backup guidance and full database recreation. The existing nine-account roster and fixed August-October 2026 transaction seed remain independent.

- [`seed_demo_units`](../operations/management/commands/seed_demo_units.py) takes explicit administrator username, minimum total quantity per active catalog item and acquisition date. Its [service](../operations/demo_units.py) registers missing Good/Available stock through the existing audited workflow, excludes archived items/categories, preserves all existing units/catalog/photos and rolls back failures. Repeats at the same quantity add no stock. Retired/maintenance units count toward the total; historical serviceable-stock/date prerequisites still apply.
- [`clear_borrowing_data`](../operations/management/commands/clear_borrowing_data.py) removes all borrowing records and borrowing-target audits, detaches retained maintenance from deleted returns, and makes Reserved/Issued stock Available. Other stock states, maintenance, catalog/photos, accounts/Profiles/sessions and settings remain.
- [`clear_equipment_units`](../operations/management/commands/clear_equipment_units.py) requires empty borrowing history, then removes all physical units/maintenance and their target audits. Catalog/photo references, accounts and settings remain. Both [purge functions](../operations/demo_cleanup.py) are atomic, trusted local data-reset tools with no prompts; DEV requires checking the target and stopping database writers first. These are explicit purges, not ordinary application state transitions.

Full empty-data setup uses the existing PostgreSQL drop/recreate procedure and migrations, restoring required settings/framework rows. Uploaded files are not deleted; deleted catalog references cannot be recreated by account/unit seeds. The runbook explains manual catalog preparation or a private database/media restore. It does not claim to distribute the workstation's manually entered catalog/photos or to reproduce the exact old asset identities after a stock purge.

No model, migration, HTTP, frontend or dependency changes. [Module 20](../docs/manual-test-guide.md#t21-05-seed-and-cleanup-command-rehearsal) covers command rehearsal and expected inspection outcomes. Original history import evidence remains in its [completed handoff](august-october-2026-transaction-history-10-22-2026.md).

## Verification

- **336 PostgreSQL tests passed in 101.342s.** The focused stock/history suite passed nine tests in 26.738s before final verification. Four added checks cover top-up/repeat/archive/preservation behavior, role/input/collision rejection with rollback, actual history-to-empty-to-stock-to-history reconstruction, and real PostgreSQL trigger failure rolling back a purge. A retained open maintenance record and retired stock remain unavailable after transaction cleanup. Existing history tests still verify reports/access/dates and import rollback.
- Django database checks, migration drift/applied checks, full Ruff lint, formatting of all seven owned Python files, `pip check`, npm source formatting, build, all nine contrast pairs and npm audit pass; audit reports zero vulnerabilities. Full Ruff formatting retains the two pre-existing findings in the archived borrower-portal handoff example and portal-equipment test line endings. djLint retains the existing portal-equipment template attribute-wrapping finding. These unrelated files were not changed.
- Documentation links/anchors, paired fences and diff whitespace were checked after final edits. Full database recreation, pgAdmin backup/restore, browser/mobile/keyboard and professor/user acceptance were **Not run** for this task. T24 backup/restore work remains separate.
- Only the separate PostgreSQL test database received cleanup/reseed writes. Read-only local checks retained nine users, 12 categories, 29 catalog items, 46 physical units, ten maintenance records, 30 requests, 20 loans and 28 returns, including 23 catalog photo references. The existing portal-equipment test left one synthetic WebP in local media; it was confirmed unreferenced and the sole file difference, then removed. Final SHA-256 digests across all domain rows and all original stored WebP files match their pre-verification values.

## Next action

Jerome can use the DEV command table to choose a future demonstration/reset scope. The current populated demonstration is ready for review without rerunning seeds or purges. Changes remain uncommitted for review. T22/T23 still require T21 publication/main integration and actual acceptance execution; this tooling does not complete them or T24.
