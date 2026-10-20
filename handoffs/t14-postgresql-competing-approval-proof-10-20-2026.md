# T14 PostgreSQL Competing-Approval Proof

- **Owner:** Jerome Avecilla with Codex assistance; Margareth's T13 approval implementation preserved.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** Authorized T14 implementation on `jerome`, verification, manual guide and current documentation. No publication or downstream feature implementation.
- **Outcome:** Done locally, uncommitted and not integrated into main.

## Prerequisite and interfaces

Fetched main `cf50d0ceb6c0413c27429f88288421d543c11aab` is [PR #35](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/35), integrating T13 query fixes `1d7a3c7`. Source ancestry and exact correction/merge tree equality were verified. `jerome` was fast-forwarded to that main before implementation. T13's acceptance/integration prerequisite is satisfied; the [earlier fix snapshot](t13-query-fixes-and-publication-10-19-2026.md) remains historical.

[Two new PostgreSQL TransactionTestCase scenarios](../borrowing/tests/test_approval_concurrency.py) call the real `approve_request(actor_id, request_id, reason)` service through separate connections with distinct borrowers/admins. A third connection holds the category lock until PostgreSQL's blocking chain proves both workers overlap. The tests account for queued lock blockers, require three distinct backend PIDs, bound waits and close worker connections. Only `WorkflowConflict` counts as the expected loser; unexpected errors propagate.

The first race requires one last-unit approval and one stock conflict, exact active allocation, winner decision/audit and untouched loser state. The second adds an uncontested item before each request's shared item and requires the loser to retain its other Available unit with no partial allocation. No application service, HTTP route, schema, dependency or production locking change was needed. Existing T13 HTTP tests cover 409 mapping; these new tests exercise service concurrency directly.

## Relevant files

- [Concurrency tests](../borrowing/tests/test_approval_concurrency.py).
- [Module 13 reproduction and fixture values](../docs/manual-test-guide.md#module-13--postgresql-competing-approvals-t14) and [DEV command/evidence](../DEV.md#postgresql-competing-approvals-t14).
- [Task acceptance and integration evidence](../docs/tasks.md#verified-task-evidence), [current handoff](../HANDOFF.md) and affected current-state documentation. Historical handoffs and original requirement/member sources are preserved.

## Actual verification

- Focused command: `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_approval_concurrency --noinput --verbosity 2` — **2 passed in 0.894s**.
- Full command: `.\.venv\Scripts\python.exe manage.py test --noinput` — **254 PostgreSQL tests passed in 42.576s**, including 28 T13 and 33 maintenance tests. Separate test database created/destroyed successfully in each run.
- Ruff lint and format, Django `check --database default`, migration drift and applied-migration checks, pip dependency check and djLint (67 templates) passed. npm format/build/audit passed with zero vulnerabilities. Documentation links/anchors, consistency and whitespace checked after final edits.
- Read-only local inspection at **07:55 Asia/Manila**: PostgreSQL 17.5 / Read Committed, transaction read-only on, limits 7 days / 3 per item. No live records changed; all new fictional fixtures existed only in the test database.

## Limits and next action

Browser/mobile/keyboard outcomes remain Not run. Cancellation/issue concurrency, release, returns, performance and backup/restore are outside this proof. Smaller T13 default/typing/helper follow-ups remain non-blocking.

Jerome reviews the local diff and publishes/integrates T14 when explicitly authorized. No commit, push or PR was created for T14. After accepted T14 reaches main, Margareth may implement T15 using integrated T13/T14; T17 still requires T15 with T16 already satisfied. T22 also requires T19/T20/T21. See [PLAN.md](../PLAN.md) for unchanged sequencing gates.
