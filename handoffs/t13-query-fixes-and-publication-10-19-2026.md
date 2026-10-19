# T13 query fixes and publication

Date: October 19, 2026, Asia/Manila.

Owner: Jerome Avecilla with Codex; Margareth Raine H. Ignacio's T13 implementation and Kenneth's integrated T16 work are preserved.

## Outcome and authorized scope

The user requested a final documentation sweep and commit/push on `jerome` with `Co-authored-by: Codex <codex@openai.com>`, then explicitly requested the two T13 functional fixes before publication. This snapshot accompanies the resulting code/test/documentation commit on `jerome`. Its publication target is `origin/jerome`; verify the commit and remote ref after pushing. No new PR, main merge or T14 implementation is included.

**Both functional defects are fixed; T13 is Done on corrected `jerome`, awaiting main integration of these corrections.** Main remains PR #34 baseline `23c1ad9`, containing Margareth's source `c5cfe37` and T16 fixes `d68d7f7` through PR #33 at `aa36c86`. Fresh fetch/remote-ref inspection confirmed that baseline before publication. The historical [integration review](t13-main-integration-and-documentation-review-10-19-2026.md) preserves the original defects and earlier test results.

## Changes and verification

- [borrowing/queries.py](../borrowing/queries.py): use `isdecimal()` before converting an ID, preserving Unicode username matching without attempting `int('²')`. Administrator Reserved units now includes only allocations with neither `ended_at` nor `released_at`; historical allocation rows remain stored.
- [borrowing/tests/test_requests.py](../borrowing/tests/test_requests.py): add two real HTTP/database integration regressions. One verifies `²` username search and Arabic-Indic decimal request IDs. The other executes administrator approval POST, borrower cancellation POST and administrator detail GET, checking restored availability, an empty reservation display, preserved ended allocation and the cancellation audit. Both tests failed on the original implementation (one exception, one assertion failure) before the query fix and pass afterward.
- [Manual guide Module 12](../docs/manual-test-guide.md#module-12--administrator-request-review-and-decisions-t13): refresh Unicode and cancellation cases to the corrected behavior and distinguish local corrections from unchanged main. Browser results remain Not run. Module 11's last stale PR #31 closure-status statement now records PR #33's integrated 409 behavior.
- Current README/DEV/AGENTS, requirements/HTTP/architecture status paragraphs, folder guide, backlog and HANDOFF now agree. The final sweep also corrected obsolete prompt/Axios integration claims, earlier suite counts presented as current, stale T11 handover text and the folder guide's font stylesheet instructions. Git ancestry verified prompt integration `805e114` and Axios removal `b129a3f`. Access/protection observations remain explicitly historical rather than newly verified claims.

No migration, dependency, workflow service or persistent schema change was needed. No live application data was created or modified. The manual-guide preparation still uses the read-only October 19, 22:31 snapshot from the original review: limits 7 days / 3 per item, 3 Pending requests, no loans, projector availability 1 and HDMI switch availability 0. Recheck those dated records before manual testing. Original requirement/member sources and all completed historical handoffs are preserved.

| Check | Actual result |
| --- | --- |
| Two new regressions before the fix | Reproduced `ValueError` and ended allocation incorrectly present in Reserved units |
| Focused `borrowing.tests.test_requests` | **28 PostgreSQL tests passed in 0.809s** |
| Full `manage.py test --noinput` | **252 PostgreSQL tests passed in 42.541s**; separate test database destroyed |
| Ruff lint / format | Passed; 207 files already formatted after formatting the new test and manual-guide Python example |
| djLint | Passed; 67 templates, zero changes required |
| Django database check / migration drift / migration application check | Passed; no issues, no model changes, no unapplied migration |
| `python -m pip check` | Passed; no broken requirements |
| npm format / build / audit | Passed; CSS/JS rebuilt, zero vulnerabilities |
| Current-documentation audit | Relative paths/anchors and fenced examples checked across current root/docs Markdown plus both new handoffs; whitespace and publication scope checked before commit |
| Historical/source preservation | Existing handoffs and source requirement/member files unchanged |

The earlier 250-test review and five temporary probes are historical, not additional tests in the 252-test suite. Only documentation changed after the successful code checks; behavior tests were not repeated without a code change.

## Remaining work and next action

Review and separately authorize main integration of this corrected T13. T14 / Jerome with Margareth may then demonstrate competing last-unit approvals on separate PostgreSQL connections. T15 remains gated on accepted/integrated T13 and T14; T17 still needs T15 with T16 already integrated. No downstream task is marked complete by these fixes.

The original review's smaller default-parameter, loose-type and decision-helper conventions remain non-blocking follow-ups for Margareth; this change fixes the two requested runtime defects without expanding into that refactor. Browser/mobile/keyboard outcomes, queue multi-page traversal, T14 concurrency, cancellation/issue races and later workflows remain unrun or unimplemented according to the backlog.
