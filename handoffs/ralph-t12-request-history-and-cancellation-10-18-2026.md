# Ralph T12 Request History and Cancellation

- **Owner:** Ralph Andre F. Giga (@dreygigz), with AI assistance
- **Date:** October 18, 2026, Asia/Manila
- **Task:** T12 — borrower request/loan tracking and cancellation
- **Branch:** `ralph`

## Outcome

T12 is **Done locally** on `ralph`; the changes are uncommitted and **not integrated into main**. The implementation adds borrower-owned request and loan history/details, request status filtering, and a CSRF-protected cancellation flow for Pending and eligible Approved requests. Cancellation rechecks the active borrower and locked workflow state, releases every qualifying reservation, and records the request transition and audit entry atomically. Request/loan IDs belonging to another borrower are not disclosed. Issued asset codes and per-unit return status/condition are displayed without internal notes.

No migration or dependency was added. T13 approval, T15 issue, and T17 return remain separate workflows; browser scenarios requiring them are documented as pending, not claimed as passed.

## Interfaces and relevant files

- Portal routes: request history `/portal/requests/` (`portal:request-list`), request detail `/portal/requests/<request_id>/` (`portal:request-detail`), cancellation `/portal/requests/<request_id>/cancel/` (`portal:request-cancel`), loan history `/portal/loans/` (`portal:loan-list`), and loan detail `/portal/loans/<loan_id>/` (`portal:loan-detail`). See [portal URL configuration](../accounts/portal_urls.py).
- [Owner-scoped history queries](../borrowing/queries.py) provide request and loan records and related unit-return information.
- [Borrowing views](../borrowing/views.py) handle filtered/paginated history, details, and the confirmation/action endpoints.
- [Cancellation form](../borrowing/forms.py) and [transactional service](../borrowing/services.py) implement POST confirmation and `cancel_request(owner_id, request_id)`.
- [Portal request templates](../templates/accounts/portal/request_list.html), [request detail](../templates/accounts/portal/request_detail.html), [cancellation confirmation](../templates/accounts/portal/request_cancel.html), [loan list](../templates/accounts/portal/loan_list.html), [loan detail](../templates/accounts/portal/loan_detail.html), and [portal navigation](../templates/accounts/portal/base.html) expose the flow.
- [PostgreSQL/client integration tests](../borrowing/tests/test_request_tracking.py) cover owner/method/CSRF boundaries, filters and pagination, cancellation success/conflicts/rollback, reservation release, and loan-unit display.
- [T12 manual test section](../docs/manual-test-guide.md#module-10--borrower-request-and-loan-tracking-t12) lists expected browser results and clearly identifies unrun and upstream-dependent scenarios.
- Contracts and developer guidance updated: [HTTP specification](../docs/api_spec.md), [architecture](../docs/architecture.md), [folder architecture](../docs/project-folder-architecture.md), and [DEV.md](../DEV.md).

## Verification

- `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_request_submission borrowing.tests.test_request_tracking --noinput` — **17 focused T11+T12 PostgreSQL tests passed**.
- `.\.venv\Scripts\python.exe manage.py test --noinput` — **191 PostgreSQL tests passed**.
- `.\.venv\Scripts\ruff.exe check .` and `.\.venv\Scripts\ruff.exe format --check .` — passed.
- `.\.venv\Scripts\python.exe manage.py check --database default`, `makemigrations --check --dry-run --noinput`, and `migrate --check` — passed; no new migration.
- `.\.venv\Scripts\python.exe -m pip check` — passed.
- `npm.cmd run format:check`, `npm.cmd run build`, and `npm.cmd audit` — passed; audit reported zero vulnerabilities.
- Targeted djLint checks for changed templates: passed. Repository-wide djLint still reports the pre-existing formatting issue in `templates/inventory/manage/unit_detail.html`; that unrelated file was not changed.
- `git diff --check`: passed.
- Browser visual, keyboard, and mobile testing: **Not run**.
- No live local test-record eligibility/data check was performed for the manual browser scenarios. The guide does not assert that suitable records currently exist; it requires a borrower request and, for later scenarios, T13/T15/T17 workflows.

## Branch and integration state

- Local branch `ralph` is at `d32199a`; the local `origin/main` ref is also at `d32199a` and is an ancestor of the branch. The integrated T11 prerequisite is present through PR #27 at `6c5ea8f`.
- T12 application and documentation changes remain uncommitted. No T12 commit, push, PR, or merge was made.
- Main integration: **Not integrated**. A Done status on `ralph` does not make T12 available to T20 or other consumers.

## Readiness and next action

- Ralph: review the uncommitted T12 diff locally. The user requested that it remain uncommitted and did not authorize publishing or integrating it.
- After separately authorized integration, complete the documented browser scenarios that depend on T13 approval, T15 issue, and T17 returns. No live local-record check date or manual pass is claimed.
- Margareth / T13 and Kenneth / T16 have independently satisfied integrated prerequisites. T20 remains gated on integrated T12, T17, T18, and T19.
