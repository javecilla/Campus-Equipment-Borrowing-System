# Registration Username Validation and T09 Status

- Date: October 18, 2026, Asia/Manila.
- Work: Jerome Avecilla with Codex; Ellyssa's T09 implementation and ownership preserved.
- Scope: the user confirms T09 is Done, then explicitly authorizes fixing invalid username registration. No commit, push or new main update requested.
- Branch/base: `jerome`, `83a4e74`; T09 is integrated through PR #21 at `9101586`, T08 through PR #22 at `6c91d48`.

## Current result

T09 is restored to **Done** in the backlog and current guides. The user confirms its delivered registration/profile scope is complete. T10 / Ellyssa, T11 / Ralph and T16 / Kenneth have their original prerequisites satisfied; they remain Not started. Earlier snapshots preserve the reviewer's former acceptance interpretation and are superseded by this current status clarification.

The separately authorized validation follow-up is fixed locally. [RegistrationForm](../accounts/forms.py) now uses Django's UsernameField and the existing User.username_validator. Normalization happens before character validation, so invalid input returns HTTP 200 with bound username errors before the creation service is invoked. The service retains its model validation, password hashing, atomic Profile creation and audit unchanged. No schema, dependency, route or template changes are needed.

One real PostgreSQL HTTP regression in [borrower portal tests](../accounts/tests/test_borrower_portal.py) covers an internal space, slash and Unicode fraction that normalizes to an invalid character. It verifies the field's invalid error code, visible error and unchanged User/Profile/AuditLog counts. Existing successful registration/profile tests continue to pass. No exception masking or catch-all recovery was added.

## Verification

| Check | Actual result |
| --- | --- |
| Full PostgreSQL integration suite | **149 tests passed in 31.332 seconds**; test database removed |
| Ruff lint / format | Passed; 172 files already formatted |
| Django database check | Zero issues |
| Migration drift / applied checks | No changes detected; no unapplied migrations |
| Affected registration template format | Passed; one template checked, zero changes |
| npm format/build/audit | Passed; zero audit vulnerabilities |
| pip check | No broken requirements |

Documentation verification passed: 438 local links across nine documents resolve, code fences are balanced, no conflict markers remain and `git diff --check` is clean. T09's backlog row is Done. Full template formatting was not repeated: the previously recorded unrelated unit_detail.html formatting issue remains unchanged. No browser, CI, concurrency, full-system acceptance, performance or backup/recovery run is claimed. Original requirement/member files and completed snapshots are preserved.

## Delivery and next action

The form/test fix and documentation are **local and uncommitted**. The fix is verified here, not published to main. Review before any separately authorized commit/push. T09 stays Done; this follow-up does not authorize starting T10/T11/T16 or claim those features exist.
