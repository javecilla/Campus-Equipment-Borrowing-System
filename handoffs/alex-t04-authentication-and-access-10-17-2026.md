# Alex T04 authentication and access

- Owner: Alex Enrico Cayanan (`@AlexCayanan`), with Codex assistance.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00); verification completed around 05:15.
- Task: T04 only—shared login/logout and role redirects, active/admin/ownership enforcement, and an authorized administrator-creation command.
- Prerequisite: T02 merge `d122518` is an ancestor of the current `alex` HEAD. Current HEAD and `origin/main` are both `021d8d467c01af1f60c65740812451a4c8ebe62c`.
- Delivery: committed locally on `alex`; no push, PR, or merge. **Not integrated into main.**

## Outcome and interfaces

T04 meets its local acceptance criteria. Registration/profile (T09), account activation/deactivation/history (T05), and live dashboard data (T18) remain outside this task.

| Area | Implemented interface |
| --- | --- |
| Routes | [accounts/urls.py](../accounts/urls.py) supplies `accounts:home`, `accounts:login`, and POST-only `accounts:logout`; [accounts/portal_urls.py](../accounts/portal_urls.py) supplies the protected `portal:home`; [operations/urls.py](../operations/urls.py) supplies the protected `operations:dashboard` role destination |
| Login behavior | [accounts/views.py](../accounts/views.py) uses Django session authentication, generic credential errors, stored-role redirects, and same-origin plus resolved-namespace validation for `next`. Anonymous `/` redirects to login; active `BASIC_USER` and `ADMIN` accounts redirect to `/portal/` and `/manage/` respectively |
| Active sessions | [accounts/middleware.py](../accounts/middleware.py) is installed immediately after Django authentication middleware. It detects a now-inactive account behind an existing session, logs it out, and returns 403 |
| Reusable access contract | [accounts/access.py](../accounts/access.py) exports `active_login_required`, `admin_required`, `basic_user_required`, `require_active_user`, `require_active_admin`, `require_active_basic_user`, and `get_owned_object_or_404(queryset, user, object_id, owner_lookup)`. Runtime access trusts only the stored two-role field, never `is_staff`/`is_superuser` or submitted role fields. Owner mismatches return 404 |
| Administrator setup | `python manage.py create_admin --username ... --first-name ... --last-name ... --email ...` prompts twice for a non-command-line password. [accounts/services.py](../accounts/services.py) validates it and atomically creates one active `ADMIN` plus Profile while fixing Django admin flags false. There is no public admin creation/promotion endpoint |
| Templates | Custom login and safe 403 pages plus minimal protected role destinations. The `/manage/` destination contains no static dashboard data. The debug-only `/test` preview remains public with DEBUG enabled and now links to `accounts:home` |

The setup command is the course-approved CLI alternative for initial administrator creation. It does not invent a SYSTEM account-creation audit actor: the current shared audit writer requires an existing active user, and T05 owns audited runtime account activation/deactivation. A later team decision can extend the audit enum/contract if command-level bootstrap auditing is explicitly required.

## Verification performed

| Check | Actual result |
| --- | --- |
| Prerequisite/integration | `git merge-base --is-ancestor d122518 HEAD` passed; `alex` HEAD and `origin/main` both resolve to `021d8d4` before these uncommitted changes |
| Authentication/security tests | Full `manage.py test --noinput`: **35 passed** on PostgreSQL, including 12 T04 tests. Coverage includes stored-role redirects, forged role inputs, unsafe/wrong-role `next`, generic invalid/inactive login, direct wrong-role access, staff/superuser bypass attempts, inactive existing-session invalidation, POST/CSRF logout, cross-owner 404, debug preview gates, password validation, atomic Profile creation, and fixed admin flags |
| Django/schema | `check --database default`, `makemigrations --check --dry-run --noinput`, and `migrate --check` passed; no model or migration change |
| Python/templates | `ruff check .`, `ruff format --check .`, and `djlint templates --check` passed |
| Frontend/dependencies | `npm run format:check` and `npm run build` passed; `npm audit` reported zero vulnerabilities; `pip check` reported no broken requirements. npm emitted the existing `min-release-age` future-version warning |
| HTTP smoke | Temporary runserver on `127.0.0.1:8011`: login 200, `/test` 200 with the application-home link and font-status element, anonymous `/manage/` 302 to `/accounts/login/?next=/manage/`. The temporary server was stopped |
| User browser verification | Alex reported successful administrator login, authorized access to `/manage/`, successful logout, and redirection to the login page when reopening `/manage/` after logout. This is user-supplied manual evidence, recorded October 17, 2026, and is distinct from the automated tests and agent-run HTTP smoke above |
| Local BASIC_USER readiness | Read-only ORM inspection found fictional `basicdemo` with stored role `BASIC_USER`, `is_active=True`, fixed staff/superuser flags false, and its required Profile. Its `last_login` is populated and there are no unexpired sessions. These observations do not by themselves prove the three requested browser page outcomes |
| BASIC_USER browser follow-up | Not yet recorded as passed. The agent did not receive the private password, the available browser-control surface could not open a browser, and a password-free headless attempt was blocked before execution. Do not claim the `basicdemo` portal/management/logout browser flow until Alex supplies manual confirmation or it is run successfully |
| Line-ending policy | Added `.gitattributes` with `* text=auto eol=lf`; `git check-attr` reports `text: auto` and `eol: lf` for `.gitattributes`, `HANDOFF.md`, `docs/tasks.md`, and `config/tests.py` |
| Diff and commit boundary | `git diff --check` passed. The reviewed 32-path T04 boundary was staged explicitly, its cached diff passed `git diff --cached --check`, and existing uncommitted MCP/setup, preview, lockfile, and IDE changes were preserved. No push, PR, or merge was performed |

