# Inactive-Account Login Message Follow-up

## Work and owner

- **Scope:** Narrow AUTH-02 usability follow-up for password-verified inactive accounts
- **Owner:** Alex Enrico Cayanan (`@AlexCayanan`) with Codex implementation assistance
- **Branch:** `alex`
- **Date:** October 20, 2026, 19:36 Asia/Manila
- **Base:** `26b1ee555ae5b98e9d744bd7a11b3bfb74153b60`, the verified PR #45 T18 merge in `origin/main`
- **Publication state:** Completed source on `alex`; scoped commit/push/PR authorized; no authentication-follow-up merge or main integration evidence

## Outcome

The existing `accounts.forms.LoginForm` now distinguishes one narrowly authorized case: when the supplied username or case-insensitive email identifies exactly one inactive account and that account's stored password hash verifies, the bound login form displays:

> Your account has been deactivated. Please contact an administrator.

The login remains blocked and no session is created. A wrong password for that inactive account, an unknown identifier and every ambiguous username/email match retain **Invalid username/email or password.** Active accounts continue through Django's configured authentication backend, then the unchanged login view performs safe-next validation and stored-role routing.

## Cause and implementation boundary

Django's `ModelBackend.authenticate()` verifies a matching account's password and then applies `user_can_authenticate()`. That method rejects `is_active=False`, so the backend returns `None` for both correct inactive credentials and invalid credentials. The project LoginForm previously mapped every `None` result to the same generic error and configured its `inactive` error to the generic text.

The form now materializes the existing combined lookup's maximum two candidates. It preserves the generic/dummy-hash path unless exactly one candidate exists. For that unique inactive candidate only, it calls the model's password-hash check once: a valid password flows through the inherited `confirm_login_allowed()` inactive error; an invalid password remains generic. Active candidates still call Django `authenticate()`. No login logic moved into the view and no custom backend, service, session path or account-existence response was added.

## Files and interfaces

- `accounts/forms.py` — password-gated inactive candidate handling and distinct inherited inactive error text
- `accounts/tests/test_authentication.py` — username/email inactive cases, generic wrong/unknown/ambiguous cases, session absence and reactivation
- `docs/api_spec.md` — shared login response contract
- `docs/manual-test-guide.md` — expected browser steps using the dated read-only local account snapshot
- `docs/tasks.md` and `HANDOFF.md` — AUTH-02 follow-up evidence and non-integration state

No model, migration, service, backend setting, URL, view, template, dependency or live account state changed. T18 source `54380fd912b6cb684c11a8c2e79fa4cac00f856a` is preserved by PR #45 merge `26b1ee555ae5b98e9d744bd7a11b3bfb74153b60`; the merged source tree was verified before restoring this separate follow-up.

## Verification

| Check | Actual result |
| --- | --- |
| Focused `accounts.tests.test_authentication` | 20 passed in 20.810s |
| Complete `accounts.tests` | 53 passed in 31.591s |
| Complete PostgreSQL suite | 301 passed in 81.817s; system check found no issues |
| `manage.py check --database default` | Passed; no issues |
| `makemigrations --check --dry-run --noinput` | Passed; no changes detected |
| `migrate --check` | Passed; no unapplied migrations |
| `ruff check .` | Passed |
| Ruff format check for `accounts/forms.py` and `accounts/tests/test_authentication.py` | Passed |
| `npm.cmd run format:check` | Passed |
| `npm.cmd run build` | Passed; all nine theme contrast pairs pass |
| `npm.cmd audit` | Passed; zero vulnerabilities |
| `python -m pip check` | Passed; no broken requirements |
| `git --no-pager diff --check` | Passed |
| Read-only local account snapshot | Active `localadmin` ADMIN and active `basicdemo` BASIC_USER; no account state changed |

Repository-wide Ruff format still flags only the untouched Python example in `handoffs/borrower-portal-ui-improvements-10-20-2026.md`. Repository-wide djLint still flags only the untouched long tag in `templates/inventory/portal/equipment_list.html`. Both AUTH-02 Python files pass their configured formatter. These unrelated files were not modified.

## Manual browser status and steps

Manual browser execution is **Not run** because the local snapshot contains no inactive account and this task did not mutate live account state for evidence. Follow [Module 1.7](../docs/manual-test-guide.md#17-block-an-inactive-account-requires-creating-one-first): deactivate fictional `basicdemo`, verify the distinct message with its correct username and uppercase email, verify generic messages for its wrong password and an unknown identifier, confirm protected routes remain anonymous, reactivate the same account, and confirm the unchanged credentials redirect to `/portal/`. Record browser/version and actual results separately, then restore the account to active.

## Remaining action

Publish the authorized authentication-only commit to `origin/alex` and open the authorized PR into `main`. Jerome's review and main integration remain separate and are not authorized by this handoff. T18 is already integrated; this publication does not start T19.
