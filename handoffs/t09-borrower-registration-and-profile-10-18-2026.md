# Work Handoff: T09 Borrower Registration and Profile Management

## Overview

- **Date:** October 18, 2026, Asia/Manila
- **Author:** Ma. Ellyssa Bianca Regodon (@ellieebeann, Member 5) with Antigravity assistance
- **Branch:** `elly` (uncommitted for review, Not integrated)
- **Task:** [T09: Borrower account registration, profile, and portal layout](../docs/tasks.md#inventory-and-borrower-portal)
- **Prerequisite:** T04 (Shared authentication and access controls, integrated into `main` at `cb96319`)

---

## Outcome and Delivered Behavior

1. **Student Registration (`/accounts/register/`, `accounts:register`):**
   - Implemented `RegistrationForm` in [`accounts/forms.py`](../accounts/forms.py) with explicit field allowlists: `username`, `first_name`, `last_name`, `email`, `contact_number`, `password1`, `password2`.
   - Validates uniqueness of `username` and `email` case-insensitively, and ensures no cross-identifier collisions (e.g., username matching another user's email) to protect AUTH-02 login resolution.
   - Enforces Django standard password validators (`validate_password`) and password confirmation matching.
   - Implemented `register_basic_user` service in [`accounts/services.py`](../accounts/services.py), creating `User` with `role=UserRole.BASIC_USER`, `is_active=True`, `is_staff=False`, `is_superuser=False` and [`Profile`](../accounts/models.py) atomically within a transaction.
   - Commits an audit entry (`AuditAction.ACCOUNT_CREATED`, `AuditTarget.USER`) within the same transaction; failure of audit rolls back creation atomically.
   - Implemented `register_view` in [`accounts/views.py`](../accounts/views.py): anonymous users see the registration form; authenticated users are redirected to their role home; successful registration redirects to `accounts:login` with a success message.
   - Created accessible, responsive template [`templates/accounts/register.html`](../templates/accounts/register.html) matching application branding, error summaries, and login linkage.
   - Added messages inclusion and borrower registration link to [`templates/accounts/login.html`](../templates/accounts/login.html).

2. **Borrower Profile Management (`/portal/profile/`, `portal:profile`):**
   - Implemented `ProfileForm` in [`accounts/forms.py`](../accounts/forms.py) with allowlisted fields: `first_name`, `last_name`, `email`, and `contact_number`.
   - Rejects email collisions with other accounts, but allows a user to save without re-triggering conflict against their own existing email.
   - Implemented `update_basic_user_profile` service in [`accounts/services.py`](../accounts/services.py), acquiring an explicit `select_for_update()` lock, verifying `require_active_basic_user`, and updating only allowlisted name/email/contact fields.
   - Commits an audit entry (`AuditAction.ACCOUNT_UPDATED`, `AuditTarget.USER`) within the transaction without leaking contact data in the audit summary.
   - Rejects privilege escalation, self-promotion, or protected-field tampering: attempts to pass `role`, `is_staff`, `is_superuser`, `is_active`, or `username` are strictly ignored.
   - Updated `profile` view in [`accounts/portal_views.py`](../accounts/portal_views.py) to accept `GET` and `POST` for active `BASIC_USER` accounts.
   - Updated [`templates/accounts/portal/profile.html`](../templates/accounts/portal/profile.html) with a read-only account identity section (displaying username and role) and an editable form for personal name and contact details.

3. **Portal Layout & Navigation Alignment:**
   - Adjusted [`operations/tests/test_navigation.py`](../operations/tests/test_navigation.py) to separate `portal:profile` (now an active, editable destination) from pending module placeholders (`PORTAL_READ_ONLY`), while preserving navigation link resolution, active indicator tests, and role protection.
   - Added comprehensive test suite [`accounts/tests/test_borrower_portal.py`](../accounts/tests/test_borrower_portal.py) containing 15 new test cases covering all registration and profile workflows.

---

## Changed Files

| File | Change |
| :--- | :--- |
| [`accounts/forms.py`](../accounts/forms.py) | Added `CONTROL_CLASSES`, `RegistrationForm`, and `ProfileForm`. |
| [`accounts/services.py`](../accounts/services.py) | Added `register_basic_user` and `update_basic_user_profile` services with atomic audit logging. |
| [`accounts/views.py`](../accounts/views.py) | Added `register_view` with authenticated redirection and flash messaging. |
| [`accounts/urls.py`](../accounts/urls.py) | Added `accounts:register` route pattern. |
| [`accounts/portal_views.py`](../accounts/portal_views.py) | Updated `profile` view to handle GET and POST. |
| [`templates/accounts/register.html`](../templates/accounts/register.html) | Created registration page template. |
| [`templates/accounts/login.html`](../templates/accounts/login.html) | Added messages inclusion and registration link. |
| [`templates/accounts/portal/profile.html`](../templates/accounts/portal/profile.html) | Updated profile template to support editing. |
| [`operations/tests/test_navigation.py`](../operations/tests/test_navigation.py) | Updated navigation tests to reflect editable `portal:profile`. |
| [`accounts/tests/test_borrower_portal.py`](../accounts/tests/test_borrower_portal.py) | Added 15 integration tests for T09. |

---

## Verification Results

| Check | Command | Result |
| :--- | :--- | :--- |
| Full Test Suite | `python manage.py test` | **125 tests passed** in 50.7s (all 15 new T09 tests, 110 existing tests). |
| Django System Check | `python manage.py check` | System check identified no issues (0 silenced). |
| Migration Drift Check | `python manage.py makemigrations --check` | No changes detected. |
| Ruff Linting | `ruff check .` | All checks passed. |
| Ruff Formatting | `ruff format --check .` | 162 files already formatted. |
| djLint Templates | `djlint templates/ --check` | 0 files would be updated. |
| Prettier Formatting | `npm run format:check` | All matched files use Prettier code style. |
| Frontend Asset Build | `npm run build` | Tailwind CSS and esbuild JS bundles built cleanly. |
| NPM Audit | `npm audit` | 0 vulnerabilities found. |
| Pip Dependencies | `pip check` | No broken requirements found. |
| Git Whitespace/Diff | `git diff --check` | Clean. |

---

## Remaining Work & Next Steps

1. **Review & Publication:** Changes remain uncommitted on branch `elly` awaiting user review. When authorized, commit with proper attribution and propose integration into `main`.
2. **Next Task for Ellie:**
   - **T10 (Borrower Equipment Catalog Browsing & Detail):** Remains **Not started** and is **Blocked** by Kenneth's **T08** (Physical-unit management, unstarted on `kenneth`) and T09 integration.
