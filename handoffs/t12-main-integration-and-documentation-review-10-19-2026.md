# T12 Main Integration and Documentation Review

- **Owner:** Jerome Avecilla with Codex review/documentation assistance; T12 implementation remains Ralph Andre F. Giga's work.
- **Date:** October 19, 2026, Asia/Manila.
- **Scope:** Review integrated T12 and synchronize documentation while the user performs manual testing. No application implementation or publication is included.
- **Branch:** `jerome`; reviewed HEAD `170cc38be1b5caa174f15d3878c551d79bbaa279`.

## Outcome and integration evidence

T12 is **Done and integrated**, rather than uncommitted on Ralph's branch. Local `origin/main` and `jerome` HEAD both identify `170cc38`. The merge commit records [PR #29](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/29), with parents `d32199a` and Ralph source `eb04470`, at October 19, 07:30:13 Asia/Manila. `git merge-base --is-ancestor eb04470 origin/main` succeeds, and `git --no-pager diff --exit-code eb04470 170cc38` reports no differences: the merge preserves Ralph's exact source tree. This review uses the user's completed pull and local Git evidence; no new remote fetch or GitHub API check was performed. The local branch named `main` remains stale and was not switched or updated.

Reviewed owner-scoped request/loan queries, route/method/access boundaries, forms, cancellation service/lock order, templates and all ten T12 integration tests against the course U4 requirement, SRS, schema and HTTP contracts. No blocking runtime defect was found in the reviewed paths. Pending cancellation changes the request and audit atomically; Approved cancellation checks complete unreleased reservations and returns every unit to Available within that transaction. Other borrowers' detail/cancel targets return 404; issue/terminal states conflict with cancellation. This does not establish browser acceptance or a cancellation/issue concurrency result.

## Review finding and remaining coverage

- **P3 — explicit-parameter convention:** [test helpers](../borrowing/tests/test_request_tracking.py) at lines 64, 74 and 111 introduce `owner_id: int | None = None`. The [coding standard](../docs/coding-standards.md#style-naming-and-types) disallows default parameters in project-authored functions. This does not change production behavior. Ralph's smallest follow-up is to require the owner ID and pass the relevant borrower ID at each call site. No test/application source was changed in this documentation scope.
- The T12 suite validates an invalid request page, but does not traverse more than 25 rows, preserve filters across multiple pages, or exercise loan pagination boundaries. The guide now marks the missing local pagination data explicitly.
- The suite does not demonstrate separate-connection cancellation versus issue or approval races. Future workflow checks must retain the shared lock contract; T14's competing-approval proof remains separate work.
- Approved cancellation, populated loan display and return display use test-database records. Browser scenarios through actual approval/issue/return actions await T13/T15/T17. The user has not supplied T12 browser, keyboard or mobile results.
- The pre-existing inventory unit-detail formatting and T10 test-media isolation follow-ups remain open; no unrelated cleanup was performed.

## Documentation and manual preparation

- [AGENTS.md](../AGENTS.md), [README](../README.md), [DEV](../DEV.md), [SRS](../docs/SRS.md), [architecture](../docs/architecture.md) and [HTTP contract](../docs/api_spec.md) identify integrated T12 and the remaining upstream workflows. Existing folder-architecture paths already match the source and needed no edit. PLAN sequencing is unchanged.
- [Manual Module 10](../docs/manual-test-guide.md#module-10--borrower-request-and-loan-tracking-t12) supplies field/value inputs for a fresh Pending request, valid/invalid filters and pages, cancellation/keep/retry outcomes, audit-page verification and a read-only cancellation-metadata query. Later-workflow cases stay pending. Module 9 retains its dated October 18 examples and recalculation warning.
- A PostgreSQL transaction explicitly set to `READ ONLY` inspected permitted local records/settings at **07:36 Asia/Manila**: active fictional seed accounts; three Pending requests owned by `auth_demo_user` (IDs 1–3); no loans or other request statuses; limits 7 days/3 units; active HDMI Projector ID 1 and category. No local records/settings were created, seeded or changed for guide preparation. This is a time-bound snapshot during ongoing user testing, not an execution result.
- [Task evidence](../docs/tasks.md#verified-task-evidence) and [current handoff/index](../HANDOFF.md) now reflect the integration. Ralph's [October 18 snapshot](ralph-t12-request-history-and-cancellation-10-18-2026.md) is preserved unchanged as historical evidence.
- Concurrent edits appeared in DEV.md during this review, including table formatting and `runserver --insecure`. They are preserved alongside the T12 documentation edits; that startup-command change was not authored or exercised by this review.

## Verification on the integrated source

| Check | Actual result |
| --- | --- |
| `.\.venv\Scripts\python.exe manage.py test --noinput` | **191 PostgreSQL tests passed in 32.738s**; separate test database created and removed. Includes all 7 T11 and 10 T12 tests; no separate focused rerun in this review |
| `.\.venv\Scripts\ruff.exe check .` | Passed |
| `.\.venv\Scripts\ruff.exe format --check .` | Passed; 195 files already formatted |
| Django `check --database default` | Passed; no issues |
| Django `makemigrations --check --dry-run --noinput` and `migrate --check` | Passed; no model changes or pending migrations |
| `.\.venv\Scripts\python.exe -m pip check` | Passed |
| `npm.cmd run format:check`, `npm.cmd run build`, `npm.cmd audit` | Passed; zero vulnerabilities |
| `.\.venv\Scripts\djlint.exe templates/accounts/portal --check` | Passed; all 9 portal templates formatted |
| `.\.venv\Scripts\djlint.exe templates --check` | Reports only the existing `templates/inventory/manage/unit_detail.html` formatting difference; unrelated file unchanged |
| Documentation links/anchors, integration-label consistency and `git --no-pager diff --check` | Passed: 548 relative links and 117 Markdown anchors across all 10 changed documents; no stale T12 pre-integration labels in current docs; whitespace check clean |
| Browser / keyboard / mobile | Not run by Codex; user testing is in progress, results not supplied |

The original [Ralph handoff](ralph-t12-request-history-and-cancellation-10-18-2026.md) records his earlier 17-test focused run and 191-test full run; the results above were freshly obtained on the integrated revision. No skill metadata, migrations, dependencies or application source were changed. The npm build updates ignored generated assets only.

## Next action and ownership

- User/Jerome: finish manual T12 cases and record actual results/revision/browser/request IDs. No manual pass is inferred from this review.
- Ralph: address the non-blocking test-helper convention and verify pagination with suitable records when that follow-up is authorized.
- Margareth / T13 (requires integrated T03/T11) and Kenneth / T16 (requires integrated T08/T03) remain independently ready; no feature starts automatically. T12 satisfies T20's tracking prerequisite, but T17/T18/T19 remain outstanding. Exercise the deferred cancellation/loan scenarios as their workflows become available.
- Review documentation changes on `jerome`. Leave them uncommitted; no commit, push, PR or merge was requested for this task.
