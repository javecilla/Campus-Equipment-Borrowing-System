# Authentication test account seed

- Owner: Jerome Avecilla, with Codex assistance.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00), around 11:16.
- Task/scope: AUTH-01, explicitly requested two-account setup for testing Alex's integrated T04. The user selected privately prompted passwords. Alex's remaining features and T21's full demonstration dataset are outside this scope.
- Delivery: local, uncommitted on `jerome` based on `cb96319`; **Not integrated**. No commit, push, new PR, or merge performed. Earlier uncommitted T04 integration-review documentation is preserved.

## Outcome and requirements

The [course brief](../docs/Project-Requirements.txt), Parts 4–5, requires fictional demonstration data and seed setup and permits documented administrator setup commands. The small seed introduces no conflict; it does not satisfy the full dataset in [T21](../docs/tasks.md#required-fictional-demonstration-dataset), which remains Not started with its T17 dependency. T02/T04 are integrated prerequisites for this independent authentication setup.

`python manage.py seed_auth_accounts` prompts twice for each account's password and creates `auth_demo_admin` (`ADMIN`) and `auth_demo_user` (`BASIC_USER`). Both accounts are active, have Profiles, and keep Django staff/superuser flags false. Passwords are validated and hashed through Django. Existing seed usernames, invalid passwords, or mismatched confirmation fail explicitly; existing accounts are not overwritten or reactivated. The account writes are atomic. Passwords are not accepted as arguments or printed.

## Relevant files and interfaces

- [Seed service](../accounts/seeding.py): `seed_auth_accounts(admin_password, basic_user_password) -> tuple[User, User]`, reusing Alex's `create_admin_account` and the current User/Profile schema. No model/migration, public endpoint, or authentication change.
- [Management command](../accounts/management/commands/seed_auth_accounts.py): terminal password prompts and validation errors.
- [Integration tests](../accounts/tests/test_auth_seed.py): real ORM and Django client flows; only terminal password input is patched.
- [DEV setup](../DEV.md#seed-authentication-test-accounts): canonical command, behavior, collision handling, and manual role-test steps. README links it; the folder guide identifies the new seed helper.
- [Backlog](../docs/tasks.md#authentication-development-setup) and [current handoff](../HANDOFF.md): AUTH-01 evidence, readiness, and this snapshot's index.

## Verification performed

| Check | Actual result |
| --- | --- |
| Full PostgreSQL suite | `manage.py test --noinput`: 39 passed in 12.016 seconds, with the separate test database created and destroyed |
| Seed checks after final command adjustment | Four seed integration tests passed again in 3.701 seconds: real login/role destinations/wrong-role 403/CSRF logout for both roles, invalid BASIC_USER password rolls back both accounts, existing username preserved without creating the other account, confirmation mismatch writes nothing |
| Django/schema | `check --database default`: no issues; `makemigrations --check --dry-run --noinput`: no changes; `migrate --check`: passed |
| Python/templates | `ruff check .`: passed; `ruff format --check .`: 101 files already formatted; `djlint templates --check`: seven checked, zero updates. Accounts lint/format checks passed again after the final command adjustment |
| Frontend/dependencies | `npm run format:check` and `npm run build` passed; `pip check`: no broken requirements. Initial sandboxed `npm audit` could not reach the registry; approved retry passed with zero vulnerabilities |
| Command discovery | `manage.py help seed_auth_accounts` passed and exposes no password argument |
| Documentation/review | 349 relative links/anchors across nine documents, fences, dated filename, unchanged T05/T06/T07/T09/T18/T19/T21 statuses, preserved Alex snapshot, and `git --no-pager diff --check` passed after edits; code reviewed against the existing account service and MTV requirements |

No local seed was executed outside the temporary test database: the user will supply their passwords directly in the terminal. Real browser testing of these accounts is pending; Django client checks are not browser results. The user's earlier supplied startup logs prove root-to-login redirection and asset serving, with 35 tests passing before this seed; they do not prove authenticated role flows. No new dependency, schema, or MCP configuration change was needed.

## Next action

Jerome runs the command documented in DEV.md, chooses private passwords, and checks both roles' login, allowed/denied destinations, and logout in the browser. Review the uncommitted changes before separately requesting publication. T05 remains ready for Alex; T18/T19 retain later workflow prerequisites, and T21 remains pending the full implemented workflow.
