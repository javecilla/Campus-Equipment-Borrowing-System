# Manual Browser Testing Guide

## Purpose and scope

Kenneth, Margareth and Ellyssa now focus on validation, documentation and manual testing under the [current responsibilities](tasks.md#current-ownership-and-support-responsibilities). Run available cases and record actual outcomes; unimplemented flows remain Not run. Report T15/T16 defects to Jerome, T17/T20 defects to Ralph and T18/T19 defects to Alex. Diagram preparation stays on standby until Jerome's go signal after system completion, subject to T25 prerequisites.

This guide covers T01-T14/T16 integrated in main, including T13 query fixes through PR #35 and T14 concurrency proof through PR #37 at `5381c83` ([Module 13](#module-13--postgresql-competing-approvals-t14)). T15 is integrated through PR #42 at `744bc39`; [Module 15](#module-15--release-due-date-revision-and-borrowing-slip-t15) records release/date/slip checks. T17 returns are integrated through PR #43 at `55899d0`, source `bd62ed7`; [Module 16](#module-16--per-unit-returns-and-overdue-t17) records the isolated browser checks. T19 reports are integrated through PR #49 at `e8f2a19`, source `16e1d4c`; [Module 18](#module-18--administrator-loan-and-overdue-reporting-t19) records the exact pending browser cases. Broader T12/T13/T16 browser results remain Not run until supplied.

The shared M3 UI refresh (UI-09) is integrated through PR #39 at `a35e0f1`, source `043822e`, preserved in main `866eb7e`; [Module 14](#module-14--shared-m3-layout-and-controls-ui-09) records its actual layout/accessibility smoke checks separately from the workflow cases below.

For the current borrower checks, go directly to [Module 9: request submission](#module-9--borrower-request-submission-t11) or [Module 10: request and loan tracking](#module-10--borrower-request-and-loan-tracking-t12). For equipment maintenance and reconciliation, see [Module 11: equipment maintenance](#module-11--equipment-maintenance-and-inventory-reconciliation-t16). Use the [result record](#recording-manual-results) to report what actually happened.

For automated tests, see [Running the automated suite](#running-the-automated-test-suite) at the bottom.

## Prerequisites

### Server must be running

Follow [DEV startup](../DEV.md#everyday-startup) and rebuild assets after pulling template changes with `npm.cmd run build`. T11/T12/T13/T15/T16 add no migration or dependency. Keep the existing local database and test records.

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Visit `http://127.0.0.1:8000/`. Anonymous visitors go to login; signed-in accounts go to their role home.

### Test accounts

For the populated T21 local dataset, use the [current nine-account roster](../DEV.md#seed-the-t21-demonstration-dataset). The optional AUTH-01 pair below is a separate development seed and was removed from the current local database during the authorized cleanup.

The seed command defines these fictional accounts; this guide does not assert that they currently exist in every local database:

| Username | Role | Active |
| --- | --- | --- |
| `auth_demo_admin` | ADMIN | Yes |
| `auth_demo_user` | BASIC_USER | Yes |

Seeded accounts use the private `SEED_ACCOUNT_PASSWORD` chosen when they were created; registered accounts have their own passwords. Changing the environment value does not change an existing password. See [DEV.md — Seed authentication test accounts](../DEV.md#seed-authentication-test-accounts) if you need to re-seed or reset.

To create a fresh admin for testing:
```powershell
.\.venv\Scripts\python.exe manage.py create_admin
```

### System settings defaults

| Setting | Default |
| --- | --- |
| Max loan duration | 7 calendar days |
| Max quantity per item | 3 units |

Verify or change these at `/manage/settings/` once logged in as an admin.

Record the settings currently displayed before changing them. The values above are initial defaults, not a claim about the current local database. Restore the original values after testing. Use fictional data and a distinct purpose marker for each request, such as `T11-manual-001`, so repeated runs can be distinguished.

### Notation used in this guide

- ✅ **Pass** — the system behaves correctly
- ❌ **Fail** — the system does not behave as expected; record it as a bug
- **Bold text** refers to a form field name or page element
- `code text` refers to a URL path or typed input value

---

## Module 1 — Authentication (T04, AUTH-01, AUTH-02)

**Base URL:** `/accounts/login/`

### 1.1 Login with username

1. Go to `/accounts/login/`
2. Enter `auth_demo_admin` and the seed password
3. Submit

✅ Redirected to `/manage/` (admin dashboard placeholder)

### 1.2 Login with email (case-insensitive)

1. Log out first, go to `/accounts/login/`
2. Enter the admin's email address in ALL CAPS (e.g. `AUTH-ADMIN@EXAMPLE.INVALID` for the seed account, unless its email was changed)
3. Submit

✅ Still logs in — email matching is case-insensitive (AUTH-02)

### 1.3 Login as basic user

1. Go to `/accounts/login/`
2. Enter `auth_demo_user` and the seed password

✅ Redirected to `/portal/` (not `/manage/`)

### 1.4 Wrong credentials

1. Enter `auth_demo_admin` with a wrong password

✅ Stays on login page, shows a generic error (no hint whether username or password was wrong)

### 1.5 Role isolation after login

1. Log in as `auth_demo_user` (BASIC_USER)
2. Manually visit `/manage/`

✅ 403 Forbidden — basic users cannot access admin pages

1. Log in as `auth_demo_admin` (ADMIN)
2. Manually visit `/portal/`

✅ 403 Forbidden — admins cannot access portal pages

### 1.6 Logout

1. Log in as any account
2. Open the account dropdown and click **Log out**
3. The existing CSRF-protected POST signs out immediately; there is no separate confirmation page

✅ Session cleared, redirected to `/accounts/login/`

### 1.7 Block an inactive account (requires creating one first)

**Integration:** Alex's fix is merged through PR #46 at `c052900`; issue #18 is closed as completed. The combined source passed 304 PostgreSQL tests and the isolated browser cases below.

Prerequisite: a fictional ADMIN and BASIC_USER with known private passwords. The October 20, 2026 integration-review read-only lookup found neither earlier example `localadmin` nor the chosen borrower's username; those names are not current setup evidence. Substitute your chosen fictional borrower in the steps below. No live account was changed during review.

1. Log in as the administrator, go to `/manage/accounts/`, find the chosen fictional borrower, choose **Deactivate**, and confirm.
2. Log out, then submit `/accounts/login/` with **Username or email** the chosen borrower's username and its correct password.

✅ Login remains blocked on the sign-in page and displays **Your account has been deactivated. Please contact an administrator.** Visiting `/portal/` still redirects to login because no authenticated session was created.

3. Submit the deactivated account's email in uppercase with the same correct password.

✅ The same deactivated-account message appears; email matching remains case-insensitive and no session is created.

4. Submit the chosen borrower's username with an incorrect password, then submit an unknown identifier such as `missing@example.invalid`.

✅ Each attempt displays only **Invalid username/email or password.** The page does not disclose whether either identifier exists, and no session is created.

5. In the administrator session, reactivate the chosen fictional borrower. Submit its unchanged username and password again.

✅ Login succeeds and redirects to `/portal/`, confirming the earlier block was caused by deactivation.

6. To test an existing session, first keep an authenticated borrower session open in a separate browser profile or private window, then deactivate that account from the administrator session and reload `/portal/equipment/` in the borrower window.

✅ The first protected request is denied with 403 and the existing session is invalidated. Subsequent anonymous requests redirect to login.

**Restore the account before continuing:** log in as admin and reactivate the fictional borrower. Record the browser/version and actual outcome separately; these steps are expected behavior, not an automated-test result.

---

## Module 2 — Borrower Registration (T09)

**Base URL:** `/accounts/register/`

**Executed integration review, October 20, 2026 Asia/Manila:** Chromium 153.0.8010.12 passed these cases using isolated `fictional_admin` and `fictional_borrower` / `borrower@example.invalid` fixtures. Correct username and uppercase email displayed the inactive message; wrong/unknown credentials stayed generic; no session was created; an existing deactivated session received 403; reactivation restored login with the same password. The 320px page had no horizontal overflow or JavaScript errors. Browser/server closed and disposable database removed. These fixtures are not live development accounts.

### 2.1 Successful registration

1. Go to `/accounts/register/` while not logged in
2. Fill in: **Username** `testborrower1`, **First name** `Test`, **Last name** `Borrower`, **Email** `testborrower1@example.com`, **Password** (twice)
3. **Contact number** is optional — leave it blank
4. Submit

✅ Redirected to `/accounts/login/` with a success message "Your account has been created successfully. You may now sign in."

No auto-login — the borrower must sign in separately.

### 2.2 Duplicate username

1. Register again with the same username `testborrower1`

✅ Form stays open, username field shows a uniqueness error. No duplicate account created.

### 2.3 Duplicate email

1. Register with a different username but the same email `testborrower1@example.com`

✅ Email collision rejected — error on the email field.

### 2.4 Invalid username characters

1. Try username `test borrower` (with a space)
2. Try username `test/borrower` (with a slash)

✅ Both rejected with a validation error on the username field. No User, Profile, or audit record created.

### 2.5 Mismatched passwords

1. Enter different values in **Password** and **Confirm password**

✅ Error on the confirm field. No account created.

### 2.6 Forged role field

Complete an otherwise valid registration form, then use browser DevTools to add an extra hidden field `role=ADMIN` before normal submission. Keep the existing CSRF field intact.

✅ The account is still created as `BASIC_USER`. The role field is ignored — it cannot be set through registration.

### 2.7 Authenticated user tries to visit registration

1. While logged in as any account, visit `/accounts/register/`

✅ Redirected to their role home — no access to registration while signed in.

---

## Module 3 — Borrower Profile (T09)

**Base URL:** `/portal/profile/`\
**Login required:** active BASIC_USER

### 3.1 View own profile

1. Log in as `auth_demo_user`
2. Go to `/portal/profile/`

✅ Shows own first name, last name, email, contact number. No role field, no activation toggle, no other users' data.

### 3.2 Edit allowed fields

1. Change **First name** to a different value and submit

✅ Saved and redirected back to `/portal/profile/` with a success message.

### 3.3 Edit blocked fields via forged POST

Complete an otherwise valid profile form, then add `role=ADMIN` or `username=something_else` through DevTools before submitting with the existing CSRF token.

✅ Role and username remain unchanged — allowlist blocks these fields.

### 3.4 Admin profile is read-only

1. Log in as `auth_demo_admin`
2. Go to `/manage/profile/`

✅ Profile displays but the page has no edit form — admin profiles are view-only.

---

## Module 4 — Admin Account Management (T05)

**Base URL:** `/manage/accounts/`\
**Login required:** active ADMIN

### 4.1 List all basic users

1. Log in as admin, go to `/manage/accounts/`

✅ Table lists all BASIC_USER accounts (not admins). Each row shows username, name, email, active status.

### 4.2 Search

1. Type part of a username or name in the search box, submit

✅ Table filters to matching accounts only.

### 4.3 Filter by active status

1. Select **Active: Yes** or **Active: No** from the filter dropdown

✅ List shows only matching accounts.

### 4.4 Deactivate an account

1. Click on `testborrower1` → **Deactivate** → confirm on the confirmation page

✅ Account status changes to inactive. Success message shown. Audit entry created (verify in `/manage/audit/`).

### 4.5 Activate an account

1. From the detail page of the deactivated account → **Activate** → confirm

✅ Account re-activated. Audit entry created.

### 4.6 Repeated action conflict

1. Try to activate an already-active account (navigate directly to the activate URL)

✅ 409 Conflict — clear error message, no duplicate write.

### 4.7 View account history

1. Click into any basic-user detail page

✅ Shows that account's profile and stored request/loan history. T11 submissions appear here with request ID, purpose, items, Pending status and due date; there are no loans created by submission. Empty states apply when that account has no records. No other borrower's records appear.

### 4.8 Basic user cannot access account management

1. Log in as `auth_demo_user`, visit `/manage/accounts/`

✅ 403 Forbidden.

---

## Module 5 — Operational Settings and Audit Log (T06)

**Base URL:** `/manage/settings/` and `/manage/audit/`\
**Login required:** active ADMIN

### 5.1 View current settings

1. Go to `/manage/settings/`

✅ Shows the persisted current values. Initial defaults are 7 calendar days and 3 units per item; use the displayed values when testing T11.

### 5.2 Change settings

1. Change **Max loan duration** to `5`, submit

✅ Settings saved. Audit log records the change with the admin's name and timestamp.

**Restore the values recorded before this test.** Use 7 and 3 only if those were the original values.

### 5.3 Invalid settings rejected

1. Enter `0` for max loan duration, submit

✅ Validation error — must be a positive integer. No change written.

1. Enter `-1`, submit

✅ Rejected.

### 5.4 Audit log list

1. Go to `/manage/audit/`

✅ Paginated list of all audit entries (settings change, account activations, etc.) with actor, timestamp, action, and target.

### 5.5 Audit log search

1. Use **Record reference** to search a model, ID or combined reference such as `inventory.CatalogItem#12` (replace 12 with an actual record ID).
2. Choose the separate **Action** filter and/or enter a numeric **Actor account ID** shown in an audit row.
3. Try an inclusive date range; then reverse the dates.

✅ Valid filters return matching rows; reversed dates show errors. The reference box does not search arbitrary action words or actor usernames.

### 5.6 Basic user cannot access audit or settings

1. Log in as basic user, visit `/manage/settings/` and `/manage/audit/`

✅ 403 on both.

---

## Module 6 — Equipment Category and Catalog Management (T07)

**Base URL:** `/manage/categories/` and `/manage/items/`\
**Login required:** active ADMIN

### 6.1 Create a category

1. Go to `/manage/categories/new/`
2. Enter **Name**: `Audio Visual Equipment`, **Description**: `Projectors, speakers, and display devices`
3. Submit

✅ Category created, redirected to the category detail page.

### 6.2 Duplicate category name (case-insensitive)

1. Create another category named `audio visual equipment` (all lowercase)

✅ Rejected — case-insensitive unique constraint. Error shown on the name field.

### 6.3 Edit a category

1. Go to the category detail page → **Edit**
2. Change the description and save

✅ Updated, audit entry created.

### 6.4 Archive a category

1. On the category detail page → **Archive** → confirm

✅ Category marked archived. No longer appears in the active catalog list or the borrower portal category filter.

### 6.5 Restore an archived category (optional feature)

1. Find the archived category in the admin list, click **Restore** → confirm

✅ Category becomes active again. Individually archived items under it stay archived until individually restored.

### 6.6 Create a catalog item

1. Go to `/manage/items/new/`
2. Select a category, enter **Name**: `HDMI Projector`, **Description**: a description
3. Optionally upload a photo
4. Submit

✅ Item created, redirected to item detail. Shows in the catalog list.

### 6.7 Archive a catalog item

1. Go to item detail → **Archive** → confirm

✅ Item disappears from active catalog. Borrowers cannot see or request it. Visiting its portal URL directly returns 404.

### 6.8 Archive entire category blocks its items

1. Archive the category that contains `HDMI Projector` (if it's active)
2. Log in as borrower, visit `/portal/equipment/`

✅ Items under the archived category do not appear in the borrower catalog.

### 6.9 Pagination

The admin catalog list uses 10 items per page. Create more than 10 catalog items and verify pagination controls appear.

### 6.10 Photo upload (optional)

1. From item detail, choose **Manage photo**, select a JPEG/PNG/WebP, and submit. New-item creation also accepts an optional photo.
2. Check replacement and confirmed removal through the photo controls; see [file limits and preview behavior](../DEV.md#equipment-photos-and-local-media).

✅ Photo saved, preview shown on item detail page.

1. Visit the item as a borrower on `/portal/equipment/<id>/`

✅ Photo visible. No asset codes, internal notes, or maintenance information exposed.

---

## Module 7 — Physical Unit Management (T08)

**Base URL:** `/manage/units/`\
**Login required:** active ADMIN

### 7.1 Register a GOOD unit

1. Go to `/manage/units/new/`
2. Select **Catalog item**: HDMI Projector, **Asset code**: `CEL-AVE-PROJ-001`, **Condition**: GOOD, **Acquired on**: `2026-09-10`
3. Leave **Internal notes** blank, no maintenance problem needed
4. Submit

✅ Unit created with status **AVAILABLE**. No maintenance record opened. One `UNIT_CREATED` audit entry.

### 7.2 Register a FAIR unit

Same as above with condition FAIR.

✅ Status is **AVAILABLE**. No maintenance record.

### 7.3 Register a DAMAGED unit

1. Go to `/manage/units/new/`
2. Condition: DAMAGED, fill in **Maintenance problem**: `Screen cracked on left edge`
3. Submit

✅ Unit created with status **MAINTENANCE** (forced — you cannot choose AVAILABLE for a damaged unit). A maintenance record is automatically opened. Two audit entries: `UNIT_CREATED` and `MAINTENANCE_OPENED`.

### 7.4 DAMAGED unit without a maintenance problem description

1. Condition: DAMAGED, leave **Maintenance problem** blank
2. Submit

✅ Rejected — error: "A maintenance problem description is required when registering a damaged unit." No unit or maintenance record created.

### 7.5 Duplicate asset code

1. Register another unit with asset code `CEL-AVE-PROJ-001` (already used above)

✅ Rejected — "A physical unit with this asset code already exists."

1. Try the same code in different casing: `cel-ave-proj-001`

✅ Still rejected — uniqueness check is case-insensitive.

### 7.6 Future acquisition date

1. Set **Acquired on** to tomorrow's Asia/Manila date

✅ Rejected — acquisition date cannot be in the future.

### 7.7 Register under an archived catalog item

1. Archive a catalog item and reopen the unit form: it must be absent from allowed choices.
2. For a server recheck, open a unit form before archival in one admin window, archive its selected item in a second admin window, then submit the old form.

✅ The stale/forged selection is rejected with a form error and no new unit.

### 7.8 Register under an archived category

1. Repeat 7.7 while archiving the selected item's category instead.

✅ Items under that category are unavailable as new choices; a stale submission is rejected without a unit write.

### 7.9 Update a unit with no transaction history

1. Find a unit that has no borrow history
2. Go to its **Edit** page
3. Change the asset code, catalog item, acquired date, and internal notes
4. Submit

✅ All fields updated. Audit entry created.

### 7.10 Update a unit with transaction history

Once a unit has borrowing **or maintenance** history, only **internal notes** can be edited. Use the DAMAGED unit from 7.3 to exercise this now; its initial maintenance record already locks the identity fields.
- Asset code, catalog item and acquisition date are locked in the form
- If protected values are forged, they must remain unchanged; disabled fields can be ignored rather than producing a separate error
- Editing internal notes only → succeeds

*The maintenance-history case is testable now. Allocation history can now be prepared through T13 approval; use fictional records and record actual outcomes.*

### 7.11 List filters

1. Go to `/manage/units/`
2. Filter by **Category** — only units under that category appear
3. Filter by **Catalog item** — only units of that specific item appear
4. Filter by **Status** — only units with that status appear (e.g. filter MAINTENANCE to see damaged units)
5. Search by asset code fragment

✅ Each filter works independently and in combination.

### 7.12 Derived inventory counts

On the unit list page, the count cards show Available, Serviceable, and Total counts. After registering units:

- Register 2 GOOD units for HDMI Projector → Available should increase by 2
- Register 1 DAMAGED unit → it goes to MAINTENANCE, not Available

✅ Numbers on the cards update to reflect real unit statuses. No static values.

### 7.13 Unit detail page

1. Click any unit from the list

✅ Shows asset code, catalog item, condition, status, acquisition date, internal notes, and transaction/maintenance history.

### 7.14 Access control

| Who | Expected |
| --- | --- |
| Anonymous | Redirect to login |
| Active BASIC_USER | 403 |
| Inactive ADMIN | 403 |
| Active ADMIN | 200 |

---

## Module 8 — Borrower Equipment Catalog (T10)

**Base URL:** `/portal/equipment/`\
**Login required:** active BASIC_USER

### 8.1 Browse all equipment

1. Log in as `auth_demo_user`
2. Go to `/portal/equipment/`

✅ Active, non-archived catalog items appear. Each shows name, category, available count, and total serviceable count.

### 8.2 Counts reflect real units

- For a fresh item with no earlier units, registering 2 GOOD units gives **Available = 2, Serviceable = 2**. With existing units, compare against the recorded starting counts.
- If you registered 1 DAMAGED unit for HDMI Switch: it is in MAINTENANCE → **Available = 0, Serviceable = 0** for that item

✅ Counts match what was registered in Module 7.

### 8.3 Search by name

1. Type `projector` in the search field, submit

✅ Only items with "projector" in their name or description appear.

### 8.4 Search returns no results

1. Search for `zzznomatch`

✅ Empty state shown — no blank or error page. A clear "no results" message with an option to clear/reset the search.

### 8.5 Filter by category

1. Select `Audio Visual Equipment` from the category filter

✅ Only items under that category appear. Items from other categories are hidden.

### 8.6 Archived items are invisible

1. Archive the HDMI Projector catalog item (as admin)
2. Return to `/portal/equipment/`

✅ HDMI Projector is gone from the list.

3. Try to access `/portal/equipment/<archived_item_id>/` directly

✅ 404 — not accessible even by guessing the ID.

### 8.7 Items under archived category are also invisible

1. Archive the `Audio Visual Equipment` category
2. Go to `/portal/equipment/`

✅ All items under that category disappear from the borrower list.

### 8.8 Item detail page shows correct information

1. Click any active catalog item

✅ Shows: item name, category badge, description, photo (or default placeholder), available count, total serviceable count.

✅ Does NOT show: asset codes, acquisition dates, internal notes, maintenance records, other borrowers' activity.

### 8.9 Photo streaming

1. Pick an item that has an uploaded photo
2. Go to its detail page

✅ Photo is displayed. The photo URL is `/portal/equipment/<id>/photo/`, accessible only to signed-in active basic users.

1. Open the photo URL in an incognito window (not logged in)

✅ Redirected to login — photo is not publicly accessible.

### 8.10 Access control

| Who | Expected |
| --- | --- |
| Anonymous | Redirect to login |
| Active ADMIN | 403 |
| Inactive BASIC_USER | 403 |
| Active BASIC_USER | 200 |

---

## Module 9 — Borrower Request Submission (T11)

**Entry:** `/portal/requests/` → **Create a request** → `/portal/requests/new/`\
**Login required:** active BASIC_USER\
**Implemented revision:** PR #27, main `6c5ea8f`

### 9.1 Verified local inputs and preparation

These example inputs were checked using read-only Django ORM queries on **October 18, 2026 at 23:06 Asia/Manila**, against local source `6c5ea8f`. They describe the local test database at that time, not every teammate's database.

| Setting / date | Verified value |
| --- | --- |
| Submission date used in the examples | October 18, 2026 (`2026-10-18`) |
| Maximum loan duration | 7 calendar days |
| Maximum quantity per item | 3 units |
| Earliest valid return date | October 19, 2026 (`2026-10-19`) |
| Last valid return date | October 25, 2026 (`2026-10-25`) |
| First invalid date beyond the limit | October 26, 2026 (`2026-10-26`) |

Pick the named date in the date picker. Tables use ISO `YYYY-MM-DD`; a browser using month/day/year displays October 21 as `10/21/2026`. **After October 18 or after changing settings, recalculate the dates/quantities from the current Asia/Manila date and current settings before reusing these tables.** A future-looking date in an old example does not establish that it remains valid.

The following nine active catalog items had available units. Select the full item/category label in the form; IDs help distinguish similarly named records.

| Item ID | Equipment item | Category | Available units |
| --- | --- | --- | --- |
| 1 | HDMI Projector | Audio Visual Equipment | 2 |
| 2 | Portable PA Speaker | Audio Visual Equipment | 1 |
| 4 | DSLR Camera (Canon EOS) | Photography & Video | 2 |
| 5 | Adjustable Tripod | Photography & Video | 1 |
| 7 | Lenovo ThinkPad Laptop | Computing Devices | 2 |
| 8 | USB-C Hub 7-in-1 | Computing Devices | 1 |
| 9 | Wireless Keyboard & Mouse Combo | Computing Devices | 1 |
| 13 | Digital Multimeter | Laboratory Tools | 2 |
| 15 | Soldering Iron Station | Laboratory Tools | 1 |

Three other active catalog items had zero available units and one unit in Maintenance each: **HDMI Switch 4-Port** (ID 3), **LED Ring Light** (ID 6), and **Vernier Caliper (150mm)** (ID 14). They can still be selected for a Pending catalog request; T11 does not allocate a physical unit or reject based on available stock. Maintenance units remain unavailable for allocation. Archived items/categories are excluded.

Before each scenario:

1. Keep an administrator session and a borrower session in separate browser profiles, or use a private window for one role. Tabs in the same browser profile share one login.
2. As admin, find the borrower at `/manage/accounts/` and open `/manage/accounts/<borrower_id>/`. Record the existing request history and relevant inventory counts.
3. As an active borrower, open `/portal/requests/`, choose **Create a request**, and enter the scenario's table at `/portal/requests/new/`.
4. Use a new purpose suffix on repeated runs, such as `T11-01-rerun-02`. Leave optional rows entirely blank when instructed. Submit once.
5. Verify the new request in the borrower's request list and **admin account detail**. The request should appear as Pending; no loan is created on submission.

The form shows three equipment rows, a purpose field, a desired return date and the current limits. It has no editable owner, status or approval fields. The outcomes below are **expected results, not records that the tests were run**. A rejected invalid form is a passing validation test.

### 9.2 Happy paths: exact values to enter

#### Test T11-01: Single item

| Field | Value |
| --- | --- |
| Purpose | `T11-01 Classroom presentation` |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | `1` |
| Rows 2 and 3 | Leave every item and quantity field blank |

**Expected acceptance:** redirected to `/portal/requests/` with a confirmation containing the request number. Admin account history shows exactly one new **Pending** request with this purpose, HDMI Projector quantity 1 and the chosen due date. Refreshing the destination page must not create another request.

#### Test T11-02: Three distinct items

| Field | Value |
| --- | --- |
| Purpose | `T11-02 Documentary camera setup` |
| Desired return date | `2026-10-23` (October 23) |
| Row 1 - Item | DSLR Camera (Canon EOS) (Photography & Video), ID 4 |
| Row 1 - Quantity | `1` |
| Row 2 - Item | Adjustable Tripod (Photography & Video), ID 5 |
| Row 2 - Quantity | `1` |
| Row 3 - Item | Portable PA Speaker (Audio Visual Equipment), ID 2 |
| Row 3 - Quantity | `1` |

**Expected acceptance:** one Pending request with all three item rows and their quantities. It must not create three separate requests. Verify the complete item list in admin account history.

#### Test T11-03: Maximum quantity per item

| Field | Value |
| --- | --- |
| Purpose | `T11-03 Lab group multimeters` |
| Desired return date | `2026-10-24` (October 24) |
| Row 1 - Item | Digital Multimeter (Laboratory Tools), ID 13 |
| Row 1 - Quantity | `3` |
| Rows 2 and 3 | Leave blank |

**Expected acceptance:** Pending request for quantity 3, because 3 is the configured per-item maximum. The snapshot shows only 2 multimeters available; this does not reject T11 submission. Inventory is checked and allocated later during T13 approval.

#### Test T11-04: Last allowed return date

| Field | Value |
| --- | --- |
| Purpose | `T11-04 Last allowed return date` |
| Desired return date | `2026-10-25` (October 25) |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | `1` |
| Rows 2 and 3 | Leave blank |

**Expected acceptance:** October 25 is exactly 7 calendar days after October 18 and is included in the valid range. Admin account history shows this due date.

#### Test T11-05: Two distinct items

| Field | Value |
| --- | --- |
| Purpose | `T11-05 Laptop and display setup` |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | Lenovo ThinkPad Laptop (Computing Devices), ID 7 |
| Row 1 - Quantity | `1` |
| Row 2 - Item | USB-C Hub 7-in-1 (Computing Devices), ID 8 |
| Row 2 - Quantity | `1` |
| Row 3 | Leave blank |

**Expected acceptance:** one Pending request with exactly two different item rows. A third row is optional.

#### Test T11-06: Active catalog item with no available units

| Field | Value |
| --- | --- |
| Purpose | `T11-06 Zero available stock request` |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | HDMI Switch 4-Port (Audio Visual Equipment), ID 3 |
| Row 1 - Quantity | `1` |
| Rows 2 and 3 | Leave blank |

**Expected acceptance:** a Pending request is saved because the item and category are active. The switch's unit stays in Maintenance; no unit is reserved or issued. This checks request submission, not permission to approve or release unavailable equipment.

### 9.3 Validation failures: exact values to enter

Each case must leave admin account request history unchanged. A normal validation error returns the same form with errors, not a success redirect or server error. Type invalid boundary values directly when the date picker or number arrows restrict selection; if the browser still prevents entry, use DevTools to adjust only that input's `min`/`max` attributes and keep the form/CSRF token intact. This changes the browser controls, not the server's rules.

#### Test T11-07: Blank purpose

| Field | Value |
| --- | --- |
| Purpose | Leave empty |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | `1` |
| Rows 2 and 3 | Leave blank |

**Expected rejection:** required-field error on Purpose; no request is saved. Repeat with spaces only to check trimming.

#### Test T11-08: Return date is today

| Field | Value |
| --- | --- |
| Purpose | `T11-08 Same day return` |
| Desired return date | `2026-10-18` (October 18) |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | `1` |
| Rows 2 and 3 | Leave blank |

**Expected rejection:** return-date error because the due date must be strictly after the submission date; no request is saved.

#### Test T11-09: Return date beyond seven days

| Field | Value |
| --- | --- |
| Purpose | `T11-09 Beyond duration limit` |
| Desired return date | `2026-10-26` (October 26) |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | `1` |
| Rows 2 and 3 | Leave blank |

**Expected rejection:** return-date error. October 25 is the last valid date for this snapshot; October 26 is eight days after submission. No request is saved.

#### Test T11-10: Quantity exceeds the maximum

| Field | Value |
| --- | --- |
| Purpose | `T11-10 Exceed quantity limit` |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | Digital Multimeter (Laboratory Tools), ID 13 |
| Row 1 - Quantity | `4` |
| Rows 2 and 3 | Leave blank |

**Expected rejection:** Row 1 quantity error because the current maximum is 3. No request is saved.

#### Test T11-11: Quantity is zero

| Field | Value |
| --- | --- |
| Purpose | `T11-11 Zero quantity` |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | `0` |
| Rows 2 and 3 | Leave blank |

**Expected rejection:** Row 1 quantity error; a positive integer is required. No request is saved.

#### Test T11-12: Duplicate item in two rows

| Field | Value |
| --- | --- |
| Purpose | `T11-12 Duplicate equipment item` |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | `1` |
| Row 2 - Item | HDMI Projector (Audio Visual Equipment), ID 1 - same item |
| Row 2 - Quantity | `1` |
| Row 3 | Leave blank |

**Expected rejection:** a duplicate-item formset error. The two quantities must not be silently combined, and no request is saved.

#### Test T11-13: No equipment items

| Field | Value |
| --- | --- |
| Purpose | `T11-13 Empty equipment rows` |
| Desired return date | `2026-10-21` (October 21) |
| Rows 1, 2 and 3 - Item | Keep every dropdown on Choose equipment |
| Rows 1, 2 and 3 - Quantity | Leave every quantity blank |

**Expected rejection:** at least one complete item row is required. No request is saved.

#### Test T11-14: Item selected without its quantity

| Field | Value |
| --- | --- |
| Purpose | `T11-14 Incomplete equipment row` |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | Leave empty |
| Rows 2 and 3 | Leave blank |

**Expected rejection:** required quantity error on Row 1. No request is saved.

### 9.4 Critical atomic test: two valid rows and one invalid row

#### Test T11-15: Invalid third row must save nothing

This checks SRS acceptance scenario 3. Record the existing admin account history first; it may already contain successful requests from earlier cases.

| Field | Value |
| --- | --- |
| Purpose | `T11-15 Atomic invalid third row` |
| Desired return date | `2026-10-21` (October 21) |
| Row 1 - Item | DSLR Camera (Canon EOS) (Photography & Video), ID 4 |
| Row 1 - Quantity | `1` - valid |
| Row 2 - Item | Adjustable Tripod (Photography & Video), ID 5 |
| Row 2 - Quantity | `1` - valid |
| Row 3 - Item | Digital Multimeter (Laboratory Tools), ID 13 |
| Row 3 - Quantity | `5` - invalid; maximum is 3 |

**Expected rejection:** Row 3 quantity error; all entered rows remain available for correction. **No BorrowRequest and no RequestItem rows are saved**, including the first two valid rows. Refresh the borrower's request list and admin account history: neither contains a record with this purpose marker. Do not expect an empty list if earlier successful cases already created records. The automated T11 rollback test directly checks both database tables.

### 9.5 Additional boundaries and tampered formset counts

Use the T11-01 input table with a new purpose marker, changing only the field shown below. Every case should be rejected with no saved request.

| Change | Exact input for this snapshot | Expected error |
| --- | --- | --- |
| Desired return date | Leave empty | Required date |
| Desired return date | `2026-10-17` (October 17) | Date must follow submission |
| Row 1 quantity | `-1` | Positive quantity required |
| Row 1 quantity | `1.5` | Whole-number quantity required |
| Row 1 item | Choose equipment, with quantity `1` | Required item |

Optional DevTools checks: on a fresh valid form, change the existing hidden `items-TOTAL_FORMS` to `4`, or `items-INITIAL_FORMS` to `1`, then submit. Keep the existing CSRF field and browser session. Expected: server-side formset rejection with no request write. Reload the form before the next case. Changing only `items-MAX_NUM_FORMS` does not change the server's limit.

### 9.6 Archived records and stale forms

1. In the borrower window, open the form and select an active item.
2. In the admin window, archive that item before the borrower submits.
3. Submit the existing borrower form with valid purpose, date and quantity.
4. Repeat with a restored item while archiving its category instead.

Expected: both submissions are rejected with errors and no new request. Reopening the form excludes those choices. Restore the category and any independently archived item afterward. Existing Pending requests remain historical records; archiving is not cancellation.

### 9.7 Access, session and CSRF checks

| Session / request | Expected |
| --- | --- |
| Anonymous GET `/portal/requests/new/` | Redirect to login |
| Active ADMIN opens the form | 403 |
| Active BASIC_USER opens the form | 200 |
| Borrower is deactivated by admin while the form is open, then submits | 403 and invalidated session; no new request |
| Signed-in borrower submits an otherwise valid form after removing its CSRF hidden field in DevTools | 403; no new request |

Use separate sessions for deactivation, then reactivate the borrower after the case. Unsupported methods and direct service permission checks are also covered by the automated T11 suite.

### 9.8 Forged protected fields

On an otherwise valid request form, optionally add hidden fields in DevTools: `owner` containing another test account's ID, `status=APPROVED`, `submitted_on=2000-01-01`, `max_loan_days_applied=1` and `max_quantity_applied=1`. Leave the real formset and CSRF token intact, then submit once with a distinct purpose marker.

Expected: the resulting request belongs to the signed-in borrower, remains Pending, uses the actual submission date and current configured limits, and creates no reservation. It must not appear in the other account's history. Extra input fields do not control protected values. Use the optional read-only check below for stored snapshots that are not shown in the UI.

### 9.9 Settings snapshots and changed limits

For the verified October 18 snapshot, use these exact values before and after changing settings:

| Field | Request A - original settings | Request B - changed settings |
| --- | --- | --- |
| Settings at submission | 7 days, 3 units per item | 5 days, 2 units per item |
| Purpose | `T11-16 Original settings snapshot` | `T11-17 Changed settings snapshot` |
| Desired return date | `2026-10-25` (October 25) | `2026-10-23` (October 23) |
| Row 1 item | Digital Multimeter, ID 13 | Digital Multimeter, ID 13 |
| Row 1 quantity | `3` | `2` |
| Rows 2 and 3 | Leave blank | Leave blank |
| Expected stored duration / quantity limits | `7` / `3` | `5` / `2` |

1. Record the original settings and submit a valid request A with a unique marker.
2. As admin, change the settings to a different positive duration and quantity limit, such as 5 days and 2 units if those differ from the current values.
3. Reopen the borrower form: its help text and date range must reflect the new limits. Submit valid request B using them.
4. An already open form using a now-disallowed date or quantity must be rejected if submitted after the change.
5. Verify A retains its original due date and both original snapshots; B stores the new snapshots. Restore the original settings after testing.

Admin account history shows due dates but not stored limit snapshots. To inspect only those values, replace 101 and 102 with the actual IDs for A and B and run this **read-only** command:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from borrowing.models import BorrowRequest; print(list(BorrowRequest.objects.filter(pk__in=[101,102]).values('id','status','submitted_on','desired_due_date','max_loan_days_applied','max_quantity_applied')))"
```

Expected: settings changes do not rewrite A; each request records the settings at its own submission. Do not modify request rows to manufacture this result.

### 9.10 Submission must not reserve equipment

Compare Available, Reserved and Issued counts before and after a successful Pending submission. They must remain unchanged, and no loan should appear in admin account history. The default quantity limit is a per-item request limit, not a check against current availability: an active item with zero available units can still be requested. Approval/allocation and shortage handling belong to T13.

### 9.11 Keyboard, mobile and known limitations

Tab through purpose, date, each equipment/quantity field and Submit. Check associated labels, visible focus, reachable errors and a usable layout at desktop and narrow mobile widths. Record actual observations; these were not verified by the automated HTTP checks.

T12 supplies the request/loan history pages and highlights the corresponding navigation tab on list, detail and confirmation pages, including request creation. Admin approval is now available through merged T13, with its verified local corrections recorded in Module 12. A lack of reserved units after submission is expected and does not indicate a failed T11 submission.

---

## Module 10 — Borrower Request and Loan Tracking (T12)

**Entry:** `/portal/requests/` and `/portal/loans/`\
**Login required:** active BASIC_USER\
**Implemented revision:** PR #29, main `170cc38`, preserving Ralph source `eb04470`\
**Prerequisite:** T11 is integrated through PR #27; T13 approval and query corrections are integrated through PR #34/#35. T15 issue is integrated through PR #42; T17 returns are integrated through PR #43 at `55899d0`.

These are expected outcomes, not tests claimed as run. Use a borrower request created through T11. For foreign-record checks, use a second fictional BASIC_USER account and its own request/loan ID. Do not expose or copy another borrower's fields in screenshots.

### Verified local preparation

A read-only PostgreSQL transaction on **October 19, 2026 at 07:36 Asia/Manila**, using source `170cc38`, found active `auth_demo_user` / `auth_demo_admin` seed accounts, three Pending requests (IDs 1, 2 and 3) owned by `auth_demo_user`, and **no loans**. No Approved, Issued or returned requests existed in that snapshot. Settings were 7 loan days / 3 units per item. HDMI Projector (Audio Visual Equipment), item ID 1, and its category were active. This snapshot does not establish a manual pass; recheck status before acting because ongoing tests can change it.

Keep admin and borrower logins in separate browser profiles. To preserve existing request records, create one fresh request at `/portal/requests/new/` for the Pending-cancellation case:

| Field | Value |
| --- | --- |
| Borrower | `auth_demo_user`, using its private existing password |
| Purpose | `T12-02 Pending cancellation 2026-10-19 run-01` |
| Desired return date | `2026-10-22` |
| Row 1 - Item | HDMI Projector (Audio Visual Equipment), ID 1 |
| Row 1 - Quantity | `1` |
| Rows 2 and 3 | Leave all item and quantity fields blank |

Record the actual new request ID from the confirmation/list. On October 19 with these settings, valid dates are October 20–26 inclusive. Recalculate from today's Asia/Manila date and current settings on later runs; use a fresh purpose suffix and recheck that the catalog choice is active. T11 does not reserve units, so this record does not require available stock.

### 10.1 Request history and status filtering

**Case T12-01.** Start with your newly created Pending request, then repeat after T12-02 cancels it.

| Field / URL | Value | Expected result |
| --- | --- | --- |
| Status | Pending (`PENDING`) | Only own Pending requests; includes the new record before cancellation |
| Status | Cancelled (`CANCELLED`) | Includes the new record after cancellation; excludes it before cancellation |
| Status | All statuses | Restores all own requests, including the cancelled record |
| URL | `/portal/requests/?status=UNKNOWN` | 200 with a filter error and no records |
| URL | `/portal/requests/?page=bad` or `?page=0` | 404 |

1. Sign in as an active borrower and open `/portal/requests/`.
2. Verify the page lists only requests belonging to the signed-in borrower, with purpose, requested items/quantities, status, submission date and desired/agreed due dates.
3. Select a status from the filter and submit. Only requests with that persisted status should remain; selecting **All statuses** clears the filter.
4. With a borrower who has no requests, verify the useful empty state and the **Create a request** link.
5. Open a request. Verify its item/category details, decision status/reason when decided, and current due dates.
6. Substitute another borrower's request ID in the detail URL. The response should be 404 without revealing record contents. Invalid page numbers should also return 404; invalid status filters should show a validation error and no records.

Pagination shows 6 records per page. If a fictional borrower already has more than 6, verify Previous/Next retains the selected status and does not duplicate/skip rows. The three-record snapshot cannot exercise that boundary; leave it Not run until suitable records exist. Cross-user checks also need a second fictional borrower's known request; the snapshot found no such request.

### 10.2 Cancel a Pending request

**Case T12-02.** Use the fresh request from the preparation table; cancellation is terminal.

1. Record its request ID and the current inventory count. Open its detail and choose **Cancel request**.
2. Load the confirmation page with GET and refresh it. The request must remain Pending and no cancellation audit entry should be created by either GET.
3. Choose **Keep request** once: expect a return to details with no mutation. Reopen cancellation and confirm using the form's POST.

✅ Redirected to `/portal/requests/<request_id>/` with a success message. The request is Cancelled and its cancel link is absent. Items and due dates are preserved; inventory counts do not change because Pending requests have no reservations. The borrower and server timestamp are stored, and one `REQUEST_CANCELLED` audit entry exists. Reopening `/portal/requests/<request_id>/cancel/` returns 409; resubmitting the original confirmation POST also returns 409 without another audit entry.

As admin, open `/manage/audit/`, select action **Request cancelled**, and search the record reference `borrowing.BorrowRequest#<request_id>` using the actual ID. Expect exactly one matching row identifying the borrower actor, timestamp and request. `/manage/requests/` is still a placeholder; use the audit page and admin account detail for current verification.

The borrower detail does not display cancellation actor/time. To verify those stored fields, replace `123` below with the actual fictional request ID and run this read-only query before and after the action:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from borrowing.models import BorrowRequest; from operations.models import AuditLog, AuditAction, AuditTarget; request_id = 123; print(list(BorrowRequest.objects.filter(pk=request_id).values('id', 'owner_id', 'status', 'cancelled_by_id', 'cancelled_at'))); print(AuditLog.objects.filter(action=AuditAction.REQUEST_CANCELLED, target_model=AuditTarget.BORROW_REQUEST, target_id=request_id).count())"
```

Before: Pending, null cancellation fields, zero matching audits. After: Cancelled, `cancelled_by_id` equals `owner_id`, a non-null timestamp and one audit; after retry: the same stored values and count.

### 10.3 Cancel an Approved request and release its reservations

**Case T12-03 — now available to prepare.** Use [T13 approval in Module 12](#module-12--administrator-request-review-and-decisions-t13) on a fresh fictional request. The October 19, 22:31 local snapshot has no Approved requests yet; prepare this prerequisite through the browser workflow, without editing database statuses. Corrected jerome detail excludes ended allocations from Reserved units while retaining their history. PR #35 integrates this display fix at main `cf50d0c`.

1. After approving through T13, record the Approved request ID and the Reserved status of every unit assigned to it.
2. As that same borrower, open the request details and confirm cancellation.

✅ The request becomes Cancelled, every associated allocation ends with its cancellation timestamp, and all of its reserved units become Available together. The cancellation and audit row commit together. If any reservation is missing, changed, or incomplete, the action returns 409 and none of the request, allocations, units or audit entries change.

### 10.4 Issued request and loan tracking

**Case T12-04.** Open `/portal/loans/` now: the snapshot has no loans, so expect **No loans yet**, with no fabricated records. An absent loan ID at `/portal/loans/<loan_id>/` returns 404.

The populated loan/return browser scenarios below require the separate T15 release and T17 return workflows. Leave them Not run until those workflows and suitable fictional records exist.

1. After T15 is integrated, release an Approved request for a fictional borrower. Sign in as that borrower and open `/portal/requests/`, the request detail, and `/portal/loans/`.
2. Verify only that borrower's loan is listed, with issue/due dates and a link to its detail. The request detail should also show issued asset codes.
3. Open the loan detail. Verify each issued unit and its asset code is listed as awaiting return. Substitute another borrower's loan ID; the response should be 404.
4. After one unit is returned through T17, reload the request and loan details.

✅ The returned unit shows its return timestamp and recorded condition while outstanding units remain marked as not returned. Return notes, internal unit notes, other borrowers' data and admin-only maintenance details are not shown. After final return, loan/request status reflects the stored workflow outcome.

### 10.5 Role, method, keyboard and narrow-screen checks

1. Verify anonymous users are redirected to sign-in; an active ADMIN and an inactive BASIC_USER receive 403 on portal history pages.
2. Send POST to the read-only request and loan list/detail routes; each should return 405. GET of the cancellation confirmation should never mutate state. POST cancellation without a valid CSRF token should return 403.
3. Use only the keyboard to reach filters, request/loan links, cancel confirmation and controls. Confirm visible focus, associated labels, readable errors and sensible reflow at narrow mobile width.

The automated T12 client tests cover role/method/CSRF, owner isolation, invalid filters/pages, cancellation conflicts, full reservation release, audit rollback, and loan-unit status display using records created in the separate test database. They do not exercise multi-page traversal or a separate-connection cancellation/issue race. Browser, keyboard and mobile outcomes for the integrated revision remain **Not run / awaiting user results**.

---

## Module 11 — Equipment Maintenance and Inventory Reconciliation (T16)

> **Baseline integrated through [PR #31](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/31) at `2615829`, source `5582868` (Kenneth Cortez). [T16 corrections](../handoffs/t16-maintenance-integrity-and-conflict-fixes-10-19-2026.md) `d68d7f7` are integrated through PR #33 at `aa36c86`. Browser checks remain Not run.**
> **Prerequisites integrated into main:** T08 physical units ([PR #22](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/22) at `6c91d48`) and T03 shared locking/audit ([PR #3](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/3) at `d122518`).
> **Required role:** `ADMIN`.
> **Entry URL:** `/manage/maintenance/` (`inventory_manage:maintenance-list`).

### Verified local database snapshot (October 19, 2026, 14:13 Asia/Manila)

The connected PostgreSQL MCP reported `transaction_read_only=on`. This review read inventory/settings only and made no live writes. Recheck with read-only queries (`manage.py shell`) before execution:

```python
from inventory.models import EquipmentUnit, MaintenanceRecord
from inventory.queries import get_overall_inventory_counts

counts = get_overall_inventory_counts()
print(
    f"Overall inventory: Available={counts.available}, Reserved={counts.reserved}, Issued={counts.issued}, Maintenance={counts.maintenance}, Retired={counts.retired}, Serviceable={counts.serviceable}, Total={counts.total}"
)
print(
    [
        (u.pk, u.asset_code, u.status, u.condition, u.catalog_item.name)
        for u in EquipmentUnit.objects.filter(status="AVAILABLE")
    ]
)
```

- **Current example:** `CEL-AVE-PROJ-002`, unit ID 2, `FAIR`, HDMI Projector / Audio Visual Equipment, is `AVAILABLE`. Dropdown label: `CEL-AVE-PROJ-002 — HDMI Projector (Fair)`.
- **Existing maintenance:** 4 Open, 0 Closed: record 4 / `CEL-AVE-PROJ-001` (unit 1), plus record 1 / `CEL-AVE-HDMI-001` (unit 4), record 2 / `CEL-PHV-RLT-001` (unit 8), record 3 / `CEL-LAB-VCL-001` (unit 15). Units 4, 8 and 15 are Damaged/Maintenance; unit 1 is Good/Maintenance. For a fresh opening use projector 002, not unit 1. To continue the previous projector-001 run, its existing record is `/manage/maintenance/4/`; do not try to open it again.
- **Initial counts:** Available 12, Reserved 0, Issued 0, Maintenance 4, Retired 0, Serviceable 12, Total 16. Settings remain 7 days / 3 units. No loans exist.
- These replace Kenneth's workstation examples; `cam-qwert` / `sony` is not in this local snapshot. If data changed, select another eligible fictional unit and record the actual baseline. Counts below assume only these sequential cases change inventory. Reserved/Issued browser rejection and more-than-5-row pagination require additional legitimate records; leave them Not run here. No seed data was created by this review.
- Test repair before retirement. Retirement has no reversal in the supplied interface; use a disposable fictional unit for that case.

---

### Test Case T16-01: Open Maintenance for an Available Unit (Successful Flow)

- **Role:** Sign in as an active `ADMIN`.
- **Navigation:** Navigate to `/manage/maintenance/` and click the **Open maintenance** button, or go directly to `/manage/maintenance/new/`. (Alternatively, click **Open maintenance** from `/manage/units/<id>/`.)
- **Form inputs:**

| Field | Value | Notes |
| --- | --- | --- |
| Physical unit (`unit`) | `CEL-AVE-PROJ-002 — HDMI Projector (Fair)` | Dropdown populated with eligible `AVAILABLE` units only |
| Problem description (`problem`) | `Projection image flickers intermittently during classroom use.` | Detailed issue description |

- **Submit:** Click **Open maintenance**.
- **Expected results:**
  - ✅ Redirects to `/manage/maintenance/<id>/` (`inventory_manage:maintenance-detail`).
  - ✅ Green flash banner: `Maintenance opened for physical unit "CEL-AVE-PROJ-002".`
  - ✅ Status badge displays `Open` in amber.
  - ✅ Physical unit card reflects unit status `Maintenance` and condition `Fair`.
  - ✅ Audit timeline shows `Opened at` timestamp and `by <admin-username>`.
  - ✅ Visiting `/manage/maintenance/` displays the record in the table and updates the summary card to `Maintenance: 5`, `Available: 11`, `Total: 16`.
  - ✅ Unit detail page (`/manage/units/2/`) reflects status `Maintenance`, hides the "Open maintenance" button, and lists this maintenance in the unit's maintenance history table with an active **Close** link.
  - ✅ Read-only database check: `MaintenanceRecord.objects.get(pk=...).status == 'OPEN'`, unit status is `'MAINTENANCE'`. `AuditLog` entry exists with `action='MAINTENANCE_OPENED'` and `target_model='inventory.MaintenanceRecord'`.

---

### Test Case T16-02: Open Maintenance Validation and Ineligible Unit Rejection

- **Role:** Active `ADMIN`.
- **Scenario A: Blank problem description**
  - **URL:** `/manage/maintenance/new/`
  - **Inputs:**
    - Physical unit: Select any available unit.
    - Problem description: Leave blank or enter whitespace only (`   `).
  - **Submit:** Click **Open maintenance**.
  - **Expected results:**
    - ✅ Page remains on `/manage/maintenance/new/` with status 200 OK.
    - ✅ Field-level error displayed: `Problem description cannot be blank.`
    - ✅ No record created and no unit status changed.

- **Scenario B: Ineligible unit rejection (already in maintenance)**
  - Note: Unit `CEL-AVE-PROJ-002` is currently in maintenance from Case T16-01.
  - Navigate to `/manage/maintenance/new/`.
  - **Expected results:**
    - ✅ The unit dropdown `unit` excludes `CEL-AVE-PROJ-002` entirely (only units in `AVAILABLE` status without active open maintenance appear).
    - ✅ If a direct forged POST is sent with `unit=2`, the form returns an error: `Select a valid choice. That choice is not one of the available choices.` or `Unit CEL-AVE-PROJ-002 already has an active open maintenance record.` No second open record is created (enforcing `maintenance_one_open_unit` constraint).

---

### Test Case T16-03: Close Maintenance with Repaired/Available Outcome

- **Role:** Active `ADMIN`.
- **Navigation:** Open `/manage/maintenance/<id>/` for the open record created in T16-01. Click **Close maintenance**, or navigate directly to `/manage/maintenance/<id>/close/`.
- **Form inputs:**

| Field | Value | Notes |
| --- | --- | --- |
| Action taken / Resolution (`action`) | `Replaced faulty HDMI cable and cleaned projector contacts; verified a stable image.` | Required resolution text |
| Maintenance outcome (`outcome`) | `Available` | Selected from dropdown (`AVAILABLE` / `RETIRED`) |
| Repaired condition (`repaired_condition`) | `Good condition` | Select `Good condition` or `Fair condition` |

- **Submit:** Click **Complete & close maintenance**.
- **Expected results:**
  - ✅ Redirects to `/manage/maintenance/<id>/` (`inventory_manage:maintenance-detail`).
  - ✅ Green flash banner: `Maintenance for "CEL-AVE-PROJ-002" closed with outcome: Available.`
  - ✅ Status badge displays `Closed` in slate.
  - ✅ Outcome badge displays `Repaired / Available` in emerald.
  - ✅ Resolution section displays the action taken, outcome, and closure timestamp/admin.
  - ✅ The "Close maintenance" button is no longer present.
  - ✅ Physical unit details show unit status restored to `Available`.
  - ✅ Visiting `/manage/maintenance/` displays the record as `Closed`, and count cards reconcile: `Available: 12`, `Maintenance: 4`, `Total: 16`.
  - ✅ Visiting unit detail (`/manage/units/2/`) shows status `Available`, the "Open maintenance" button is restored, and the maintenance table shows `Closed` with outcome `Repaired / Available`.
  - ✅ Read-only database check: `MaintenanceRecord` status is `'CLOSED'`, outcome is `'AVAILABLE'`, `closed_at` and `closed_by` are set. `AuditLog` entry exists with `action='MAINTENANCE_CLOSED'`.

---

### Test Case T16-04: Close Maintenance with Retired Outcome

- **Role:** Active `ADMIN`.
- **Preparation:** Open maintenance on an available unit (e.g. `CEL-AVE-PROJ-002` or test unit) with problem `Catastrophic internal sensor failure; circuit board cracked.`
- **Navigation:** Go to `/manage/maintenance/<id>/close/`.
- **Form inputs:**

| Field | Value | Notes |
| --- | --- | --- |
| Action taken / Resolution (`action`) | `Unit evaluated by technician; replacement sensor discontinued by manufacturer. Decommissioning and retiring unit.` | Required resolution |
| Maintenance outcome (`outcome`) | `Retired` | Selected from dropdown |

- **Submit:** Click **Complete & close maintenance**.
- **Expected results:**
  - ✅ Redirects to `/manage/maintenance/<id>/`.
  - ✅ Green flash banner: `Maintenance for "<asset-code>" closed with outcome: Retired.`
  - ✅ Status badge: `Closed`; Outcome badge: `Retired` in slate.
  - ✅ Physical unit status is permanently set to `Retired`.
  - ✅ Summary count cards reconcile: `Retired: 1`, `Maintenance: 4`, `Available: 11`, `Serviceable: 11`, `Total: 16`.
  - Retired unit cannot be selected for new maintenance. Borrowers choose catalog items, not physical units; availability falls by one. T13 now allocates eligible units; browser cases remain unrun; Module 13 verifies the integrated T14 approval races.

---

### Test Case T16-05: Repeat Closure and Invalid Form Submissions Rejected

- **Role:** Active `ADMIN`.
- **Scenario A: Repeat closure attempt**
  - Attempt to access `/manage/maintenance/<id>/close/` for an already-closed maintenance record.
  - **Expected results:**
    - **Corrected local behavior:** GET and POST return 409 with `This maintenance record is already closed.` and no writes. The closed-record page has no submit form. PR #33 integrated this 409 behavior; do not confuse the original PR #31 baseline with current main.
    - ✅ No state modification occurs.
- **Scenario B: Blank action taken on close**
  - Use existing open record 1 (`CEL-AVE-HDMI-001`) at `/manage/maintenance/1/close/`; select `Available` and `Good condition`, but leave `action` blank (`   `). This validation case must not close that record.
  - **Expected results:**
    - ✅ Page returns with 200 OK.
    - ✅ Field-level error displayed: `Action taken cannot be blank.`
    - ✅ Maintenance record remains `Open` and unit remains in `Maintenance`.

---

### Test Case T16-06: Maintenance List Search, Status Filtering, and Pagination

- **Role:** Active `ADMIN`.
- **Navigation:** `/manage/maintenance/`
- **Scenarios:**
  - **Search by asset code:** Enter `CEL-AVE-PROJ-002` in `q` field and click **Filter**.
    - ✅ Result shows only maintenance records matching `CEL-AVE-PROJ-002`.
  - **Status filter:** Select `Open` in Status dropdown and click **Filter**.
    - ✅ Displays only open maintenance records.
  - **Status filter:** Select `Closed` in Status dropdown and click **Filter**.
    - ✅ Displays only closed maintenance records.
  - **Clear filters:** Click **Clear**.
    - ✅ Restores unfiltered list.
  - **Pagination:** List paginates at 5 rows per page; pagination links preserve active `q` and `status` query parameters using `{% querystring %}`. Invalid page returns 404.

---

### Test Case T16-07: Authorization, Role Enforcement, and CSRF Protection

- **Role / Method Checks:**
  1. **Anonymous visitor:** Accessing `/manage/maintenance/`, `/manage/maintenance/new/`, `/manage/maintenance/<id>/`, or `/manage/maintenance/<id>/close/` redirects to `/accounts/login/?next=...`.
  2. **Borrower account (`BASIC_USER`):** Accessing any `/manage/maintenance/*` route returns **403 Forbidden**.
  3. **Method protection:** Sending `POST` to `/manage/maintenance/` or `/manage/maintenance/<id>/` returns **405 Method Not Allowed**.
  4. **CSRF protection:** Submitting POST to `/manage/maintenance/new/` or `/manage/maintenance/<id>/close/` without a valid CSRF token returns **403 Forbidden**.
  5. **Keyboard & Responsive navigation:** Use `Tab` / `Shift+Tab` to verify visible focus order across all filter inputs, action buttons, form controls, and table links. Verify clean grid stacking and no horizontal overflow on mobile viewports (375px).

All 33 maintenance tests also pass within the T15 273-test PostgreSQL suite (the earlier T16 review passed 224 total tests). They include manual lifecycle/access/filter/count checks, seven new real integrity tests for the removed return-link argument, opening/repair audit rollback, changed-state 409, CSRF/protected fields, competing administrators and unit-before-maintenance closure locking. Browser, keyboard, mobile and pagination-boundary results remain **Not run**; these tests do not implement T17.

---

The manual `open_maintenance` action accepts no `source_return_id` and always applies Available-unit eligibility. Browser-supplied return/actor/status fields cannot control it. T17 creates matching damaged-return maintenance inside its complete return/allocation/audit transaction; the manual opener is not a damaged-return interface.

## Module 12 — Administrator Request Review and Decisions (T13)

**Owner:** Margareth Raine H. Ignacio (`marga`); Jerome with Codex for the authorized query fixes. **Revision:** PR #34 baseline `23c1ad9`, preserving `c5cfe37`, plus [fixes `1d7a3c7`](../handoffs/t13-query-fixes-and-publication-10-19-2026.md) integrated through PR #35 at main `cf50d0c`. **Status:** Done and integrated; browser verification pending. **Role:** active ADMIN. **Entry:** `/manage/requests/`. T03/T11 are integrated; release/slips are integrated under T15; T17 returns are integrated through PR #43. Decision/lifecycle browser cases below remain **Not run**; focused UI-10 row-navigation results are recorded in T13-01. Two automated HTTP/database regressions failed before the fixes and now pass.

### Preparation and verified local records

Read-only check: **October 19, 2026, 22:31 Asia/Manila**, main `23c1ad9`; `SET TRANSACTION READ ONLY` and `SHOW transaction_read_only` confirmed `on`. Settings: **7 days / 3 units per item**. Local records: **3 Pending requests**, no requests in other states, **0 loans**. No live rows were created or changed to write these cases. Prepare your own fictional requests rather than repurpose another borrower's records.

| Catalog item | ID | Available at inspection | Use |
| --- | --- | --- | --- |
| HDMI Projector | 1 | 1 | Quantity 1 approval; quantity 2 shortage |
| HDMI Switch 4-Port | 3 | 0 | Rejection or shortage without stock changes |

Recheck settings, active borrower, item/category archive flags and availability before each action. Sign in as a fictional BASIC_USER, submit at `/portal/requests/new/`, record the resulting request ID, then switch to an active ADMIN. Queue search accepts **ID or borrower username**, not the purpose marker.

| Field | Successful example value |
| --- | --- |
| Purpose | `T13-02 Approval 2026-10-19 run-01` |
| Desired return date | `2026-10-22` |
| Equipment item | HDMI Projector (ID 1) |
| Quantity | `1` |
| Other item rows | Blank |

Use a new purpose/run suffix for every new request. On October 19, valid desired dates are October 20–26 inclusive; recompute as tomorrow through today + 7 days when testing later. Per-item quantities must be 1–3. Submission does not check stock; approval does. Record baseline status, available units and active allocations before each decision.

### T13-01: Queue, filters and read-only detail

| Field / action | Value | Expected result |
| --- | --- | --- |
| Request ID or borrower username | Your new request ID | Matching request only |
| Request ID or borrower username | Your fictional borrower's username | That borrower's matching requests |
| Status | Pending | Pending requests only |
| Submitted from / through | `2026-10-19` / `2026-10-19` | Inclusive same-day results; adjust for actual submission date |
| Submitted from / through | `2026-10-20` / `2026-10-19` | Date-range error and no unfiltered results |
| Direct query | `?status=INVALID` or `?date_from=invalid` | Bound errors and no results |
| Direct query | `?page=abc` or `?page=999999` | 404 on this snapshot |
| Clear filters | Clear filters link | All requests, newest submission/ID first |
| Open from the whole row (UI-10) | Click the Borrower, Items, Submitted, Due date or Status cell, or row padding | Opens the same request detail as its ID link |
| Keyboard / native link (UI-10) | Tab to the request ID and press Enter; Ctrl-click the ID separately | Opens detail; Ctrl-click retains the native new-tab behavior |
| Select row text (UI-10) | Select borrower text | Text remains selectable without row navigation |
| JavaScript disabled (UI-10) | Click the request ID | The original native link still opens detail |
| Row text alignment (UI-10) | Inspect ID, borrower, item count, dates and status at desktop and compact widths | All cells are vertically centered; item count/status labels stay on one line |

Open detail and verify borrower, purpose, requested/agreed dates, quantities and current availability. Detail and decision confirmation GETs must not change status, allocations or audits. Pagination holds 25 rows and retains filters. With only 3 local requests, **multi-page traversal is Not run / insufficient records**; invalid-page checks do not prove that traversal.

**UI-10 actual check, October 20, 2026:** original local run on `ralph`; source `bd62ed7` is now integrated through PR #43 at `55899d0`. Isolated Chrome 155 checks passed for all six cell-padding targets, native ID click, keyboard Enter, Ctrl-click/new tab, selected-text preservation, pointer cursor, 320px page bounds/row navigation and the ID link with JavaScript disabled. These focused checks do not establish the remaining T13 decision/lifecycle browser cases. See the [row-navigation handoff](../handoffs/request-queue-clickable-rows-10-20-2026.md). Use an actual request shown in your current queue; fixture IDs are not live records.

The [alignment follow-up](../handoffs/request-queue-text-alignment-10-20-2026.md) measured **0px vertical text-position spread** across all six columns at 1440px and 320px after centering cells and preventing count/status wrapping. Screenshots and the existing row-navigation interactions were checked again in the isolated database.

### T13-02: Approve and reserve exact quantities

Use the fresh quantity-1 projector request while one projector remains Available.

| Field / action | Value |
| --- | --- |
| Detail action | Approve |
| Reason | `Approved for classroom demonstration - T13-02` |
| Submit action | Approve and reserve units |

Expected: GET changes nothing; valid POST returns 302 to request detail. Status becomes Approved with reason, deciding ADMIN and timestamp. Exactly one allocation is active for the requested unit, which becomes Reserved. Projector availability falls by one; other requests/units do not change. One `REQUEST_APPROVED` audit commits for this request, and no loan exists. Use the read-only verification below when the UI cannot show persisted state.

### T13-03: Reason validation and stale decisions

Test validation on a fresh Pending request before completing a valid decision.

| Reason / action | Expected result |
| --- | --- |
| Empty or whitespace-only reason, either action | Required-field error; no decision, allocation, unit or audit change |
| 501-character reason | Browser maximum-length enforcement or bound error (200 if submitted directly); no workflow change |
| Valid reason up to 500 characters | Eligible action can proceed |

For stale POST behavior, open two confirmation tabs while Pending, complete one valid decision, then submit the second with a valid reason. Expected: 409, no second decision/audit or extra reservation. A fresh GET for a non-Pending confirmation shows that it can no longer be decided and omits the form (currently 200). Cancelled/rejected requests cannot be approved.

### T13-04: Reject without changing inventory

Create a new request with purpose `T13-04 Rejection 2026-10-19 run-01`, date `2026-10-22`, HDMI Switch 4-Port, quantity `1`. Zero available stock does not block submission or rejection.

| Field / action | Value |
| --- | --- |
| Detail action | Reject |
| Reason | `Equipment not suitable for this activity - T13-04` |
| Submit action | Reject request |

Expected: 302 to detail, Rejected status with actor/time/reason, one `REQUEST_REJECTED` audit, no allocations and unchanged inventory. A stale repeat decision must not add another audit or change the recorded reason.

### T13-05: Shortage is all-or-nothing

First restore projector availability by cancelling the approved T13-02 request as its borrower (T13-06). Create purpose `T13-05 Shortage 2026-10-19 run-01`, date `2026-10-22`, projector quantity `2` (valid maximum 3, available 1). Approve with reason `Check atomic shortage - T13-05`.

Expected: HTTP 409 with requested/available quantities and **Nothing was reserved**. The request stays Pending, no allocation/approval audit exists, and stock stays Available. For a multi-item check, use projector quantity 1 plus HDMI Switch 4-Port quantity 1; switch shortage must leave the projector unreserved too. Recheck dated stock first.

### T13-06: Approved cancellation preserves history and clears Reserved units

Run [T12-03](#module-10--borrower-request-and-loan-tracking-t12) on the approved T13-02 request as its owning BASIC_USER. Expected: Cancelled, allocation `cancelled_at`/`ended_at` set, physical unit Available again, and a `REQUEST_CANCELLED` audit. Reopen administrator detail.

Expected on corrected jerome: Reserved units shows None for the cancelled request, availability is restored and the ended allocation remains stored. The new integration regression verifies all three plus the cancellation audit. PR #35 integrates this fix into main `cf50d0c`; the earlier `23c1ad9` baseline showed ended allocations as Reserved. Browser result remains Not run; do not edit historical rows to hide the original defect.

### T13-07: Unicode numeric search succeeds without an exception

| Field | Value |
| --- | --- |
| Request ID or borrower username | `²` (superscript two) |

Expected on corrected jerome: HTTP 200 with normal username matches or empty results. The query uses `isdecimal()` before converting an ID; `²` remains username search text. The new integration regression confirms a username containing `²` is found and Arabic-Indic decimal digits still match a request ID. PR #35 integrates this fix into main `cf50d0c`; the earlier `23c1ad9` baseline raised `ValueError` for `²`. Browser result remains Not run.

### T13-08: Access, eligibility and audit integrity

- Signed out: list/detail/confirmation redirect to login. Active BASIC_USER: direct administrator GET/POST returns 403. Inactive ADMIN sessions cannot mutate. Missing request IDs return 404; unsupported PUT/DELETE return 405.
- Both decision POSTs require CSRF (403 without a valid token). Extra actor/owner/status/allocation fields must not control writes; use the real form for normal testing and retain any private tokens locally during direct HTTP tests.
- Approval for an inactive borrower or archived item/category returns 409 without reservations. These browser cases need deliberately prepared fictional records through existing account/catalog interfaces; no such live changes were made for this guide.
- Temporary PostgreSQL probes forced rejection of approval/rejection audit inserts and verified rollback of their business writes. These ran only in the test database; no live audit constraints were installed.
- Desktop/mobile, keyboard focus, pagination boundaries and stale browser submissions still need actual results. **Module 13 now verifies competing approvals separately with PostgreSQL TransactionTestCase; these browser cases and the T13 TestCase suite alone do not establish concurrency.**

### Read-only verification of your fictional request

In `manage.py shell`, replace `request_id` with your recorded ID before running; no preassigned T13 fixture ID exists:

```python
from django.db import connection, transaction
from borrowing.models import BorrowRequest, Loan, UnitAllocation
from operations.models import AuditLog, AuditTarget

request_id = 123  # Replace with your fictional request ID.
with transaction.atomic():
    with connection.cursor() as cursor:
        cursor.execute("SET TRANSACTION READ ONLY")
    request = BorrowRequest.objects.get(pk=request_id)
    print(request.status, request.decision_reason, request.decided_by_id, request.decided_at)
    print(
        list(
            UnitAllocation.objects.filter(request_item__request_id=request_id).values_list(
                "unit__asset_code", "unit__status", "cancelled_at", "ended_at"
            )
        )
    )
    print(
        list(
            AuditLog.objects.filter(
                target_model=AuditTarget.BORROW_REQUEST, target_id=request_id
            ).values_list("action", "actor_id")
        )
    )
    print("Loans:", Loan.objects.filter(request_id=request_id).count())
```

Record actual browser outcomes and fictional IDs in the shared [result record](#recording-manual-results). Expected outcomes, known failures and Not run cases remain separate. No browser pass is claimed by this review.

---

## Module 13 — PostgreSQL Competing Approvals (T14)

**Owner:** Jerome Avecilla (`jerome`), with Margareth's existing approval service. **Revision:** source `058357c`, integrated through PR #37 at main `5381c83975753426208ffde6370c4e8da09fe5d9`. **Status:** Done and integrated. **Entry:** terminal in the repository, with the project virtual environment and PostgreSQL configured. No browser/server session or live fixture preparation is required.

### T14-01: Reproduce the last-unit race

Run this command while no other process is running this checkout's test database:

```powershell
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_approval_concurrency --noinput --verbosity 2
```

The runner creates and removes `test_<DB_NAME>`; the configured database user needs test-database creation permission. Never point tests at a database containing retained data. Fixtures are generated in this separate database, with runtime IDs; do not seed or edit live equipment to run T14.

| Field / setup | Exact fixture value |
| --- | --- |
| First ADMIN / borrower usernames | `fictional_admin` / `fictional_borrower` |
| Second ADMIN / borrower usernames | `t14_second_admin` / `t14_second_borrower` |
| Account eligibility | Active; distinct ADMIN and BASIC_USER accounts respectively |
| Category / shared catalog item | `Test cameras` / `Test camera`, both active |
| Last physical unit | `TEST-CAM-001`, GOOD, AVAILABLE |
| Each Pending request | One shared item, quantity `1`; purpose `Fictional classroom activity` |
| Due date / request limit snapshots | Test run's local date + 3 days; 7 days / 3 units per item |
| Decision reason | `T14 competing approval for request <generated request ID>` |

The test holds the category lock in a third connection until PostgreSQL reports that both worker connections are waiting in its blocking chain. All three backend PIDs must differ. Releasing that lock lets the real `approve_request` services compete. The expected loser is specifically `WorkflowConflict` from stock shortage; a database timeout, deadlock, integrity error or unexpected exception fails the test. The winner is intentionally unspecified.

Expected: `test_last_unit_has_one_approval_and_one_workflow_conflict ... ok`. Exactly one request is Approved with its actor, timestamp, reason and active allocation; the unit is Reserved. The loser remains Pending with no decision metadata, allocation or audit. Exactly one `REQUEST_APPROVED` audit belongs to the winner; no loan exists. Existing T13 HTTP tests establish the conflict's 409 mapping; this scenario tests the service transactions directly.

### T14-02: Multi-item atomicity under the same contention

The same command also runs `test_multi_item_loser_keeps_other_stock_available_without_partial_allocations`. Each request gets an additional uncontested item before its shared item in request-line order:

| Field / setup | Exact fixture value |
| --- | --- |
| Additional item for each request | `T14 extra item <generated request ID>` |
| Additional unit for each request | `T14-EXTRA-<generated request ID>`, GOOD, AVAILABLE |
| Requested quantity per item | `1` (two distinct items per request) |
| Shared item / unit | Same `Test camera` / `TEST-CAM-001` last-unit competition |

Expected: one complete approval with exactly two allocations and two Reserved units. The loser stays Pending without decision metadata, allocations or audit, and its additional unit stays Available. This tests actual overlapping multi-item approvals, including an otherwise available item preceding the shortage; it does not implement issue/return or establish cancellation/issue concurrency.

### Actual verification and limits

On October 20, 2026, a **read-only local inspection at 07:55 Asia/Manila** verified PostgreSQL 17.5, Read Committed isolation and limits 7 days / 3 per item. The fixture snapshots above match those limits but do not read or modify live settings, accounts or stock. Actual automated results: the implementation run passed **2 focused tests in 0.894s**; the fresh publication run passed **254 full-suite tests in 39.994s**. Both runs created and destroyed the separate PostgreSQL test database. All required configured checks pass; see [integration receipt](../handoffs/t14-publication-main-integration-and-t15-readiness-10-20-2026.md).

Manual/browser simultaneous submissions are **Not run**. To record a fresh terminal reproduction, retain its command, revision, Asia/Manila timestamp, count and actual outcome in the result record below. T14 and T15 are integrated; T15 reached main through PR #42 at `744bc39`.

---

## Module 14 — Shared M3 Layout and Controls (UI-09)

**Owner:** Jerome Avecilla with Codex assistance. **Revision:** the original UI browser run used local `jerome` on main `01b25a9` (PR #38); UI-09 source `043822e` is now integrated through PR #39 at `a35e0f1`, preserved in main `866eb7e`. These are the original run results, not a new full UI execution. **Scope:** shared presentation across existing templates, not T15/T17 workflows or full T20 acceptance. Follow [DEV setup/build](../DEV.md#frontend-assets-tailwind-and-page-scripts) and the [canonical M3 component rules](coding-standards.md#shared-m3-roles-and-components-ui-09).

The October 20, 2026, **08:42 Asia/Manila read-only inspection** confirmed active fictional `auth_demo_admin` / `auth_demo_user` accounts, limits 7 days / 3 per item, active item IDs 21/1/2, unit IDs 2/3/4, maintenance IDs 1/2/3 and that the fictional borrower's request #3 was Approved. These are dated local fixtures, not a seed promise. Recheck your own records before opening their IDs; use your existing account's private password, never share credentials. UI checks need no new inventory, approval, cancellation or settings writes.

### UI09-01: Build and compare responsive layouts

```powershell
npm.cmd ci
npm.cmd run build
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

The build reads the fixed palette from `app.css`, verifies nine foreground/background role pairs at **at least 4.5:1** without a third-party color library, then compiles shared CSS and browser modules. There is no separate `theme.css` request. Restart the server after source changes when using `--noreload`; otherwise use the ordinary development server's template reload behavior.

| Field / action | Value / expected result |
| --- | --- |
| ADMIN entry pages | `/manage/`, `/manage/items/`, `/manage/units/new/`, `/manage/requests/`, `/manage/settings/`, `/manage/audit/` |
| BASIC_USER entry pages | `/portal/`, `/portal/equipment/`, `/portal/requests/new/`, `/portal/requests/`, `/portal/profile/` |
| Compact viewport | `320 × 1000` and `375 × 1000`; single-column fields/cards, compact account avatar and horizontally scrollable tabs |
| Medium viewport | `768 × 1000`; no whole-page horizontal overflow |
| Sidebar breakpoint | `1023 × 1000` keeps compact navigation; `1024 × 1000` has a 240px desktop sidebar and remaining-width main column. |
| Expanded viewport | `1440 × 1000` and `1920 × 1000`; white panels, neutral gray canvas, teal active navigation, matching header/main gutters and adaptive catalog tracks |
| Form breakpoint | Unit form at `839px` uses one field column; `840px` uses two. Equipment/asset code and condition/acquisition date share rows. |
| Request form breakpoint | At `1440px`, purpose/date and requested-item rows occupy adjacent 1:2 panes; compact screens stack them. |
| Home shortcuts | ADMIN: equipment, requests, accounts, maintenance plus settings/audit tools; two panel columns from 1200px. BASIC_USER: equipment, request creation, own requests, profile. Each opens an existing named route; no static dashboard counts are shown. |

Expected: consistent labels, input height, primary/tonal/outlined/destructive action emphasis, surface shape and table spacing. Controls are at least 48px high. Long tables scroll inside their own region while the page remains within the viewport. Labels remain associated with controls; view pages have no duplicate IDs.

### UI09-02: Keyboard, motion, scrolling and error states

| Field / action | Concrete value / expected result |
| --- | --- |
| Keyboard entry | Reload an ADMIN page, `Tab` to Skip to content and `Enter`; focus moves to main content with no missing tab destination. |
| Profile link | At 320/375/640/768/1023/1024/1440/1702px, the top workspace bar shows the avatar, display name and role without a dropdown. Click it or focus it and press Enter: ADMIN opens `/manage/profile/`; BASIC_USER opens `/portal/profile/`. The link has `aria-current="page"` on the profile page. |
| Log out row | At 1024px and wider, the red icon/text row sits at the bottom of the sidebar with the same padding, spacing and icon size as the other links. At 320px it sits beside the brand. Confirm it remains visible at 1024 × 500. Activate it to submit a CSRF-protected POST, return to sign-in, then verify a protected profile URL redirects to sign-in. |
| Compact current destination | Open `/manage/audit/` at 320px; the active tab is revealed in the scrolling navigation. |
| Table scrolling | On `/manage/accounts/` at 320px, focus the named scrollable table region; arrow/trackpad scrolling reaches off-screen columns without scrolling the whole page sideways. |
| Reduced motion | Emulate `prefers-reduced-motion: reduce`; press/hover changes occur without animated transitions and keyboard focus remains visible. |
| Press feedback | Hold the New equipment item action before releasing; subtle scale feedback is visible. Release navigates to the existing item form without a business write. |
| Cancellation emphasis | Open the eligible request cancellation confirmation without submitting; Confirm cancellation uses the shared danger button. |
| Unicode queue filter | `q=²`; normal results/empty state, no exception. |
| Invalid date filters | From `2026-10-22`, through `2026-10-20`; bound range error without workflow writes. |
| Invalid request | Leave purpose, return date and item rows blank, then Submit request; bound errors retain labels/unique IDs and no request is created. |
| Invalid sign-in | Username/email `ui-check@example.invalid`, password `invalid-local-ui-check`; the generic sign-in error remains visible and readable. |
| Wrong role | BASIC_USER opens `/manage/items/`; custom 403 remains enforced and styled. |

Use the [result record](#recording-manual-results) for additional tests. Do not submit valid create/update/decision/cancellation actions just to inspect their appearance; their workflow cases remain in their existing modules.

### Actual execution and limits

The fixed-palette follow-up on October 20 passed **12 home/profile page checks** across both roles at 320/1024/1440px in Chrome **155.0.8059.84**: expected colors/font, visible profile link, one compiled stylesheet, no separate theme request and no page overflow. Both roles' direct profile navigation and logout passed **4 interaction checks**. All 31 semantic color values match the earlier generated palette exactly. The dependency-free build check accepts the nine text-role pairs and rejects low-contrast/missing-role fixtures without changing application CSS. The new campus-ui skill and Django skill passed metadata validation. See the [dependency/skill handoff](../handoffs/fixed-palette-and-shared-campus-ui-skill-10-20-2026.md) for verification and concurrent-work limits. Prior navigation acceptance remains in the [navigation handoff](../handoffs/sidebar-logout-and-topbar-profile-link-10-20-2026.md), with broader routes/forms in the [reference-design handoff](../handoffs/minimal-dashboard-reference-and-ui-review-10-20-2026.md).

The earlier UI follow-up PostgreSQL suite passed **254 tests in 42.919s** using a separately named test database after the standard shared test database run encountered fixture/teardown interference; see the handoff for the failed attempt. Configured build/format/template/Django/migration/pip/audit checks pass. These UI checks do not establish complete screen-reader conformance, Firefox/Safari results, every populated loan/return screen or the outstanding full lifecycle/manual cases. No business mutations were performed in the browser. Temporary sessions for the existing fictional accounts were used and logged out. No new account/inventory seed data or migrations were introduced. UI-09 is integrated; T15 is verified on `jerome` and still requires main integration for T17. T20 retains its workflow gates.

---

## Module 15 — Release, Due-Date Revision and Borrowing Slip (T15)

**Owner:** Jerome Avecilla (`jerome`). **Revision:** T15 source `74924dd` committed/pushed on `jerome` from main baseline `866eb7e`; **integrated through PR #42 at `744bc39`**. T13/T14 prerequisites and T16 are integrated. **Role:** active ADMIN. **Entry:** `/manage/requests/` → Approved request → **Revise due date** or **Release equipment**; **Issued loans** opens `/manage/loans/`. Run `npm.cmd run build` before starting Django so the native print button's module exists.

### Checked records and date boundaries

A **read-only local check on October 20, 2026, 15:38 Asia/Manila** found limits 7 days / 3 per item, two Approved requests, two Pending requests, two Reserved units and no loans. Both Approved owners were active BASIC_USER accounts and neither request had a loan. No live rows were changed for this guide or the browser checks.

| Request | Submitted | Original / agreed due date | Snapshot maximum due date | Complete reservation |
| --- | --- | --- | --- | --- |
| #3 | 2026-10-18 | 2026-10-24 | 2026-10-25 | One unit: `CEL-LAB-DMM-001`, item ID 13, request-item ID 5 |
| #4 | 2026-10-19 | 2026-10-21 | 2026-10-26 | One unit: `CEL-PHV-TRP-001`, item ID 5, request-item ID 6 |

Reservations had no release/cancellation/end timestamps and matched their Reserved units and requested quantities. These are dated, unexecuted live examples: recheck status, ownership eligibility, relationships and dates before use. The valid revised date is after submission, on/after today's campus date and within the request's snapshotted maximum, regardless of later settings changes. A stale/expired example is not evidence of a defect. If no valid date remains, the borrower must cancel and submit a new request; do not backdate live records.

### T15-01: Revise the agreed due date before issue

Open `/manage/requests/4/due-date/`. GET displays the existing date and changes nothing.

| Field | Value |
| --- | --- |
| Agreed due date | `2026-10-24` |
| Reason | `Laboratory schedule moved` |

**Expected:** Save redirects to request #4. Agreed due date becomes October 24; original desired date stays October 21, approval metadata and quantity/duration snapshots remain intact. Audit history shows `DUE_DATE_REVISED`, the administrator and old/new dates with the reason. No loan or unit-state change occurs.

| Invalid input / boundary | Expected |
| --- | --- |
| `2026-10-19` or earlier for request #4 | Bound date error; must be after submission and on/after today |
| `2026-10-27` for request #4 | Bound date error; exceeds the October 26 snapshot maximum |
| Blank reason or more than 500 characters | Bound reason error; no date/audit change |
| Date already stored as agreed due date | Bound error; no duplicate revision audit |
| Request #4 submitted October 19, revised to October 20 while today is October 20 | Valid boundary; release on that same campus date is allowed |

Invalid forms return 200 with errors. Non-Approved/already-issued actions return 409. Only use the same-day example when that date is still valid; it changes the due date if actually submitted.

### T15-02: Release once and inspect the loan/slip

After the successful revision above, open `/manage/requests/4/release/`.

| Field / control | Value |
| --- | --- |
| Request | #4, still Approved and unissued |
| Borrower | The existing active owner displayed on the request |
| Reserved asset | `CEL-PHV-TRP-001`, quantity 1 |
| Due date | `2026-10-24`, from the stored agreed date |
| Action | **Confirm release**; no actor, status or unit-selection fields |

**Expected:** GET and Cancel do not write. Confirm redirects to the generated `/manage/loans/<loan_id>/`; record the real ID. Request becomes Issued, the reserved unit becomes Issued, one Loan and one LoanUnit exist, and the allocation's release timestamp matches the loan's issue timestamp. The allocation remains active (no end timestamp) until a future return. `LOAN_RELEASED` appears in audit history for the Loan reference. Actor/time/date come from the server; forged workflow fields cannot override them.

Use **Borrowing slip** to open `/manage/loans/<loan_id>/slip/`. Check borrower name/username, request/loan IDs, issue date/time in Asia/Manila, issuer, agreed due date, and the exact asset code. **Print slip** opens native browser printing; navigation and controls do not appear in the printed content. Detail and slip use the same stored loan/assets. The list search accepts a loan ID or borrower username and shows issued/outstanding counts and Active/Closed state. Returns are not implemented by T15.

### T15-03: Conflicts, authorization and rollback

| Scenario | Expected |
| --- | --- |
| Repeat Confirm release, or revise an issued request | 409; no extra loan, LoanUnit, release audit or date change |
| Owner tries to cancel after issue | 409; active issued allocation remains intact |
| Pending, Rejected, Cancelled or returned request is submitted to release | 409; no loan or inventory changes |
| Current campus date is later than agreed due date | 409; revision within the original snapshot or a new borrower request is required |
| Missing/extra/ended/released allocations, mismatched item or non-Reserved unit | 409; all business records remain unchanged |
| Basic user directly opens any management form, list, detail or slip | 403; anonymous users redirect to login; inactive sessions are denied |
| Mutation without CSRF, or POST to list/detail/slip | 403 for missing CSRF; 405 for the read-only endpoint |
| Existing reservation's item/category is subsequently archived | Release remains possible under BR-13; archival does not strand an otherwise valid reservation |

Use the automated checks below for expired/inconsistent records and database-induced audit failure; do not corrupt or backdate live records to create these cases. PostgreSQL audit-constraint rejection must roll back the whole date revision or release. Two overlapping release attempts must produce one loan and one conflict; overlapping release/cancel must produce exactly one complete winner and one conflict.

```powershell
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_release borrowing.tests.test_release_concurrency --noinput
```

### Actual verification and remaining manual coverage

- Full PostgreSQL suite: **273 tests passed in 45.268s**, including 19 T15 tests and all 33 T16 maintenance tests. The focused T15/cancellation/T16 run passed 62 tests in 8.722s. Both race tests prove overlapping separate-connection lock waits before checking complete stored outcomes. Audit rollback uses real temporary PostgreSQL check constraints, with no mocked audit writer.
- Playwright CLI 0.1.22 / Chrome, October 20, 2026: an **isolated test database** supplied request #1 with `TEST-CAM-001` and `T15-BROWSER-002`. Browser revision changed October 23 to October 24; blank reason was rejected; keyboard Tab reached Save; release Cancel returned without issuing; Confirm created loan #1 with both assets and counts `2 / 0 / 2`. Search, detail, slip, native print invocation and hidden print controls passed. Screenshots at desktop 1440px and compact 390/320px were inspected; tested pages stayed within the viewport, with local table scrolling. Browser console had no errors or warnings. These fixture IDs are **not live records**.
- Initial focused run failed because the new print module had not been built; `npm.cmd run build` fixed that prerequisite and the rerun passed. Configured checks are recorded in the handoff. Repository-wide Ruff formatting reports three untouched files; changed Python files pass formatting. No T16 lifecycle browser result is inferred from T15 checks.
- Actual live release/revision examples above, more-than-25-loan pagination, Firefox/Safari, physical printer output and complete screen-reader testing are **Not run**. Record new outcomes in the shared result table. T15 is now integrated through PR #42 at `744bc39`; T17's return checks are recorded in Module 16.

## Module 16 — Per-unit returns and overdue (T17)

**Owner:** Ralph Andre F. Giga (`ralph`) with Codex assistance. **Revision:** source `bd62ed7`, integrated through PR #43 at main `55899d0`; T15 source `74924dd` is integrated through PR #42 and T16 corrections `d68d7f7` through PR #33. T17 is **Done and integrated**; the merged source passed 294 PostgreSQL tests in 107.414s during Jerome's review. **Role:** active ADMIN for returns; active BASIC_USER for own tracking. **Entry:** `/manage/loans/` → loan → **Return units** (`/manage/loans/<loan_id>/returns/new/`). Build assets first using `npm.cmd run build`.

### Setup and dated data check

Ralph's earlier October 20 read-only check found no loans. The reviewer's read-only check at **18:23 Asia/Manila, October 20, 2026**, found **1 loan, 1 outstanding loan unit and 0 returns**, with limits of **7 calendar days / 3 units per item**. A one-unit loan supports final-return testing; the two-unit examples below remain disposable fixtures. No live records were created to write this guide. Prepare an eligible loan through the existing submission, approval and [release workflow](#module-15--release-due-date-revision-and-borrowing-slip-t15), using fictional identities and currently Available units. Recheck limits, current date and asset eligibility before doing so. A two-unit loan permits partial and final returns; a one-unit loan closes on its first return.

The concrete examples below were executed in a disposable browser-test database: loan #1, unit `TEST-CAM-001` (first LoanUnit) and `T17-CAM-002` (second LoanUnit), both from `Test camera`. These IDs/assets **are not current live loan records**. In another database, use the actual loan ID and issued-unit choices shown on the page. The temporary database was removed after checking the flow.

### T17-01: Partial healthy return

Open the issued loan detail, confirm quantities `2 / 0 / 2`, then choose **Return units**. Opening the form or selecting **Cancel** must leave every stored value unchanged.

| Field | Value |
| --- | --- |
| Unit 1 → Return this unit | Checked |
| Unit 1 → Issued unit | `TEST-CAM-001 · Test camera` |
| Unit 1 → Returned condition | `Fair` |
| Unit 1 → Return notes (admin only) | `Inspected on receipt` |
| Unit 1 → Maintenance problem | Blank |
| Unit 2 → Return this unit | Unchecked |
| Submit | Confirm selected returns |

**Expected:** 302 to loan detail with a success message; request becomes Partially returned; quantities `2 / 1 / 1`; loan stays Active with no closure timestamp. First unit becomes Available/Fair; its allocation has an end timestamp matching its ReturnRecord, while its original release timestamp/history remain. The unselected unit stays Issued with an active allocation. One `UNIT_RETURNED` audit identifies the receiving administrator and ReturnRecord. Reloading the return form displays only the remaining outstanding row.

### T17-02: Damaged final return and maintenance

| Field | Value |
| --- | --- |
| Remaining row → Return this unit | Checked |
| Remaining row → Issued unit | `T17-CAM-002 · Test camera` |
| Returned condition | `Damaged` |
| Return notes (admin only) | `Damage found during inspection` |
| Maintenance problem | `Cracked lens` |
| Submit | Confirm selected returns |

**Expected:** 302 to loan detail; quantities `2 / 2 / 0`, request Returned, loan Closed, and no Return units action. Closure timestamp equals the final return timestamp. The damaged unit becomes Maintenance/Damaged, its allocation ends, and exactly one matching open MaintenanceRecord references this ReturnRecord and physical unit. Both `UNIT_RETURNED` and `MAINTENANCE_OPENED` audits commit together. Open the existing maintenance list/detail to inspect the problem and perform the [T16 repair/retirement cases](#module-11--equipment-maintenance-and-inventory-reconciliation-t16). Good/Fair returns instead become Available directly. Returning both rows in one submission must also close the loan with complete records and matching totals.

Sign in as the owner and inspect `/portal/loans/`, the loan detail and its request detail. Returned condition/date and current request status must match management; return notes and maintenance problem text must be absent. A different borrower receives 404 for those detail IDs. Basic users cannot open or POST the management return form.

### T17-03: Invalid inputs, stale submissions and atomicity

| Case / Field | Value or action | Expected result |
| --- | --- | --- |
| Selection | Leave every Return this unit unchecked | 200 with bound formset error; no return or inventory changes |
| Returned condition | Blank on a checked row | 200 with field error; all rows remain unchanged |
| Maintenance problem | Blank or spaces with Damaged | 200 with field error; no ReturnRecord/maintenance/audit writes |
| Duplicate units | Select the same Issued unit in both checked rows | 200 with formset error; no writes |
| Foreign/nonexistent LoanUnit | Forge a row's `loan_unit` ID from another loan | 200 with choice error; no writes; direct service callers also reject foreign membership |
| Oversized/missing management form | Set `returns-TOTAL_FORMS=10000`, or omit management fields | 200 with formset errors; no partial records |
| Mixed validity | First row Good; second row Damaged with no problem | Both rows rejected together, with no partial return |
| Already returned unit | Resubmit an old selected unit while another remains outstanding | 409 when the row count remains valid; no additional return. An old form exceeding the new outstanding-row maximum receives a 200 formset error |
| Fully returned loan | Open or POST the old return URL | 409; no form or duplicate return |
| Wrong actor/date/status/unit | Forge `received_by`, `returned_at`, `status` or physical `unit` fields | Ignored; receiving actor and timestamp come from the server, relationships from the addressed LoanUnit |
| Basic user / anonymous | Open or submit the management URL | 403 / sign-in redirect; no writes |
| Inactive administrator session | Request the URL after deactivation | 403 and session termination; subsequent anonymous requests redirect to login |
| Missing CSRF / wrong method | POST without token / PUT | 403 / 405; no writes |
| Borrower deactivated or catalog archived after issue | Active admin receives an existing issued unit | Return remains possible; existing equipment is recoverable |

Use automated tests for deliberately inconsistent relationships/timestamps, temporary audit-constraint failures and overlapping transactions. Do not corrupt live data to prepare these cases. A return or maintenance audit failure must roll back every selected return, unit/condition change, allocation end, maintenance record, request transition and loan closure.

### T17-04: Derived overdue behavior

| Loan state / campus date | Expected |
| --- | --- |
| Outstanding; before or on due date | Active, overdue days 0, no Overdue label |
| Outstanding; one calendar day after due date | Active, Overdue 1 day |
| Partially returned; two calendar days after due date | Still Active, Overdue 2 days; issued/returned/outstanding counts reflect the partial return |
| All units returned, even after due date | Closed, overdue days 0, no Overdue label |

October 20 example: an outstanding loan due October 18 is 2 days overdue; a loan due October 20 is not overdue. These are dated examples, not live loans. The automated test passes dates explicitly around a loan's stored due date. HTTP integration checks render an overdue fixture on both roles' loan lists/details and verify the labels disappear after its final return. Reads must not write an overdue request status or change any timestamps. Historical date preparation is limited to disposable test fixtures.

### Read-only stored verification and executed results

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from borrowing.models import Loan; print(list(Loan.objects.values('id', 'request__status', 'issued_on', 'due_date', 'closed_at')))"
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_returns borrowing.tests.test_return_concurrency --noinput
```

For an actual loan ID, inspect its ReturnRecord `loan_unit_id`, `received_by_id`, `returned_at`, condition, corresponding allocation `ended_at`, and MaintenanceRecord `source_return_id`/`unit_id` with read-only ORM queries. The existing administrator unit history, maintenance pages and audit search provide the review paths. Keep tokens, passwords and private identities out of results.

- **Automated:** 21 T17 tests passed in 6.283s; the complete 294-test PostgreSQL suite passed in 109.763s. Tests use the real approval/release/return services, PostgreSQL audit check constraints, and separate backend connections with observed lock waits. Duplicate returns produce one success/one conflict and one return/maintenance/audit pair; different units on the same loan both return and the second closes the loan.
- **Browser:** Chrome 155.0.8059.84, October 20, 2026, isolated database. Passed form/labels, keyboard focus from Confirm to Cancel, cancellation without writes, blank damaged-problem error, Fair partial return, damaged final return, closed-loan 409 and owner portal privacy. Layout bounds passed at 1440/390/320px; desktop and compact screenshots were inspected. No unexpected console or JavaScript errors. Disposable database/session files were removed; no live business records were changed.
- **Merged-source review:** all 294 PostgreSQL tests passed in 107.414s on `55899d0`; the browser results above are Ralph's earlier checks, not a fresh browser run. Live records were inspected read-only and were not returned or otherwise modified.
- **Not run:** Firefox/Safari, complete screen-reader evaluation, live populated loan execution, full T16 maintenance lifecycle in a browser, full T20 acceptance or system-wide user acceptance. Existing manual results from other modules remain separate.

## Module 17 — Live administration dashboard (T18)

**Status:** Done and integrated through PR #45 at `26b1ee5`, source `54380fd`. Fresh merged-source review passes all 298 PostgreSQL tests in 56.385s; see the [review receipt](../handoffs/t18-main-integration-review-and-t19-readiness-10-20-2026.md). Alex / T19 used these accepted prerequisites and is now integrated through PR #49 at `e8f2a19`.

**Entry URL:** `/manage/`

**UI-11/UI-12 follow-up:** The Chart.js dashboard and Kiro-assisted workspace improvements are integrated through user-merged PR #48 at `9d67fab`. Combined source `f3d42ba` is committed/pushed on `origin/jerome` with Codex/Kiro credit recorded; source/receipt ancestry and exact published-tree equality are verified. Install the locked npm packages and rebuild assets before reviewing. T18's integrated baseline and Alex's credit remain intact; see [publication review](../handoffs/dashboard-and-workspace-publication-review-10-20-2026.md).

**Required role:** Active `ADMIN`. Use fictional/disposable workflow records only. Do not change production-like records merely to make a chart look populated.

**Read-only local snapshot:** Rechecked October 20, 2026 Asia/Manila during combined UI-11/UI-12 publication review on `jerome` (based on `5527432`). The configured development database reported the following values inside a transaction verified as `transaction_read_only = on`; this inspection changed no live records:

| Field | Value |
| --- | ---: |
| Campus date | `2026-10-20` |
| Available units | `9` |
| Pending requests | `2` |
| Active loans | `1` |
| Overdue loans | `0` |
| Monthly chart points | `1`: `Oct 2026`, `2` loans |
| Category chart points | `2`: `Photography & Video`, `3` issued units; `Audio Visual Equipment`, `1` issued unit |

Recheck these values before every manual run; they are a dated local snapshot, not demonstration data or a permanent expected total.

### T18-01 - Access, methods and empty state

| Action / field | Value |
| --- | --- |
| Anonymous request | `GET /manage/` |
| BASIC_USER request | `GET /manage/` |
| Active administrator request | `GET /manage/` and `HEAD /manage/` |
| Wrong method | `POST /manage/` with any field, such as `available_units=999` |
| Inactive administrator | Sign in while active, deactivate that account from a separate active-admin session, then revisit `/manage/` |

Expected results:

- Anonymous access redirects to login with a safe `next=/manage/`; BASIC_USER access returns 403.
- Active ADMIN GET/HEAD returns the shared administrator shell and current database values; POST returns 405 and changes nothing.
- An inactive administrator receives 403 and the existing session is invalidated.
- With the dated snapshot above, cards show `9`, `2`, `1`, `0`; the monthly chart contains one point and the category chart two. In a disposable database with no business records, all four cards show `0`, and the two useful empty messages read `No issued loans yet.` and `No issued equipment usage yet.`

### T18-02 - Cards and charts follow committed workflows

Prepare one fictional category with one item and two Available physical units, then submit one request for quantity `2`. Refresh `/manage/` after every committed step.

| Step | Expected dashboard result |
| --- | --- |
| Pending request committed | Pending requests increases by `1`; both units remain Available |
| Request approved | Pending requests decreases by `1`; Available units decreases by `2`; Active loans remains unchanged |
| Approved request released once | Active loans increases by `1`; the issue month's chart increases by `1`, not by the two issued units; the category chart increases by `2` |
| First unit returned Good or Fair | Available units increases by `1`; Active loans remains `1`; category issued-unit usage remains `2` |
| Final unit returned Damaged | Active loans decreases by `1`; Available units stays at `1`; category issued-unit usage remains `2`; the damaged unit follows T17 maintenance behavior |

If the loan is already past its stored due date on the campus date, Overdue loans follows Active loans through the partial return and drops after the final return. If no eligible historical overdue fictional loan exists, record that overdue browser case as **Not run** rather than modifying live dates outside the controlled seed workflow.

### T18-03 - Chart safety, readability and responsive layout

| Check | Expected result |
| --- | --- |
| Category label containing `<`, `>` or `&` in a disposable test database | The label renders as text; it cannot close the embedded JSON script or inject markup |
| Monthly chart | Columns are chronological from the first release through the current month, including months with zero releases; each loan contributes once |
| Category chart | Horizontal bars rank categories by issued-unit count, highest first, with alphabetical ties; each issued LoanUnit contributes once, including returned units and repeat issues |
| Axes and exact values | Count axes begin at zero with whole-number ticks; hovering/tapping a bar shows its full label and exact count; category tooltips wrap on compact screens |
| Data disclosure | `View monthly chart data` and `View category chart data` expose the same labels/counts in tables |
| Keyboard | Navigation, disclosure controls and real workflow links remain keyboard reachable with visible focus |
| Widths | Check desktop plus `390px` and `320px`; cards stack, charts remain readable and the page has no viewport overflow. Long month histories scroll inside the chart region; many categories scroll vertically inside their region. Full category names remain in tooltips/tables |
| JavaScript disabled | The disclosure tables retain the stored chart data even though enhanced bars are absent |

Do not backdate live records to manufacture chart history. If historical releases or multiple categories are unavailable, record those browser cases as Not run; the automated chart-history case uses disposable PostgreSQL records.

### T18-04 - Dashboard card actions (UI-11)

| Control | Expected destination and result |
| --- | --- |
| `dashboard-view-available` | `/manage/units/?status=AVAILABLE`; existing unit filter is selected |
| `dashboard-review-pending` | `/manage/requests/?status=PENDING`; existing request filter is selected |
| `dashboard-view-loans` | `/manage/loans/`; existing issued-loan records and progress |
| `dashboard-review-due-dates` | `/manage/loans/`; inspect stored due dates and overdue labels. This existing list has no active/overdue filter; the link does not imply one |

Use Tab/Enter as well as pointer input, then return to the dashboard. Confirm the four cards describe the current state, while chart totals describe all recorded releases. Refresh after a real authorized transaction to obtain new values; the dashboard does not poll automatically.

Use this read-only command to recheck card and series sizes without exposing borrower identities:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from django.utils import timezone; from operations.queries import dashboard_snapshot; snapshot=dashboard_snapshot(timezone.localdate()); print(timezone.localdate(), snapshot.cards, len(snapshot.monthly_issued_loans), len(snapshot.category_issued_units))"
```

### T18-05 - Workspace shortcuts, pending badge and filters (UI-12)

| Field / action | Expected result |
| --- | --- |
| Active ADMIN; Pending count `0` | Borrowing navigation has no badge |
| Active ADMIN; Pending count `2` in the dated live snapshot | `nav-manage-borrowing-badge` displays `2`, with an accessible count; dashboard Pending card also reads `2` on reload |
| Disposable queue count `100` | Badge displays `99+`; its accessible label retains `100 pending requests`. Do not create live requests merely to run the cap case |
| BASIC_USER, anonymous or deactivated administrator | No administrator badge context is supplied; protected management pages retain their role/active-account behavior |
| Dashboard versus request queue | Inactive badge uses teal/white; active Borrowing badge inverts to white/teal. Counts follow committed decisions on the next page load |
| `home-manage-equipment`, `home-manage-requests`, `home-manage-accounts`, `home-manage-maintenance` | Full-width shortcut rows retain their named routes; the final Maintenance row has no trailing separator |
| `home-manage-settings`, `home-manage-audit` | Existing tool rows remain functional; the final Audit row has no trailing separator |
| `/manage/requests/` | Clear filters appears before Search requests. Submit a harmless search and clear it using the real controls; refer to [T13 queue cases](#t13-01-queue-filters-and-read-only-detail) for filter behavior |
| Desktop and `320px` / `390px` | Badge aligns within navigation; page stays within viewport. Equipment subnav tabs remain content-width rather than stretching across their row |

### T18 verification

- **Implementation verification:** Alex's original run passed 4 focused T18 PostgreSQL tests in 0.304s, 32 operations tests in 3.864s and the complete 298-test suite in 54.443s; see [his snapshot](../handoffs/alex-t18-live-administration-dashboard-10-20-2026.md). Coverage includes actual approval/release/partial/final-return services, returned-unit category totals, one-loan monthly counts, active/overdue changes, empty states, safe JSON embedding, active-admin access, inactive-session denial and 405 POST behavior.
- **Frontend build:** Fresh theme contrast, Tailwind and JavaScript builds pass, including `dashboard-charts.js`.
- **Merged-source review:** All **298 PostgreSQL tests passed in 56.385s** on `26b1ee5`, including the four T18 tests. Build/contrast, npm formatting/audit (zero vulnerabilities), Django database/schema/migration checks, Ruff lint, T18 Python/template formatting and pip consistency pass. Repository-wide Ruff formatting flags untouched `accounts/views.py`, `inventory/tests/test_portal_equipment.py` (line endings) and `handoffs/borrower-portal-ui-improvements-10-20-2026.md` (Python example); djLint flags untouched `templates/inventory/portal/equipment_list.html`. These remain separate cleanup findings; no application files were changed by this review.
- **Read-only local data:** The dated snapshot above was executed against the configured development database with `transaction_read_only = on`; no live records were changed.
- **Combined publication verification:** All **301 PostgreSQL tests pass in 48.703s**; 11 focused navigation/dashboard checks pass in 2.923s. The two added real navigation tests cover Pending counts after real approval/rejection, zero hiding, 99+ display/exact label and role isolation. Fresh Chromium 153 desktop/390px/320px, active/inactive badge colors, shortcut rows/borders, request Search/Clear, keyboard disclosures, subnav sizing and no-JavaScript tables pass. Clean npm install/build/audit and changed-file format checks pass; four earlier unrelated repository-wide formatting findings remain. Browser/server contexts were closed and disposable review data removed. See [publication review](../handoffs/dashboard-and-workspace-publication-review-10-20-2026.md).
- **UI-11 automated:** Five focused PostgreSQL dashboard tests passed in 0.419s; the full suite passed **299 tests in 56.043s**. The added real-ORM case verifies an idle month and category ranking; existing partial/final-return, access and JSON-safety checks remain passing.
- **UI-11 browser:** Chromium 153.0.8010.12, October 20 Asia/Manila, disposable database. Desktop 1440px, 390px and 320px bounds/screenshots pass. Exactly two populated charts, integer zero-based axes, hover/tap tooltips (including a long category label), both native data disclosures, four card destinations, keyboard horizontal scrolling and JavaScript-disabled tables pass. Empty-state review shows real inventory and two empty messages with no canvases. No JavaScript errors observed. Browser contexts/server were closed and the disposable database was removed; no live business data changed.
- **UI-11 browser fixture:** Cards `11 / 1 / 3 / 1`; May–October 2026 monthly counts `1 / 3 / 0 / 2 / 0 / 2`; category counts `6 / 6 / 4`, including returned units. These are isolated verification records, not the live snapshot or T21 demonstration dataset.
- **Not run:** Firefox/Safari, complete screen-reader evaluation, performance measurement, many-category vertical scrolling, live transaction mutations in a browser and system-wide acceptance. Alex's earlier Not run browser state remains historical in his handoff.

## Module 18 — Administrator loan and overdue reporting (T19)

**What you are testing:** an administrator can view loans, filter by issue date and download the same results as CSV. T19 is integrated through PR #49; the current reviewed checkout is `6f18116` (PR #51).

### Before you start

1. Start the app using [the everyday startup steps](../DEV.md#everyday-startup). Open `http://127.0.0.1:8000/accounts/login/` and sign in with your existing **administrator** test account.
2. Follow T19-01 through T19-05 in order. Record your results in [the checklist](#t19-and-t20---your-test-checklist).
3. If a case needs records you do not have, write **Not run - needs test data**. An empty report can be correct.

**Verified local example, October 21, 2026, 16:38 Asia/Manila:** a read-only check found these two loans. These are a dated starting point; this guide did not create them. If someone changes loans/returns, use current loan details instead of expecting these old totals.

| Loan | Issued on | Due date | Issued units | Returned | Outstanding | Loan status on October 21 |
| --- | --- | --- | --- | --- | --- | --- |
| #1 | 2026-10-20 | 2026-10-24 | 1 | 1 | 0 | Closed |
| #2 | 2026-10-20 | 2026-10-23 | 3 | 0 | 3 | Active |
| **Totals: 2 loans** | | | **4** | **1** | **3** | |

Neither loan is overdue on October 21, so an **empty Overdue report with zero totals is correct**. Overdue means the due date is **before today** and units are still outstanding. Due today is not overdue. Date filters use **Issued on**, not Due date.

### T19-01 - Open both reports

| Step | What to do | What should happen |
| --- | --- | --- |
| 1 | Open `/manage/reports/loans/`. Click **Clear filters**. | Loan report opens; Reports is selected in navigation. |
| 2 | Compare rows and totals with current loan details. | For the unchanged example: 2 loans, 4 issued, 1 returned, 3 outstanding. #1 is Closed; #2 is Active. |
| 3 | Click **View overdue report**. | Only outstanding loans due before today appear. For the October 21 example: no rows and zero totals. |
| 4 | Click **View all loans**. | You return to Loan report. Viewing reports changes no transactions. |

**Pass when:** both pages open and match current records. An empty Overdue report is a pass when no loan is overdue.

### T19-02 - Filter by issue date

On Loan report, enter each row below and click **Filter report**. If the database changed, substitute an actual issue date from a visible loan.

| Issue date from | Issue date through | Expected for the verified example |
| --- | --- | --- |
| 2026-10-20 | 2026-10-20 | Both loans appear. The boundary dates are included. |
| 2026-10-21 | 2026-10-21 | No loans; zero totals. |
| Leave blank | 2026-10-20 | Both loans; no lower date limit. |
| 2026-10-20 | Leave blank | Both loans; no upper date limit. |

Repeat on Overdue report: the same issue-date rules apply, but non-overdue loans must stay excluded. Click **Clear filters** afterward.

**Pass when:** dates select the correct loans and **issued - returned = outstanding** for each row. Summary totals cover all matching records, not just the visible page.

### T19-03 - Download and compare CSV

1. On Loan report, set both dates to `2026-10-20` (or a current issue date you checked). Click **Filter report**.
2. Write down the four summary totals. Click **Download CSV** and open `loan-report.csv` in Excel or another spreadsheet application.
3. Compare loan IDs, dates, statuses and quantities with the webpage. A spreadsheet may display dates in a different style.
4. Check the final `TOTALS` row. For the unchanged example: **2 loans; 4 issued / 1 returned / 3 outstanding**. This totals row is not another loan.
5. Repeat on Overdue report. It downloads `overdue-report.csv` with an **Overdue days** column. An empty report still downloads headings and a zero totals row.

**Pass when:** both files open correctly and match the filtered reports. CSV includes **all matching loans**, including other pages. If no spreadsheet application is available, mark the opening check **Not run**.

### T19-04 - Check phone width and keyboard use

1. Open a report at desktop width, then at **390px** and **320px** using the browser's responsive/device toolbar.
2. Check that labels/buttons remain readable. The table can scroll sideways inside its own area; the whole page should not scroll sideways.
3. Use **Tab**, **Shift+Tab** and **Enter** to reach date fields, Clear filters, Filter report and Download CSV. Focus must stay visible.
4. If Next/Previous appears, use it: date filters must stay in the address bar. With 25 or fewer matching loans, record pagination **Not run - needs more than 25 loans**.

### T19-05 - Check errors and restricted access

| What to do | Expected result |
| --- | --- |
| Enter From `2026-10-21`, Through `2026-10-20`; click Filter report on both reports. | Date-range error; no unfiltered rows or download action. |
| Open `/manage/reports/loans/export/?date_from=2026-10-21&date_to=2026-10-20`; repeat with `/manage/reports/overdue/export/`. | HTML error page instead of a CSV download. |
| Sign out; open all four report/export URLs below. | Each sends you to login. |
| Sign in as a basic user; open the same four URLs directly. | Each shows Access denied (403); no report data or download. |

Protected URLs: `/manage/reports/loans/`, `/manage/reports/overdue/`, `/manage/reports/loans/export/`, `/manage/reports/overdue/export/`. A correctly blocked request is a **Pass**.

### T19 additional checks - need prepared data or developer tools

Record missing setup as **Not run**. Do not edit stored dates or your computer clock just to force a case.

| Setup needed | Expected result |
| --- | --- |
| Overdue, partially returned, fully returned and due-today loans | Only outstanding loans due before today appear in Overdue. Partial returns reduce Outstanding; final returns make Closed and remove the loan from Overdue. Use [Module 16](#module-16--per-unit-returns-and-overdue-t17) for return steps. |
| More than 25 matching loans | Page 2 preserves filters; CSV includes all matching rows in newest issue-date/time/ID order. Invalid pages (`0`, `abc`, out of range) return 404. |
| Disposable fictional text containing Unicode, commas, quotes and newlines | CSV keeps text in the correct cells. Text beginning with `=`, `+`, `-`, `@`, tab or carriage return is apostrophe-prefixed and treated as text, not a formula. |
| Developer tools / existing report integration suite | GET works; HEAD/POST and unsupported methods return 405 on all four routes. `date_from=not-a-date` gives HTML errors, including exports. CSV uses UTF-8 BOM and `text/csv; charset=utf-8`. Report reads/exports write no business data. |
| Existing [report integration suite](../operations/tests/test_reports.py), using its isolated test database | The inactive-admin test verifies denial/session removal on all four routes. The account-management UI only deactivates BASIC_USER accounts; it cannot prepare an inactive administrator. Run the existing automated case instead of changing a live admin account. |

### T19 verification

**Previous evidence:** [T19 review](../handoffs/t19-main-review-and-local-merge-conflict-resolution-10-21-2026.md): 315 PostgreSQL tests passed. [Later T20 integration review](../handoffs/t20-main-integration-review-and-documentation-10-21-2026.md): 322 passed, including all 11 report tests. [Ralph's delivery](../handoffs/ralph-t20-role-workspace-integration-10-21-2026.md) records report browser checks at five widths, CSV downloads and parsed totals. Detailed commands, fixtures and limitations remain in those handoffs.

**This guide update:** read-only data inspection only; no new browser/spreadsheet run. Spreadsheet opening, screen-reader and extra-browser checks remain pending. Fill in your own results below.

## Module 19 — Integrated role workspaces (T20)

**What you are testing:** borrower Home shows that user's real records, and both roles have consistent navigation, forms, messages and usable small-screen pages. T20 is integrated through PR #51 at `6f18116`, source `b43fb99`.

### Before you start

- Use existing fictional **basic-user** and **administrator** test accounts. Use two separate browser profiles, or one normal window and one private/incognito window. Ordinary windows and tabs in the same profile share a session; multiple private windows also share their private session.
- The app should be running at `http://127.0.0.1:8000`. If styling is missing, follow [asset setup](../DEV.md#fonts-and-static-assets).
- October 21, 16:38 read-only check: three active basic users, one active admin; limits **7 loan days / 3 units per item**. Home counts vary by owner.
- **T20-02 creates and cancels one fictional request.** Use an account you are permitted to change. The other basic walkthrough steps inspect pages.

### T20-01: Home summary, ownership and empty states

Sign in as a **basic user** and open `/portal/`.

| Step | What to do | What should happen |
| --- | --- | --- |
| 1 | Look at the four cards. | Pending requests, Approved requests, Active loans and Overdue loans count this account's records only. Zero is allowed. |
| 2 | Open Pending requests; return Home and open Approved requests. | My requests opens with the matching Status selected. Count matching requests across all pages to compare with each card. |
| 3 | Open Active loans. | Full own-loan history opens. It can include Closed loans; the card counts only loans with outstanding units. |
| 4 | Return Home; click Overdue loans. | Focus moves to Equipment to return on this page. This is a preview shortcut, not an overdue-only list. |
| 5 | Check Equipment to return and Recent requests. | At most five active loans, earliest due first; five requests, newest first. View all links open full histories. |
| 6 | Open a preview detail, Browse equipment and My profile. | The existing pages work; details belong to this borrower and the correct parent navigation stays selected. |

**Empty account:** expect zero cards and Nothing to return / No requests yet. Try its browse/create links; mark populated-preview checks **Not run - account has no records**. Pass when counts/links agree with this user's histories.

### T20-02: Forms, filters, confirmations and status text

As the basic user, note the Pending requests count, then click **Create a request**.

| Field | Value |
| --- | --- |
| Purpose | `T20 classroom equipment check` |
| Desired return date | `2026-10-23` for October 21; on another day use campus today + 2 days within current limits |
| Equipment item | One active item actually offered in the form |
| Quantity | `1` |
| Other equipment rows | Leave both item and quantity blank |

1. Fill the table, but leave Purpose blank for the first submission. Submit: a browser/field error should appear and **no request** should be created.
2. Enter the Purpose and submit again: expect a success message on My requests. Find `T20 classroom equipment check`, open it and note its ID.
3. Return Home: Pending should increase by **one**, and the request should appear in Recent requests (assuming nobody else changed this account's records).
4. Open that request's cancellation action; choose **Keep request**. It stays Pending. Opening a confirmation changes nothing.
5. Reopen cancellation; click **Confirm cancellation**. Expect a success message and Cancelled status. Pending returns to its original count; the request stays in history.
6. Open `/portal/requests/?status=INVALID`. Expect a filter error and recovery content. Click **Clear filters** to restore the normal list.

**Pass when:** invalid submission creates nothing; valid submission creates one request; Keep preserves it; confirmation updates status/message/count. A correct validation error is a pass.

### T20-03: Responsive, keyboard, downloads and recovery

| Step | What to do | What should happen |
| --- | --- | --- |
| 1 | As borrower, visit Home, Equipment, My requests, My loans and My profile. | Consistent layout, working links and correct active parent navigation, including details. |
| 2 | As admin in the separate profile or private window, visit `/manage/`, requests, loans and both reports. | Admin navigation and the shared field/status/message styles work. Test downloads using T19-03. |
| 3 | Repeat representative pages at desktop, 390px and 320px widths. | Readable controls; wide tables scroll within their area, not the whole page. |
| 4 | Use Tab, Shift+Tab and Enter, including Skip to content and confirmations. | Visible focus, usable labels/controls and readable status text, not color alone. |
| 5 | As borrower, open `/manage/`; as admin, open `/portal/`. | Access denied (403); return-home recovery leads to the correct role Home. |
| 6 | Use **Log out** in each role, then reopen its protected Home. | Login is required again. Use the real logout control. |

### T20 additional checks - run when records are ready

| Setup needed | What to check |
| --- | --- |
| Second borrower with a known request/loan ID | First borrower gets 404 for that foreign detail. Home `?owner_id=999999&user_id=999999` still shows the signed-in user's records. |
| More than six Pending requests | Filter My requests to Pending; Next/Previous retain Status. |
| More than five requests/active loans | Previews stay capped at five; counts cover all matching records. |
| Request eligible for approval/release | Follow [Module 12](#module-12--administrator-request-review-and-decisions-t13) and [Module 15](#module-15--release-due-date-revision-and-borrowing-slip-t15). Back-out preserves state; approval moves Pending to Approved; release removes Approved and adds an Active loan. |
| Multi-unit loan eligible for return | Follow [Module 16](#module-16--per-unit-returns-and-overdue-t17). Partial return keeps the loan Active with fewer outstanding units; final return removes it from Active. A final damaged return also creates maintenance. |
| Overdue / due-today loans | Only outstanding loans due before today count as Overdue; due today is not overdue. Do not alter dates/clock to force it. |
| Empty borrower / JavaScript disabled | Empty-state browse/create links and native logout work without JavaScript. Re-enable JavaScript afterward. |
| Developer tools / disposable inactive account | Home GET/HEAD is read-only; POST is 405; inactive sessions are denied/ended. Invalid return dates (today or today + maximum + 1) and quantity maximum + 1 (4 under checked settings) create no request. |

### T20 executed results

**Previous evidence:** [merged-source review](../handoffs/t20-main-integration-review-and-documentation-10-21-2026.md): **322 PostgreSQL tests passed in 127.102s**, including seven workspace tests. [Ralph's handoff](../handoffs/ralph-t20-role-workspace-integration-10-21-2026.md) records his earlier 322-test/87.253s run, 24 focused checks, 17 routes at five widths, keyboard checks, request/return/cancellation flows, CSV downloads and JavaScript-disabled navigation.

**This guide update:** no new browser run or user acceptance session. Screen-reader, Firefox/Safari, spreadsheet opening and complete maintenance-repair browser coverage remain pending. Subsequent T21/T22/T23 deliveries are Done/integrated; that does not turn these unrun browser checks into passes.

### T19 and T20 - your test checklist

Fill this after testing. For a failure, note the step and a screenshot or fictional record ID. Keep passwords/private details out. Blank entries below do not replace earlier execution evidence.

| Case | What it checks | Your result: Pass / Fail / Not run | Notes / record ID |
| --- | --- | --- | --- |
| T19-01 | Both report pages, rows and totals | Not run | |
| T19-02 | Issue-date filters and quantities | Not run | |
| T19-03 | CSV downloads and spreadsheet comparison | Not run | |
| T19-04 | Phone width, keyboard and available pagination | Not run | |
| T19-05 | Invalid ranges and restricted access | Not run | |
| T20-01 | Own home counts, previews and links | Not run | |
| T20-02 | Validation, submission, Keep request and cancellation | Not run | |
| T20-03 | Both layouts, phone width, keyboard, access and logout | Not run | |
| Additional checks | Name each extra check actually run | Not run | |

Use **Not run - needs test data** when appropriate. Record browser/version, date and revision with your results using the shared format below.

## Module 20 — Fictional demonstration dataset (T21)

T21 is **Done and integrated through PR #53** and includes the user-requested **August-October 22, 2026 transaction history**, using the existing manually entered equipment and seeded accounts. Source `e3402bf` and publication `ae6b147` are integrated at main `b828945`, with exact published/merge-tree equality verified; see [integration/acceptance evidence](../handoffs/t22-automated-system-acceptance-10-22-2026.md). [DEV.md](../DEV.md#seed-august-october-2026-transactions) owns the setup, expected dataset totals and repeat-run behavior; [the account table](../DEV.md#seed-the-t21-demonstration-dataset) lists every full name, username, email and private password source. These are realistic fictional demonstration events, not actual campus activity records.

### T21-01: Review the dated local records

The following read-only snapshot was verified **October 22, 2026, Asia/Manila**, after the transaction import. Settings remain **7 days / 3 units per item**. Recheck after any manual workflow action or date change; numeric IDs are workstation-specific, so identify records by borrower/purpose on another database.

| Field / record | Verified value |
| --- | --- |
| Existing inventory and photos | 12 categories, 29 catalog items, 46 units; all 23 photo paths/file hashes preserved |
| Accounts / Profiles | 1 ADMIN, 8 BASIC_USER accounts, 9 Profiles; same names/passwords as the DEV table |
| Partial overdue loan | Loan 27, Miguel Santos (`miguel.santos`), issued October 18, due October 21; camera returned October 20, tripod outstanding |
| Fully outstanding overdue loan | Loan 28, Sofia Reyes (`sofia.reyes`), laptop issued October 19, due October 21 |
| Current loan | Loan 29, Gabriel Cruz (`gabriel.cruz`), speaker issued October 21, due October 24 |
| Today's issue | Loan 30, Isabella Garcia (`isabella.garcia`), router/switch/cable issued October 22, due October 26 |
| Earlier completed loan | Loan 11, Miguel Santos; speaker issued/returned August 7, loan closed |
| Damaged return and repair | Loan 19; maintenance 10 on `CEL-LAB-DMM-001`, damaged lead returned October 6 at 14:05, repair closed October 8 at 15:00 |
| Approved cancellations | Requests 49 and 50 retain ended/cancelled allocations; no issued loans |
| Waiting for collection | Approved requests 51 and 52 |
| Pending queue | Requests 53, 54 and 55 |

All new submission/decision/reservation/issue/return/repair events fall in August through October 22. Due dates for outstanding loans extend through October 26. Original account/catalog entry times remain their real database import times; they can be later than these imported events. Physical-unit acquisition dates and historical allocation/maintenance windows were validated without changing existing inventory dates.

### T21-02: Check dashboard and filtered reports

1. Sign in as `andrea.mendoza` at `/accounts/login/` using the private seed password. Open `/manage/`. Expect monthly issued-loan bars **Aug 2026 = 3, Sep = 4, Oct = 13**, with category usage from the real catalog. Expected cards on October 22: **30 Available / 3 Pending / 4 active loans / 2 overdue loans**.
2. Open `/manage/reports/loans/`. With empty date filters, expect **20 loans / 34 issued units / 28 returned / 6 outstanding**. Set the inclusive issue-date range to the following values and search:

| Field | Value |
| --- | --- |
| From | `2026-10-01` |
| To | `2026-10-22` |

Expected October-only totals: **13 loans / 23 issued units / 17 returned / 6 outstanding**. Export the same filter and compare rows/totals. Requests are not the monthly chart's unit of counting; it counts issued loans.

3. Open `/manage/reports/overdue/`. Expect only loans 27 and 28 on October 22, with **2 outstanding units** in total. Current loans 29 and 30 must be absent. Due dates change their overdue eligibility naturally as the campus date advances.
4. Open `/manage/maintenance/10/`: expect the returned damaged multimeter lead linked to its source ReturnRecord, a completed repair action and Available outcome. Existing maintenance records 1-9 and their earlier remarks/dates remain intact.

### T21-03: Borrower history and ownership

1. Sign out and sign in as `miguel.santos`. Open `/portal/loans/27/`: expect one returned camera and one outstanding tripod, with an overdue label as of October 22. Open the fully returned August loan 11 and confirm its unit return and closed state.
2. Attempt `/portal/loans/28/`; expect 404 because it belongs to Sofia. `/manage/reports/loans/` must return 403 for a basic user.
3. Sign in as `sofia.reyes` and confirm her own overdue laptop loan/history. Use the other DEV-table accounts to inspect their own records. Equipment photos should still display; existing catalog descriptions and asset codes remain intact.

### T21-04: Controlled import and preservation checks

| Input / case | Expected outcome |
| --- | --- |
| Repeat `manage.py seed_demo_transactions` against this database | Explicit existing-history error; no duplicates, password resets or changed records |
| Missing or duplicate required equipment name, isolated test | Specific equipment-name error; no partial history |
| Unit acquired after its planned reservation, isolated test | Acquisition-date error; complete rollback |
| PostgreSQL constraint rejects issue audit, isolated test | All new history and inventory state changes roll back |
| Incorrect reference date, isolated test | Explicit actual-campus-date error |

Run `manage.py test operations.tests.test_demo_transactions --noinput`; schema-failure checks belong only in its separate PostgreSQL test database. The account-only `seed_demo_data` command remains independent and must not be rerun to refresh transaction dates.

### T21-05: Seed and cleanup command rehearsal

[DEV.md's command runbook](../DEV.md#demo-command-runbook) owns the runnable PowerShell commands, parameters, backup steps and deletion scopes. Use a disposable database for this rehearsal; the populated local history is retained for demonstration. CLI access is the authorization boundary; unit registration requires the named active ADMIN. These T21 CLI tools are integrated through PR #53 at `b828945`, preserving source `e3402bf`.

| Setup / input | Expected stored result and inspection |
| --- | --- |
| Existing active catalog; `seed_demo_units --admin-username andrea.mendoza --quantity-per-item 2 --acquired-on 2026-07-01` | Each active item has at least two total units, counting all states. New stock is Good/Available with the supplied date and creation audits; existing stock/photos/maintenance unchanged. Check `/manage/units/` and its details |
| Repeat the same top-up | Zero new units; archived items/categories remain untouched |
| Basic-user/missing admin, invalid date, zero quantity or asset-code collision | Specific error; no partial unit/audit creation |
| Seeded transaction history; `clear_equipment_units` before clearing borrowing | Explicit prerequisite error; no deletions |
| Stop writers; `clear_borrowing_data` | Requests/loans/returns and their audits removed; Reserved/Issued units Available; other states unchanged. Maintenance retained with source-return links cleared. Check empty `/manage/requests/`, `/manage/loans/`, reports, dashboard and retained inventory/maintenance |
| Then `clear_equipment_units` | No stock or maintenance; catalog/photo references/accounts/settings remain. Check catalog pictures, empty units/maintenance pages and zero stock |
| Top up units with July 1 acquisition date, then seed fixed history | New asset identities; 30 requests, 20 loans and 28 returns imported. Available counts depend on the new stock count |

Run `manage.py test operations.tests.test_demo_units operations.tests.test_demo_transactions --noinput` for the isolated PostgreSQL rehearsal, including actual database-error rollback. Do not run purge SQL/commands on the populated demonstration merely to check this guide. Full database drop/recreate and private backup restore remain separate manual procedures; no completed restore rehearsal is claimed here.

### T21 actual execution

The local import ran atomically after a private database backup. Before commit, comparisons confirmed unchanged original accounts, Profiles, catalog/category/settings rows, all nine old maintenance records/audits and all 23 photo paths/SHA-256 hashes. Existing units were retained, with workflow-derived state changes only. All 30 requests use the existing photographed equipment records; no generic sample item or new stock was substituted. Read-only ORM reports confirm the counts and dates above. Real PostgreSQL integration tests exercise the entire import, HTTP dashboard/reports/CSV, owner isolation, repeat rejection and rollback; the current handoff owns the exact final test result. Browser/mobile/keyboard, spreadsheet opening and actual user acceptance remain **Not run for this history delivery** until recorded below. Earlier empty-data examples in completed handoffs are historical.

## Module 21 — Automated system acceptance (T22)

T22 validates the integrated workflows using PostgreSQL and actual Django HTTP requests. T14/T19/T20/T21 prerequisites are integrated; T21 source `e3402bf` and publication receipt `ae6b147` are included in PR #53 at main `b828945`. The local `jerome` checkout was fast-forwarded to that merge before this work. [DEV.md](../DEV.md#t22-automated-system-acceptance) owns the complete, focused, concurrency and saved-output commands. T22 source `a7ce0a2` and publication `7d0043d` are integrated through PR #54 at fetched main `6e6f594`; merge/publication tree equality is verified. The earlier [publication receipt](../handoffs/t22-automated-acceptance-publication-10-22-2026.md) retains its historical state; [T23 preparation](../handoffs/ralph-t23-usability-session-preparation-10-22-2026.md) records the fresh integration check.

### T22-01: Run complete automated acceptance

Run the complete DEV command against the separate PostgreSQL test database. The final summary must show `OK` and exit code 0. All rows below are executed by the complete suite, rather than requiring eleven separate manual data setups. A failed row requires investigation and a rerun of the affected checks; do not mark it passed from an earlier revision's evidence.

| SRS scenario | Observable automated evidence |
| --- | --- |
| 1. Authentication, privilege forgery, deactivated sessions | [Authentication tests](../accounts/tests/test_authentication.py), [registration/profile](../accounts/tests/test_borrower_portal.py), [account management](../accounts/tests/test_account_management.py); both roles' real login flows, protected-field rejection and inactive session invalidation |
| 2. Ownership and direct management/export access | [T22 route sweep and foreign-owner checks](../operations/tests/test_system_acceptance.py), [request tracking](../borrowing/tests/test_request_tracking.py), [reports](../operations/tests/test_reports.py); all 45 current management routes deny basic-user access, inactive management sessions are cleared, missing CSRF blocks POST, foreign request/cancel/loan IDs return 404 |
| 3. Three valid items and invalid-row rollback | [T22 complete HTTP flow](../operations/tests/test_system_acceptance.py) and [submission tests](../borrowing/tests/test_request_submission.py); invalid third row saves no request, valid three-item request captures server owner/status/limits |
| 4. Last-unit contention | [PostgreSQL competing approvals](../borrowing/tests/test_approval_concurrency.py); overlapping separate connections produce one complete winner/one conflict, including no partial multi-item allocations |
| 5. Approved cancellation and issued conflict | [Request tracking](../borrowing/tests/test_request_tracking.py), [cancel/release race](../borrowing/tests/test_release_concurrency.py); ended reservations free stock, issue prevents cancellation, audit failure rolls back |
| 6. Issue once, slip, expiry and date revision | [Release HTTP/services](../borrowing/tests/test_release.py), [release concurrency](../borrowing/tests/test_release_concurrency.py), [T22 flow](../operations/tests/test_system_acceptance.py); repeat issue conflicts, correct asset slip, expired issue rejected, snapshot-based revision audited |
| 7. Partial/duplicate/damaged/final returns | [Return HTTP/services](../borrowing/tests/test_returns.py), [return races](../borrowing/tests/test_return_concurrency.py), [T22 flow](../operations/tests/test_system_acceptance.py); only final return closes a loan, damage opens linked maintenance atomically, audit errors roll back all writes |
| 8. Maintenance states and inventory reconciliation | [Maintenance](../inventory/tests/test_maintenance.py), [integrity/races](../inventory/tests/test_maintenance_integrity.py), [T22 flow](../operations/tests/test_system_acceptance.py); Reserved/Issued rejected, repair/retirement and all five inventory counts verified |
| 9. Before/on/after due date and closure | [Return/overdue checks](../borrowing/tests/test_returns.py), [reports](../operations/tests/test_reports.py); derived overdue days and outstanding counts, partial versus final closure |
| 10. Live dashboard, reports and exports | [T22 live HTML/CSV comparison](../operations/tests/test_system_acceptance.py), [dashboard](../operations/tests/test_dashboard.py), [reports](../operations/tests/test_reports.py), [seeded history](../operations/tests/test_demo_transactions.py); changing issued/returned stock changes cards/totals consistently, including CSV totals and formula protection |
| 11. Archive/settings/search/pagination/errors | [Catalog restore](../inventory/tests/test_catalog_restore.py), [catalog management](../inventory/tests/test_catalog_management.py), [settings/audit](../operations/tests/test_settings_audit.py), [equipment browsing](../inventory/tests/test_portal_equipment.py), [workspace](../accounts/tests/test_workspace.py), [reports](../operations/tests/test_reports.py); preserved historical references, future-only limits and bounded/invalid/empty filter handling |

The new route sweep uses HTTP method restrictions as valid denials: GET-only or POST-only paths can return 405 before role checking; supported unauthorized requests return 403. It checks that denied requests do not change borrowing, stock, maintenance, audit or settings rows. The lifecycle test uses CSRF-enforcing clients; it uses role fixtures for setup, while the existing authentication/registration tests exercise real credential handling separately.

### T22-02: Inspect the integrated HTTP rehearsal

The focused command runs its own fictional fixtures; these values are not instructions to alter the populated local demonstration. Existing Module 20 stock, photos and transaction IDs remain intact.

| Field / case | Fixture value / expected outcome |
| --- | --- |
| Roles | `fictional_admin` as ADMIN; `fictional_borrower` as BASIC_USER; `t22_other_borrower` for owner-isolation checks |
| Equipment / quantity | Test camera, Presentation projector and Wireless microphone, one unit each |
| Purpose | `=Media studies presentation and recorded class demonstration`; CSV must escape the leading formula character |
| Requested / revised due | Campus today + 3 days / today + 4 days; issue uses the stored revised date |
| Invalid third quantity | `0`: bound errors, no parent/child request saved |
| Forged owner/status/issuer/due | Server-owned fields prevail; a borrower cannot choose ADMIN ownership or issue metadata |
| Approval / issue | All three units Reserved, then Issued; repeat issue returns 409; the borrowing slip lists all asset codes |
| Partial / duplicate return | First unit returned: 3 issued / 1 returned / 2 outstanding, loan open; duplicate return returns 409 |
| Final damaged return | Remaining two returned, including loose projector socket: 3 / 3 / 0, loan closed, linked Open maintenance |
| Repair | Secure/test socket, Available outcome and Good condition: three Available units, no active allocation or active loan |
| Missing CSRF / foreign IDs | Administrator POST without CSRF returns 403; another borrower's request/cancel/loan routes return 404 |

### T22 execution and limits

**T22 is Done and published on `jerome` at `a7ce0a2`, Not integrated into main.** All **339 PostgreSQL tests passed in 96.345s**; the documented three-test focused command passed in 1.470s and eight-test concurrency command in 3.319s. The [T22 handoff](../handoffs/t22-automated-system-acceptance-10-22-2026.md) records the branch/revision, failures corrected and checks not run. The photo-download test now uses temporary media and consumes its streaming response, preventing leftover files and Windows file-lock cleanup errors. Formatting that owned test also resolves its earlier mixed-line-ending finding. Remaining unrelated formatting findings are reported separately.

No browser, keyboard, phone, screen-reader, spreadsheet-opening or real participant session is implied by these automated HTTP checks. T23 is Done on its retained limited acceptance record; subsequent [T24 operational results](operational-verification.md) now record measurements and a demonstrated local restore. T22 completion alone does not complete those tasks or authorize new commits/main integration.

## Module 22 — Participant usability sessions (T23)

**Status: Done with limited user-reported acceptance; implementation/review fixes integrated through PR #56/#57.** The [canonical T23 criteria/evidence](usability-acceptance.md#completion-gate-and-next-action) maps R01's actual both-role report and attributed R02/F02/E01 feedback/fix to the required deliverables. Missing session metadata and Not-run human recheck are retained limits, not mandatory additional gates. No new participant run is claimed. The original preparation tasks below remain facilitator references with historical inputs; completion does not imply a representative campus sample.

### T23-01: Prepare the session

Use Ralph's [historical read-only local setup snapshot](usability-acceptance.md#local-setup-checked-before-sessions) only as a preparation example. Ordinary startup now uses shared Neon; current setup is in [DEV](../DEV.md#shared-neon-database-and-photos). Ralph's preparation differed from Module 20's demonstration: his local accounts were `auth_demo_user` and `auth_demo_admin`, with passwords provided privately. Recheck eligibility and use a disposable session copy for write exercises. Begin each participant at the role home, with the app running through [DEV startup](../DEV.md#everyday-startup). Apply the [existing consent/feedback guidance](user-needs-evidence-guide.md#collecting-feedback), record the real environment and clearly label proxy users.

### T23-02: Borrower tasks

Give the goal before helping with the navigation. The routes and expected results below are facilitator references, not a script to read as a step-by-step answer.

| Task / participant goal | Facilitator reference and expected behavior |
| --- | --- |
| B1: Find an item you could borrow and explain its availability | From `/portal/`, find Equipment and search by name/category; detail shows catalog description and availability without internal administration data |
| B2: Request one item for a class, then explain what happens next | Use the concrete inputs below on `/portal/requests/new/`; success creates a Pending request and a review confirmation. Do not promise collection before approval/release |
| B3: Find the new request's status and due date; decide whether to keep or cancel it | Use own history/detail; on a writable session copy try Keep request before confirming cancellation. Only Pending/Approved may cancel; no existing eligible cancellation was found during preparation |
| B4: Explain what equipment is still due and what has already been returned | Inspect own loans 1 and 2 only if the copied dataset still matches the checked snapshot; loan 1 is closed, loan 2 has two outstanding overdue units on October 22 |
| B5: Complete a navigation task using keyboard or a compact device, then sign out | Focus remains visible; tables scroll locally; role navigation/profile stay usable; logout uses the existing POST form |

| Request field | October 22, 2026 example |
| --- | --- |
| Purpose | `T23 classroom usability exercise` |
| Desired return date | `2026-10-24`; recompute as campus today + 2, within the current maximum |
| Catalog item | Nokia, item 2, category Camera; recheck active flags and stock before use |
| Quantity | `1`; the checked local availability is 1 |
| Other rows | Leave blank |
| Validation exercise, if attempted | Leave purpose empty or use a date equal to today; expect associated errors without creating a request. Then correct the input |

### T23-03: Administrator tasks

Run the request/release exercise on a separate participant request from the cancellation exercise. Use the writable session copy and inspect the actual IDs created; do not reuse another borrower's records as if owned by this participant.

| Task / participant goal | Facilitator reference and expected behavior |
| --- | --- |
| A1: Find the participant's request and decide whether it can be approved | Queue/detail shows purpose, quantity, dates and current availability. Approval/rejection requires a reason; e.g. `T23 classroom exercise reviewed`. A confirmation GET/back-out must not change the request |
| A2: Prepare equipment collection and review the slip | Approved request has reserved units; release confirmation creates one loan once. Explain asset codes and due date using the existing slip |
| A3: Record a return and explain its effect | For the new single-unit loan, a Good final return closes it. After B4, copied loan 2 can support a partial/final return if its two outstanding units still exist; follow Module 16 for the condition/problem inputs. Current Nokia stock cannot support a new two-unit issue. Do not alter the preserved original loan merely for this exercise |
| A4: Find overdue equipment and export a report for a date range | Use `/manage/reports/loans/` and `/manage/reports/overdue/`; try October 1 through October 22 only on that date, otherwise use actual current dates. Note whether filtering/export/status text is understandable |
| A5: Recover from an error and sign out | Try an invalid report date range without mutation, explain the message, clear/correct it, and use native logout |

Record tasks not attempted because of stock, account or environment setup as Not attempted, with that reason. Do not mark a setup limitation as a completed partial-return session or a product usability defect without an actual observation.

### T23-04: Debrief and required follow-up

Ask what was clear/confusing, what the participant expected and what they would change. Record their own words or a labeled paraphrase, task outcome and assistance. Link actionable observations to requirements, choose a real feedback-driven improvement, implement it within scope, run relevant checks and ask the participant to retry the affected task. Use the [session and enhancement registers](usability-acceptance.md#session-register); leave results pending until actually observed.

**Historical preparation only ? executed then:** read-only local data/settings/account checks, prerequisite/main ancestry checks and runtime preflight only. **Not run:** participant tasks B1-B5/A1-A5, interviews, participant satisfaction measurements, feedback-driven enhancement and participant recheck. This preparation packet alone does not complete T23; subsequent E01 verification is below.

**Subsequent user report, October 22:** the user confirmed that both borrower and administrator flows are working. [Report R01](usability-acceptance.md#r01-user-reported-functional-confirmation) preserves that statement; individual task outcomes, browser/device and assistance were not specified. R01 supplied no actionable improvement or rating. Separate R02/E01 delivery evidence and fresh technical checks are recorded below; human recheck remains Not run. The earlier preparation checks above remain separately attributed.

### T23-05: Missing-build feedback enhancement (E01)

E01 is integrated through PR #56, source `cc00a93`. [R02/F02](usability-acceptance.md#r02-reported-missing-build-failure) attributes the source symptom to Ralph's delivery snapshot; the original traceback is not retained here. This case checks configuration failure visibility, without changing borrowing records.

1. Run `npm.cmd ci`, then `npm.cmd run build` from the project root. Run `.\.venv\Scripts\python.exe manage.py check --tag staticfiles`; with the complete build, expect exit 0 and no issues.
2. Exercise absent-build/recovery cases through the isolated integration tests below. They copy actual built files to temporary directories, remove only the temporary dashboard bundle and verify `operations.E001`; replacing it restores a successful preflight and fingerprinted URL. A completely absent temporary build reports actionable errors. The project's real generated bundles remain intact.

    ```powershell
    .\.venv\Scripts\python.exe -c "import os, subprocess, sys; sys.exit(subprocess.call([sys.executable, 'manage.py', 'test', 'operations.tests.test_assets', '--noinput'], env={**os.environ, 'IS_LOCAL_DB_CONNECTION': 'True', 'DATABASE_URL': '', 'MEDIA_STORAGE': 'local'}))"
    ```

3. With the real build present, start the app normally and open sign-in. With a missing required entry, ordinary CLI `runserver` must reject startup with the missing path and `npm ci` / `npm run build` hint. Hosts that skip checks must explicitly run the preflight. Do not delete project bundles during an active teammate session; the temporary tests cover this condition safely.

**Fresh review execution:** registered missing-chart/recovery and complete-missing-build checks pass in the full isolated suite; ordinary CLI startup was independently rejected using a temporary real build missing charts. See [review receipt](../handoffs/t23-main-integration-review-and-t24-readiness-10-22-2026.md) for full results. Ralph's earlier Edge/Chromium results remain attributed to his [delivery snapshot](../handoffs/t23-acceptance-and-startup-asset-feedback-enhancement-10-22-2026.md); this review did not repeat those browser sessions or a human recheck. The check does not detect stale content or every generated chunk.

## Module 23 — Performance and recovery (T24)

**Done and integrated through PR #58 at `478eab3`, source `49d5538`.** October 22, 2026, Asia/Manila; baseline `a9fff7e`, T22 prerequisite integrated through PR #54. [DEV replay commands](../DEV.md#t24-readiness-and-consumer-handoff) and [canonical results](operational-verification.md) define the exact procedure, measured scope and limitations. These are operational HTTP/ORM checks, not human/browser usability evidence.

### T24-01: Verify isolation before writing

| Field | Verified rehearsal value / expected boundary |
| --- | --- |
| Ordinary app database | Shared `neondb`; unchanged `.env.local`, no schema/seed/workflow writes for T24 |
| Benchmark | `campus_t24_benchmark`, loopback `127.0.0.1:55424`, PostgreSQL 18.6, local media |
| Restore | Fresh empty `campus_t24_restore` on the same dedicated local server; separate restored-media directory |
| Regression suite | Existing local PostgreSQL 17 `test_campus_equipment`; explicit empty `DATABASE_URL` / local media child override |
| Private configuration | Ignored `.env.t24.local`; do not copy passwords or raw dumps into Git |

Use DEV's connection printout before migration/fixture/restore commands. Expected: guarded local target, or an explicit refusal before mutation. A populated fixture/restore target and reused output path must fail instead of being cleared. **Executed:** both benchmark and restore guards were invoked against configured Neon and rejected it. Local benchmark migrations were applied only after its name/loopback target was checked.

### T24-02: Measure the actual scale

Follow DEV's fresh-cluster performance replay. Expected: exactly 1,000 physical units and 5,000 requests, five authenticated sessions for each role, successful warm-up, ten workers participating in each of 260 request waves. Read `latency.json`: all 2,600 measured GETs should be 200; nearest-rank p95 <= 2 seconds for lists/details and <= 3 seconds for dashboards/reports. Inspect retained raw statuses if a request fails; missing or partial output is not a pass.

**Executed:** 2,600/2,600 HTTP 200, no latency miss; worst concrete-route p95 0.483s, largest single response 0.593s. Query profiles and real EXPLAIN plans cover 20 representative routes, 3 to 9 ORM queries each; largest sampled plan 15.442ms. No production query/index/cache change was needed. See the canonical route table for sample counts and hardware/workload limits.

### T24-03: Back up and restore current data plus photos

Follow DEV's read-only Neon backup and fresh local restore. Expected: dump SHA-256 matches its manifest; every restored table count and complete-content hash matches the exported snapshot **before** sign-in/session checks; every referenced image is restored to separate local media and matches its hash. Never restore over the shared database or preserved development database. The target's empty `public` schema is removed without CASCADE because this archive recreates it; populated targets are refused.

**Executed:** 22 exact table fingerprints, all 23 photo hashes, both-role CSRF/password login and role denial, reports/CSV and protected photo bytes passed in 58 HTTP checks. A recovered submit -> approve -> release -> return cycle also passed and its verification transaction rolled back. Dump: 5.431s; complete backup/media verification: 19.989s; native restore: 0.414s; restore/media/hash/HTTP verification: 4.852s. Initial empty-schema conflict was diagnosed and corrected; no restore error remains unresolved.

### T24-04: Retain evidence and close the rehearsal

Expected: raw measurements/SQL plans/dump/media/manifest remain private under ignored `output/`, while public results contain only configuration, aggregate timings/counts and limitations. Stop the temporary HTTP process and dedicated portable database cluster; keep the original PostgreSQL service and ordinary Neon configuration intact. Record the actual result in the [dated handoff](../handoffs/t24-performance-and-recovery-verification-10-22-2026.md).

**Executed:** temporary HTTP server and isolated PostgreSQL cluster stopped, private artifact exclusions verified. Full isolated regression suite: **344 PostgreSQL tests passed in 147.179s**. Two pre-existing unrelated format findings remain. Cloud load, production hosting, cold-cache/static-image/browser timing, sustained concurrent writes, every report filter/export throughput, cross-service atomic snapshots, scheduled/off-site recovery and restore back into Neon were **Not run**. These lab results are not an RPO/RTO or production latency guarantee.

## Recording manual results

Use one row per actual test run. Expected outcomes in this guide do not count as passes. Keep evidence fictional and do not include passwords, session/CSRF tokens or private environment values.

| Case | Revision / browser / date | Actual result | Pass / Fail / Not run | Evidence / issue |
| --- | --- | --- | --- | --- |
| Example: T11-15 | `6c5ea8f`, browser/version, Asia/Manila date/time | Fill in after running | Not run | Screenshot or request marker/ID, without private data |
| Example: T13-02 | corrected jerome, browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional request ID; corrections integrated through PR #35 |
| Example: T12-01 | `170cc38`, browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional request/loan ID; no private data |
| Example: T16-01 | `23c1ad9` including integrated T16 fixes, browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional asset code/maintenance ID; no private data |
| Example: T18-02 | `26b1ee5`, browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional request/loan/category markers; no private data |
| Example: T19-03 | `e8f2a19` (PR #49), browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional report range/loan IDs and CSV filename; no borrower-private data |
| Example: T21-02 | uncommitted `jerome`, browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional request/loan marker; no credentials |

Report the purpose marker/request ID and the smallest reproduction steps for a failure. Retain test records rather than deleting history to make counts match. Save real findings in the current handoff or the team's review record when supplied.

---

## Module 22 - Shared Neon database and photos (HOST-01)

**Delivery:** integrated through PR #55 at `29003cf`, source `6dcad58`. Use [DEV teammate setup](../DEV.md#shared-neon-database-and-photos) as the canonical command/configuration guide. Credentials are sent privately by Jerome; do not record them here. Existing Django roles and page behavior remain authoritative.

### HOST-01-01 - Connect an existing team dataset

Use these values after installing the reviewed source, locked dependencies and built frontend assets:

| Field | Value |
| --- | --- |
| Database | Private pooled Neon URL from email, selecting `neondb` with TLS required |
| Database selector | `IS_LOCAL_DB_CONNECTION=False`; keep the shared URL private |
| Media backend | `MEDIA_STORAGE=neon`; private emailed S3 values; bucket `assets` |
| Local Django host | `127.0.0.1:8000` |
| Admin username | `andrea.mendoza` |
| Basic-user username | `miguel.santos` |
| Application password | Existing seeded login password from private email; never the database/storage password |

1. Run the read-only connection and migration checks in DEV. Expect `neondb`, client TLS `True`, and no pending migrations. Do not seed or clear anything.
2. Start Django and sign in as the admin. Open Dashboard, Equipment, Physical units, and both report pages/CSV downloads. Expect existing data and no missing-photo errors.
3. Open an existing photographed item. Its image must load through `/manage/items/<id>/photo/`; the original file's relative path remains stored on the catalog item.
4. Sign out, sign in as Miguel, and browse Equipment and an item's photo. Expect portal access, with `/manage/` returning 403.
5. Sign out and reopen a protected image URL. Expect a login redirect. An unsigned URL to an existing private bucket object must return 403.

**Read-only data check, October 22, 2026:** Neon had 9 users, 12 categories, 29 items, 46 units, 10 maintenance records, 30 requests, 20 loans, 28 returns and 23 referenced photos. Later team transactions can change these counts; do not delete records to match this snapshot.

**Executed:** a temporary local Django server on port 8011 used the actual pooled Neon connection. Real HTTP sessions passed both role logins, dashboard, catalog, stock, reports/CSV, all 23 administrator photo downloads with SHA-256 equality to local originals, borrower photo access, role denial, anonymous redirects and CSRF logout. A temporary object passed Django storage save/read/delete and unsigned HTTP 403; it was removed. Browser rendering, a second teammate workstation and a new image upload through the browser chooser are **Not run** for this delivery.

### HOST-01-02 - Keep automated tests isolated

Configure local PostgreSQL `DB_*` alongside Neon and run [the exact isolated test command](../DEV.md#isolated-tests-while-using-neon). Expect a separate `test_campus_equipment` database and `OK`, leaving the central dataset intact. Do not run the direct test commands below against the shared Neon URL. Local originals and the cloud's domain-record counts were retained during verification.

The coordinator-only photo importer was exercised against actual Neon storage: 23 uploaded and verified, followed by zero uploaded / 23 matching on repetition. Its documented command is not an onboarding step. Missing-source and mismatched-object errors must be resolved before repeating an import; it does not overwrite conflicting objects.

## Module 24 - Explicit database selection and screenshot evidence (HOST-02)

**Delivery:** source `c3fb6bb` is committed/pushed on `origin/jerome` and integrated through user-merged PR #64 at `8dda8c9`; exact source/merge-tree equality verified in the [integration receipt](../handoffs/database-switch-and-screenshot-main-integration-10-22-2026.md). See the [publication receipt](../handoffs/database-switch-and-screenshot-publication-10-22-2026.md). [DEV connection switching](../DEV.md#switch-between-local-and-shared-databases) owns the setup instructions; [SUBMISSION.md](../SUBMISSION.md#screenshots-checklist) owns the captured-page checklist. Existing fictional local data/photos were inspected October 22, 2026: 9 accounts, 29 catalog items, 46 units, 30 requests, 20 loans and 10 maintenance records; every assigned image existed locally.

| Field | Local example | Shared example |
| --- | --- | --- |
| `IS_LOCAL_DB_CONNECTION` | `True` | `False` |
| Connection keys | Existing private local `DB_*`; database `campus_equipment` | Existing private TLS `DATABASE_URL`; database `neondb` |
| `MEDIA_STORAGE` | `local` | `neon`, with private storage keys |
| Shared URL retained in file | Yes; ignored in local mode | Yes; required in shared mode |

1. Select local mode and restart Django. Run the read-only target check from DEV; expect `campus_equipment`. Open both role dashboards/catalogs and an existing photo. Local data and photo files must already exist; switching does not synchronize them.
2. Select shared mode and restart. Run the read-only check; expect `neondb` with TLS. Inspect existing pages only; do not seed, migrate, reset or purge shared data for this check. Restore local mode afterwards if desired.
3. Check configuration failures in an isolated temporary environment file/process: missing/invalid selector, or shared mode with no URL, must raise a specific configuration error. No connection failure may choose another database. Never damage real shared credentials to simulate this case.
4. Run the explicit local child-process test command from DEV even when the private file selects shared mode. Expect a separate `test_campus_equipment` database. Confirm the original local and shared records remain intact.

**Executed October 22:** `True` connected read-only to `campus_equipment`; `False` connected read-only to `neondb` with TLS. All **345 tests passed in 128.527s** using explicit local selection/media and `test_campus_equipment`; configuration selection/failure checks are included. Django/schema/migration checks pass, without applying migrations.

**Screenshot evidence:** 72 unretouched browser PNGs using a 1440 x 1000 desktop viewport, including two captures at a 390 x 844 mobile viewport cover all 39 checklist entries and additional forms/details. A native browser CSV download was saved and verified: 13 loan rows plus totals. The screenshot server used only `campus_screenshots_20261022`, restored from a read-only dump of the existing local database. One item archive and an account deactivation/reactivation occurred only in that copy through the application; invalid category submission produced real inline errors without creating a record. The copy/server/browser sessions were removed, all 22 original local table fingerprints match, and the private file ends in local database/media mode. No new shared workflow or cloud-media write occurred. Screenshots establish page evidence; they do not complete T30 packaging, policy review or clean-machine verification.

## Remaining validation and demonstration work

T01-T21 are integrated; PR #53 at `b828945` contains the August-October dataset. T22 source `a7ce0a2` is integrated through PR #54, with its 339-test delivery including the complete HTTP repair lifecycle; see Module 21. T23 is Done with its limited self-report and verified E01 retained; review fixes are integrated through PR #57. T24 [performance/recovery verification](operational-verification.md) is Done/integrated through PR #58; T25 prerequisite integration is satisfied and diagram execution still waits for Jerome's explicit go signal. Earlier browser coverage remains attributed to Module 19; screen-reader evaluation, Firefox/Safari, spreadsheet opening and complete browser maintenance-lifecycle checks remain unrun follow-ups.

---

## Running the automated test suite

With shared Neon enabled, use [the isolated local command](../DEV.md#isolated-tests-while-using-neon). Direct commands in this section assume local database/media configuration.

T22 source `a7ce0a2`, published on `jerome` over integrated main `b828945`, passes **339 PostgreSQL tests in 96.345s** on October 22, including three new system acceptance tests. The preceding T21 source passed 336 tests before integration through PR #53; its five account-seed, seven history/cleanup and two physical-unit tests remain included. The earlier 327-test account-only stage is historical in its dated handoff. The integrated PR #51 checkout at `6f18116` passed **322 PostgreSQL tests in 127.102s** on October 21, including all seven T20 workspace tests and 11 T19 report tests. The earlier PR #49 checkout passed 315 tests in 57.317s. The preceding PR #46 authentication/UI checkout passed 304 tests in 74.818s. The integrated T18 baseline at `26b1ee5` previously passed 298 tests in 56.385s. The published T14 checkout previously passed 254 tests in 39.994s, including 2 T14, 28 T13 and 33 maintenance tests. Earlier suite/probe results remain historical in the dated handoffs. To run the current suite yourself:

```powershell
.\.venv\Scripts\python.exe manage.py test --noinput
```

Run a specific module's tests:

```powershell
# Integrated borrower workspace (T20)
.\.venv\Scripts\python.exe manage.py test accounts.tests.test_workspace --noinput

# Per-unit returns, overdue and overlapping returns (T17)
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_returns borrowing.tests.test_return_concurrency --noinput

# PostgreSQL separate-connection competing approvals (T14)
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_approval_concurrency --noinput --verbosity 2

# Administrator queue, review, approval and rejection (T13)
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_requests --noinput

# Equipment maintenance and reconciliation (T16)
.\.venv\Scripts\python.exe manage.py test inventory.tests.test_maintenance --noinput

# Physical unit management (T08)
.\.venv\Scripts\python.exe manage.py test inventory.tests.test_unit_management --noinput

# Request submission (T11)
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_request_submission --noinput

# Request history, loans and cancellation (T12)
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_request_tracking --noinput

# Borrower registration/profile and username validation (T09)
.\.venv\Scripts\python.exe manage.py test accounts.tests.test_borrower_portal --noinput

# Borrower equipment catalog (T10)
.\.venv\Scripts\python.exe manage.py test inventory.tests.test_portal_equipment --noinput

# Authentication and access (T04)
.\.venv\Scripts\python.exe manage.py test accounts.tests.test_authentication --noinput

# Account management (T05)
.\.venv\Scripts\python.exe manage.py test accounts.tests.test_account_management --noinput

# Schema and settings (T03/T06)
.\.venv\Scripts\python.exe manage.py test operations.tests --noinput

# Live administrator dashboard cards and charts (T18)
.\.venv\Scripts\python.exe manage.py test operations.tests.test_dashboard --noinput

# Administrator loan/overdue reports and CSV exports (T19)
.\.venv\Scripts\python.exe manage.py test operations.tests.test_reports --noinput
```

All tests must pass before handover; the T24 checkout passed **344 PostgreSQL tests in 147.179s** on October 22 using the isolated local override. T01-T22 are integrated; T24 is Done/integrated through PR #58. Record actual count/timing in the handoff; [DEV.md](../DEV.md#before-handing-over-work) owns the full check list.

---

*Manual testing guide - scope: T01-T22 integrated; T23 Done/integrated with evidence limits retained; T24 operational checks are integrated through PR #58. T25 prerequisite integration is satisfied; diagrams still await the explicit go signal. Earlier browser results remain separately attributed. Maintained alongside [HANDOFF.md](../HANDOFF.md) and [docs/tasks.md](tasks.md). Record browser outcomes only after execution.*
