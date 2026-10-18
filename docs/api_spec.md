# HTTP Routes and Form Contracts

## Status and interface choice

Feature contracts for the server-rendered application in [architecture.md](architecture.md). T04 implements the shared home, login, logout, role landing, and access-control interfaces; T09 implements borrower registration and profile editing, and T10 implements borrower equipment browsing/detail/photos. The remaining feature endpoints are planned unless identified below as implemented. There is no separate frontend/backend or microservice API in this scope, so a REST/OpenAPI document would imply an interface the project does not require. This document specifies the HTML form and download interfaces instead. Add OpenAPI only if a real programmatic API is later authorized.

T05 implements the account-management list/detail and activation/deactivation routes. T06 implements operational settings and read-only audit search as described below. T07 implements the category and catalog item list/detail/create/update/archive routes and optional restoration, including derived inventory counts and protected references; implementation and integration evidence are in [the backlog](tasks.md#verified-task-evidence). UI-07 adds shared role layouts and **GET/HEAD-only placeholder pages** at the following remaining contracted destinations: `portal:request-list`, `portal:loan-list`, `inventory_manage:maintenance-list`, `borrowing_manage:request-list`, `borrowing_manage:loan-list`, and `operations:loan-report`. Each placeholder enforces its active role, displays pending-module guidance, and rejects POST with 405. The tables below describe the eventual feature behavior; these placeholders provide no domain queries, forms, mutations, reports, or exports. `/manage/` remains a dashboard placeholder until T18. Feature owners replace the pending views while preserving the contracted names and shared layout.

UI-08 supplies the role-specific account dropdown and supplied default avatars. `operations:profile` at `/manage/profile/` remains GET/HEAD-only and read-only; POST returns 405. T09 replaces the borrower profile placeholder at `/portal/profile/` (`portal:profile`) with GET/POST editing for active BASIC_USER accounts. Both profiles derive identity from the signed-in account, ignoring submitted account identifiers. Log out remains the existing CSRF-protected POST action inside the dropdown.

Use named Django URLs and integer primary-key path converters. `<id>` below denotes the relevant record ID. Successful mutations redirect to the related detail/list page with a message. All management pages are custom group-authored Django views/forms/templates.

The [coding standards](coding-standards.md#http-endpoint-design) define endpoint implementation and [browser interaction conventions](coding-standards.md#browser-interactions) within these contracts. They do not add a JSON response format or change the status table below.

## Common protocol

- Authentication: Django session cookie. All protected routes require an active account; every `/manage/` route requires ADMIN, every `/portal/` route requires BASIC_USER. Portal requests/loans are filtered by the current owner before lookup.
- Form encoding: `application/x-www-form-urlencoded`, except catalog item forms and the equipment photo upload use `multipart/form-data`. All POST forms include `csrfmiddlewaretoken`; GET never changes application state.
- Confirmation: GET on an action route renders a confirmation form only; POST performs the explicitly named action. POST-only sign-out has no GET mutation.
- Dates: `YYYY-MM-DD` calendar dates, interpreted using Asia/Manila. Operational timestamps and actors are always assigned server-side.
- Numeric IDs/quantities: validated positive integers. Invalid or missing values produce field/non-field errors; ignore unrelated extra fields, and never assign them to models. Tampered read-only values cannot change state.
- URL names in tables are proposed stable names, referenced with Django URL reversing. Do not hardcode links in templates.
- `page`: positive integer, 25 rows per page except the administrator catalog at `/manage/items/`, which uses 10. Malformed or nonexistent pages return 404. `q`: optional trimmed search text, maximum 200 characters. Invalid enum/date filters render useful errors without executing a mutation.
- Missing filter values mean no restriction. `date_from` and `date_to` are inclusive campus dates; reject reversed ranges. Date ranges on request queues use submission date, on reports use issue date, and on audit search use occurrence date.
- Response bodies: UTF-8 HTML unless CSV is explicitly requested. CSV responses use `text/csv; charset=utf-8` and attachment filenames without private borrower data.

| Condition | Response |
| --- | --- |
| Successful page or valid form display | 200 HTML |
| Successful login or mutation | 302 redirect using URL reversing; no mutation on redirect GET |
| Anonymous access to a protected page | 302 to sign-in; validate any subsequent `next` target as same-origin and appropriate to the signed-in role |
| Wrong role, inactive session, or CSRF failure | 403; invalidate an inactive account's session |
| Missing record or another borrower's portal record | 404 without revealing whether another owner's record exists |
| Wrong HTTP method | 405 |
| Invalid submitted form values | 200 with bound form errors and no writes |
| Changed workflow state, duplicate action, or insufficient inventory | 409 with a clear conflict message and no partial writes |
| Unexpected internal failure | 500 with a safe error page; structured internal log retains the cause without secrets |

## Development preview

| Method | Path | URL name | Access / result |
| --- | --- | --- | --- |
| GET, HEAD | `/test` | `frontend-test` | Public only with `DEBUG=True`; Tailwind/font samples with no application data; 404 with `DEBUG=False`; other methods return 405 |

See [DEV.md](../DEV.md#frontend-preview) for asset build/run instructions. The preview does not implement or bypass the role routes below. T04 replaced the temporary development index at `/` with the contracted `accounts:home` route; `/test` remains debug-only.

## Shared account routes

| Method | Path | URL name | Access | Inputs / result |
| --- | --- | --- | --- | --- |
| GET | `/` | `accounts:home` | Public | Anonymous redirects to login; active signed-in user redirects to role home |
| GET, POST | `/accounts/login/` | `accounts:login` | Public | `username` accepts a username or email; `password`; successful role redirect; safe generic invalid-credentials error |
| POST | `/accounts/logout/` | `accounts:logout` | Signed-in account | CSRF only; clear session and redirect to login |
| GET, POST | `/accounts/register/` | `accounts:register` | Anonymous | `username`, `first_name`, `last_name`, `email`, `contact_number`, `password1`, `password2`; create BASIC_USER + Profile atomically, then redirect to login |

Role, `is_active`, permission flags, user ID, and password hash are not registration inputs. Password fields use Django validation and account-creation helpers. There is no public admin-creation endpoint; [DEV.md](../DEV.md#create-an-administrator-account) documents the authorized setup command.

T04 implements the first three routes above; T09 implements registration. Authenticated registration requests redirect to the active account's role home. Valid anonymous registration creates an active BASIC_USER with staff/superuser flags false, a Profile and ACCOUNT_CREATED audit entry atomically, then redirects to login without automatically signing in. The documented `create_admin` management command creates an active ADMIN and Profile from trusted local CLI access; no public form accepts an administrator role.

Registration requires username, first/last name, email and matching passwords validated by Django; contact number is optional (30 characters maximum). Current forms normalize usernames and email domains, reject exact username or cross-identifier collisions and case-insensitive email collisions, and ignore extra privilege/identity fields. These are form checks, not a new database email-uniqueness constraint; [the schema contract](db_design.md#accounts) remains unchanged. The validation correction integrated through PR #24 at `f29bd91` uses Django's UsernameField normalization and the model's UnicodeUsernameValidator before calling the creation service. Invalid characters return 200 with bound username errors and no User, Profile or audit writes. T09 remains Done; see [current integration evidence](tasks.md#verified-task-evidence) and the [implementation snapshot](../handoffs/registration-username-validation-and-t09-status-10-18-2026.md).

AUTH-02 adds email sign-in locally without changing the POST field name `username`. Its label is "Username or email" and it accepts up to 254 characters. Match usernames exactly and emails case-insensitively; the combined lookup must identify exactly one account. Duplicate emails or a username matching another account's email are rejected with the same generic error as invalid/inactive credentials. Never choose the first match or try accounts until a password succeeds. Native Django password/session authentication, active checks, safe role redirects, and CSRF remain authoritative. No schema uniqueness change is implied; local acceptance and main integration are recorded in [the backlog](tasks.md#verified-task-evidence).

## Basic-user portal

T09's profile POST derives the target from the signed-in user, locks and rechecks active BASIC_USER eligibility, updates only the allowlisted name/email/contact fields and writes ACCOUNT_UPDATED in one transaction. Success redirects to `portal:profile`; username, role, activation and ownership fields cannot be edited. The profile form applies the same email-collision checks as registration, excluding the current account. T10 implements the GET/HEAD equipment list, detail and photo routes below for active BASIC_USER accounts. Search accepts trimmed `q` (name/description, maximum 200 characters), optional active `category` and `page`; invalid filters return bound errors with no results, and invalid pages return 404. Results use 25-item pagination with preserved filters, serviceable = Available + Reserved + Issued, and available = Available. Archived items or categories return 404 on direct detail/photo access and are absent from lists. Catalog pages hide physical asset codes, internal notes, maintenance details and borrower identities. Photo responses stream stored WebP with `nosniff` and `private, no-store`; missing photos return 404 and templates use the shared static default when no upload is assigned. Request/loan feature routes remain planned or protected placeholders until their tasks are accepted.

| Method | Path | URL name | Inputs / result |
| --- | --- | --- | --- |
| GET | `/portal/` | `portal:home` | Own summary and navigation |
| GET, POST | `/portal/profile/` | `portal:profile` | Only `first_name`, `last_name`, `email`, `contact_number`; account identity/authorization unchanged |
| GET, HEAD | `/portal/equipment/` | `portal:equipment-list` | `q`, `category`, `page`; active catalog and allowed quantity fields |
| GET, HEAD | `/portal/equipment/<id>/` | `portal:equipment-detail` | Active item description, serviceable total, availability |
| GET, HEAD | `/portal/equipment/<id>/photo/` | `portal:equipment-photo` | Active item/category only; private WebP stream, 404 for missing photo |
| GET, POST | `/portal/requests/new/` | `portal:request-create` | Request form contract below |
| GET | `/portal/requests/` | `portal:request-list` | Own requests only; `status`, `page` |
| GET | `/portal/requests/<id>/` | `portal:request-detail` | Own request items, decision/status, due date, issued/returned units; no internal notes |
| GET, POST | `/portal/requests/<id>/cancel/` | `portal:request-cancel` | Confirmation and CSRF only; Pending/Approved owner requests |
| GET | `/portal/loans/` | `portal:loan-list` | Own loans only; `page` |
| GET | `/portal/loans/<id>/` | `portal:loan-detail` | Own loan's due date, asset codes, and individual return status |

### New request form

| Input | Validation |
| --- | --- |
| `purpose` | Required nonblank text |
| `desired_due_date` | Required date under SRS BR-02 |
| `items-TOTAL_FORMS` | Django formset management count, 1–3; hard-limit form construction and validate max count server-side |
| `items-INITIAL_FORMS` | 0 for a new request |
| `items-<index>-catalog_item` | Required active item ID, active category, distinct within request |
| `items-<index>-quantity` | Positive integer within configured per-item maximum |

Use a validated Django formset with prefix `items`; ignore entirely blank optional extra rows, but every populated row must be complete and at least one row must be submitted. Both submitted management counts and actual cleaned row counts must satisfy the maximum. No nested JSON payload is expected. Owner, status, snapshots, and timestamps are server-controlled. Validate the entire formset before the atomic write.

## Custom administration: accounts and inventory

All routes in the following tables require an active ADMIN.

| Method | Path | URL name | Inputs / result |
| --- | --- | --- | --- |
| GET | `/manage/` | `operations:dashboard` | Four live cards and database-derived charts |
| GET, HEAD | `/manage/profile/` | `operations:profile` | Current signed-in administrator's read-only account/profile; POST 405 |
| GET | `/manage/accounts/` | `accounts:manage-list` | `q`, `active` (`true`/`false`), `page`; basic-user accounts |
| GET | `/manage/accounts/<id>/` | `accounts:manage-detail` | Basic-user details and related request/loan history |
| GET, POST | `/manage/accounts/<id>/activate/` | `accounts:manage-activate` | Confirm active status change and audit |
| GET, POST | `/manage/accounts/<id>/deactivate/` | `accounts:manage-deactivate` | Confirm deactivation; preserve history and audit |
| GET | `/manage/categories/` | `inventory_manage:category-list` | `q`, `archived` (`true`/`false`), `page` |
| GET | `/manage/categories/<id>/` | `inventory_manage:category-detail` | Category and related catalog |
| GET, POST | `/manage/categories/new/` | `inventory_manage:category-create` | `name`, `description` |
| GET, POST | `/manage/categories/<id>/edit/` | `inventory_manage:category-update` | `name`, `description` |
| GET, POST | `/manage/categories/<id>/archive/` | `inventory_manage:category-archive` | Confirmation; preserve referenced records |
| GET, POST | `/manage/categories/<id>/restore/` | `inventory_manage:category-restore` | Optional enhancement; confirmation and CSRF only; restore category, preserve individual item archive flags; already active returns 409 |
| GET | `/manage/items/` | `inventory_manage:item-list` | `q`, `category`, `archived`, `page` |
| GET | `/manage/items/<id>/` | `inventory_manage:item-detail` | Item, units, and derived counts |
| GET, POST | `/manage/items/new/` | `inventory_manage:item-create` | `category`, `name`, `description`; optional multipart `photo` with the validation below. Invalid photo or audit failure leaves no new item/file |
| GET, POST | `/manage/items/<id>/edit/` | `inventory_manage:item-update` | `name`, `description`; category only before transactional use |
| GET, POST | `/manage/items/<id>/archive/` | `inventory_manage:item-archive` | Confirmation; block new requests/approval without destroying existing workflow |
| GET, POST | `/manage/items/<id>/restore/` | `inventory_manage:item-restore` | Optional enhancement; confirmation and CSRF only; clear item archive flag, preserve category/unit statuses; already active returns 409 |
| GET, HEAD | `/manage/items/<id>/photo/` | `inventory_manage:item-photo` | Active ADMIN only; stored WebP response, private/no-store; 404 when no uploaded photo |
| GET, POST | `/manage/items/<id>/photo/upload/` | `inventory_manage:item-photo-upload` | Separate optional photo action after item creation; multipart `photo`; one JPEG/PNG/WebP, max 5 MiB / 20 million pixels; no animations; generated WebP fitted within 1600×1600 |
| GET, POST | `/manage/items/<id>/photo/remove/` | `inventory_manage:item-photo-remove` | Confirmation and CSRF only; remove uploaded photo, display static default; repeat removal returns 409 |
| GET | `/manage/units/` | `inventory_manage:unit-list` | `q` for asset code, `category`, `item`, `status`, `page` |
| GET | `/manage/units/<id>/` | `inventory_manage:unit-detail` | Physical unit and its allocation/loan/maintenance history |
| GET, POST | `/manage/units/new/` | `inventory_manage:unit-create` | `catalog_item`, `asset_code`, `condition`, `acquired_on`, `internal_notes`; if DAMAGED, required `maintenance_problem` opens maintenance atomically |
| GET, POST | `/manage/units/<id>/edit/` | `inventory_manage:unit-update` | `internal_notes`; `asset_code`, `catalog_item`, `acquired_on` only before any transactional use |

T08 implements the four unit routes above with active-ADMIN authorization, 25-row pagination and unit history. Creation rejects archived catalog/category choices, duplicate asset codes and future acquisition dates. Initial GOOD/FAIR units become AVAILABLE; DAMAGED requires a problem description and creates open maintenance with both audit entries atomically. Metadata updates accept internal notes; asset code, catalog item and acquisition date are locked after allocations or maintenance exist. Generic edits never accept workflow status or condition.

Subsequent unit condition/status changes belong to the planned return/maintenance services. A catalog item's category cannot change after any of its units or request items has transactional history, preserving category reporting. No generic delete, role-edit, allocation-edit, or status-edit route exists.

Restoration is an active-ADMIN-only enhancement to the required archive workflow. GET confirms without writing; POST rechecks the actor and locked record, clears only the target's archive flag, writes `CATEGORY_RESTORED` or `ITEM_RESTORED` atomically, and redirects to its detail page. Restoring an item under an archived category is allowed, with a warning; the item remains ineligible for new requests/approvals until the category is active. Restoring a category never clears individually archived items. Photos, physical-unit statuses (including RETIRED), allocations, loans, and history remain unchanged. Find archived records through the list's Status filter, open View, and choose Restore category or Restore item.

## Custom administration: requests, loans, and maintenance

| Method | Path | URL name | Inputs / result |
| --- | --- | --- | --- |
| GET | `/manage/requests/` | `borrowing_manage:request-list` | `q` for request ID or borrower username, `status`, `date_from`, `date_to`, `page` |
| GET | `/manage/requests/<id>/` | `borrowing_manage:request-detail` | Items, purpose, requested/agreed date, borrower, availability, decision and allocations |
| GET, POST | `/manage/requests/<id>/approve/` | `borrowing_manage:request-approve` | Required `reason`; deterministic server selection of eligible units; atomic all-or-nothing reservation |
| GET, POST | `/manage/requests/<id>/reject/` | `borrowing_manage:request-reject` | Required `reason`; Pending only |
| GET, POST | `/manage/requests/<id>/due-date/` | `borrowing_manage:request-due-date` | `agreed_due_date`, required `reason`; Approved/pre-issue only under BR-06 |
| GET, POST | `/manage/requests/<id>/release/` | `borrowing_manage:request-release` | Confirmation and CSRF only; server assigns actor/time and validates full allocation |
| GET | `/manage/loans/` | `borrowing_manage:loan-list` | `q`, `page`; include active/closed label |
| GET | `/manage/loans/<id>/` | `borrowing_manage:loan-detail` | Issued units, returns, outstanding quantity, due date, overdue label |
| GET | `/manage/loans/<id>/slip/` | `borrowing_manage:loan-slip` | Printable borrowing slip; no workflow mutation |
| GET, POST | `/manage/loans/<id>/returns/new/` | `borrowing_manage:return-create` | Validated per-unit return formset described below |
| GET | `/manage/maintenance/` | `inventory_manage:maintenance-list` | `q` for asset code, `status` (OPEN/CLOSED), `page` |
| GET | `/manage/maintenance/<id>/` | `inventory_manage:maintenance-detail` | Unit, problem, action, actors, dates, outcome |
| GET, POST | `/manage/maintenance/new/` | `inventory_manage:maintenance-create` | `unit`, `problem`; require eligible Available unit |
| GET, POST | `/manage/maintenance/<id>/close/` | `inventory_manage:maintenance-close` | Required `action`, `outcome` (AVAILABLE/RETIRED); server closure actor/time |

Return formset prefix `returns`: each selected row requires `loan_unit`, `returned_condition` (GOOD/FAIR/DAMAGED), and optional `notes`; DAMAGED additionally requires nonblank `maintenance_problem`. At least one row must be selected, loan units must be unique and outstanding on the addressed loan, and maximum row count equals that loan's outstanding quantity. Validate all rows before one atomic return operation. Client-supplied actor/date/unit relationships are never trusted.

## Custom administration: reports, audit, settings

| Method | Path | URL name | Inputs / result |
| --- | --- | --- | --- |
| GET | `/manage/reports/loans/` | `operations:loan-report` | `date_from`, `date_to`, `page`; SRS report contract |
| GET | `/manage/reports/loans/export/` | `operations:loan-export` | Same date filters, all matching rows; CSV |
| GET | `/manage/reports/overdue/` | `operations:overdue-report` | `date_from`, `date_to`, `page`; outstanding overdue loans only |
| GET | `/manage/reports/overdue/export/` | `operations:overdue-export` | Same date filters, all matching rows; CSV |
| GET, HEAD | `/manage/audit/` | `operations:audit-list` | `q` for record reference, `action`, `actor`, `date_from`, `date_to`, `page`; read-only, POST 405 |
| GET, HEAD, POST | `/manage/settings/` | `operations:settings` | Positive integers `max_loan_days`, `max_quantity_per_item`; audited update |

T06 accepts only the two settings fields, each from 1 through 2147483647. Actor/time/singleton identity are server-controlled. A valid POST uses the existing atomic `update_settings` service and redirects to `operations:settings`; invalid values retain bound errors with no writes. Current values and last-update metadata are displayed on GET. The consistent `get_loan_limits()` reader supplies new-request validation/snapshots; existing request snapshots are preserved. T11 must use that interface when submission is implemented, and its full submission flow remains separately unverified.

Audit `q` searches the case-insensitive historical reference `target_model#target_id`, accepting model names, IDs, or their combined reference. `action` uses `AuditAction`; `actor` is an optional positive account ID, including inactive historical actors, rather than a username. System initialization has no account ID and is searchable by its action. Inclusive `date_from`/`date_to` filter occurrence dates in Asia/Manila; invalid/reversed filters show errors without exposing unfiltered rows. Results use 25 rows per page ordered by descending occurrence time and ID, and paging retains the filters. No audit edit/delete action is supplied.

The dashboard embeds chart datasets safely into its rendered page using Django's JSON-safe template facilities. No AJAX/JSON chart endpoint is planned. Exports and print pages receive full role/active checks, not authorization inherited from a previous page visit.
