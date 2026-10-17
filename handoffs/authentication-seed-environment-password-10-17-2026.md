# Authentication seed environment password

- Owner: Jerome Avecilla, with Codex assistance.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00), around 11:25.
- Scope: AUTH-01 follow-up explicitly requested by the user: replace password prompts with one shared private environment password and create the two authentication test accounts.
- Delivery: local, uncommitted on `jerome`, based on `cb96319`; **Not integrated**. No commit, push, new PR, or merge performed. Earlier handoffs and uncommitted T04 integration-review changes are preserved.

## Outcome and interfaces

[The seed command](../accounts/management/commands/seed_auth_accounts.py) now requires `SEED_ACCOUNT_PASSWORD` from ignored `.env.local` or the process environment and passes it to both accounts. It has no prompt, password argument, or embedded default password. The supplied value was saved only in the private file and is not reproduced here. Missing/blank values fail clearly; Django password validation and atomic account creation remain enabled. Existing accounts are never reset or overwritten.

[config/environment.py](../config/environment.py) exposes `read_environment_values(path, process_environment)` by extracting the existing strict literal/duplicate-key parser. Normal application configuration continues through `read_environment`; seed configuration is required only when the command runs. Process values retain precedence. [.env.example](../.env.example) declares a blank seed key. [DEV.md](../DEV.md#seed-authentication-test-accounts) owns setup instructions, linked from README.

The command successfully created `auth_demo_admin` (`ADMIN`) and `auth_demo_user` (`BASIC_USER`) in the local database, each active with a Profile and false Django staff/superuser flags. Both use the user's configured shared password through Django hashes. Real local-database Django client requests verified login, correct role redirects, allowed destinations, forbidden cross-role destinations, CSRF-protected logout, and anonymous redirects afterward. These checks update normal last-login/session state; no equipment or workflow records were seeded.

The [original seed snapshot](authentication-test-account-seed-10-17-2026.md) retains the earlier prompt-based design. This follow-up supersedes that interface and its pending local-seed observation. [Task evidence](../docs/tasks.md#verified-task-evidence) and [HANDOFF.md](../HANDOFF.md) reflect the current state. T21 remains Not started; its full fictional demonstration dataset still requires implemented workflows.

## Verification performed

| Check | Actual result |
| --- | --- |
| Full PostgreSQL suite | `manage.py test --noinput`: 39 passed in 11.466 seconds; separate test database created and destroyed |
| Seed coverage | Four ORM/HTTP tests cover private file loading with a shared password and both-role login/access/logout, rollback on invalid password, existing-account preservation, and missing/blank seed configuration. Only process environment input is isolated in the command tests |
| Local creation and authentication | `manage.py seed_auth_accounts`: both accounts created. Follow-up Django client checks against the actual local database passed for both roles, including correct password hashes/Profiles/flags, 200 allowed pages, expected 403 cross-role pages, CSRF logout, and 302 after logout |
| Django/schema | Database check: no issues; migration drift: no changes; applied-migration check: passed. No schema change |
| Python/templates | Ruff lint passed; Ruff format: 102 files already formatted; djLint: seven templates checked, zero updates |
| Frontend/dependencies | npm formatting/build passed; pip check found no broken requirements. Sandboxed npm audit could not reach the registry; approved retry passed with zero vulnerabilities |
| Documentation/privacy | 358 relative links/anchors, fences, handoff naming, downstream task statuses, preserved completed snapshots, private-file Git exclusion, absence of the private seed password from shareable files, and diff whitespace passed after edits |

Browser automation/manual browser login was not performed. Existing Alex-reported browser evidence remains separate. No dependency installation, MCP change, or publication was needed.

## Next action

Jerome can sign in now with either seeded username and the configured shared password. Use the browser to verify both roles and logout. Rerunning the seed reports existing usernames; changing `.env.local` does not reset their passwords. Review the uncommitted changes before separately requesting publication. Other members' feature statuses and T21's prerequisites remain unchanged.
