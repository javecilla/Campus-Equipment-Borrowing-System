# Username or email sign-in

- Owner: Jerome Avecilla, with Codex assistance, explicitly authorized by the user to extend Alex's shared T04 authentication.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00), around 11:41.
- Task: AUTH-02. Alex's T04 remains the integrated authentication foundation; T05, T18, and T19 were not implemented or reassigned.
- Delivery: local, uncommitted on `jerome`, based on `cb96319`; **Not integrated**. Earlier uncommitted work and completed handoffs preserved. No commit, push, PR, merge, schema migration, reset, or reseed performed.

## Outcome and contract

[LoginForm](../accounts/forms.py) accepts either an exact username or case-insensitive email in the existing POST field `username`. The visible label is "Username or email". The field accepts 254 characters, including valid addresses longer than the model username's 150-character limit. The inherited native form's length override is explicitly corrected.

The combined username/email query must identify exactly one User. Shared emails and cross-account username/email collisions fail with the same generic error as invalid or inactive credentials. Account selection never depends on the password or database row order. Email remains nonunique in the schema; users sharing an address can use an unambiguous username. No account data is repaired or merged automatically.

After resolution the form uses the existing Django `authenticate` backend, password checks, and active-account policy. It retains native session backend identity, role destinations, safe `next`, CSRF, and existing authorization helpers. Unknown/ambiguous identities perform dummy password hashing like Django's native unknown-user handling; password-bearing local variables remain marked sensitive. No public role/activation inputs were added.

## Relevant files

- [Login form](../accounts/forms.py) and [authentication integration tests](../accounts/tests/test_authentication.py).
- [Portal home](../templates/accounts/portal/home.html) and [management home](../templates/operations/manage/dashboard.html): stable `logout-submit` test IDs for browser verification.
- [HTTP contract](../docs/api_spec.md#shared-account-routes), [database design](../docs/db_design.md#user-accountsuser), and [SRS](../docs/SRS.md): agreed username/email behavior and ambiguity boundaries, without a schema uniqueness change.
- [DEV sign-in steps](../DEV.md#seed-authentication-test-accounts), [folder guide](../docs/project-folder-architecture.md), [backlog](../docs/tasks.md#verified-task-evidence), and [current handoff](../HANDOFF.md).

## Verification performed

| Check | Actual result |
| --- | --- |
| Focused authentication suite | 17 tests passed in 10.369 seconds against PostgreSQL |
| Full PostgreSQL suite | 44 tests passed in 16.655 seconds; separate test database created and destroyed |
| New behavioral coverage | Five integration cases cover both-role mixed-case email login with CSRF logout, invalid/inactive/unknown email rejection, duplicate email with preserved username login, cross-account username/email collisions, and valid email longer than 150 characters |
| Live Chrome | Existing local server at `127.0.0.1:8000`: administrator email reached `/manage/`; uppercase basic-user email reached `/portal/`; both sign-out actions returned to sign-in. Stable input IDs and test IDs used. Final screenshot confirms the updated label and visible focused input; the test tab is left signed out |
| Django/schema | Database check: no issues; migration drift: no changes; applied-migration check: passed |
| Python/templates | Ruff lint passed; Ruff format: 104 files already formatted. Initial template check identified indentation in the two edited buttons; djLint corrected those owned templates and the repeated full template check passed with zero updates |
| Frontend/dependencies | npm formatting and build passed; approved npm audit reported zero vulnerabilities; pip check found no broken requirements |
| Documentation/privacy/review | 407 relative links/anchors across 14 documents, fences, filename/date, downstream task statuses, preserved Alex snapshot, private seed-password exclusion from shareable files, and diff whitespace passed after edits. Form/lookup/native authentication behavior reviewed against installed Django source |

No dependency or schema change was needed. Browser smoke covered the desktop sign-in flow; a full mobile/accessibility audit and unimplemented account/workflow pages were not tested. Existing native sessions retain their backend path. Browser login/logout updates normal account/session state; no passwords were changed, saved to the browser, or written into shared files.

## Next action

Jerome may sign in now with either seed username or email and the existing private seed password. Review the uncommitted change before separately requesting publication. Alex / T05 and Ellyssa / T09 keep their existing ownership and dependencies; their future forms reuse the documented identity rules after authorized integration. The full demonstration seed remains T21 and is not completed by this authentication change.
