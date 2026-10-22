# Software Requirements Specification

## Status, references, and terminology

This specification covers implemented and future behavior. T01-T21 are Done and integrated, including the T18 dashboard, T19 loan/overdue reports with CSV and T20 role workspaces; the [backlog](tasks.md#verified-task-evidence) records acceptance and main integration separately. Ralph's T20 is integrated through PR #51 at `6f18116`, preserving source `b43fb99`. T22 automated minimum-scenario acceptance is integrated through PR #54 at `6e6f594`, preserving source `a7ce0a2`; T23 startup asset enhancement E01 is integrated through PR #56 at `17873b6`, source `cc00a93`, and technically verified. T23 is Done on the [canonical limited user-reported acceptance and verified enhancement](usability-acceptance.md#completion-gate-and-next-action); no independent session observations or human recheck are invented. Review fixes are integrated through PR #57 at `87098a6`, source `9a491c6`. T24 [lab performance/recovery verification](operational-verification.md) is Done locally and Not integrated: the proposed full-scale response targets and current database/photo recovery passed under the recorded local configuration and limits. T25 readiness is prepared but awaits T24 main integration and Jerome's separate diagram go signal. See [current readiness](../HANDOFF.md) and [executed acceptance mapping](manual-test-guide.md#module-21--automated-system-acceptance-t22). Remaining requirements stay planned until their own acceptance evidence exists. Requirement identifiers A1–A8 and U1–U4 refer to [Project-Requirements.txt](Project-Requirements.txt). Product purpose is defined in [PRD.md](PRD.md), field definitions in [db_design.md](db_design.md), and HTTP contracts in [api_spec.md](api_spec.md).

A **catalog item** describes an equipment type; an **equipment unit** is one physical asset. An **allocation** holds a specific unit for a request item. A **loan** records release; a **loan unit** records one issued allocation; a **return** records one loan unit coming back. An **active allocation** has no end timestamp and continues through reservation and issue until cancellation or return.

## Roles and access

| ID | Required behavior | Acceptance criterion |
| --- | --- | --- |
| SEC-01 | Exactly `BASIC_USER` and `ADMIN`, using Django authentication | Successful username or unambiguous case-insensitive email login redirects to `/portal/` or `/manage/` according to the stored role; ambiguous identifiers are denied |
| SEC-02 | Server-side admin checks on every management action, report, export, and detail page | A basic user cannot invoke them through GET, POST, forged form fields, or direct URLs |
| SEC-03 | Scope portal lookups to the signed-in owner | Guessing another request/loan ID returns 404 and exposes no data |
| SEC-04 | Check active status on every protected request, including existing sessions | Deactivation blocks login and subsequent protected operations without deleting history |
| SEC-05 | Registration fixes the role to `BASIC_USER`; profile forms allow only name/contact | Forged role, activation, ownership, and permission fields do not change protected values |
| SEC-06 | Only an active authorized admin or documented management command can create an admin | No public registration or profile path can create/promote an admin |

## Functional requirements

| ID | Required behavior | Acceptance criterion |
| --- | --- | --- |
| A1 | Custom account list, search, detail/history, activate, and deactivate | Status changes are audited; user history remains intact |
| A2 | Custom category/item list, detail, create, update, archive; unit registration/update and filters; optional catalog photo and restoration enhancements | Asset codes are unique; referenced history is preserved; archived catalog records cannot receive new requests. Optional photo upload/replacement/removal and catalog restoration are ADMIN-only; see the [inventory interface contract](api_spec.md#custom-administration-accounts-and-inventory) and BR-13 |
| A3 | Searchable, paginated review queue with status/date filters, quantities, due date, purpose, and live availability | Approval/rejection records admin, timestamp, and reason; approval reserves every requested quantity or changes nothing |
| A4 | Issue an Approved request and show a printable borrowing slip | Exactly one loan per request; slip contains borrower, asset codes, release date, and due date; invalid or repeated issue is rejected |
| A5 | Return individual issued units with date and condition; support partial returns | No duplicate return; loan closes only after all loan units return; damaged return opens maintenance within the same transaction |
| A6 | Open and close maintenance with problem, action, dates, and admin; reconcile inventory | Reserved/Issued units reject maintenance creation; repaired units become Available; retired units remain unavailable |
| A7 | Four live cards: available units, pending requests, active loans, overdue loans | Each value changes appropriately after committed transactions; active includes partially returned loans |
| A7-CHART | Monthly issued-loan chart and equipment-category usage chart | Use stored loans/loan units; monthly count counts loans once; category usage counts issued physical units, including returned units |
| A7-REPORT | Date-filtered loan and overdue reports with CSV export | HTML and CSV use identical filters and calculations; related borrower, item, unit, and return data produce computed totals |
| A8-AUDIT | Admin-only searchable audit history | Approval, rejection, cancellation, release, return, maintenance, account, catalog, and settings changes identify actor, time, action, and record |
| A8-SETTINGS | Manage positive maximum loan duration and quantity per request item | Initial values are 7 calendar days and 3 units per request item; changes apply to newly submitted requests |
| U1 | Register, sign in/out, and edit personal name/contact only | Django hashes passwords; identity and authorization fields cannot be self-edited |
| U2 | Search active items by name/category and show description, total serviceable units, and available quantity | Portal never exposes other borrowers, internal notes, audit entries, or maintenance details |
| U3 | Submit purpose, desired return date, and one to three distinct item/quantity rows | All rows validate before any save; successful submission creates only Pending records |
| U4 | View own requests/loans, due dates, issued units, and returns; cancel only before issue | Only Pending/Approved can cancel; Approved cancellation releases all held units atomically |

## State transitions

Persist only the following request states and transitions. Overdue is derived, not stored as a request state.

| Current state | Action | Next state | Required inventory effect |
| --- | --- | --- | --- |
| PENDING | Approve | APPROVED | Allocate all quantities; Available units become Reserved |
| PENDING | Reject | REJECTED | None |
| PENDING | Cancel by owner | CANCELLED | None |
| APPROVED | Cancel by owner | CANCELLED | End allocations; Reserved units become Available |
| APPROVED | Release by admin | ISSUED | Create loan/loan units; Reserved units become Issued |
| ISSUED | Return some units | PARTIALLY_RETURNED | Returned units become Available or Maintenance |
| ISSUED | Return all units | RETURNED | Close loan; each returned unit becomes Available or Maintenance |
| PARTIALLY_RETURNED | Return remaining units | PARTIALLY_RETURNED or RETURNED | Close only when no outstanding loan unit remains |

REJECTED, CANCELLED, and RETURNED are terminal. Reopening, editing quantities after submission, post-issue due-date changes, and re-approval are outside this baseline. Admins review requests; borrower cancellation is the defined cancellation action.

Each physical unit has exactly one stored inventory status: `AVAILABLE`, `RESERVED`, `ISSUED`, `MAINTENANCE`, or `RETIRED`. Terminal request status does not erase allocation or loan history.

## Business rules and calculations

| ID | Rule |
| --- | --- |
| BR-01 | Validate 1–3 distinct active catalog items, positive integer quantities within the configured per-item maximum, nonblank purpose, and valid due date before saving any request rows. Active category is also required. |
| BR-02 | For submission date D and configured maximum M, require D < desired due date <= D + M calendar days. Use Asia/Manila calendar dates. |
| BR-03 | Snapshot the duration and quantity limits on submission. Existing requests retain those limits when settings change. |
| BR-04 | Approve under one database transaction, rechecking request state, active borrower, eligible catalog items, and locked unit availability. Any shortage rolls back the entire approval. |
| BR-05 | Release requires APPROVED state, exact allocation counts for every request item, valid unit/item relationships, active borrower, and local release date <= agreed due date. |
| BR-06 | An admin may revise an APPROVED request's due date before issue with a required reason and audit entry. It must remain after submission, within the snapshotted duration limit, and on/after the current local date. Preserve the original desired date. If no valid date remains, the borrower must cancel and submit a new request. |
| BR-07 | A unit cannot have simultaneous active allocations. Releasing an allocation does not end its exclusivity; return or cancellation ends it. |
| BR-08 | A return belongs to an issued loan unit, occurs no earlier than issue, is recorded by an admin, and cannot be repeated. Use server timestamps; historical seed data is a separate controlled process. |
| BR-09 | A damaged return ends its allocation and opens maintenance atomically. Manual maintenance opening rejects Reserved, Issued, Retired, or already-in-maintenance units. |
| BR-10 | Closing maintenance requires an action and either AVAILABLE or RETIRED as its outcome. Repaired units become serviceable; retired units stay unavailable and cannot be reactivated through generic editing. |
| BR-11 | Outstanding units are loan units without a ReturnRecord. A loan is active if at least one unit is outstanding; overdue if active and local today > loan due date. Overdue days = max(0, today - due date) in calendar days for active loans. Closed loans are excluded from overdue results. |
| BR-12 | Inventory total = Available + Reserved + Issued + Maintenance + Retired. Proposed meaning of serviceable total = Available + Reserved + Issued. These counts are queried, never manually entered. |
| BR-13 | Archive category/item master records rather than deleting transaction references. Archival blocks new requests and approvals; existing reservations, issue, returns, and maintenance must still be handled. Optional admin restoration clears only the selected master record's archive flag and is audited atomically. Individually archived items stay archived when their category is restored; an item restored under an archived category stays ineligible until its category is active. Physical-unit statuses and historical references are unchanged. |
| BR-14 | Commit the audit record in the same transaction as its business change. Missing audit data must fail the operation. Audit entries have no ordinary edit/delete interface. |
| BR-15 | Generic unit editing cannot change workflow status, catalog identity after transactional use, or transaction-linked asset codes. New units start Available only if serviceable; otherwise start Maintenance with an associated maintenance record. |

BR-03, BR-06 details, BR-12's serviceable definition, and BR-15 are proposed implementation conventions that clarify the brief. Validate them during team/acceptance review; they do not represent additional instructor instructions.

## Report contracts

Use optional inclusive `date_from` and `date_to` values, comparing the Asia/Manila issue date. Reject invalid/reversed ranges. Missing bounds mean unbounded on that side. Overdue reports first select currently outstanding overdue loans, then apply the same issue-date range. Clearly label this filter in the UI.

Loan rows include loan ID, borrower, issue date, due date, request status, issued quantity, returned quantity, and outstanding quantity. Overdue rows additionally include overdue days. CSV exports include the same columns and protect spreadsheet cells from formula interpretation. Aggregate per loan before joining returns to avoid multiplying counts.

## Non-functional requirements

Security requirements derive from the brief. Numerical performance targets below are proposed acceptance targets, not measured results or instructor-specified service levels.

| ID | Requirement and verification |
| --- | --- |
| NFR-01 Security | CSRF on every state-changing form; POST-only mutations; Django password validation/hashing; escaped user content; server-side field allowlists, ownership, role, and activation checks. Test direct HTTP requests. |
| NFR-02 Confidentiality | Collect only authentication and necessary name/contact data. Keep secrets, raw passwords, session/CSRF tokens, and private borrower data out of logs, public documents, and seed data. Reports/audit/maintenance stay admin-only. |
| NFR-03 Integrity | Use atomic workflow services, database constraints, and PostgreSQL row locks. Demonstrate one successful reservation from two competing approvals and no partial writes after failed validation. |
| NFR-04 Usability | Responsive role layouts, explicit empty states, form-specific errors, confirmation for consequential actions, readable status labels, keyboard-operable forms, and associated field labels. Verify manually at mobile and desktop widths. |
| NFR-05 Performance | Proposed lab target: p95 <= 2 seconds for lists/details and <= 3 seconds for dashboard/reports with 10 concurrent sessions, 1,000 units, and 5,000 requests. Measure on a recorded machine/database configuration; record failures and findings. |
| NFR-06 Growth | Use the route-specific page sizes in [the HTTP contract](api_spec.md#common-protocol); validate page/filter inputs; index common lookups; use related-object loading and ORM aggregation. No distributed deployment or enterprise-scale capacity claim is required. |
| NFR-07 Maintainability | Follow [AGENTS.md](../AGENTS.md), reusable service functions, named URLs, per-role base templates, migrations, and feature-level integration tests. Exact tested dependencies belong in the future requirements file. |
| NFR-08 Failure visibility | Validation/conflict failures give actionable messages and preserve data. Configuration errors fail clearly; unexpected exceptions are logged safely and return an error page without technical or private data. No silent recovery. |
| NFR-09 Recovery | Before evaluation, demonstrate a database backup/restore and record limitations and maintenance guidance. No recovery-time promise is made before measurement. |
| NFR-10 Accessibility and ethics | Review applicable campus/privacy/accessibility policies, asset licenses, and permitted AI assistance; retain decisions and evidence without claiming unverified legal compliance. |

## Minimum acceptance scenarios

1. Register/login both roles, reject forged privilege fields, and block a deactivated account with an existing session.
2. Attempt cross-user access to detail/history/cancel routes and direct basic-user access to all management routes and exports.
3. Submit three valid items; then submit with one invalid row and verify that no parent or child request is saved.
4. Have two transactions approve different requests for the final available unit; exactly one succeeds, with consistent units, allocations, and audit data.
5. Cancel an Approved request and verify every reservation is freed; reject cancellation after issue.
6. Release once, print a correct slip, reject repeat issue and issue after due date, and test audited pre-issue date revision.
7. Return one of several units, reject duplicate return, process a damaged return, and close only after the final return.
8. Reject maintenance on Reserved/Issued units; complete repair and retirement; reconcile all five inventory counts.
9. Verify overdue behavior before/on/after due date and disappearance from overdue results after full return.
10. Change live transactions and verify dashboard, charts, filtered reports, and CSV results change consistently.
11. Verify archive behavior, quantity/duration settings for new requests, and search/pagination/empty/error states.

The demonstration dataset and course evidence checklist are maintained only in [tasks.md](tasks.md). Requirements are accepted only when observable behavior and relevant evidence are available.
