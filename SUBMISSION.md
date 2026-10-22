# Submission Checklist

**IT401W WEB PROGRAMMING AND FRAMEWORKS — Final Project A**  
Target date: Saturday, October 24, 2026 · Confirm exact section/group name with Jerome for the ZIP filename.

Instructor confirmed: submit **source code + screenshots of the system** in a digital folder.
No PPT/slides needed. Bring a **printed project rubric in two copies** on demo day.

---

## Quick status overview

| #   | Item                                                         | Owner                                           | Status      |
| --- | ------------------------------------------------------------ | ----------------------------------------------- | ----------- |
| 1   | Application (T01–T24): all workflows implemented and tested  | Team                                            | Done        |
| 2   | System diagrams — editable (Lucidchart or similar) T25       | Kenneth / Ellyssa / Margareth                   | In Progress |
| 3   | [User needs, options comparison, emerging-tech evaluation T26](docs/user-needs-evidence-guide.md) | Jerome / Alex + everyone                        | Done |
| 4   | Professional judgment, AI/reuse/policy disclosure T27        | Alex coordinates + everyone                     | In Progress |
| 5   | Team participation and individual contribution evidence T28  | Everyone — rotate leadership                    | In Progress |
| 6   | Verified user / admin / technical guides T29                 | Ellyssa+Ralph / Margareth+Kenneth / Jerome+Alex | Not Started |
| 7   | Screenshots of the system | Jerome with Codex assistance | Done (72 PNGs) |
| 8   | Submission ZIP assembled and clean-machine tested T30        | Everyone                                        | Not Started |
| 9   | Demo rehearsed; printed rubric ready T31                     | Everyone                                        | Not Started |

---

## Screenshots checklist

View the [system screenshot gallery](docs/system-screenshots.md) for all 72 images displayed with short page descriptions. Source `c3fb6bb` is published on `origin/jerome`; [publication receipt](handoffs/database-switch-and-screenshot-publication-10-22-2026.md) verifies remote equality and Codex credit. Main integration remains pending.

The instructor confirmed screenshots of the system are the required evidence format.
Captured October 22, 2026, Asia/Manila: **72 actual browser PNGs** in `screenshots/`, using a disposable copy of the local fictional dataset and local photos. Desktop viewport: 1440 x 1000; two mobile captures: 390 x 844. All 39 checklist entries below have evidence. This completes screenshot collection, not T30 ZIP assembly or clean-machine verification.

The copy was restored from local `campus_equipment` into `campus_screenshots_20261022`; archive/account-state examples changed only that disposable copy. The damaged-return example links its existing maintenance record, which was subsequently repaired. CSV confirmation is Chrome's real completed download entry; browser automation gives its temporary file a generated name. The companion [loan-report.csv](screenshots/loan-report.csv) contains 13 October loans plus their totals row, verified against the report. No screenshot content was retouched or synthesized. See [connection switching](DEV.md#switch-between-local-and-shared-databases) and the [capture handoff](handoffs/local-database-switch-and-submission-screenshots-10-22-2026.md).

### Admin role

- [x] [Sign-in page](screenshots/01-signin.png)
- [x] [Admin dashboard — four live cards (available units, pending requests, active loans, overdue loans)](screenshots/02-admin-dashboard.png)
- [x] [Admin dashboard — monthly issued-loan chart and equipment-category usage chart](screenshots/03-admin-dashboard-charts.png)
- [x] [Equipment categories list with search](screenshots/04-admin-categories-search.png)
- [x] [Catalog items list (active and archived)](screenshots/05-admin-catalog-active.png); [06-admin-catalog-archived](screenshots/06-admin-catalog-archived.png)
- [x] [Physical units list with status filter (Available / Reserved / Issued / Maintenance / Retired)](screenshots/07-admin-units-available.png); [08-admin-units-reserved](screenshots/08-admin-units-reserved.png); [09-admin-units-issued](screenshots/09-admin-units-issued.png); [10-admin-units-maintenance](screenshots/10-admin-units-maintenance.png); [11-admin-units-retired](screenshots/11-admin-units-retired.png)
- [x] [Request queue — pending requests, searchable](screenshots/12-admin-request-queue.png)
- [x] [Request detail — approval/rejection form with reason field](screenshots/13-admin-pending-request.png); [14-admin-approval-form](screenshots/14-admin-approval-form.png); [15-admin-rejection-form](screenshots/15-admin-rejection-form.png)
- [x] [Approved request showing allocated units](screenshots/16-admin-approved-allocations.png)
- [x] [Rejected request with reason](screenshots/17-admin-rejected-request.png)
- [x] [Cancelled request](screenshots/18-admin-cancelled-request.png)
- [x] [Equipment release form](screenshots/19-admin-release-form.png)
- [x] [Generated borrowing slip (borrow receipt)](screenshots/20-admin-borrowing-slip.png)
- [x] [Per-unit return form](screenshots/21-admin-unit-return-form.png)
- [x] [Partial return (some units returned, loan still active/overdue)](screenshots/22-admin-partial-return.png)
- [x] [Damaged return that opens a maintenance record](screenshots/23-admin-damaged-return.png); [24-admin-linked-maintenance](screenshots/24-admin-linked-maintenance.png)
- [x] [Maintenance records list (open and closed)](screenshots/25-admin-maintenance-list.png); [26-admin-maintenance-closed](screenshots/26-admin-maintenance-closed.png); [27-admin-maintenance-open](screenshots/27-admin-maintenance-open.png)
- [x] [Overdue loans highlighted in the loan report](screenshots/28-admin-loan-report.png)
- [x] [Loan report with date filter applied](screenshots/29-admin-filtered-loan-report.png)
- [x] [Overdue report](screenshots/30-admin-overdue-report.png)
- [x] [CSV export download confirmation](screenshots/31-csv-export-download.png); [actual CSV](screenshots/loan-report.csv)
- [x] [Audit log with search/filter](screenshots/32-admin-audit-filter.png)
- [x] [Settings page (loan duration and max units per item)](screenshots/33-admin-settings.png)
- [x] [Account management — user list](screenshots/34-admin-accounts.png)
- [x] [Account detail with activate/deactivate action](screenshots/35-admin-account-detail.png)
- [x] [A form validation error example (any form showing inline field errors)](screenshots/36-form-validation-error.png)

