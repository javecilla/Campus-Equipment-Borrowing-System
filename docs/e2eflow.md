# End-to-End Flow Test — Campus Equipment Borrowing System

**Date:** October 23, 2026
**Environment:** Local PostgreSQL (`campus_equipment`), `IS_LOCAL_DB_CONNECTION=True`, `MEDIA_STORAGE=local`
**Server:** `http://127.0.0.1:8000/` on the presentation machine. Use separate browser profiles against this one instance/database; independent local databases do not share transactions.

**Reviewed:** October 23, 2026, 21:55 Asia/Manila, in a local transaction with `transaction_read_only=on`.
Presentation is Monday, October 26. Recheck settings and stock before use. Checkmarks below describe **expected outcomes**;
the result table is unfilled, and no workflow was executed during this review. Jerome's earlier team-testing confirmation
is retained in the [T28 record](../handoffs/t28-team-participation-completion-10-23-2026.md).
The [canonical manual guide](manual-test-guide.md) and [HTTP contract](api_spec.md) define full coverage and exact fields.

## Verified local starting data

| Check | Read-only result |
| --- | --- |
| Accounts | Andrea is ADMIN; Daniel, Rafael and Alyssa are BASIC_USER; all active |
| New-request limits | 7 calendar days; 3 units per item |
| Dataset | 12 categories, 29 items, 46 units, 30 requests, 20 loans, 10 maintenance records |
| Photos | All 23 referenced uploads exist under local media; HTTP delivery was not rerun |
| Available stock | HDMI Projector 1; DSLR Camera 1; Wireless Keyboard & Mouse Combo 1; Soldering Iron Station 1; Portable PA Speaker 1; Digital Multimeter 2; LCD Classroom Projector 3 |
| Unavailable original examples | Adjustable Tripod and Lenovo ThinkPad Laptop have 0 available units; use replacements below |
| Overdue examples on October 23 | Loan #27 / request #42 (Miguel Santos), loan #28 / request #43 (Sofia Reyes); both due October 21, one unit outstanding each |
| Approved examples | Request #51 due October 25, #52 due October 26; neither is expired at review |
| Purpose markers | No requests starting `E2E-` at review; choose unique markers for a later run |

## Personas

| Member | Account | Role | Username |
| --- | --- | --- | --- |
| Jerome | Andrea Mendoza | ADMIN | `andrea.mendoza` |
| Alex | Daniel Navarro | BASIC_USER | `daniel.navarro` |
| Kenneth | Rafael Ramos | BASIC_USER | `rafael.ramos` |
| Ellie | Alyssa Flores | BASIC_USER | `alyssa.flores` |

> Password for all accounts: use the `SEED_ACCOUNT_PASSWORD` Jerome sent by email.

---

## Before You Start

1. On the presentation machine, use private local settings:
   ```dotenv
   IS_LOCAL_DB_CONNECTION=True
   MEDIA_STORAGE=local
   ```
   Confirm `DB_*` points to local PostgreSQL. Retain the existing dataset and media. Start one server:
   ```powershell
   .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
   ```
2. Confirm the presentation database is active:
   ```powershell
   .\.venv\Scripts\python.exe manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('DB:', connection.settings_dict['NAME'])"
   ```
   Expected: `DB: campus_equipment`. Stop and correct the connection if it differs.

3. Use a distinct **purpose marker** on every request you submit (e.g. `E2E-01-Alex`) so teammates can identify your records in the admin view.

4. Use separate browser profiles on the presentation machine for the personas. Coordinate approvals, issues and returns;
   these manual steps persist local changes. Record actual request/loan IDs and assets. The reviewer did not execute them.

---

## Flow 1 — Login and Role Isolation

**Exercises login/active-session and role-isolation portions of SRS Scenarios 1 and 2.** Registration and forged-role-field
cases remain in the canonical manual guide and existing automated acceptance tests.

### Step 1.1 — Everyone logs in

| Member | Action | Expected |
| --- | --- | --- |
| Jerome | Go to `/accounts/login/`, enter `andrea.mendoza` + password | Redirected to `/manage/` (admin dashboard) |
| Alex | Go to `/accounts/login/`, enter `daniel.navarro` + password | Redirected to `/portal/` |
| Kenneth | Go to `/accounts/login/`, enter `rafael.ramos` + password | Redirected to `/portal/` |
| Ellie | Go to `/accounts/login/`, enter `alyssa.flores` + password | Redirected to `/portal/` |

### Step 1.2 — Role isolation checks

