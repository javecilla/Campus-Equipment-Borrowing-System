# T13 main integration review and documentation

Date: October 19, 2026, Asia/Manila. Integration reviewed after the 22:27 merge; live read-only snapshot at 22:31.

Implementation owner: Margareth Raine H. Ignacio (`marga`, source Git author Margareth Ignacio); review/documentation: Jerome Avecilla with Codex. Kenneth's T16 baseline and Jerome's corrections are preserved.

## Outcome and scope

PR #34 merged T13 at `23c1ad9ee5443c38d7c8035fa690c051d11f85c1`. Local `jerome`, `origin/main`, and remote main (`git ls-remote`) agree. Head `c5cfe37`, decision services `faa2a13`, and tests `fa64ea9` are preserved in history. The merge tree equals `c5cfe37` exactly. PR #33 already integrated T16 fixes `d68d7f7` at `aa36c86`; both are ancestors of this checkout. Remote `jerome` still points to `d68d7f7`; pulling main changed the local branch, without publishing this documentation.

The nine-file T13 merge contains queue/detail/decision forms, queries, views, services, routes, templates and 26 tests, with no documentation, migration or dependency changes. This review adds the missing documentation/manual cases and records actual integration. Application source was not modified. Existing historical handoffs and source requirement/member files are preserved.

**T13 is merged but In progress, pending the two reproduced functional findings below.** T16 is Done and integrated. T14 remains Not started; T15 requires accepted T13/T14 and T17 requires T15/T16. No application fixes, subsequent feature implementation, commits, pushes, PRs or merges were performed.

## Review findings