### Basic-user (portal) role

- [x] [Portal home after sign-in](screenshots/37-portal-home.png)
- [x] [Browse equipment catalog with category/search filter](screenshots/38-portal-catalog-filter.png)
- [x] [Equipment detail page (serviceable units shown; no internal notes or maintenance details)](screenshots/39-portal-equipment-detail.png)
- [x] [Borrowing request form (1–3 items, quantities, dates, purpose)](screenshots/40-portal-request-form.png)
- [x] [Submitted Pending request in own history](screenshots/41-portal-pending-request.png)
- [x] [Approved request showing reserved units](screenshots/42-portal-approved-request.png)
- [x] [Active (Issued) loan in history](screenshots/43d-portal-issued-history.png); [43c-portal-issued-loan](screenshots/43c-portal-issued-loan.png)
- [x] [Cancelled request](screenshots/44-portal-cancelled-request.png)
- [x] [Profile / account page](screenshots/45-portal-profile.png)

### Access controls and errors

- [x] [Inactive user blocked at sign-in](screenshots/46-inactive-login-blocked.png)
- [x] [Admin redirected to `/manage/`, user redirected to `/portal/` after login](screenshots/37-portal-home.png); [02-admin-dashboard](screenshots/02-admin-dashboard.png)
- [x] [403 / access-denied page when a user hits a protected admin route](screenshots/48-access-denied.png)
- [x] [Empty state (no requests yet, or no search results)](screenshots/49-empty-search.png)

---

### Additional page and mobile captures

These supplement the checklist with actual create/edit/detail, confirmation and mobile pages.

- [43-portal-active-loans](screenshots/43-portal-active-loans.png)
- [43b-portal-loan-detail](screenshots/43b-portal-loan-detail.png)
- [50-admin-category-detail](screenshots/50-admin-category-detail.png)
- [51-admin-category-create](screenshots/51-admin-category-create.png)
- [52-admin-category-edit](screenshots/52-admin-category-edit.png)
- [53-admin-item-detail](screenshots/53-admin-item-detail.png)
- [54-admin-item-create](screenshots/54-admin-item-create.png)
- [55-admin-item-edit](screenshots/55-admin-item-edit.png)
- [56-admin-unit-detail](screenshots/56-admin-unit-detail.png)
- [57-admin-unit-create](screenshots/57-admin-unit-create.png)
- [58-admin-unit-edit](screenshots/58-admin-unit-edit.png)
- [59-admin-maintenance-create](screenshots/59-admin-maintenance-create.png)
- [60-admin-maintenance-close](screenshots/60-admin-maintenance-close.png)
- [61-admin-loan-list](screenshots/61-admin-loan-list.png)
- [62-admin-profile](screenshots/62-admin-profile.png)
- [63-admin-due-date-revision](screenshots/63-admin-due-date-revision.png)
- [64-admin-account-deactivation](screenshots/64-admin-account-deactivation.png)
- [65-borrower-registration](screenshots/65-borrower-registration.png)
- [66-portal-request-history](screenshots/66-portal-request-history.png)
- [67-portal-cancel-confirmation](screenshots/67-portal-cancel-confirmation.png)
- [68-mobile-portal-home](screenshots/68-mobile-portal-home.png)
- [69-mobile-equipment-catalog](screenshots/69-mobile-equipment-catalog.png)
- [70-admin-account-reactivation](screenshots/70-admin-account-reactivation.png)

---

## T30 — Submission ZIP checklist

### ZIP filename (must be exact)

