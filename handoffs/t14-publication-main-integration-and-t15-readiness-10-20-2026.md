# T14 Publication, Main Integration and T15 Readiness

- **Owner:** Jerome Avecilla with Codex co-author credit; Margareth's approval service preserved.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** Authorized final documentation review, T14 commit/push and ordinary merge PR integration. T15 implementation is not included.
- **Outcome:** T14 is Done and integrated; Margareth / T15 is ready, Not started.

## Publication and integration evidence

Source [`058357cffcf34b1ea257998b25add675d5b5ba43`](https://github.com/javecilla/Campus-Equipment-Borrowing-System/commit/058357cffcf34b1ea257998b25add675d5b5ba43) was committed/pushed on `jerome` with `Co-authored-by: Codex <codex@openai.com>`. [PR #37](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/37) merged it at **`5381c83975753426208ffde6370c4e8da09fe5d9`**, October 20, 2026, 08:23 Asia/Manila. The merge commit also includes Codex credit. The GitHub merge result, fetched main, source ancestry and exact source/merge tree equality were verified; `jerome` was fast-forwarded to that merge. Permanent member branches were preserved.

The [implementation snapshot](t14-postgresql-competing-approval-proof-10-20-2026.md) preserves the earlier local state. Current README/DEV/AGENTS, backlog, HANDOFF, requirements/architecture/HTTP/folder summaries and [Module 13](../docs/manual-test-guide.md#module-13--postgresql-competing-approvals-t14) now record the actual integration and next owner. This receipt and the current-state updates are documentation only; they do not alter the tested application or concurrency tests.

## Verification

- Fresh publication run: `manage.py test --noinput` — **254 PostgreSQL tests passed in 39.994s**, including 2 T14, 28 T13 and 33 maintenance tests. Separate test database created and destroyed.
- Ruff lint/format, Django database check, migration drift/applied checks, pip dependency check, djLint (67 templates), npm format/build/audit (zero vulnerabilities) and whitespace checks passed. Documentation relative links/anchors, fences, Unicode and integration-label consistency checked after receipt updates.
- Original focused T14 run: 2 tests passed in 0.894s. PostgreSQL 17.5 / Read Committed and limits 7 days / 3 per item were inspected read-only at 07:55 Asia/Manila. No live data changed.
- PR #37 had no registered checks/statuses. No repository test CI workflow exists; the GitHub platform Copilot cloud-agent entry is separate. The optional no-mistakes CLI is not installed, so no pipeline/automated-review pass is claimed. Local configured checks and source review supplied the evidence.
- Original requirement/member files and earlier completed handoffs are unchanged. Browser/mobile/keyboard results remain unrun; earlier cleanup findings are retained rather than closed by publication.

## Next owner and scope

**Margareth on `marga` can take T15 after syncing main and rechecking the evidence.** T13 is accepted/integrated through PR #35 at `cf50d0c`; T14 is accepted/integrated through PR #37 at `5381c83`. No T15 prerequisite merge remains missing. T15 stays Not started until its owner begins authorized implementation.

Use the existing [backlog acceptance](../docs/tasks.md#administrator-operations), [SRS BR-05/BR-06](../docs/SRS.md#business-rules-and-calculations), [HTTP contract](../docs/api_spec.md#custom-administration-requests-loans-and-maintenance), [schema](../docs/db_design.md) and [transaction lock order](../docs/architecture.md#transaction-boundaries-and-lock-order). T15 covers audited pre-issue due-date revision, one-time release with Loan/LoanUnits and printable slip. Reuse existing allocation/authentication contracts; verify invalid/expired/incomplete/repeated issue, audit rollback and cancellation/release contention, then add concrete manual cases before handoff. The approval service interface and existing reservations remain unchanged by T14.

T17 still needs T15 with T16 already integrated. T20/T22 retain their other backlog dependencies. T10 test-photo storage isolation, T11 navigation/style, T12 helper defaults, T13 typing/default/helper conventions and outstanding manual/pagination checks remain follow-ups; this readiness decision does not claim they were fixed. See [current handoff](../HANDOFF.md) for the active state and [PLAN.md](../PLAN.md) for unchanged sequencing rules.
