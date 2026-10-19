# T16 maintenance integrity and conflict fixes

- Date: October 19, 2026, Asia/Manila (UTC+08:00).
- Owner: Jerome Avecilla with Codex assistance, continuing Kenneth T. Cortez's T16 baseline with the user's explicit repair authorization.
- Outcome: **T16 corrections Done locally on `jerome`, uncommitted and not integrated into main.** No new commit, push, PR, main merge or T17 implementation.
- Baseline: local HEAD `42f8b21` is the published documentation commit above PR #31 merge `2615829`, preserving Kenneth source `5582868`. Final remote inspection verified PR #32 documentation merge `614cd1fe5b224688c558e367b044df9f0358f0b7` on main, preserving `42f8b21`; application/dependency/template source is unchanged from `2615829`. The branch was not switched or merged during this repair. The preceding [review](t16-main-integration-and-documentation-review-10-19-2026.md) and [publication snapshot](t16-documentation-publication-10-19-2026.md) remain historical evidence.

## Implemented correction

- [Maintenance services](../inventory/services.py): `open_maintenance` is explicitly manual-only. The unused `source_return_id` argument and its status-check bypass are removed; every opening requires an Available unit and stores no source return. No application caller supplied a non-null return identifier. Future T17 must create matching damaged-return maintenance within the complete return/allocation/audit transaction, rather than invoking this manual action. This repair does not implement or claim that return workflow.
- Closure first reads the unit identifier, locks the unit, then locks/re-reads its maintenance record and validates current state. The actor is locked/rechecked before these domain rows. Reassociated or changed records fail explicitly without partial changes.
- `MaintenanceConflict` distinguishes workflow conflicts from invalid inputs. [Views](../inventory/views.py) return 409 for authoritative service conflicts and closed-record GET/POST; invalid submitted forms retain 200 and successful actions retain 302. A closed-record [page](../templates/inventory/manage/maintenance_close.html) displays its conflict without a submit form.
- [Forms](../inventory/forms.py) and [queries](../inventory/queries.py): touched T16 interfaces use explicit parameters; the maintenance constructor uses a concrete initial unit ID, and repaired-condition cleaning returns its value rather than overriding a loose mapping. Existing UI repair/retirement behavior is preserved.

These changes resolve the three blocking findings and the touched T16 defaults/mapping follow-up. T12's separate test-helper standards finding is unchanged. Browser and pagination-boundary evidence remain pending.

## Verification actually executed

| Check | Actual result |
| --- | --- |
| Focused maintenance suite before the final CSRF case | 32 PostgreSQL tests passed in 7.702s |
| Full `manage.py test --noinput` after all code/test changes | **224 PostgreSQL tests passed in 37.343s**, including all 33 maintenance tests; separate test database destroyed |
| [Seven new integrity checks](../inventory/tests/test_maintenance_integrity.py) | Removed return-link argument cannot change an Issued unit; real PostgreSQL audit rejection rolls back both opening and repair/closure; changed-state closure is 409 with no writes; real CSRF and protected fields are enforced; different administrators competing to open produce one record/audit and one conflict; a separate closure waits for the unit while the maintenance row remains lockable |
| [Updated existing tests](../inventory/tests/test_maintenance.py) | Invalid workflow states raise the specific conflict; closed-record GET and POST return 409 without another audit or submit control; manual lifecycle and count checks pass |
| `manage.py check --database default` | No issues |
| `manage.py makemigrations --check --dry-run --noinput` | No changes detected |
| `manage.py migrate --check` | Exit 0, no unapplied migrations |
| Ruff lint and format check | Pass; 202 files already formatted |
| `djlint templates --check` | Pass; all 64 templates, 0 updates |
| `python -m pip check` | No broken requirements |
| npm format check, asset build and audit | Pass; Tailwind/page scripts built, 0 vulnerabilities |
| Read-only local inventory/settings check | October 19, 14:13 Asia/Manila; `transaction_read_only=on`. Available 12, Maintenance 4, Total 16; no Reserved/Issued/Retired units or loans. Four open records. Projector 001 is Good/Maintenance with record 4; projector 002 is Fair/Available. Settings 7 days/3 units |

Tests use real PostgreSQL and Django request clients, with no mocked audit writer or locking. The test-only audit constraints are rolled back with the test transactions. The concurrency checks do not establish the future T14 approval race, complete T17 returns or universal deadlock freedom. No live inventory was changed by this repair. Browser, keyboard, mobile, pagination boundaries, performance and backup/restore were not run.

## Documentation and next action

The [manual guide](../docs/manual-test-guide.md#module-11--equipment-maintenance-and-inventory-reconciliation-t16) now describes corrected 409 responses and uses the fresh projector-002 example with matching count deltas. Its baseline was inspected read-only; expected outcomes are not browser passes. Current status, contracts and entry points distinguish local completion from main integration. PLAN sequencing and original requirements/member sources are unchanged; prior completed handoffs are preserved.

Final documentation verification passed: **588 relative links and 125 heading anchors across 11 changed/new Markdown files**, balanced code fences, current status/manual-input consistency and `git diff --check`. Original requirement/member sources, historical completed handoffs and dependency files are unchanged. No migration or dependency was added.

Next: review the local diff and separately authorize publication/integration. Kenneth remains the original T16 owner; Jerome's continuation is explicitly credited. Margareth / T13 remains independently ready. T17 remains Not started until T15 and the corrected T16 implementation are accepted and integrated into main, and owns the complete damaged-return transaction. The user records actual T12/T16 browser outcomes when available.
