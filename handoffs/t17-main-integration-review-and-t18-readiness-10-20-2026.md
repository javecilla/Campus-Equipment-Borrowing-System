# T17 main integration review and T18 readiness

- **Work / owner:** Jerome with Codex review/documentation assistance; Ralph Andre F. Giga retains T17/UI-10 implementation credit. Earlier member contributions and historical handoffs are preserved.
- **Date:** October 20, 2026, Asia/Manila (UTC+08:00).
- **Outcome:** T17 is accepted and integrated. No blocking runtime defect found in the reviewed return workflow. Alex / T18's T15/T17 prerequisites are satisfied; T18 remains Not started until requested. This session changes documentation only, with no commit, push, PR, merge, teammate message or live business-data write.

## Integration and reviewed scope

Fetched `origin/main` and local `jerome` HEAD are `55899d0f18e5f0ec76dc3374db1765f32b49893e`. PR #43 merged October 20 at 18:18:48 Asia/Manila; its parents are T15 integration `744bc3995f310fe365d7e00d8b187d765df326a8` and Ralph's source `bd62ed7b93db965ed5b4442af84e8186ccf45065`. The source and merge trees match exactly. T15 source `74924dd` and T16 corrections `d68d7f7` remain ancestors. No integration action was performed in this review.

Reviewed the T17 service/formset/view, loan progress query and administrator/borrower templates against SRS BR-07 through BR-11, BR-13 and BR-14, the database/HTTP contracts and canonical lock order. The implementation covers whole-selection rollback, loan membership and duplicate/state checks, active administrator authorization, server timestamps, partial/final closure, damaged-return maintenance linkage/audit, derived overdue values and borrower privacy. Separate PostgreSQL connections test overlapping duplicate and disjoint returns. UI-10 request-row navigation/alignment accompanies the same published source; its original browser evidence remains in Ralph's snapshots.

Actual interfaces remain canonical in [DEV's consumer handoff](../DEV.md#t17-readiness-and-consumer-handoff), [return service](../borrowing/return_services.py), [formset](../borrowing/return_forms.py), [view](../borrowing/return_views.py), [queries](../borrowing/queries.py) and [HTTP contract](../docs/api_spec.md#custom-administration-requests-loans-and-maintenance). No schema/dependency/application change was needed for this review.

## Documentation findings and corrections

Current-state files still described T17 and UI-10 as local/uncommitted/not integrated after PR #43. DEV also described `borrowing_manage:return-create` as planned and not mounted although the route exists. These records now identify the real source/merge revision, keep Ralph's authorship and distinguish original browser evidence from fresh review checks. The API description now matches the manual guide's stale-form behavior: valid-sized stale selections produce 409; forms exceeding the new outstanding-row maximum produce bound 200 errors with no writes.

Updated [AGENTS](../AGENTS.md), [README](../README.md), [DEV](../DEV.md#t18-readiness-and-consumer-handoff), [current handoff](../HANDOFF.md), [task evidence](../docs/tasks.md#verified-task-evidence), SRS, architecture, database/HTTP contracts, folder/coding guides and [manual Module 16](../docs/manual-test-guide.md#module-16--per-unit-returns-and-overdue-t17). No original requirement/member record or completed handoff was changed. T27/T28 remain In progress; their included source records do not prove completion of outstanding institutional/team evidence.

## Fresh verification

| Check | Actual result |
| --- | --- |
| `python manage.py test --noinput --verbosity 1` | **294 PostgreSQL tests passed in 107.414s**, including 21 T17 tests, return/maintenance audit rollback and both overlapping-return races. Test database removed by the runner. |
| `npm.cmd run build` | Passed; all nine theme text-role pairs meet 4.5:1. |
| `npm.cmd run format:check` | Passed. |
| `ruff check .` | Passed. |
| `ruff format --check .` | Existing findings in three untouched files: mixed-EOL `accounts/views.py`, mixed-EOL `inventory/tests/test_portal_equipment.py`, and the Python code block in archived `handoffs/borrower-portal-ui-improvements-10-20-2026.md`. |
| `djlint templates --check` | Existing formatting finding in untouched `templates/inventory/portal/equipment_list.html`, among 77 templates. |
| Changed T17 Python/templates | Eight Python files pass Ruff formatting; six changed templates pass djLint formatting. |
| Django database check | Passed, no issues. |
| Migration drift / applied migration checks | Passed; no changes detected or unapplied migrations. |
| `python -m pip check` | Passed, no broken requirements. |
| Development database inspection | Explicit read-only transaction at **18:23 Asia/Manila**: 1 loan, 1 outstanding LoanUnit, 0 returns, 0 return-linked maintenance records; limits 7 days / 3 units per item. No identities or private fields published; no business writes. |

Documentation validation passed **879 local links/anchors across 20 documents**, balanced code fences, all 31 canonical task rows unchanged, source ancestry, source/merge tree equality and diff whitespace. No application file changed. Formatting findings remain outside this review's scope and do not demonstrate a T17 workflow failure.

**Earlier evidence, not rerun:** Ralph's 21-test focused run and Chrome 155 partial/damaged/final return, labels, keyboard, cancellation, owner privacy and 1440/390/320px checks remain in the [implementation snapshot](ralph-t17-per-unit-returns-and-overdue-10-20-2026.md). This review ran the full automated suite, not a new browser flow. npm audit, Firefox/Safari, full screen-reader testing, live return execution, full T16 browser lifecycle, user acceptance, performance and backup/restore were not run here. Existing broader manual/standards follow-ups remain open.

## Next consumer

Alex works on `alex` after an explicit T18 implementation request, syncing main and verifying source ancestry first. The [T18 consumer handoff](../DEV.md#t18-readiness-and-consumer-handoff) links the live-card/chart requirements, actual query interface, existing protected placeholder and verification expectations. T18's counts must respond to committed transactions; category-issued totals must include returned units without multiplying loan counts.

Jerome / T21 also has its integrated T17 prerequisite but remains Not started. Alex / T19 still needs accepted integrated T18; Ralph / T20 still needs accepted integrated T18/T19. Kenneth, Margareth and Ellyssa can continue validation/documentation/manual testing. Diagram conversion stays on standby until system completion and Jerome's explicit go signal, subject to T25's prerequisites. No notification was sent and no next feature was started.