| Member | Action | Expected |
| --- | --- | --- |
| Alex | While logged in, visit `/manage/` | ✅ 403 Forbidden |
| Alex | Visit `/manage/accounts/` | ✅ 403 Forbidden |
| Jerome | While logged in, visit `/portal/equipment/` | ✅ 403 Forbidden |
| Jerome | Visit `/portal/requests/new/` | ✅ 403 Forbidden |

### Step 1.3 — Deactivate and block an active session (Jerome + Alex)

1. **Alex** stays on `/portal/equipment/` — do not navigate away yet.
2. **Jerome** goes to `/manage/accounts/`, finds **Daniel Navarro**, clicks **Deactivate**, and confirms.
3. **Alex** refreshes the page.
   - ✅ The current request returns **403** and the inactive session is cleared.
   - Open `/accounts/login/` for the next step; the inactive-login message appears after a rejected login attempt.
4. **Alex** tries to log in again with the correct password.
   - ✅ Login is blocked with the deactivation message.
5. **Jerome** reactivates Daniel Navarro: go to Daniel's detail page → **Activate** → confirm.
6. **Alex** logs in again successfully.
   - ✅ Redirected to `/portal/`.

---

## Flow 2 — Browse Equipment Catalog

**Covers SRS Scenario 11 (partial)**

| Member | Action | Expected |
| --- | --- | --- |
| Alex, Kenneth, Ellie | Go to `/portal/equipment/` | ✅ Active catalog items appear with available/serviceable counts |
| Alex | Search `projector` | ✅ Only projector-related items appear |
| Kenneth | Search `zzznomatch` | ✅ Empty state shown — no blank or error page |
| Ellie | Filter by a category (e.g. Photography & Video) | ✅ Only items in that category appear |
| Alex | Click any item with a photo | ✅ Photo loads from the presentation machine's local media |

---

## Flow 3 — Submit Borrow Requests

**Covers SRS Scenario 3**

### Step 3.1 — Alex submits a valid single-item request

1. **Alex** goes to `/portal/requests/new/`
2. Fill in:
   - Purpose: `E2E-01-Alex presentation`
   - Desired return date: **tomorrow's date** (or any date within 7 days from today, strictly after today)
   - Row 1 Item: **HDMI Projector**, Quantity: `1`
   - Rows 2 and 3: leave blank
3. Submit.
   - ✅ Redirected to `/portal/requests/` with a confirmation and request number.
   - ✅ **Jerome** checks `/manage/accounts/` → Daniel Navarro's history — the new request appears as **Pending**.

### Step 3.2 — Kenneth submits a multi-item request

1. **Kenneth** goes to `/portal/requests/new/`
2. Fill in:
   - Purpose: `E2E-02-Kenneth camera setup`
   - Desired return date: pick a date within 7 days
   - Row 1: **DSLR Camera (Canon EOS)**, Quantity: `1`
   - Row 2: **Wireless Keyboard & Mouse Combo**, Quantity: `1`
   - Row 3: **Soldering Iron Station**, Quantity: `1`
3. Submit.
   - ✅ One request with all three valid items. Verify in `/portal/requests/`.

### Step 3.3 — Ellie submits a request

1. **Ellie** goes to `/portal/requests/new/`
2. Fill in:
   - Purpose: `E2E-03-Ellie laptop`
   - Desired return date: pick a date within 7 days
   - Row 1: **Student Loan Laptop**, Quantity: `1` (three Available units in the local snapshot)
   - Rows 2 and 3: leave blank
3. Submit.
   - ✅ Request appears as Pending.

### Step 3.4 — Atomic rollback: two valid rows + one invalid row

**Coordinator: Alex**

1. **Alex** goes to `/portal/requests/new/`
2. Fill in:
   - Purpose: `E2E-04-Alex atomic test`
   - Desired return date: valid date
   - Row 1: **DSLR Camera (Canon EOS)**, Quantity: `1` — valid
   - Row 2: **Wireless Keyboard & Mouse Combo**, Quantity: `1` — valid
   - Row 3: **Digital Multimeter**, Quantity: `5` — **INVALID** (max is 3)
3. To exercise server validation, remove only the quantity input's client-side `max` in browser developer tools, then
   submit the actual CSRF-protected form. Browser-only rejection does not prove server rollback.
   - ✅ Row 3 quantity error shown. Form stays open.
   - ✅ **No request is saved** — Alex's request list does not contain `E2E-04-Alex atomic test`.
   - ✅ Jerome verifies in `/manage/accounts/` → Daniel Navarro: no `E2E-04` record.

