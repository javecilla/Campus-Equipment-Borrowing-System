# Manual Browser Testing Guide

## Purpose and scope

This guide covers **T01-T11 integrated into main at `6c5ea8f`** as of October 18, 2026, including Ralph's request submission through PR #27. Request history/cancellation, approval, release and returns remain pending. Use it to check individual modules and regressions; it does not establish full-system acceptance. The user is currently testing T11; the expected results below are instructions, not recorded passes.

For the current request tests, go directly to [Module 9: borrower request submission](#module-9--borrower-request-submission-t11). Use the [result record](#recording-manual-results) to report what actually happened.

For automated tests, see [Running the automated suite](#running-the-automated-test-suite) at the bottom.

## Prerequisites

### Server must be running

Follow [DEV startup](../DEV.md#everyday-startup) and rebuild assets after pulling template changes with `npm.cmd run build`. T11 adds no migration or dependency. Keep the existing local database and test records.

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Visit `http://127.0.0.1:8000/`. Anonymous visitors go to login; signed-in accounts go to their role home.

### Test accounts

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

1. Log in as admin, go to `/manage/accounts/`
2. Find `auth_demo_user`, click **Deactivate**, confirm
3. Log out, then try to log in as `auth_demo_user`

✅ Login rejected — inactive accounts cannot sign in

1. To test an existing session, first reactivate and sign in as the borrower in a separate browser profile or private window.
2. Keep that session open while the administrator deactivates the account again.
3. In the borrower window, reload `/portal/equipment/`.

✅ The first protected request is denied with 403 and the session is invalidated. Subsequent anonymous requests redirect to login.

**Restore the account before continuing:** log in as admin, re-activate `auth_demo_user`.

---

## Module 2 — Borrower Registration (T09)

**Base URL:** `/accounts/register/`

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

*The maintenance-history case is testable now. The allocation-history case still requires T13 or existing coherent historical test data.*

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
5. After submission, refresh that borrower's **admin account detail** to verify whether a new request was saved. The borrower request section does not yet list request history; T12 will add it.

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

**Expected rejection:** Row 3 quantity error; all entered rows remain available for correction. **No BorrowRequest and no RequestItem rows are saved**, including the first two valid rows. Refresh the borrower's admin account history: its request count is unchanged and this purpose marker is absent. Do not expect an empty list if earlier successful cases already created records. The automated T11 rollback test directly checks both database tables; borrower request history is not available until T12.

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

Known review follow-up: the new-request page currently does not highlight **My requests** as the active navigation tab. Request/loan history and cancellation are pending T12; admin approval is pending T13. Neither the missing history table nor a lack of reserved units after submission indicates a failed T11 submission.

---

## Recording manual results

Use one row per actual test run. Expected outcomes in this guide do not count as passes. Keep evidence fictional and do not include passwords, session/CSRF tokens or private environment values.

| Case | Revision / browser / date | Actual result | Pass / Fail / Not run | Evidence / issue |
| --- | --- | --- | --- | --- |
| Example: T11-15 | `6c5ea8f`, browser/version, Asia/Manila date/time | Fill in after running | Not run | Screenshot or request marker/ID, without private data |

Report the purpose marker/request ID and the smallest reproduction steps for a failure. Retain test records rather than deleting history to make counts match. Save real findings in the current handoff or the team's review record when supplied.

---

## What is not testable yet

The following features are **Not started** and have no implementation to test in the browser:

| Task | Feature | Owner |
| --- | --- | --- |
| T12 | View own requests and cancel pending/approved requests | Ralph |
| T13 | Admin request review queue, approval, and rejection | Margareth |
| T14 | Competing-approval concurrency test | Jerome + Margareth |
| T15 | Equipment release and printable borrowing slip | Margareth |
| T16 | Maintenance open/close, repair, retirement | Kenneth |
| T17 | Per-unit returns, partial returns, damaged-return maintenance | Margareth + Kenneth |
| T18 | Live dashboard cards and charts | Alex |
| T19 | Loan/overdue reports and CSV export | Alex |
| T20 | Full cross-workflow UI/accessibility acceptance; shared role layouts already exist | Ralph + Ellyssa |

---

## Running the automated test suite

The integrated-source review passed **181 PostgreSQL tests**. To run the current suite yourself:

```powershell
.\.venv\Scripts\python.exe manage.py test --noinput
```

Run a specific module's tests:

```powershell
# Physical unit management (T08)
.\.venv\Scripts\python.exe manage.py test inventory.tests.test_unit_management --noinput

# Request submission (T11)
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_request_submission --noinput

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
```

All tests in the current suite must pass before handing over work; 181 is the verified count at this revision. Record the actual count and timing in your handoff. See [DEV.md — Before handing over work](../DEV.md#before-handing-over-work) for the full required check list.

---

*Manual testing guide — scope: T01-T11 integrated features. Maintained alongside [HANDOFF.md](../HANDOFF.md) and [docs/tasks.md](tasks.md). Update this file when new features are accepted and integrated into main.*
