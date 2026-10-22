# August-October 2026 transaction history

- Date: October 22, 2026, Asia/Manila.
- Owner: Jerome Avecilla with Codex implementation/verification assistance; earlier team contributions remain intact.
- Scope: user-authorized realistic fictional history from August through October 22, concentrated in October and linked to the existing equipment. No commit, push, PR/main merge, teammate message, diagram work or actual user acceptance session.

## Outcome and interfaces

**T21 is Done locally on `jerome`, uncommitted and Not integrated into main**, over main `4f285cb`. The accepted/integrated T17 prerequisite remains unchanged. The complete course demonstration minimum is now met using the existing 1 admin / 8 users / 12 categories / 29 items / 46 units and 23 uploaded catalog photos.

[`seed_demo_transactions(today)`](../operations/demo_transactions.py) and the [CLI command](../operations/management/commands/seed_demo_transactions.py) import the [fixed typed scenario plan](../operations/demo_transaction_plan.py) atomically into an empty borrowing history. The separate account seed remains account-only. Missing/ambiguous equipment names, invalid account roles, insufficient stock, date/acquisition/maintenance conflicts and database failures produce errors rather than substitutes or partial writes. Repeat execution rejects existing history without changing records. No schema, dependency, frontend, HTTP or ordinary workflow contract was added or changed.

The importer resolves the existing manually entered equipment by name, calls the actual request/approval/issue/cancellation/return/repair services, then dates only its new transaction and audit records. All states and stock changes come from those services. The controlled historical import validates acquisition dates, nonoverlapping reservations, maintenance windows and event sequencing before commit; it never patches the server clock or disables constraints. Existing equipment/account entry timestamps retain their real database registration/import times, which can be later than historical events. New actual-event dates end October 22; current loan due dates extend through October 26, inside the requested October scope.

| Result as of October 22 | Count |
| --- | --- |
| Requests | 30: August 3, September 4, October 23 |
| Issued loans | 20: August 3, September 4, October 13 |
| Loan units / returned / outstanding | 34 / 28 / 6 |
| Fully returned / partially returned / still-issued loans | 16 / 1 / 3 |
| Other requests | 2 Approved, 2 Rejected, 3 Cancelled, 3 Pending |
| Dashboard Available / Pending / active / overdue | 30 / 3 / 4 / 2 |
| Inventory | 30 Available, 3 Reserved, 6 Issued, 5 Maintenance, 2 Retired |
| Maintenance | 9 original records unchanged; 1 new damaged-return repair closed |

All eight borrowers have meaningful history. Purposes cover orientations, class reports, photography, capstone work, electronics and network laboratories. Return/decision/repair notes describe those fictional scenarios. Two Approved cancellations retain ended reservations; the current queue includes equipment awaiting review/collection. October accounts for 23/30 requests and 13/20 loans. Category charts derive from the existing real catalog categories, without generic sample inventory substitutions.

## Verification and local execution

- Final complete PostgreSQL suite: **332 tests passed in 86.104s**, including five [historical-import tests](../operations/tests/test_demo_transactions.py). The earlier focused run passed four tests in 13.785s before adding the missing/ambiguous equipment test; the final suite includes all five. Tests verify monthly/report totals, all request states, original account/catalog/audit preservation, constraints, linked damaged-return repair, real HTTP dashboard/reports/CSV, borrower owner/foreign-loan boundaries, repeat rejection, acquisition conflicts and complete rollback after a real PostgreSQL issue-audit constraint failure.
- Executed the command locally after saving a fresh private custom-format PostgreSQL backup at ignored `output/private-backups/before-aug-oct-history-20261022-091821.dump`. `pg_restore --list` inspected its archive directory; no restore is claimed. The import/preservation wrapper used one transaction and checked its assertions before commit.
- Compared original accounts, Profiles, categories, catalog items, settings, all nine previous maintenance rows and old audits field-for-field: unchanged. All 46 prior units retain their identities, asset codes, acquisition dates and notes; only authorized workflow status/condition/update metadata can change. All 23 photo paths and SHA-256 file hashes match. Every new RequestItem refers to the existing photographed catalog, with no new accounts/items/units created.
- Local repeat-import rejection preserved every record across all 14 domain models. Read-only ORM reports verify exact totals above. The inclusive October 1-22 report returns **13 loans / 23 issued units / 17 returned / 6 outstanding**. The monthly chart contains only August, September and October 2026.
- Django database/schema/applied-migration checks, full Ruff lint, owned-file formatting and `pip check` pass. npm formatting/build, nine contrast checks and npm audit pass, with zero vulnerabilities. Full formatting retains the same three unrelated findings in the archived borrower-portal handoff Python example, portal-equipment test line endings and portal-equipment template attribute wrapping. Those files were preserved.
- [DEV setup/snapshot](../DEV.md#seed-august-october-2026-transactions), [Module 20](../docs/manual-test-guide.md#module-20--fictional-demonstration-dataset-t21), README, task/evidence, HANDOFF and AGENTS now reflect the populated history. Previous account-only/empty-data snapshots remain historical. Documentation verification passed: 820 relative targets, 207 heading anchors and paired fences across seven documents, plus diff whitespace checks.

## Current examples and next action

Module 20 records workstation-specific IDs and dates: Miguel's partial overdue loan 27, Sofia's overdue laptop loan 28, Gabriel's current speaker loan 29, Isabella's October 22 network-kit loan 30 and repaired multimeter maintenance 10. Loan 11 provides a completed August example. Recheck those IDs/eligibility on another database or after manual changes; usernames/password sources remain in the DEV table. No credentials are copied into this handoff.

Review the populated dashboard/history and the uncommitted source/documentation. **T22/T23 remain Not started and await authorized T21 main integration and their own actual execution.** No new browser/mobile/keyboard, spreadsheet-application, screen-reader, performance, restore, clean-machine or teammate/user acceptance result is claimed. Course evidence must not treat these fictional records as actual campus events or technician work. Publication and diagram work retain their separate authorization gates.