---

## Flow 4 — Admin Approves and Rejects Requests

**Covers SRS Scenario 4 & 5**

### Step 4.1 — Jerome approves Alex's request (E2E-01)

1. **Jerome** goes to `/manage/requests/`, finds Alex's `E2E-01-Alex presentation` request (Pending).
2. Reviews the items and clicks **Approve**.
3. Enter a nonblank **Reason** (`id=decision-reason`), e.g. `E2E approved for presentation`, and confirm
   (`data-testid=request-decision-submit`). The service automatically allocates available units; there is no unit-picker.
   - ✅ Request status changes to **Approved**.
   - ✅ The allocated units' status changes to **Reserved**.
   - ✅ **Alex** refreshes `/portal/requests/` — `E2E-01` now shows **Approved**.

### Step 4.2 — Jerome rejects Kenneth's request (E2E-02)

1. **Jerome** finds Kenneth's `E2E-02-Kenneth camera setup` request.
2. Clicks **Reject**, enters a reason (e.g. `Cameras are undergoing inspection`), confirms.
   - ✅ Request status changes to **Rejected**.
   - ✅ **Kenneth** refreshes `/portal/requests/` — `E2E-02` shows **Rejected** with the reason.
   - ✅ Pending rejection creates no reservations and changes no units. The reason and decision are audited.

### Step 4.3 — Cancel an approved request, verify units freed

1. **Ellie's** `E2E-03-Ellie laptop` should be Pending. **Jerome** approves it with a written reason; a Student Loan Laptop unit is allocated automatically.
2. **Ellie** goes to `/portal/requests/`, opens `E2E-03`, and clicks **Cancel**.
   - ✅ Request status changes to **Cancelled**.
   - ✅ **Jerome** checks `/manage/units/` — the laptop unit that was Reserved is now **Available** again.
3. After Step 5.1, **Alex** opens `/portal/requests/<E2E-01-request-id>/cancel/` for his own Issued request:
   - ✅ **409 Conflict**; no cancellation form or change. Administrators have no borrower-cancellation route.

### Step 4.4 — Competing approvals for the last available unit

> This requires two Pending requests that both want the same item with only one unit left. Coordinate with Jerome.

1. **Alex** submits a new request: `E2E-05-Alex last unit`, Row 1: **Portable PA Speaker**, Quantity: `1`.
2. **Kenneth** submits a new request: `E2E-06-Kenneth last unit`, Row 1: **Portable PA Speaker**, Quantity: `1`.
3. **Jerome** opens both approval forms in separate profiles/tabs, enters a reason in each, and submits as closely together
   as practical. Allocation is automatic; both compete for the only Available speaker.
   - ✅ Exactly **one** succeeds — the other fails with a conflict message (no available unit).
   - ✅ The speaker unit is Reserved for the successful request only.
   - ✅ No duplicate reservation or corrupted allocation exists.

