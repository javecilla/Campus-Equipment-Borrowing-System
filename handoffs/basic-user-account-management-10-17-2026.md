# T05 Basic-user Account Management Handoff

## Work, owner, and date

- Task: T05 basic-user account management
- Owner: Alex, with Codex assistance
- Branch: `alex`
- Date: October 17, 2026, Asia/Manila
- State: locally complete, uncommitted, unstaged, and not integrated into `main`

## Current outcome

The synchronized local `alex` branch and fetched `origin/main` now resolve to `34d4806`. T03, T04, the exact four-extension LF correction from PR #10, the username-or-email authentication follow-up, the light shared interface, and the native-form/Axios-removal follow-up are integrated in that base. The previous T05 candidate was based on `5f42ac0`; every dirty path was compared across `5f42ac0..34d4806`, and T05 was rebuilt in a detached clean worktree from `34d4806` instead of accepting the byte-restored overlapping files. The isolated candidate preserves the newer login form and light UI. Upstream-deleted `scripts/copy-licenses.mjs` and `static/js/http.js` are absent from the candidate and remain unrelated untracked files in Alex's original checkout.

T05 provides administrator-only basic-user account search, active-status filtering, fixed 25-row pagination, detail/profile display, request history, and loan history with issued asset codes. `/manage/` links to the account list using the integrated light interface. The list and all detail/action routes use T04's active-ADMIN guard.

The reported browser concern that `q=basicdemo` was present in the URL while the search control appeared empty was not reproduced in the server-rendered response. The bound Django form renders the submitted search value and selected status, and pagination links carry both parameters. A regression test now forces two matching pages and verifies the search value and Active selection on the submitted first page and the second page. A live visual browser recheck was not available in this review session, so no additional browser result is claimed.

Activation and deactivation are separate POST actions with CSRF-protected confirmation pages. Both transactional services lock the actor and target in stable primary-key order, recheck that the actor is an active `ADMIN`, scope the target to `BASIC_USER`, update only `is_active`, and write the matching actor/target audit in the same transaction. Repeating an already-current action returns 409. Missing records and ADMIN targets return 404. Submitted actor, target, role, identity, password, staff, and superuser fields are not trusted or applied.

Deactivation does not delete or mutate the target Profile, requests, request items, allocations, loans, returns, or prior audit records. T04's middleware invalidates an existing session for the newly inactive account on its next request.

Alex manually verified in the browser that deactivating the fictional `basicdemo` account blocked its access, reactivating it restored portal access, and `basicdemo` was denied access to `/manage/accounts/`. These are user-performed checks, separate from the automated PostgreSQL test results. Profile and history preservation were not manually checked.

## Relevant files

- `accounts/forms.py`
- `accounts/queries.py`
- `accounts/services.py`
- `accounts/urls.py`
- `accounts/views.py`
- `accounts/tests/test_account_management.py`
- `templates/accounts/manage/list.html`
- `templates/accounts/manage/detail.html`
- `templates/accounts/manage/status_confirmation.html`
- `templates/operations/manage/dashboard.html`
- `docs/tasks.md`
- `HANDOFF.md`
- `handoffs/basic-user-account-management-10-17-2026.md`

This is the proposed 13-path T05 commit boundary. In `HANDOFF.md`, include only the T05 current-state bullet, T05 dated-index row, T05 work-at-handover row, T05 verification row, and T05 portion of the open action. In `docs/tasks.md`, include only T05's `Done` status and T05 evidence row, plus the minimum T04 next-consumer text needed to remove the obsolete “T05 remains Not started” statement. Exclude earlier MCP/setup hunks and unrelated table or prose formatting in those shared files.

Also exclude `.gitattributes`; `config/views.py`; `package.json`; `package-lock.json`; `scripts/copy-licenses.mjs`; `static/css/app.css`; `static/js/http.js`; `templates/dev/index.html`; `handoffs/local-developer-database-mcp-verification-10-17-2026.md`; `.idea/`; `.env.local`; `.venv/`; `node_modules/`; generated `static/build/`; and every unrelated MCP, preview, setup, lockfile, IDE, dependency, or formatting-only change. No model or migration change was required.

## Verification and actual results

