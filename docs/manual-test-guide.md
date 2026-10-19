# Manual Browser Testing Guide

## Purpose and scope

This guide covers the T01-T13/T16 baseline in main `23c1ad9` plus the [verified T13 query fixes](../handoffs/t13-query-fixes-and-publication-10-19-2026.md) on `jerome`. Both functional defects are fixed on that branch and await main integration. Expected results below describe the corrected checkout. T14 concurrency proof, release and returns remain pending; T12/T13/T16 browser results remain Not run until supplied.

For the current borrower checks, go directly to [Module 9: request submission](#module-9--borrower-request-submission-t11) or [Module 10: request and loan tracking](#module-10--borrower-request-and-loan-tracking-t12). For equipment maintenance and reconciliation, see [Module 11: equipment maintenance](#module-11--equipment-maintenance-and-inventory-reconciliation-t16). Use the [result record](#recording-manual-results) to report what actually happened.

For automated tests, see [Running the automated suite](#running-the-automated-test-suite) at the bottom.

## Prerequisites

### Server must be running

Follow [DEV startup](../DEV.md#everyday-startup) and rebuild assets after pulling template changes with `npm.cmd run build`. T11/T12/T13/T16 add no migration or dependency. Keep the existing local database and test records.

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
**Prerequisite:** T11 is integrated through PR #27; T13 approval is now merged through PR #34 with verified query corrections on jerome awaiting integration. T15 issue and T17 returns remain pending.

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

Pagination shows 25 records per page. If a fictional borrower already has more than 25, verify Previous/Next retains the selected status and does not duplicate/skip rows. The three-record snapshot cannot exercise that boundary; leave it Not run until suitable records exist. Cross-user checks also need a second fictional borrower's known request; the snapshot found no such request.

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

**Case T12-03 — now available to prepare.** Use [T13 approval in Module 12](#module-12--administrator-request-review-and-decisions-t13) on a fresh fictional request. The October 19, 22:31 local snapshot has no Approved requests yet; prepare this prerequisite through the browser workflow, without editing database statuses. Corrected jerome detail excludes ended allocations from Reserved units while retaining their history. Main `23c1ad9` still has the original display defect until integration.

1. After approving through T13, record the Approved request ID and the Reserved status of every unit assigned to it.
2. As that same borrower, open the request details and confirm cancellation.

✅ The request becomes Cancelled, every associated allocation ends with its cancellation timestamp, and all of its reserved units become Available together. The cancellation and audit row commit together. If any reservation is missing, changed, or incomplete, the action returns 409 and none of the request, allocations, units or audit entries change.

### 10.4 Issued request and loan tracking

**Case T12-04.** Open `/portal/loans/` now: the snapshot has no loans, so expect **No loans yet**, with no fabricated records. An absent loan ID at `/portal/loans/<loan_id>/` returns 404.

The populated loan/return browser scenarios below require the separate T15 release and T17 return workflows. Leave them Not run until those workflows and suitable fictional records exist.

1. After T15 is integrated, release an Approved request for a fictional borrower. Sign in as that borrower and open `/portal/requests/`, the request detail, and `/portal/loans/`.
2. Verify only that borrower's loan is listed, with issue/due dates and a link to its detail. The request detail should also show issued asset codes.
3. Open the loan detail. Verify each issued unit and its asset code is listed as awaiting return. Substitute another borrower's loan ID; the response should be 404.
4. After T17 is integrated and one unit is returned, reload the request and loan details.

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
- These replace Kenneth's workstation examples; `cam-qwert` / `sony` is not in this local snapshot. If data changed, select another eligible fictional unit and record the actual baseline. Counts below assume only these sequential cases change inventory. Reserved/Issued browser rejection and more-than-25-row pagination require additional legitimate records; leave them Not run here. No seed data was created by this review.
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
  - Retired unit cannot be selected for new maintenance. Borrowers choose catalog items, not physical units; availability falls by one. T13 now allocates eligible units; browser cases remain unrun and T14 competing-approval proof is still pending.

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
  - **Pagination:** List paginates at 25 rows per page; pagination links preserve active `q` and `status` query parameters using `{% querystring %}`. Invalid page returns 404.

---

### Test Case T16-07: Authorization, Role Enforcement, and CSRF Protection

- **Role / Method Checks:**
  1. **Anonymous visitor:** Accessing `/manage/maintenance/`, `/manage/maintenance/new/`, `/manage/maintenance/<id>/`, or `/manage/maintenance/<id>/close/` redirects to `/accounts/login/?next=...`.
  2. **Borrower account (`BASIC_USER`):** Accessing any `/manage/maintenance/*` route returns **403 Forbidden**.
  3. **Method protection:** Sending `POST` to `/manage/maintenance/` or `/manage/maintenance/<id>/` returns **405 Method Not Allowed**.
  4. **CSRF protection:** Submitting POST to `/manage/maintenance/new/` or `/manage/maintenance/<id>/close/` without a valid CSRF token returns **403 Forbidden**.
  5. **Keyboard & Responsive navigation:** Use `Tab` / `Shift+Tab` to verify visible focus order across all filter inputs, action buttons, form controls, and table links. Verify clean grid stacking and no horizontal overflow on mobile viewports (375px).

All 33 maintenance tests pass within the current 252-test PostgreSQL suite (the earlier T16 review passed 224 total tests). They include manual lifecycle/access/filter/count checks, seven new real integrity tests for the removed return-link argument, opening/repair audit rollback, changed-state 409, CSRF/protected fields, competing administrators and unit-before-maintenance closure locking. Browser, keyboard, mobile and pagination-boundary results remain **Not run**; these tests do not implement T17.

---

The manual `open_maintenance` action accepts no `source_return_id` and always applies Available-unit eligibility. Browser-supplied return/actor/status fields cannot control it. Future T17 must create matching damaged-return maintenance inside its complete return/allocation/audit transaction; the manual opener is not a damaged-return interface.

## Module 12 — Administrator Request Review and Decisions (T13)

**Owner:** Margareth Raine H. Ignacio (`marga`); Jerome with Codex for the authorized query fixes. **Revision:** PR #34 main baseline `23c1ad9`, preserving `c5cfe37`, plus [fixes on jerome](../handoffs/t13-query-fixes-and-publication-10-19-2026.md) awaiting main integration. **Status:** Done on corrected jerome; browser verification pending. **Role:** active ADMIN. **Entry:** `/manage/requests/`. T03/T11 are integrated; release/slips/returns remain pending. All browser cases below are **Not run**. Two automated HTTP/database regressions failed before the fixes and now pass.

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

Open detail and verify borrower, purpose, requested/agreed dates, quantities and current availability. Detail and decision confirmation GETs must not change status, allocations or audits. Pagination holds 25 rows and retains filters. With only 3 local requests, **multi-page traversal is Not run / insufficient records**; invalid-page checks do not prove that traversal.

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

Expected on corrected jerome: Reserved units shows None for the cancelled request, availability is restored and the ended allocation remains stored. The new integration regression verifies all three plus the cancellation audit. Main `23c1ad9` still shows the ended allocation as Reserved until the fix is integrated. Browser result remains Not run; do not edit historical rows to hide the original defect.

### T13-07: Unicode numeric search succeeds without an exception

| Field | Value |
| --- | --- |
| Request ID or borrower username | `²` (superscript two) |

Expected on corrected jerome: HTTP 200 with normal username matches or empty results. The query uses `isdecimal()` before converting an ID; `²` remains username search text. The new integration regression confirms a username containing `²` is found and Arabic-Indic decimal digits still match a request ID. Main `23c1ad9` raises `ValueError` for `²` until integration. Browser result remains Not run.

### T13-08: Access, eligibility and audit integrity

- Signed out: list/detail/confirmation redirect to login. Active BASIC_USER: direct administrator GET/POST returns 403. Inactive ADMIN sessions cannot mutate. Missing request IDs return 404; unsupported PUT/DELETE return 405.
- Both decision POSTs require CSRF (403 without a valid token). Extra actor/owner/status/allocation fields must not control writes; use the real form for normal testing and retain any private tokens locally during direct HTTP tests.
- Approval for an inactive borrower or archived item/category returns 409 without reservations. These browser cases need deliberately prepared fictional records through existing account/catalog interfaces; no such live changes were made for this guide.
- Temporary PostgreSQL probes forced rejection of approval/rejection audit inserts and verified rollback of their business writes. These ran only in the test database; no live audit constraints were installed.
- Desktop/mobile, keyboard focus, pagination boundaries and stale browser submissions still need actual results. **T14's separate-connection competing last-unit approvals are not implemented or verified by these cases or the T13 TestCase suite.**

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

## Recording manual results

Use one row per actual test run. Expected outcomes in this guide do not count as passes. Keep evidence fictional and do not include passwords, session/CSRF tokens or private environment values.

| Case | Revision / browser / date | Actual result | Pass / Fail / Not run | Evidence / issue |
| --- | --- | --- | --- | --- |
| Example: T11-15 | `6c5ea8f`, browser/version, Asia/Manila date/time | Fill in after running | Not run | Screenshot or request marker/ID, without private data |
| Example: T13-02 | corrected jerome, browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional request ID; corrections awaiting main integration |
| Example: T12-01 | `170cc38`, browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional request/loan ID; no private data |
| Example: T16-01 | `23c1ad9` including integrated T16 fixes, browser/version, Asia/Manila date/time | Fill in after running | Not run | Fictional asset code/maintenance ID; no private data |

Report the purpose marker/request ID and the smallest reproduction steps for a failure. Retain test records rather than deleting history to make counts match. Save real findings in the current handoff or the team's review record when supplied.

---

## What is not testable yet

T13 is available on corrected jerome with both functional findings resolved (Module 12); main integration is pending. The following tasks are **Not started**; T14 requires separate-connection integration testing and the other feature workflows have no browser implementation:

| Task | Feature | Owner |
| --- | --- | --- |
| T14 | Competing-approval concurrency test | Jerome + Margareth |
| T15 | Equipment release and printable borrowing slip | Margareth |
| T17 | Per-unit returns, partial returns, damaged-return maintenance | Margareth + Kenneth |
| T18 | Live dashboard cards and charts | Alex |
| T19 | Loan/overdue reports and CSV export | Alex |
| T20 | Full cross-workflow UI/accessibility acceptance; shared role layouts already exist | Ralph + Ellyssa |

---

## Running the automated test suite

The corrected jerome checkout passed **252 PostgreSQL tests in 42.541s**, including 28 T13 and 33 maintenance tests. The focused T13 suite passed 28 tests in 0.809s. Both added regressions failed against main baseline `23c1ad9` and pass with the query fixes. Earlier 250-test/five-probe review results remain historical in the dated review; those temporary probes were not committed. To run the current suite yourself:

```powershell
.\.venv\Scripts\python.exe manage.py test --noinput
```

Run a specific module's tests:

```powershell
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
```

All tests must pass before handover; 252 is the verified count on corrected jerome. Corrections must be integrated before dependent tasks consume accepted T13 from main. Record actual count/timing in the handoff; [DEV.md](../DEV.md#before-handing-over-work) owns the full check list.

---

*Manual testing guide - scope: T01-T13/T16 baseline integrated, plus verified T13 query fixes on jerome awaiting main integration. Maintained alongside [HANDOFF.md](../HANDOFF.md) and [docs/tasks.md](tasks.md). Record browser outcomes only after execution.*