Record actual timing/responses. Manual clicks exercise contention but do not establish synchronized concurrency.
The [isolated PostgreSQL tests](../DEV.md#isolated-tests-while-using-neon) provide controlled race verification.

---

## Flow 5 — Issue Equipment (Release / Loan)

**Covers SRS Scenario 6**

**Order:** perform Step 5.5 on E2E-01 before Step 5.1; date revision is blocked after issue.

### Step 5.1 — Jerome releases Alex's approved request

1. **Jerome** finds `E2E-01-Alex presentation` (Approved) in `/manage/requests/`.
2. Clicks **Release / Issue**.
   - ✅ Request status becomes **Issued** (`ISSUED`); the separate loan badge is **Active** until overdue or closed.
   - ✅ Allocated units' status changes to **Issued**.
   - ✅ **Alex** sees the request as Issued and the linked Active loan/due date in `/portal/loans/` or request detail.

### Step 5.2 — Print borrowing slip

1. **Jerome** opens the active loan for `E2E-01` and clicks **Print Slip** (or **View Slip**).
   - ✅ Slip shows borrower name, equipment list, issue date, and due date correctly.
   - ✅ `/manage/loans/<loan_id>/slip/` is print-ready HTML with native print controls; browser Print can save a PDF.

### Step 5.3 — Reject repeat issue

1. **Jerome** tries to issue `E2E-01` again (navigate directly to the release URL or click release if still shown).
   - ✅ Rejected — loan is already active; no duplicate loan created.

### Step 5.4 — Reject issue after due date (if applicable)

> No expired Approved request exists on the October 23 snapshot: #51 is due October 25, #52 October 26.
> Record **Not run** unless one is actually expired when presenting. Recheck status/date; do not backdate records or change the clock.

1. **Jerome** finds an **Approved** request whose desired return date is in the past.
2. Attempts to issue it.
   - ✅ Issue is rejected — cannot release after the due date has passed.

### Step 5.5 — Audited due-date revision before issue

1. **Jerome** uses **Approved E2E-01**, before Step 5.1. Its original requested date should be tomorrow.
2. Open `/manage/requests/<request_id>/due-date/`. Set **Agreed due date** to the following day and a nonblank reason.
   It must differ, be on/after today, and remain within the original submission-date + 7-day snapshot.
   The original desired due date remains unchanged.
   - ✅ Revision saved. Audit log records the change with Jerome's name and timestamp.
3. Continue with Step 5.1.
   - ✅ Loan created with the revised agreed due date.

---

## Flow 6 — Return Equipment

**Covers SRS Scenario 7**

### Step 6.1 — Partial return (one of several units)

> Prepare a separate three-unit loan: **Alex** submits `E2E-07-Alex return sequence`, **LCD Classroom Projector**,
> quantity `3`, with a valid due date. **Jerome** approves with a written reason and releases it. All three units are Available
> in the reviewed local snapshot. Record the new loan ID. Keep Kenneth's E2E-02 Rejected; do not reuse it for this sequence.

1. **Jerome** goes to `/manage/loans/` (or the active loan detail), selects one unit to return.
2. Marks condition: **GOOD**, submits.
   - ✅ That unit's status changes to **Available**.
   - ✅ Request becomes **Partially returned**; loan badge stays **Active** while outstanding and not overdue.
   - ✅ Audit entry created.

### Step 6.2 — Reject duplicate return

1. **Jerome** tries to return the same unit again.
   - ✅ Rejected — unit already returned; no duplicate record.

### Step 6.3 — Damaged return

1. **Jerome** selects the second unit from the same loan, marks condition: **DAMAGED**, enters a problem description: `E2E damaged return test`, submits.
   - ✅ Unit status changes to **Maintenance**.
   - ✅ A maintenance record is automatically opened for this unit.
   - ✅ Audit entries: `UNIT_RETURNED` + `MAINTENANCE_OPENED`. Two of three units are returned; one is still outstanding.

### Step 6.4 — Final return closes the loan

1. **Jerome** returns all remaining units from the same loan.
   - ✅ Request becomes **Returned**; loan badge becomes **Closed** after the third/final unit is returned.
   - ✅ No units remain Issued on that loan.
   - ✅ **Alex** sees the request as Returned and the loan as Closed in `/portal/loans/`.

---

## Flow 7 — Equipment Maintenance

**Covers SRS Scenario 8**

### Step 7.1 — Reject maintenance on Reserved/Issued unit

1. **Jerome** finds a unit currently in **Reserved** or **Issued** status (from an active loan).
2. Open `/manage/maintenance/new/`; the unit must be absent from eligible choices. Inspect its unit detail separately.
   - ✅ Reserved/Issued units are ineligible; only Available units with no open maintenance can be selected.
   - A server-side tampered-ID rejection is a separate existing integration-test case; hidden choices alone do not prove it.

### Step 7.2 — Complete a repair

1. **Jerome** finds a unit in **Maintenance** status (e.g. the damaged-return unit from Step 6.3).
2. Open `/manage/maintenance/<maintenance_id>/close/`. Set **Outcome = Available**, **Repaired condition = Good**,
   and **Action taken / Resolution = E2E repair completed**. Submit (`data-testid=submit-maintenance-close`).
   Maintenance status becomes **Closed**, not Completed.
   - ✅ Unit status changes back to **Available**.
   - ✅ Maintenance record is closed.
   - ✅ Audit entry created.

### Step 7.3 — Retire a unit

1. Use already-Open maintenance record **#3**, unit **CEL-LAB-VCL-001** (Vernier Caliper), if still Open.
2. On its close form, choose **Outcome = Retired** and a nonblank action, e.g. `E2E decommissioned after inspection`.
   Confirm this local presentation-data change is intended: retirement has no restore workflow. Otherwise record **Not run**.
   - ✅ Unit status changes to **Retired**.
   - ✅ Unit no longer counts in Available or Serviceable totals.

### Step 7.4 — Inventory count reconciliation

After the steps above, **Jerome** checks `/manage/units/` counts:
- Available, Serviceable, In Maintenance, Reserved, Issued, Retired totals are consistent with actual unit statuses.
- ✅ No phantom counts — every count reflects real unit states.

---

## Flow 8 — Overdue Behavior

**Covers SRS Scenario 9**

Use **loan #27 / request #42**, `miguel.santos`, due **October 21**, one unit outstanding in the local snapshot.
For this flow, **Alex's separate browser profile** signs out of Daniel and signs in as fictional `miguel.santos`, an active
BASIC_USER, using the privately supplied seed password. Return to Daniel afterward.

1. **Jerome** opens `/manage/reports/overdue/` and verifies loan #27 appears. `/manage/loans/` accepts loan-ID/username
   search; it has no status filter.
2. **Alex as Miguel** opens `/portal/loans/27/` and verifies the Overdue badge/outstanding unit.
   A new E2E-01 request due tomorrow is not overdue yet.
3. If intended for the local demonstration dataset, **Jerome** returns loan #27's remaining unit through its return form.
   - ✅ Loan #27 becomes Closed and disappears from the overdue report; its request becomes Returned.
   - ✅ Other outstanding overdue loans remain; the report need not be empty.
4. Recheck dates on presentation day. Before/on/after-date boundaries require the existing isolated tests;
   do not claim all boundaries verified by this one example or change the workstation clock.

---

## Flow 9 — Dashboard, Reports, and CSV Export

**Covers SRS Scenario 10**

### Step 9.1 — Dashboard reflects live changes

1. **Jerome** opens `/manage/` (admin dashboard).
   - ✅ Loan counts, overdue counts, and pending request counts match what was just worked through.
   - ✅ Charts (Chart.js) display realistic data — not zeros or static values.

### Step 9.2 — Filtered loan report

1. **Jerome** opens `/manage/reports/loans/`.
2. Set **Issue date from** and **Issue date through** to the actual date the E2E loans were released.
   - ✅ Only loans with inclusive stored issue dates inside the range appear; compare actual loan IDs and totals.
3. Open `/manage/reports/overdue/` for overdue loans, with the same available date fields.
   - Borrower/status dropdown filters are not implemented on reports. Clear date filters to include older overdue loans.

### Step 9.3 — CSV export

1. **Jerome** exports the current filtered report as CSV.
   - ✅ `/manage/reports/loans/export/` exports all rows matching the issue-date filters, including other borrowers,
     all pages and totals. The overdue export additionally has Overdue days.
   - ✅ Compare loan/request IDs, borrower, purpose, dates, request/loan statuses, issued/returned/outstanding counts
     and totals. Daniel's new E2E loans appear if their issue dates match.

### Step 9.4 — Basic users cannot access reports

1. **Alex** visits `/manage/reports/loans/`, `/manage/reports/overdue/` and their `/export/` routes directly.
   `/manage/reports/` itself is not a registered report page.
   - ✅ 403 Forbidden.

---

## Flow 10 — Archive and Settings

**Covers SRS Scenario 11**

### Step 10.1 — Change max loan duration

1. **Jerome** goes to `/manage/settings/`.
2. Changes **Max loan duration** to `5` days, saves.
   - ✅ Audit log entry created.
3. **Alex** submits a new request with a return date 7 days from today.
   For the server check, remove only the date input's client-side `max` in developer tools before submitting the normal form.
   - ✅ Rejected — new limit is 5 days; 7-day date is now beyond the maximum.
4. **Jerome** restores the setting to `7` days after the test.

### Step 10.2 — Archive a catalog item

1. **Jerome** goes to `/manage/items/`, picks an item with no active loans, clicks **Archive**, confirms.
   - ✅ Item disappears from `/portal/equipment/` (Alex verifies).
   - ✅ Visiting the item's portal URL directly returns 404.

### Step 10.3 — Archive blocks new requests for that item

1. **Alex** tries to submit a new request and looks for the archived item in the equipment dropdown.
   - ✅ Archived item is not in the list.

### Step 10.4 — Restore the archived item

1. **Jerome** restores the archived item.
   - ✅ Item reappears in `/portal/equipment/`.

---

## Flow 11 — Audit Log Verification

**Throughout all flows above**, verify:

1. **Jerome** goes to `/manage/audit/`.
   - ✅ Entries exist for: account deactivation/reactivation, request approval/rejection, loan issue, unit return, maintenance open/close, settings change, archive/restore.
2. Each entry shows: actor name, timestamp, action, and target record.
3. **Jerome** uses **Record reference** with `borrowing.Loan#<actual_loan_id>` for release,
   `borrowing.BorrowRequest#<actual_request_id>` for decisions and actual return/maintenance references for those actions.
   This searches model/ID references, not borrower names.
   - ✅ Matching entries returned.
4. **Alex** visits `/manage/audit/`.
   - ✅ 403 Forbidden.

---

## Flow 12 — Cross-User Access Checks

**Covers SRS Scenario 2**

| Member | Action | Expected |
| --- | --- | --- |
| Alex | Visit `/portal/requests/<kenneth_request_id>/` (Kenneth's request ID) | ✅ 404; owner-scoped lookup |
| Kenneth | Visit `/portal/loans/<alex_loan_id>/` | ✅ 404 |
| Ellie | Open `/portal/requests/<another_owner_request_id>/cancel/` | ✅ 404; no confirmation form |
| Alex | Try to access `/manage/units/` | ✅ 403 |
| Alex | Try to access `/manage/audit/` | ✅ 403 |

---

## Pass/Fail Record

Blank Result cells mean **Not run / not recorded** for this guide. Expected checkmarks above do not fill them.
Record actual date, database, request/loan IDs and observations. ✅ = Pass, ❌ = Fail, ⬜ = Not run.

| Flow | Step | Member(s) | Result | Notes |
| --- | --- | --- | --- | --- |
| 1 | 1.1 Login all | All | | |
| 1 | 1.2 Role isolation | Alex, Jerome | | |
| 1 | 1.3 Deactivate + block session | Jerome, Alex | | |
| 2 | Catalog browse | Alex, Kenneth, Ellie | | |
| 3 | 3.1 Single-item request | Alex | | |
| 3 | 3.2 Multi-item request | Kenneth | | |
| 3 | 3.3 Single request | Ellie | | |
| 3 | 3.4 Atomic rollback | Alex | | |
| 4 | 4.1 Approve E2E-01 | Jerome | | |
| 4 | 4.2 Reject E2E-02 | Jerome | | |
| 4 | 4.3 Cancel approved request | Ellie, Jerome | | |
| 4 | 4.4 Competing approvals | Jerome | | |
| 5 | 5.1 Issue/release | Jerome | | |
| 5 | 5.2 Print slip | Jerome | | |
| 5 | 5.3 Reject repeat issue | Jerome | | |
| 5 | 5.4 Expired issue (requires expired Approved request) | Jerome | | |
| 5 | 5.5 Due date revision (before 5.1) | Jerome | | |
| 6 | 6.1 Partial return | Jerome | | |
| 6 | 6.2 Reject duplicate return | Jerome | | |
| 6 | 6.3 Damaged return | Jerome | | |
| 6 | 6.4 Final return closes loan | Jerome | | |
| 7 | 7.1 Reject maintenance on active unit | Jerome | | |
| 7 | 7.2 Complete repair | Jerome | | |
| 7 | 7.3 Retire a unit | Jerome | | |
| 7 | 7.4 Inventory counts | Jerome | | |
| 8 | Overdue detection + clear | Jerome, Alex | | |
| 9 | 9.1 Dashboard live counts | Jerome | | |
| 9 | 9.2 Filtered report | Jerome | | |
| 9 | 9.3 CSV export | Jerome | | |
| 9 | 9.4 Basic user blocked from reports | Alex | | |
| 10 | 10.1 Settings change + reject | Jerome, Alex | | |
| 10 | 10.2–10.4 Archive + restore | Jerome, Alex | | |
| 11 | Audit log entries | Jerome, Alex | | |
| 12 | Cross-user access | Alex, Kenneth, Ellie | | |

---

## Notes

- **Local database**: use one presentation machine/database and separate browser profiles; independent local PostgreSQL instances do not share these transactions. No Neon connection is needed.
- **Purpose markers**: always include your name/number in the Purpose field (e.g. `E2E-01-Alex`) so records can be identified in the admin view.
- **Restore test data**: after archive/settings tests, restore the original values so the system remains usable for remaining flows.
- **Photos**: keep `MEDIA_STORAGE=local`; all 23 referenced uploads were found locally during review. Database paths alone do not copy image bytes to another machine; follow [local media guidance](../DEV.md#equipment-photos-and-local-media).
- **Preserve the dataset**: no migration, seed, flush or cleanup is needed for this review. Keep the populated presentation database. Shared Neon restrictions remain in [AGENTS.md](../AGENTS.md#shared-database-and-media-safety).
