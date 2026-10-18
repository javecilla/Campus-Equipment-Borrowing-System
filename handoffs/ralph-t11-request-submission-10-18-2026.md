# Ralph T11 Request Submission

- **Owner:** Ralph Andre F. Giga (@dreygigz), with AI assistance
- **Date:** October 18, 2026, Asia/Manila
- **Task:** T11 — borrower request submission

## Outcome

T11 is **Done locally** on `ralph`; it is not integrated into main. Active BASIC_USER borrowers can submit a Pending request with a purpose, desired return date, and one to three distinct active catalog items. Form and formset validation completes before writes. The transactional service locks and rechecks the borrower, current SystemSetting row, and eligible catalog records, snapshots both limits, then creates the request and all request items atomically. Invalid rows, including an invalid third row, leave no request or request items.

The request-create page is available at `/portal/requests/new/` (`portal:request-create`) through `borrowing.views.request_create`. The existing `/portal/requests/` page provides submission confirmation and a link to start another request; request history, details, loan tracking, and cancellation remain T12 scope. No migration or dependency was added.

## Relevant files

- [Request forms and formset](../borrowing/forms.py)
- [Atomic submission service](../borrowing/services.py)
- [Borrowing views](../borrowing/views.py)
- [Portal route registration](../accounts/portal_urls.py)
- [Request creation template](../templates/borrowing/portal/request_form.html)
- [Request section template](../templates/accounts/portal/request_list.html)
- [PostgreSQL integration tests](../borrowing/tests/test_request_submission.py)
- [HTTP form contract](../docs/api_spec.md)
- [Transaction lock order](../docs/architecture.md)
- [T11 backlog and integration evidence](../docs/tasks.md#verified-task-evidence)

## Verification

- `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_request_submission --noinput` — **7 tests passed**.
- `.\.venv\Scripts\python.exe manage.py test --noinput` — **156 tests passed** in 284.281 seconds.
- `.\.venv\Scripts\ruff.exe check .` and `ruff format --check .` — passed; all 179 Python files checked.
- `manage.py check --database default`, `makemigrations --check --dry-run --noinput`, and `migrate --check` — passed; no new migration detected.
- `python -m pip check` — passed.
- `npm.cmd run format:check`, `npm.cmd run build`, and `npm.cmd audit` — passed; audit reported zero vulnerabilities.
- djLint checks on both changed templates passed. Repository-wide `djlint templates --check` still reports the pre-existing formatting issue in `templates/inventory/manage/unit_detail.html`; that unrelated file was not changed.
- Relative file links in all seven changed Markdown files passed. An explicit Prettier check flagged formatting in the six edited existing project documents; no broad reformat was applied, and this new handoff passes its own Prettier check.
- No browser-based visual, keyboard, or responsive smoke test was run. Django client tests cover access, rendered form content, success, and invalid submissions; integrated UI/accessibility review remains part of T20.
- `git diff --check` — passed.

## Branch and integration state

- Branch: `ralph`; the worktree is uncommitted for review.
- The branch was based on `origin/main` at `f29bd91`, which includes the integrated T03, T08, and T09 prerequisites. `origin/main` is an ancestor of the current branch.
- The local branch is 16 commits ahead of the stale `origin/ralph` reference at `f7c32f8`; no Ralph commit was created and nothing was pushed.
- **Main integration: Not integrated.** There is no commit or PR for T11. Commit, push, PR, and merge were explicitly outside this request.

## Remaining work and next action

- T12 remains Not started until T11 is reviewed and integrated into main. After an authorized integration, Ralph must sync main into `ralph`, verify the interface, and then resume T12.
- T10 / Ellyssa and T16 / Kenneth have their own integrated prerequisites and may proceed on their assigned branches.
- T20 is not ready; its T10, T12, T17, T18, and T19 dependencies are not all integrated.
- No additional design decision is needed for the verified T11 scope.