| Check | Actual result |
| --- | --- |
| Prerequisite and review base | Local `alex` and `origin/main` resolve to `34d4806`; `d122518`, `7ae5e87`, `5f42ac0`, PR #11's `aa6d8e8`, and the Axios-removal source commit are ancestors. Every dirty path was classified against `5f42ac0..34d4806`. Isolated T05 base: exact detached `34d4806` |
| Focused PostgreSQL suite | Isolated `manage.py test accounts.tests.test_account_management --verbosity 2`: 13 tests passed |
| Full PostgreSQL suite | Isolated `manage.py test`: 57 tests passed |
| Django configuration | `manage.py check --database default`: no issues |
| Schema drift | `manage.py makemigrations --check --dry-run --noinput`: no changes detected |
| Applied migrations | `manage.py migrate --check`: passed with no pending migration |
| Python lint/format | `ruff check .`: passed; `ruff format --check .`: 118 files already formatted |
| Django template format | `djlint templates --check`: 14 files checked; none would be updated |
| Locked frontend installation and build | Isolated `npm ci`: 50 packages installed from the `34d4806` lockfile and 0 vulnerabilities; `npm run format:check`: passed; `npm run build`: passed after the sandboxed esbuild wildcard scan was denied and the same build was rerun with local runtime access. npm emitted the existing non-blocking warning that `min-release-age` will not be recognized as an environment config in its next major version |
| Dependency checks | Isolated `npm audit`: 0 vulnerabilities; `python -m pip check`: no broken requirements |
| Query-state regression | The focused suite confirms submitted `q` and `active` values render on page 1, remain in the page-2 link, and render again on page 2. The reported server-rendered value loss was not reproduced |
| Documentation, scope, and patch integrity | All T05-added relative link targets resolve; isolated status contains exactly the proposed 13 paths; `.env.local` is ignored; dependency/generated/private/IDE/setup/preview/lockfile files are absent; `.gitattributes` is unchanged from `34d4806`; `git diff --check` passed with only expected working-tree line-ending conversion warnings |
| Original-checkout reconciliation | The 12 T05 paths other than `HANDOFF.md` are Git-content-identical to the isolated candidate. `HANDOFF.md` has the same T05 hunks plus only the preserved unrelated MCP current-state/index/evidence changes. The original index is empty. Explicitly excluded non-IDE file hashes still match the synchronization snapshot |
| Manual browser checks by Alex | Deactivating `basicdemo` blocked its access; reactivating `basicdemo` restored portal access; `basicdemo` was denied access to `/manage/accounts/` |

The focused tests exercise active-ADMIN access; anonymous and BASIC_USER denial; exact lowercase status filters; trimmed search and 200-character validation; retained search/status controls and links through pagination; 25-row pagination and malformed/nonexistent-page 404s; detail/profile/request/loan rendering; GET confirmation, POST-only mutation, and CSRF enforcement; forged protected fields and target IDs; ADMIN-target rejection at views and services; activation/deactivation audit actor, action, and target; repeated-action 409 responses; inactive-session invalidation; a real PostgreSQL audit constraint failure rolling back deactivation; and preservation of account and transaction history.

## Unresolved issues and limitations

- Alex's manual browser verification was limited to the three results recorded above. Profile/history preservation was not manually confirmed, and no additional manual check is claimed.
- The reported empty search-control appearance was checked at the rendered-response level, including pagination, and was not reproduced. No browser surface or credentials were available for a new live visual check, so a CSS/autofill/browser-only cause was not ruled out.
- Verification ran against an isolated detached worktree assembled from only the proposed T05 boundary on exact base `34d4806`, not against unrelated dirty files in Alex's checkout. The original checkout remains uncommitted and unstaged.
- The LF correction is integrated in `34d4806` and remains outside T05. The upstream-deleted license-copy and HTTP-client files are absent from the candidate; their unrelated untracked copies in the original checkout were preserved, not deleted or included.
- `.idea/` remains excluded and untracked/ignored. Several live PyCharm metadata hashes changed relative to the earlier synchronization snapshot during this review; those current IDE files were preserved as found and were not reverted or included in T05.
- T05 is not integrated into `main`; no commit, push, PR, merge, registration work, demonstration seeding, or other task was performed.

## Manual verification status and next action

Completed by Alex with the fictional `basicdemo` account:

1. Deactivation blocked the account's access.
2. Reactivation restored access to `/portal/`.
3. Direct access to `/manage/accounts/` was denied.

The checks below remain optional review steps and are not recorded as completed. In particular, do not treat Profile or history preservation as manually verified.

Use fictional local accounts only: one active `ADMIN`, one active `BASIC_USER` with a Profile (for example `basicdemo`), one inactive `BASIC_USER`, and optionally existing coherent request/loan rows. Do not create artificial history solely for this smoke check.

1. Start PostgreSQL, run `npm.cmd run build`, then run `manage.py runserver 127.0.0.1:8001`.
2. Sign in as the fictional administrator at `http://127.0.0.1:8001/accounts/login/` and open `http://127.0.0.1:8001/manage/accounts/`.
3. Search by username/name/email/contact number, filter active and inactive accounts, and open `http://127.0.0.1:8001/manage/accounts/<basic-user-id>/`. Confirm Profile, request history, and loan history match stored records.
4. Open the separate deactivate confirmation URL, submit it, and confirm the detail changes to Inactive while request/loan history remains unchanged. Re-submit the same action and confirm a conflict response rather than a second audit.
5. From a browser session already signed in as that basic user, open `/portal/` and confirm a 403 plus session invalidation. Confirm a new sign-in attempt is rejected.
6. Return as the administrator, use the separate activate action, and confirm the account can sign in and reach `/portal/` again.
7. While signed in as the BASIC_USER, directly open the account list/detail/action URLs and confirm access is denied. Attempt an administrator account ID in the detail and action URLs and confirm 404 without a status change.
8. Inspect the account-status audits through PostgreSQL or the later authorized T06 audit UI, confirming the acting administrator, action, USER target, target ID, and one row per successful transition.

After review and the optional browser smoke, stage only the T05 boundary and its T05-specific documentation hunks if publication is separately authorized. Do not include the unrelated dirty-tree changes or start another task as part of this handoff.