- [ ] `IT401W_ProjectA_Section_Group.zip` — confirm the exact Section and Group values with Jerome before assembling

### Required contents

- [ ] All application source code (`accounts/`, `borrowing/`, `inventory/`, `operations/`, `config/`, `templates/`, `static/`)
- [ ] `migrations/` folders (inside each app)
- [ ] `requirements.txt` and `requirements-dev.txt`
- [ ] `package.json` and `package-lock.json`
- [ ] `README.md` — setup instructions for a clean machine
- [ ] `DEV.md` — team and technical setup guide
- [ ] `manage.py` and `setup.cfg` / `ruff.toml` / `.python-version`
- [ ] `.env.example` — configuration key template (no real values)
- [ ] Seed command documented (see `README.md` / `DEV.md` — `seed_demo_data`)
- [ ] `screenshots/` folder — all screenshots from the checklist above
- [ ] T25 diagram exports (images/PDFs from Lucidchart or equivalent)
- [ ] T26 [user-needs evidence and recommendations](docs/user-needs-evidence-guide.md) accepted record (T26 integrated through PR #63; include in the final ZIP)
- [ ] T27 professional judgment / AI/reuse disclosure document
- [ ] T28 team participation evidence
- [ ] T29 user guide (borrower) and admin guide

### Must NOT be included

- [ ] `.venv/` virtual environment
- [ ] `node_modules/`
- [ ] `.env.local` — contains real credentials, database URL, and secrets
- [ ] `media/` — team's private cloud-stored photos (do not include)
- [ ] `__pycache__/`, `.ruff_cache/`, `.playwright-cli/`
- [ ] Any file with real passwords, tokens, or private keys

### Demo credentials (submit separately — NOT in the ZIP)

- [ ] 1 admin account → submit through the instructor-designated channel
- [ ] 2 basic-user accounts → submit through the instructor-designated channel

### Final ZIP verification

- [ ] Unzip on a clean machine with no project dependencies installed
- [ ] Follow `README.md` Run locally steps from start to finish
- [ ] Run migrations, seed demo data, start server — app loads
- [ ] Both roles sign in with the demo credentials
- [ ] All principal workflows operate without errors

---

## T31 — Demo day checklist

**No PPT or slides needed (instructor-confirmed). Go directly to the system demo.**

### Before the demo day

- [ ] Printed project rubric — 2 copies (bring to class)
- [ ] App running on demo machine with seeded demonstration data
- [ ] Demo credentials confirmed and accessible offline
- [ ] Each member knows their assigned segment (see table below)

### Demo segments — 12 minutes total

Fill in the Presenter column and rehearse timing before October 24.
Every member must have an identifiable part.

| #   | Segment                     | What to show                                                                                  | Presenter | Target time |
| --- | --------------------------- | --------------------------------------------------------------------------------------------- | --------- | ----------- |
| 1   | Authentication and access   | Sign-in for both roles; inactive-user block; role-based redirect                              | —         | ~1 min      |
| 2   | Equipment catalog and units | Categories, items, physical units, status counts                                              | —         | ~1 min      |
| 3   | Borrower workflow           | Browse catalog, submit a borrowing request                                                    | —         | ~1 min      || Done |
| 4   | Request review              | Admin views queue, approves (with unit allocation), rejects with reason                       | —         | ~2 min      |
| 5   | Equipment release           | Admin releases approved request; borrowing slip generated                                     | —         | ~1 min      |
| 6   | Returns                     | Borrower view of active loan; admin records partial return, damaged return; maintenance opens | —         | ~2 min      |
| 7   | Screenshots of the system | Jerome with Codex assistance | Done (72 PNGs) |
| 8   | Settings and audit          | Change loan limits; audit log entries for all recorded actions                                | —         | ~1 min      |
| 9   | Concurrency (optional)      | Competing approvals; only one succeeds (T14 evidence)                                         | —         | bonus       |

### Q&A — 3 minutes

- [ ] Every member is prepared to explain any part of the submitted work
- [ ] AI assistance (Codex as Primary/Kiro/Devin/Antigravity/Copilot), third-party packages, and reused code declared on request
- [ ] Feedback from instructor and agreed action items recorded after the session

---

## README compliance check

Required README content per [Part 5 of the course brief](docs/Project-Requirements.txt).

- [x] Starts the application on a clean machine (Run locally section)
- [x] Environment-variable guidance (`DEV.md` and `.env.example`)
- [x] Migration command documented (`manage.py migrate`)
- [x] Seed command documented (`seed_demo_data` with link to DEV.md)
- [x] Tested dependency versions referenced (`requirements.txt`, `package-lock.json`)
- [x] Project scope and two-role system described
- [x] Third-party packages declared and justified
- [x] No committed credentials or application secrets
- [ ] Confirm section/group name matches the ZIP filename before final submission

---

_For task status and integration evidence see [docs/tasks.md](docs/tasks.md). For current readiness see [HANDOFF.md](HANDOFF.md)._
