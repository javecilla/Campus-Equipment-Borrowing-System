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
| 3   | User needs, options comparison, emerging-tech evaluation T26 | Jerome / Alex + everyone                        | In Progress |
| 4   | Professional judgment, AI/reuse/policy disclosure T27        | Alex coordinates + everyone                     | In Progress |
| 5   | Team participation and individual contribution evidence T28  | Everyone — rotate leadership                    | In Progress |
| 6   | Verified user / admin / technical guides T29                 | Ellyssa+Ralph / Margareth+Kenneth / Jerome+Alex | Not Started |
| 7   | Screenshots of the system                                    | Everyone                                        | Not Started |
| 8   | Submission ZIP assembled and clean-machine tested T30        | Everyone                                        | Not Started |
| 9   | Demo rehearsed; printed rubric ready T31                     | Everyone                                        | Not Started |

---

## Screenshots checklist

The instructor confirmed screenshots of the system are the required evidence format.
Organize them in a `screenshots/` folder inside the ZIP. Name files clearly (e.g. `01-signin.png`, `05-request-approval.png`).

### Admin role

- [ ] Sign-in page
- [ ] Admin dashboard — four live cards (available units, pending requests, active loans, overdue loans)
- [ ] Admin dashboard — monthly issued-loan chart and equipment-category usage chart
- [ ] Equipment categories list with search
- [ ] Catalog items list (active and archived)
- [ ] Physical units list with status filter (Available / Reserved / Issued / Maintenance / Retired)
- [ ] Request queue — pending requests, searchable
- [ ] Request detail — approval/rejection form with reason field
- [ ] Approved request showing allocated units
- [ ] Rejected request with reason
- [ ] Cancelled request
- [ ] Equipment release form
- [ ] Generated borrowing slip (borrow receipt)
- [ ] Per-unit return form
- [ ] Partial return (some units returned, loan still active/overdue)
- [ ] Damaged return that opens a maintenance record
- [ ] Maintenance records list (open and closed)
- [ ] Overdue loans highlighted in the loan report
- [ ] Loan report with date filter applied
- [ ] Overdue report
- [ ] CSV export download confirmation
- [ ] Audit log with search/filter
- [ ] Settings page (loan duration and max units per item)
- [ ] Account management — user list
- [ ] Account detail with activate/deactivate action
- [ ] A form validation error example (any form showing inline field errors)

### Basic-user (portal) role

- [ ] Portal home after sign-in
- [ ] Browse equipment catalog with category/search filter
- [ ] Equipment detail page (serviceable units shown; no internal notes or maintenance details)
- [ ] Borrowing request form (1–3 items, quantities, dates, purpose)
- [ ] Submitted Pending request in own history
- [ ] Approved request showing reserved units
- [ ] Active (Issued) loan in history
- [ ] Cancelled request
- [ ] Profile / account page

### Access controls and errors

- [ ] Inactive user blocked at sign-in
- [ ] Admin redirected to `/manage/`, user redirected to `/portal/` after login
- [ ] 403 / access-denied page when a user hits a protected admin route
- [ ] Empty state (no requests yet, or no search results)

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
- [ ] T26 user needs evidence document
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
| 3   | Borrower workflow           | Browse catalog, submit a borrowing request                                                    | —         | ~1 min      |
| 4   | Request review              | Admin views queue, approves (with unit allocation), rejects with reason                       | —         | ~2 min      |
| 5   | Equipment release           | Admin releases approved request; borrowing slip generated                                     | —         | ~1 min      |
| 6   | Returns                     | Borrower view of active loan; admin records partial return, damaged return; maintenance opens | —         | ~2 min      |
| 7   | Reports and dashboard       | Live dashboard cards and charts; loan report with date filter; overdue report; CSV export     | —         | ~2 min      |
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