1. **P2 — Valid search text can crash the queue.** [borrowing/queries.py](../borrowing/queries.py), lines 25–26, calls `int(search_query)` after `isdigit()`. Superscript `²` passes that predicate but is not accepted by `int()`. An authenticated ADMIN GET to `/manage/requests/?q=%C2%B2` raises `ValueError`, producing a server error rather than a normal username/ID search response. An isolated HTTP probe reproduced the exception. Recognize only integer-convertible decimal ID text (while keeping the username query) and add integration coverage for non-decimal Unicode numeric text. Do not hide this with a catch-all handler.
2. **P2 — Ended allocations are presented as current reservations.** [borrowing/queries.py](../borrowing/queries.py), lines 50–52, includes all historical allocations; [request_detail.html](../templates/borrowing/manage/request_detail.html), lines 67 and 83, labels all returned asset codes as Reserved units. The probe approved a real request, cancelled it through T12, then fetched administrator detail: the physical unit was Available and allocation `ended_at` was set, but its asset code still appeared under Reserved units. This misstates current inventory and will also affect later released/returned history. Preserve historical rows; either show only current reservations there or render allocation history with its actual state. Add an approval → cancellation → administrator-detail integration check.
3. **P3 — Project coding conventions need follow-up.** New default parameters in [request_queue](../borrowing/queries.py) and [make_request](../borrowing/tests/test_requests.py), raw `list[dict]` detail data, `dict[int, list]` allocation candidates, untyped planning collections, the untyped `RequestQueueForm.clean()` return, and untyped callable dispatch in `_decide()` do not meet the [coding guide](../docs/coding-standards.md#style-naming-and-types). Review `_decide()` against the explicit single-purpose-function convention; retain distinct approval/rejection actions and typed presentation helpers. Ruff passing does not establish these standards. Keep any corrections limited to T13.

Margareth owns the corrections. The two functional findings remain open; this documentation work does not imply that they were fixed.

## Verified behavior and interfaces

- Active-ADMIN GET/HEAD `/manage/requests/` (`borrowing_manage:request-list`) validates search, persisted status and inclusive submission-date filters. Results order by newest submission/ID, 25 per page. Invalid filters show errors without unfiltered results; invalid page numbers return 404. Template pagination preserves filter query strings, but actual multi-page traversal was not executed.
- GET/HEAD `/manage/requests/<id>/` (`request-detail`) displays borrower, purpose, requested/agreed dates, quantities, current availability and decision/cancellation history. Current allocation presentation has finding 2.
- GET/HEAD/POST `/manage/requests/<id>/approve/` and `/reject/` use `DecisionForm`: stripped nonblank reason, maximum 500 characters. GET/HEAD does not mutate; valid POST redirects to detail, validation errors render 200, workflow conflicts render 409.
- `approve_request(actor_id, request_id, reason)` rechecks active ADMIN, Pending state, active borrower and active catalog/category records, then uses shared request/catalog/available-unit locks. It reserves complete quantities and commits allocations, unit statuses, decision metadata and audit together; shortages roll back. `reject_request(...)` records only the Pending decision and audit. No generic status endpoint was added.
- Five temporary review probes ran against a newly created test database: Unicode exception reproduction; ended-allocation display reproduction; real approval audit-insert failure rollback; real rejection audit-insert failure rollback; and missing-CSRF rejection on both decision POSTs. Audit probes used temporary PostgreSQL CHECK constraints inside test transactions, following existing project patterns, without mocks or live schema changes. These probes were supplied through standard input, not added as repository tests. They are separate from the 250-test suite.

## Documentation and manual preparation

Updated [README](../README.md), [DEV](../DEV.md), [AGENTS](../AGENTS.md), [current handoff](../HANDOFF.md), [task evidence](../docs/tasks.md#verified-task-evidence), [SRS](../docs/SRS.md), [architecture](../docs/architecture.md), [HTTP contracts](../docs/api_spec.md), [database status](../docs/db_design.md), and [folder guide](../docs/project-folder-architecture.md). The folder guide now points to the actual shared `request_decision.html` rather than the proposed `request_approve.html`. PLAN.md sequencing remains valid and was left unchanged.

[Manual guide Module 12](../docs/manual-test-guide.md#module-12--administrator-request-review-and-decisions-t13) supplies concrete success/rejection/shortage inputs, filters, stale-state/access cases, read-only audit/allocation verification and both known defects. T12 approved cancellation can now be prepared through real T13 approval; T15/T17 browser steps remain pending. T16 integration labels now reflect PR #33. Earlier dated local examples retain their dates and require a fresh eligibility check before use.

At October 19, 22:31 Asia/Manila, a live transaction with `transaction_read_only=on` found limits 7 days / 3 per item, 3 Pending requests, no requests in other states and no loans. Active HDMI Projector (ID 1) had 1 Available unit; HDMI Switch 4-Port (ID 3) had 0. Module 12 uses fresh fictional request markers and October 22 due dates, within October 20–26 boundaries for an October 19 submission. No borrower identities, credentials or live request purposes were published; no live data was seeded or changed.

## Checks actually run

| Check | Result |
| --- | --- |
| `.venv/Scripts/python.exe manage.py test --noinput` | **250 PostgreSQL tests passed in 42.713s**, including 26 T13 and 33 maintenance tests; test database destroyed |
| Five temporary PostgreSQL review probes | **5 passed in 0.226s**; two confirm existing defects, two verify audit rollback, one checks both CSRF paths; separate test database destroyed |
| Ruff lint and format checks | Passed; 205 files already formatted |
| `djlint templates --check` | Passed; 67 templates, 0 changes required |
| Django database check / migration drift / migration application check | Passed; no issues, no model changes detected, no pending migration |
| `python -m pip check` | Passed; no broken requirements |
| npm format / build / audit | Passed; CSS/JS generated successfully, zero vulnerabilities |
| Git integration | Remote main/head agreement, source/fix ancestry and exact source/merge tree equality verified |
| Live fixture inspection | PostgreSQL read-only transaction verified; only settings/catalog/availability and aggregate request/loan counts read |
| Documentation | Changed-file relative links/anchors, code fences, statuses, examples, source/scope preservation and whitespace checks passed after final reconciliation |

The 26 T13 tests ran as part of the full suite; the focused command is documented for reuse, not claimed as a separate run. Documentation changes after those tests did not change application behavior, so the suite was not repeated.

## Remaining work and next owner

Margareth corrects findings 1–2, addresses T13 typing/default/helper conventions and runs affected integration tests plus required checks. Verify browser decisions, cancelled-history display, mobile/keyboard behavior and multi-page filters, recording actual outcomes in the shared manual guide. Once T13 is accepted and corrections are integrated, Jerome with Margareth can implement T14's real competing approvals with separate PostgreSQL connections. T15 stays gated on T13/T14; T17 has its T16 prerequisite satisfied but still needs T15.

Browser checks were not run in this review. T14 competing approvals, cancellation/issue races, release, returns, reporting, performance, backup/restore and full demonstration data remain unverified or unimplemented according to the backlog. Keep this review's documentation uncommitted for user inspection.