During the earlier agent verification, the user-started process at `127.0.0.1:8001` was still serving the older development index/preview and was left untouched. Alex subsequently supplied the manual authentication results recorded above. The earlier successful DM Sans/Poppins result remains separate prior evidence.

The pre-existing `docs/tasks.md` working copy used CR-only separators, so the patcher saw the backlog as one line. The project's pinned Prettier normalized that affected file before T04 status/evidence was added; its earlier MCP wording was preserved. This accounts for the larger mechanical backlog diff.

## Commit preparation review

The reviewed T04 commit consists of these 30 whole files:

```text
.gitattributes
accounts/access.py
accounts/forms.py
accounts/management/__init__.py
accounts/management/commands/__init__.py
accounts/management/commands/create_admin.py
accounts/middleware.py
accounts/portal_urls.py
accounts/services.py
accounts/tests/__init__.py
accounts/tests/test_authentication.py
accounts/urls.py
accounts/views.py
operations/urls.py
operations/views.py
templates/403.html
templates/accounts/login.html
templates/accounts/portal/home.html
templates/operations/manage/dashboard.html
config/settings.py
config/tests.py
config/urls.py
templates/dev/frontend-test.html
README.md
DEV.md
docs/SRS.md
docs/api_spec.md
docs/architecture.md
docs/project-folder-architecture.md
handoffs/alex-t04-authentication-and-access-10-17-2026.md
```

Only the T04 hunks in `HANDOFF.md` and `docs/tasks.md` belong with that candidate, producing the reviewed 32-path boundary. Both files also contain earlier MCP/setup work; `docs/tasks.md` additionally has a mechanical whole-file formatting diff. They require hunk-level staging or a prior separate commit instead of whole-file staging.

Exclude `config/views.py`, `package-lock.json`, `handoffs/local-developer-database-mcp-verification-10-17-2026.md`, `.idea/`, and the eight status-only line-ending paths reported by Git. `.env.local`, `.venv/`, `node_modules/`, and generated `static/build/` are ignored; none of those private/generated paths is tracked or in the commit. A sensitive-value comparison against the local `.env.local` and a high-risk token scan found no live credential in the 32 commit paths; the credential-shaped PostgreSQL URL in `DEV.md` uses the literal placeholders `YOUR_USER` and `YOUR_URL_ENCODED_PASSWORD`.

The configured checks still pass after this review. An extra direct Prettier probe against the nine affected Markdown files—not part of `npm run format:check`—reported that it would reformat all nine; no write was made because that would expand the mixed and historical documentation diffs.

## Next action and gates

1. Alex reviews the local T04 commit and the recorded limitation that the three `basicdemo` browser page outcomes were not independently rerun by the agent.
2. Push and PR creation require separate authorization. Jerome alone integrates `main`; do not push, open a PR, or merge as part of this commit action.
3. T05 (Alex), T06 (Jerome), T07 (Kenneth), and T09 (Ellyssa) still require T04 to be reviewed and integrated into main. Local completion on `alex` does not satisfy their integration gate.
4. After integration, record the actual commit/PR/main revision, rerun relevant checks on the integrated tree, and update the backlog/current handoff before those consumers start.
