# T09 Main Integration and Documentation Review

- Date: October 18, 2026, Asia/Manila.
- Review/documentation: Jerome Avecilla with Codex assistance.
- Implementation owner: Ma. Ellyssa Bianca Regodon, `elly`, with Antigravity assistance; original [work snapshot](t09-borrower-registration-and-profile-10-18-2026.md) preserved.
- Scope: review merged T09 and align current project documentation. No application implementation or publication requested.

## Outcome and integration

Local `jerome` HEAD and `origin/main` both resolve to `91015868cbb44bfa96e0e510f2f84e69ff1c18ef`, the merge of [PR #21](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/21), preserving Ellyssa's source `9ffbe2d16666870b417b0d46e10fd6aee6a78473`. T04 prerequisite `cb96319` is an ancestor. T09 is integrated, rather than uncommitted or awaiting a PR as its original snapshot recorded.

T07's continuation `32b7cc2` and publication record `9c0416c` are also ancestors of main through [PR #20](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/20), merge `a4634b9d33fbe643c1a092cc9cf57696e518dc73`. Kenneth / T08 has its prerequisite accepted and integrated; T08 remains Not started. `.idea/` remains ignored and untracked.

T09 delivers anonymous registration at `accounts:register`, fixed BASIC_USER creation with Profile and transactional ACCOUNT_CREATED audit, and signed-in borrower name/email/contact editing at `portal:profile` with account locking and ACCOUNT_UPDATED audit. Privilege and target identifiers come from server-controlled state. Administrator profiles remain read-only. No migration or dependency was added by T09. Interfaces and field rules are recorded in the [HTTP contract](../docs/api_spec.md#shared-account-routes).

## Open review finding

**P1: invalid username characters cause an unhandled exception during registration.** In [RegistrationForm](../accounts/forms.py:119), the username CharField lacks the model's username-character validator; [clean_username](../accounts/forms.py:219) checks normalization/collisions only. The [registration view](../accounts/views.py:125) calls the service after form validity. [User.full_clean](../accounts/services.py:122) then raises ValidationError, which the view does not map to bound form errors.

Reproduction in a temporary PostgreSQL test database: submit otherwise valid registration fields with username `review student` and an internal space. RegistrationForm is valid, then the POST raises the username ValidationError. The transaction leaves no account behind, but the response fails the required 200-with-field-errors contract. The existing 125 tests do not cover this input. The extra one-test probe intentionally asserted the current exception to confirm the finding; its passing result does not mean the application behavior is accepted. The probe was run from standard input and added no repository test file.

T09 status is reopened from Done to **In progress**, while main integration remains recorded. Minimum next correction for Ellyssa: apply the existing model username validator at the form boundary and verify invalid registration POST returns bound username errors with no User, Profile or audit writes; rerun registration/profile and full integration checks before closing acceptance. No code correction was made during this documentation review.

## Documentation aligned

- [README](../README.md), [DEV](../DEV.md), [HANDOFF](../HANDOFF.md) and [backlog](../docs/tasks.md): actual PR #20/#21 integration, current phase, 125-test evidence, T09 finding, T08 readiness and T10/T11 blockers.
- [PLAN](../PLAN.md): remove stale publication status from its starting-point guidance and keep status in the backlog/current handoff, preserving sequencing and ownership.
- [HTTP contract](../docs/api_spec.md), [architecture](../docs/architecture.md), [SRS](../docs/SRS.md) and [folder guide](../docs/project-folder-architecture.md): implemented registration/profile behavior and real file paths, administrator profile distinction, planned browsing/workflows and unchanged schema/dependencies.
- [AGENTS](../AGENTS.md): current documentation-only authorization. Source requirement/member files and all earlier snapshots preserved.

## Fresh verification

| Check | Result |
| --- | --- |
| `python manage.py test --noinput` using `.venv` | All 125 existing PostgreSQL tests passed in 27.345 seconds; test database removed |
| Isolated registration probe | One test passed in 0.456 seconds, confirming the unhandled invalid-username ValidationError and no account persistence; separate test database removed |
| `.venv/Scripts/ruff.exe check .` | Passed |
| `.venv/Scripts/ruff.exe format --check .` | 163 files already formatted |
| djLint check of registration, login and borrower profile templates | Three files checked; zero would be updated |
| `python manage.py check --database default` | Zero issues |
| `python manage.py makemigrations --check --dry-run --noinput` | No changes detected |
| `python manage.py migrate --check` | Passed; no unapplied migrations |
| `npm.cmd run build` and `npm.cmd run format:check` | Passed |

Documentation verification passed: 494 local Markdown links across 11 documents resolve, code fences are balanced, and `git diff --check` passes. Source requirement/member files and Ellyssa's original snapshot have no changes. No browser or clean-machine run, dependency audit, CI, concurrency acceptance, performance or backup/recovery check was run during this review. Ellyssa's original handoff retains her separately reported results. The user's local audit-template edit was excluded from formatting and its SHA-256 remained unchanged during final review.

## Next actions

Ellyssa resolves and verifies the T09 finding; Kenneth can begin authorized T08 work after syncing main and applying the [existing setup steps](../DEV.md#continuing-with-t08). T10 / Ellyssa and T11 / Ralph remain Not started until T08 and T09 are accepted and integrated. Changes in this review remain local and uncommitted; no commit, push, PR or merge was performed. Local `jerome` was already two commits ahead of its tracking ref at entry because the user had pulled main.
