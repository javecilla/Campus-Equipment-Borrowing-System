# T16 main integration and documentation review

- Date: October 19, 2026, Asia/Manila (UTC+08:00).
- Review/documentation: Jerome Avecilla with Codex assistance. Implementation: Kenneth T. Cortez with the AI assistance disclosed in his original handoff.
- Scope: verify merged T16 and update current documentation on `jerome`. Application source and historical handoffs are unchanged; no commit, push, PR or dependent implementation.
- Outcome: implementation integrated; **T16 In progress for review fixes**, despite the passing submitted suite. Browser results remain Not run.

## Integration evidence

[PR #31](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/31) merged at `26158298e27073572bf3e8b14dbb24502fa46678`, October 19, 2026, 13:35:04 Asia/Manila. Local `jerome`, `origin/main` and `git ls-remote origin refs/heads/main` match. Kenneth source `558286816806bf4f6c30f63998567924ea789cdd` and T12 merge `170cc38` are ancestors; `git diff-tree` finds no difference between the T16 source and merge trees. The working tree was clean before review. PR #30 at `ff84d74` already integrated the earlier T12 documentation publication.

Kenneth's [original snapshot](kenneth-t16-maintenance-and-inventory-reconciliation-10-19-2026.md) is preserved as historical evidence. Its uncommitted/not-integrated labels, absolute workstation links and comprehensive-verification claims are superseded by this review, not adopted as fresh evidence. There are no maintenance type fields, `completed_at`, `action_taken`, `resolution_outcome` or `serviced_by` in the implementation; actual fields are in [MaintenanceRecord](../inventory/models.py). The list orders by `-opened_at`, `-pk`.

## Review findings

1. **P1 — Return linkage bypasses unit eligibility and cross-record integrity.** [open_maintenance](../inventory/services.py) applies its status checks only when `source_return_id is None`; it never verifies that the linked return belongs to the selected unit or was Damaged. Two real PostgreSQL probes reproduced (a) an unrelated damaged return moving another Reserved unit to Maintenance and (b) acceptance of a Good return. `MaintenanceRecord.full_clean()` only checks the declared row/FK constraints; it does not enforce these cross-table relationships. This violates [SRS BR-09](../docs/SRS.md#business-rules-and-calculations), course A6's Reserved/Issued restriction and the [source-return contract](../docs/db_design.md#maintenancerecord). The public form does not accept this argument, so the observed bypass is at the service boundary intended for T17. Kenneth must make manual opening and damaged-return handling explicit, validate the matching damaged return and authoritative state under the established locks, and keep the complete return/allocation/maintenance/audit transition atomic. Do not let a non-null identifier serve as permission to bypass state checks.

2. **P2 — Closure reverses the shared lock order.** [close_maintenance](../inventory/services.py) locks MaintenanceRecord first at line 577, then EquipmentUnit at line 585. Both [architecture](../docs/architecture.md#transaction-boundaries-and-lock-order) and [shared lock helpers](../operations/locking.py) require unit before maintenance. A transaction already holding the unit and requesting its maintenance record can deadlock against this closure. This is a source-level finding; no deadlock was executed or claimed. Correct the order, re-read state while locked, and verify separate-connection competing operations before T17 relies on the interface. T17 also needs a consistent plan for the administrator lock when calling a service from a return transaction; do not acquire earlier locks after units.

3. **P2 — Workflow conflicts use success/form-error HTTP responses.** [maintenance_close](../inventory/views.py) returns 302 for an already-closed record, including POST. A changed unit state raises ValidationError and renders 200. Both were reproduced with Django's real request client. The [HTTP contract](../docs/api_spec.md#common-protocol) requires 409 for duplicate/changed-state actions. No partial closure occurred in the changed-state probe, but clients cannot distinguish conflict correctly. Use a specific workflow-conflict exception and map it to 409; retain 200 for invalid input forms. Review the opening conflict path for the same mapping.

4. **Verification and standards follow-up.** The 26 submitted tests use TestCase and cover selected manual service transitions, rejected states, audit creation, counts, basic access, list filters and successful forms. They contain no separate-connection concurrency scenario, explicit CSRF-enforcing client, page-boundary test or audit-failure rollback scenario; they do not exercise non-null `source_return_id`. The original snapshot's simulated-lock/comprehensive-coverage claims are unsupported by these tests. New defaults in the maintenance services, query and form constructor also violate the explicit-parameter rule; new `Any` mappings retain weak typing. Kenneth should address these with the smallest useful changes and real integration evidence. No dependency or broad test framework is needed.

## Actual verification

| Check executed in this review | Result |
| --- | --- |
| `manage.py test --noinput` | **217 PostgreSQL tests passed in 84.098s**, including 26 T16 tests; test database removed |
| Five additional isolated review probes | Completed in **0.742s** using separate database `test_campus_equipment_t16_review`, then removed. Four observed-defect probes confirmed unrelated-return/state bypass, non-damaged return acceptance, duplicate-close 302 and changed-state 200; the fifth verified create CSRF 403 and list POST 405. These assert observed behavior, not acceptance correctness; no project test files were added |
| `manage.py check --database default` | No issues |
| `manage.py makemigrations --check --dry-run --noinput` | No changes detected |
| `manage.py migrate --check` | Exit 0; no unapplied migrations |
| Ruff lint and format checks | Pass; **199 files already formatted** |
| `djlint templates --check` | Pass; **64 templates**, 0 updates; prior unit-detail formatting issue resolved by T16 |
| `python -m pip check` | No broken requirements |
| `npm.cmd run format:check`, `npm.cmd run build` | Pass; Tailwind and page scripts built |
| `npm.cmd audit` | 0 vulnerabilities |
| Read-only local PostgreSQL inventory/settings check | `transaction_read_only=on`; October 19, 13:39 Asia/Manila: 16 units, Available 13, Reserved 0, Issued 0, Maintenance 3, Retired 0; 3 open maintenance records, no loans, limits 7 days/3 units. Manual guide updated with current fictional assets and count deltas |

The first exploratory runner attempt stopped before database creation because its custom TEST mapping omitted Django's MIRROR setting. The corrected attempt changed only TEST.NAME and produced the five results above. No live operational data or private configuration was written. The checked suite does not establish audit-failure rollback or concurrency safety. Browser/mobile/keyboard, full return workflows, T14 competing approvals, performance and backup/restore were not run.

## Documentation and transfer

Updated [AGENTS.md](../AGENTS.md), [README.md](../README.md), [DEV.md](../DEV.md), [current handoff](../HANDOFF.md), [backlog](../docs/tasks.md), [architecture](../docs/architecture.md), [HTTP status/interface description](../docs/api_spec.md) and [manual Module 11](../docs/manual-test-guide.md#module-11--equipment-maintenance-and-inventory-reconciliation-t16). Required 409 semantics and integrity rules are preserved. PLAN sequencing is unchanged. Source requirement/member files and Kenneth's historical handoff remain unchanged.

Documentation verification: all **567 local links and 122 heading anchors across 9 changed/new Markdown files resolve**; code fences are balanced. Current T16 status, integration references, manual inputs/count deltas and prerequisite gates were checked against source and the read-only snapshot. `git diff --check` passes. The diff contains documentation only; source requirement/member files, application code, dependencies and Kenneth's original handoff are unchanged. No skill metadata changed, so no skill validator was run. Changes remain uncommitted.

Next owner/action: **Kenneth / T16** corrects and verifies the findings; Jerome reviews the resulting member-branch change before separately authorized integration. **Margareth / T13** has accepted integrated prerequisites and remains ready. **T17 / Margareth with Kenneth** still needs T15 and accepted T16 fixes; the current service must not be consumed as a verified damaged-return implementation. The user records actual T12/T16 browser outcomes when run. No new publication or implementation starts automatically.
