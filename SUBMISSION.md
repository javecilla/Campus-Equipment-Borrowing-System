# Submission Checklist

**IT401W WEB PROGRAMMING AND FRAMEWORKS — Final Project A**  
Presentation: **Monday, October 26, 2026**, confirmed by Jerome. Exact upload/submission deadline not supplied. Retain the required ZIP filename below.

**Completion confirmed by Jerome on October 25, 2026:** all non-presentation checklist items are complete, including repository access, the final package and verification, upload/submission and separate demo credentials. Only the October 26 presentation/demo remains pending. These delivery results are coordinator-reported; this documentation review does not independently inspect the final ZIP, external submission receipt or clean-machine run. See the [completion record](handoffs/submission-completion-and-demo-readiness-10-25-2026.md).

Instructor confirmed: submit **source code + screenshots of the system** in a digital folder.
No PPT/slides needed. Bring a **printed project rubric in two copies** on demo day.

---

## GitHub access for professor review

Repository: [javecilla/Campus-Equipment-Borrowing-System](https://github.com/javecilla/Campus-Equipment-Borrowing-System). Jerome confirms public repository access and the review-branch/access checks are complete as of October 25. [DEV.md](DEV.md#repository-access-and-professor-review) owns access and evaluator setup guidance.

- [x] After changing visibility, open the repository while signed out or in a private browser window and verify README, documentation, screenshot images and the promotional video player are accessible.
- [x] Confirm the professor's review branch contains the intended submission; the default `main` branch may not include deliveries still recorded on member branches in [HANDOFF.md](HANDOFF.md).

Public repository access is source/documentation access. Running the application follows [README's local setup](README.md#run-locally); demonstration credentials still use the [separate instructor channel](#demo-credentials-submit-separately--not-in-the-zip). T30 packaging and clean-machine checks are complete per Jerome; their results are distinct from this source-document review.

## Quick status overview

| #   | Item                                                                                              | Owner                                           | Status         |
| --- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------- | -------------- |
| 1   | Application (T01–T24): all workflows implemented and tested                                       | Team                                            | Done           |
| 2 | System diagrams — editable Mermaid sources and five PDF exports (T25) | Kenneth / Ellyssa / Margareth; Jerome accepts delivery | Done locally |
| 3   | [User needs, options comparison, emerging-tech evaluation T26](docs/user-needs-evidence-guide.md) | Jerome / Alex + everyone                        | Done           |
| 4   | Professional judgment, AI/reuse/policy disclosure T27                                             | Alex coordinates + everyone                     | Done (documented assessment) |
| 5   | Team participation and individual contribution evidence T28                                       | Everyone — rotate leadership                    | Done    |
| 6   | Verified user / admin / technical guides T29                                                      | Ellyssa+Ralph / Margareth+Kenneth / Jerome+Alex | Done |
| 7   | Screenshots of the system                                                                         | Jerome with Codex assistance                    | Done (72 PNGs) |
| 8 | Submission handoff T30 | Jerome packages/uploads/invites; Alex submits | Done (Jerome-confirmed October 25) |
| 9   | Demo rehearsed; printed rubric ready T31                                                          | Everyone                                        | Not Started    |

---

## Minimum demonstration data

**All current local dataset minimums pass.** A read-only inspection of `campus_equipment` (PostgreSQL 17.5) on October 22, 2026 at 22:03 Asia/Manila verified the following. The transaction explicitly used `transaction_read_only=on`; no records, seeds or schema were changed. These are totals for this populated local database, not a promise that an empty installation already contains them.

| Required data                                                      | Minimum | Verified total | Result |
| ------------------------------------------------------------------ | ------- | -------------- | ------ |
| Categories                                                         | 3       | 12             | Pass   |
| Catalog items                                                      | 6       | 29             | Pass   |
| Physical units                                                     | 18      | 46             | Pass   |
| Admin accounts                                                     | 1       | 1              | Pass   |
| Basic-user accounts                                                | 8       | 8              | Pass   |
| Requests, all states                                               | 20      | 30             | Pass   |
| Loans that have been issued, including subsequently returned loans | 8       | 20             | Pass   |
| Maintenance records, open and closed                               | 4       | 10             | Pass   |

Required scenarios are present: **2 rejected requests, 3 cancelled requests, 1 currently partially returned request, 1 damaged return linked to maintenance and 2 overdue outstanding loans**. The nine accounts match the fictional demo roster and use `example.invalid` emails; no extra account with a different email domain was found. The [seed roster](DEV.md#seed-the-t21-demonstration-dataset) and [transaction plan](operations/demo_transaction_plan.py) define their fictional identity/history provenance.

The dashboard cards summarize current work; they are not the complete dataset counts:

| Dashboard card   | Verified value | Meaning                                                                                                                                                                    |
| ---------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Available units  | 30             | Ready to reserve. All unit states total **46 = 30 Available + 3 Reserved + 6 Issued + 5 Maintenance + 2 Retired**.                                                         |
| Pending requests | 3              | Awaiting a decision, within 30 total requests.                                                                                                                             |
| Active loans     | 4              | At least one unit remains outstanding: 3 Issued requests and 1 Partially returned request. Another 16 loans are fully returned, so **20 loans have been issued in total**. |
| Overdue loans    | 2              | A subset of those 4 active loans, past their agreed due dates. This count changes with the actual calendar date.                                                           |

**T30 package/data preparation: complete per Jerome on October 25.** His confirmation covers the final-package content and complete-data/clean-machine checks below. The repository commands retain their existing scopes: `seed_demo_data` creates accounts, `seed_demo_units` needs an existing catalog, and `seed_demo_transactions` needs the named items, serviceable stock and empty borrowing history. This status update adds no catalog/maintenance fixture or seed implementation to the checkout and does not independently reproduce the reported package result. [README seed steps](README.md#5-seed-the-demonstration-data) and [DEV runbook](DEV.md#demo-command-runbook) remain the command references.

## Part 5 and Part 6 evidence readiness

[README Part 5](README.md#part-5-business-rules-and-technical-implementation) explains each of the six business rules, their purpose, source and tests; it also maps the required Django implementation, PostgreSQL concurrency strategy and limitations. [README local setup](README.md#run-locally) gives dependency, environment, migration, seed and server commands. A working local demonstration is sufficient. The team voluntarily uses Neon for centralized records during end-to-end testing; online deployment and external integrations are not course requirements.

Use the following evidence groups when assembling the documentation/evidence folder. Documentation and delivery items are complete under the existing evidence limits and Jerome's October 25 confirmation; live presentation/Q&A remains T31.

| Evidence group        | Available references                                                                                                                                                                                                                                                                                                                                | Required completion before submission                                                                                                                                                                                                                           |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| User needs            | [Requirements](docs/SRS.md), [personas](docs/PRD.md#users-and-stakeholders), [T26 options/recommendation](docs/user-needs-evidence-guide.md), [acceptance, resolved issue and enhancement](docs/usability-acceptance.md)                                                                                                                            | Retain the limited proxy-feedback evidence honestly and the reviewed maintenance guidance indexed in DEV under T29. T26 is Done/integrated; Final-package replay is separately confirmed by Jerome on October 25. |
| System | [MTV/workflow sources and PDFs](docs/architecture.md), [database sources and PDFs](docs/db_design.md), [manual/automated acceptance](docs/manual-test-guide.md), [operational results](docs/operational-verification.md), [screenshots](docs/system-screenshots.md) | T25 Done locally on Jerome-accepted PDF exports and editable Mermaid definitions, with existing source/test evidence and recorded export limits. Package inclusion is confirmed by Jerome; Git main integration remains a separate recorded fact. Retain T27/T28 evidence and export limits. |
| Technology            | [Django implementation map](README.md#required-django-implementation), [package justifications](README.md#third-party-packages-and-assets), [dependency inventory](docs/third-party-dependencies.md), Git/handoffs/test/configuration records, [emerging-technology evaluation](docs/user-needs-evidence-guide.md#evaluate-one-emerging-technology) | Keep effectiveness, compatibility, security, user-needs analysis and conditional adoption recommendation. Retain T27 policy/account limitations; clarify actual applicable instructions without claiming formal clearance.                                                                                               |
| Professional judgment | [AI use declaration and T27 record](docs/professional-judgment-and-ethics.md#ai-use-declaration), [consumer handoff](DEV.md#t27-readiness-and-consumer-handoff), [Ralph's technical contribution](handoffs/ralph-t17-per-unit-returns-and-overdue-10-20-2026.md#ralphs-t27-technical-contribution)                                                                                       | Required topic analysis, Codex/Kiro/Gemini disclosure, asset-origin evidence and accessibility results/limits are recorded. T27 documented assessment is complete; T28 participation is complete per Jerome; presentation/Q&A remains T31. University AI policy compliance remains unverified and applicable instructions must be clarified. Institutional real-data approvals remain conditional adoption controls. |
| Team                  | [Original allocations](docs/Project-Members.txt), [current ownership](docs/tasks.md#current-ownership-and-support-responsibilities), [collaboration records](handoffs/)                                                                                                                                                                             | T28 Done per Jerome's October 23 confirmation that every member's participation requirements and the team meeting are complete, everyone agrees to the system, and full end-to-end testing is complete. See the [completion record](handoffs/t28-team-participation-completion-10-23-2026.md).                                                 |
| Communication         | [Basic-user/admin manual](docs/user-manual-guides.md), [technical setup](README.md#run-locally), [development guide](DEV.md), [demo plan](#t31--demo-day-checklist) | T29 guide scope is Done on source/screenshot review and existing technical/maintenance verification evidence; final-ZIP inclusion and complete-data replay are confirmed by Jerome on October 25. Each member still needs a presentation segment, Q&A participation and recorded feedback/actions under T31. |

The rubric assesses **all four indicators** for each of **PO-d, PO-e, PO-g, PO-h, PO-j and PO-n**, using the application, evidence, demo and Q&A. Every member needs identifiable individual evidence. T30 is Done on Jerome's October 25 delivery confirmation; the live October 26 demonstration and Q&A remain pending under T31.

## Screenshots checklist

View the [system screenshot gallery](docs/system-screenshots.md) for all 72 images displayed with short page descriptions. Source `c3fb6bb` is published on `origin/jerome`; [publication receipt](handoffs/database-switch-and-screenshot-publication-10-22-2026.md) verifies remote equality and Codex credit. User-merged PR #64 at `8dda8c9` exactly preserves the source tree; see the [integration receipt](handoffs/database-switch-and-screenshot-main-integration-10-22-2026.md).

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

**Submission delivery: Done per Jerome on October 25, 2026.** Jerome confirms that packaging/content review, complete-data and clean-machine checks, secure-drive upload/Alex access, professor-channel submission and separate credential delivery are complete. The checkmarks below record that confirmation, rather than new automated or external verification by this review. No private drive URL, receipt or credentials are copied into this public document.

- [x] Assign packaging/upload/invitation to Jerome and professor-channel submission to Alex.
- [x] Jerome creates the final ZIP and completes the content/verification checks below.
- [x] Jerome uploads the reviewed ZIP to the secure drive and invites Alex.
- [x] Alex confirms access and submits through the professor's dedicated channel.
- [x] Confirm submission receipt and delivery of demonstration credentials through the designated channel.

Presentation is **Monday, October 26, 2026**. Submission is confirmed complete; the exact upload/submission deadline and private secure-drive link are not reproduced here.

### ZIP filename (must be exact)

- [x] `IT401W_ProjectA_BSIT4EG1_Group2.zip` — filename/Section/Group confirmed by Jerome

### Required contents

- [x] All application source code (`accounts/`, `borrowing/`, `inventory/`, `operations/`, `config/`, `templates/`, `static/`)
- [x] `scripts/` required by the npm asset build, plus `LICENSE` and third-party notices
- [x] `migrations/` folders (inside each app)
- [x] `requirements.txt` and `requirements-dev.txt`
- [x] `package.json` and `package-lock.json`
- [x] `README.md` — setup instructions for a clean machine
- [x] `DEV.md` — team and technical setup guide
- [x] `manage.py`, `pyproject.toml` and `.python-version` (the actual project configuration files)
- [x] `.env.example` — configuration key template (no real values)
- [x] All existing account/unit/history seed commands and their prerequisites, following [README](README.md#5-seed-the-demonstration-data)
- [x] Reviewed fictional catalog/maintenance preparation sufficient for every minimum in the final package, confirmed by Jerome; no new fixture is added to this checkout
- [x] `screenshots/` folder — all screenshots from the checklist above
- [x] Include all five delivered T25 PDF exports and their editable Mermaid source documents; see [delivered diagrams](DEV.md#t25-readiness-and-consumer-handoff)
- [x] T26 [user-needs evidence and recommendations](docs/user-needs-evidence-guide.md) accepted record (T26 integrated through PR #63; include in the final ZIP)
- [x] T27 [professional judgment / AI/reuse disclosure document](docs/professional-judgment-and-ethics.md), with its completed written assessment; keep completed T28 participation, pending T31 presentation/Q&A, conditional real-data safeguards and unverified policy limits explicit
- [x] Include the completed [T28 team participation record](handoffs/t28-team-participation-completion-10-23-2026.md) and linked contribution records
- [x] Include the completed T29 [borrower/admin manual](docs/user-manual-guides.md) and technical setup/maintenance guidance in the final ZIP; retain linked screenshots and the documented verification limits
- [x] Documentation/evidence folder covering all six [Part 6 evidence groups](#part-5-and-part-6-evidence-readiness), including test records, limitations and maintenance guidance

These checkboxes record **final-ZIP inclusion and review confirmed by Jerome**, beyond file presence in this repository. The accepted T25–T29 evidence and its limitations remain intact. This review checks linked repository material; final-package inclusion and complete-data replay are coordinator-reported results.

### Must NOT be included

- [x] `.venv/` virtual environment
- [x] `node_modules/`
- [x] `.env.local` — contains real credentials, database URL, and secrets
- [x] Local `media/` uploads and any unreviewed/private photos; approved fictional assets require their T27 rights/provenance review before inclusion
- [x] `__pycache__/`, `.ruff_cache/`, `.playwright-cli/`
- [x] `.git/`, `.idea/`, `output/`, private database/media backups, browser profiles, session cookies, logs and test artifacts
- [x] Real identities, sensitive records and private database exports; include only reviewed fictional seed data
- [x] Any file with real passwords, tokens, or private keys

### Demo credentials (submit separately — NOT in the ZIP)

- [x] 1 admin account → submit through the instructor-designated channel
- [x] 2 basic-user accounts → submit through the instructor-designated channel
- [x] Coordinate the private seed password with those credentials; do not distribute Neon database/storage credentials to evaluators

### Final ZIP verification

- [x] Unzip on a clean machine with no project dependencies installed
- [x] Follow `README.md` Run locally steps from start to finish
- [x] Run migrations, seed demo data, start server — app loads
- [x] Reconstruct all [minimum demonstration data](#minimum-demonstration-data) without Neon access or a private database backup; verify required scenarios and record actual results/date
- [x] Both roles sign in with the demo credentials
- [x] All principal workflows operate without errors
- [x] Validate a three-item request with a failing row; confirm no partial save, ownership/role denial and POST/CSRF protection
- [x] Demonstrate competing last-unit approvals using [the isolated PostgreSQL test command](README.md#run-the-verification); only one succeeds
- [x] Inspect the actual ZIP for excluded secrets/private data and verify screenshots, diagram exports, guides and evidence links

---

## T31 — Demo day checklist

**No PPT or slides needed (instructor-confirmed). Go directly to the system demo.**

### Before the demo day

- [ ] Printed project rubric — 2 copies (bring to class)
- [ ] App running on demo machine with seeded demonstration data
- [ ] Demo credentials confirmed and accessible offline
- [ ] Each member knows their assigned segment (see table below)

### Demo segments — 12 minutes total

Fill in the Presenter column and rehearse timing before Monday, October 26, 2026.
Every member must have an identifiable part.

| #   | Segment                     | What to show                                                                                  | Presenter | Target time |
| --- | --------------------------- | --------------------------------------------------------------------------------------------- | --------- | ----------- |
| 1   | Authentication and access   | Sign-in for both roles; inactive-user block; role-based redirect                              | —         | ~1 min      |
| 2   | Equipment catalog and units | Categories, items, physical units, status counts                                              | —         | ~1 min      |
| 3   | Borrower workflow           | Browse catalog; submit a request; show invalid-row validation                                 | —         | ~1 min      |
| 4   | Request review              | Admin views queue, approves (with unit allocation), rejects with reason                       | —         | ~2 min      |
| 5   | Equipment release           | Admin releases approved request; borrowing slip generated                                     | —         | ~1 min      |
| 6   | Returns                     | Borrower view of active loan; admin records partial return, damaged return; maintenance opens | —         | ~2 min      |
| 7   | Reports and overdue         | Loan/overdue reports, filters, CSV totals and dashboard charts                                | —         | ~2 min      |
| 8   | Settings and audit          | Change loan limits; audit log entries for all recorded actions                                | —         | ~1 min      |
| 9   | Concurrency                 | Show the real PostgreSQL last-unit race result; one succeeds and one conflicts                | —         | ~1 min      |

### Q&A — 3 minutes

- [ ] Every member is prepared to explain any part of the submitted work
- [ ] Declare actual reused code, third-party assets and permitted AI assistance according to the BulSU AI Policy and instructor instructions; retain T27 evidence and be ready to explain the submitted work
- [ ] Feedback from instructor and agreed action items recorded after the session

---

## README compliance check

Required README content per [Part 5 of the course brief](docs/Project-Requirements.txt).

- [x] Project name, system overview, two roles and boundaries explained
- [x] Copyable local dependency, database, environment, migration, seed and server instructions in [Run locally](README.md#run-locally)
- [x] Explicit local/shared selector, separate media selection, restart behavior and shared-write guard documented
- [x] Migration purpose/defaults explained; committed migration/check commands documented
- [x] Separate account/unit/history seeds explained honestly, including required catalog and existing-history restrictions
- [x] Tested dependency versions referenced (`requirements.txt`, `package-lock.json`)
- [x] All six Part 5 rules mapped to implementation, purpose and tests; Django features/database limitations explained
- [x] Part 6 evidence/package/demo requirements indexed with pending tasks distinguished
- [x] Third-party packages declared and justified
- [x] Secret handling, private demo credential channel and package exclusions documented
- [x] Complete catalog/maintenance preparation and minimum-data replay from an empty local database, confirmed by Jerome
- [x] Final clean-machine startup from the actual ZIP confirmed by Jerome
- [x] Final ZIP checked for credentials, secrets and private data
- [x] Confirm section/group name matches the ZIP filename before final submission

---

_For task status and integration evidence see [docs/tasks.md](docs/tasks.md). For current readiness see [HANDOFF.md](HANDOFF.md)._
