# T22 automated system acceptance

- Date: October 22, 2026, Asia/Manila.
- Owner: Jerome Avecilla with Codex verification assistance. Alex's security-coordination and the team's existing implementation/testing credit are preserved; no other member's participation in this run is claimed.
- Scope: user-authorized T22 acceptance checks and repeatable commands in DEV.md. No new product workflow, schema, dependency, commit/push, PR, main merge, participant session or live-data reset.

## Outcome and integrated prerequisites

**T22 is Done locally, uncommitted on `jerome` over `b828945` and Not integrated.** All eleven [SRS minimum acceptance scenarios](../docs/SRS.md#minimum-acceptance-scenarios) were exercised through the full real PostgreSQL test suite. [Module 21](../docs/manual-test-guide.md#module-21--automated-system-acceptance-t22) maps each scenario to its executed tests and separates automation from unrun browser/participant/operational work. No blocking product-runtime defect was found in those automated scenarios.

Fresh fetch found user-merged **PR #53**, main **`b82894549c7e50a37e91cfa2a6f22d9599e446c2`**, merged October 22 at **09:50:53 Asia/Manila**. Source `e3402bf` and publication `ae6b147` are ancestors, and `git diff --exit-code ae6b147 origin/main` confirmed exact published-tree equality. Local `jerome` was clean and fast-forwarded to that merge before work. T14 `058357c`, T19 `16e1d4c`, T20 `b43fb99` and T21 `e3402bf` are accepted ancestors of fetched main, satisfying the T22 entry gate. T21 is now **Done and integrated**, preserving source credit and prior historical snapshots.

## Delivered checks and commands

[DEV.md](../DEV.md#t22-automated-system-acceptance) documents the full acceptance command, prerequisites, success/failure interpretation, focused T22 rerun, eight concurrency checks, private PowerShell output capture and test-database isolation. It uses native Django commands without a new runner, dependency or application endpoint.

[`SystemAcceptanceTests`](../operations/tests/test_system_acceptance.py) adds three real integration checks:

- CSRF-enforced three-item HTTP submission/approval/date revision/issue/slip/partial return/damaged final return/repair, with forged-field and repeat-action checks, live dashboard and filtered HTML/CSV agreement after changes. CSV totals and formula protection are checked independently of detail rows.
- Basic-user GET/POST denial across all **45 current management routes**, plus inactive existing-session invalidation and unchanged operational records. Unsupported methods can return 405 before role checks; supported unauthorized requests return 403.
- Foreign request/cancel/loan IDs return 404, and administrator POSTs without CSRF are rejected across all management paths without workflow writes.

The existing suites supply credential/registration checks, settings/archive/filter cases, audit-failure rollback, before/on/after due-date behavior, retirement/count reconciliation and all eight real separate-connection concurrency scenarios. Those tests were executed, rather than inferred from their source.

## Failures resolved

The existing [portal photo test](../inventory/tests/test_portal_equipment.py) wrote its fixture into development media and left a streaming response unconsumed. It now enters temporary class-level media storage **before** fixture creation and consumes/validates the streamed bytes, allowing Django's test client to close the file. The initial isolation rehearsal exposed Windows file-lock cleanup failure; a trial explicit second response close disturbed the test transaction, so the final fix uses the installed Django client's documented iterator lifecycle. The final targeted and full runs pass without suppressing cleanup errors or changing product behavior. Formatting this owned test also resolves its previously recorded mixed-line-ending finding.

An initial new CSV assertion counted the existing totals row as a loan; the test was corrected to compare detail rows and totals independently. This was a test expectation error, not a report defect.

## Actual verification

| Command / check | Result |
| --- | --- |
| `manage.py test --noinput` | **339 tests passed in 96.345s** on PostgreSQL 17.5; includes all SRS acceptance coverage and all eight concurrency cases |
| `manage.py test operations.tests.test_system_acceptance --noinput --verbosity 2` | **3 passed in 1.470s**, exact documented focused command |
| Documented four-module concurrency command | **8 passed in 3.319s**; approval, release/cancel, return and maintenance locking |
| Final focused lifecycle plus photo class rehearsal | **6 passed in 1.560s** |
| Django database checks, migration drift/applied checks, full Ruff lint, changed-Python formatting | Pass; no schema changes |
| npm source format/build, nine contrast pairs, npm audit, `pip check` | Pass; zero npm vulnerabilities |
| Full Ruff / djLint formatting | Two unrelated existing findings remain: archived borrower-portal handoff Python example and portal-equipment template attribute wrapping; neither file changed |
| Development preservation | SHA-256 comparison across every domain row and every existing media path/file matched before/after final runs; 9 users, 12 categories, 29 items, 46 units, 10 maintenance records, 30 requests, 20 loans and 28 returns retained, including 23 catalog photo references |

Documentation links/anchors, paired fences, command paths and diff whitespace were checked after final updates. No real browser/keyboard/mobile/screen-reader/spreadsheet or participant session ran in this task. These HTTP tests do not constitute T23 feedback sessions. Performance measurements and backup/restore remain T24 work; instructor policy/course evidence remains under its existing tasks.

## Next action

Jerome reviews the uncommitted T22 changes; publication/main integration requires a separate request. T23 has its integrated T20/T21 prerequisites and can begin when actual participant sessions are arranged. T24 awaits T22 main integration and its own execution authorization. Preserve the populated local demonstration; rerunning automated acceptance needs no development seed/cleanup.
