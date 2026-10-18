# T11 manual guide with exact local inputs

- Date: October 18, 2026, Asia/Manila (+08:00).
- Work/owner: Jerome with Codex documentation assistance; no feature logic changed by this task.
- Request: make the manual guide concrete, with field/value tables and explicit expected results matching the user's examples.
- Outcome: [Module 9](../docs/manual-test-guide.md#module-9--borrower-request-submission-t11) now provides named T11 cases using verified local catalog labels/IDs, dates and limits. Manual execution remains in progress; no pass/fail result is fabricated.

## Verified input source

At **23:06:26 Asia/Manila**, a Django ORM query inside a PostgreSQL transaction explicitly set to **READ ONLY** inspected active catalog items under active categories, unit aggregates and SystemSetting row 1. The local date was October 18, 2026, with limits **7 calendar days / 3 units per item**. Nine active catalog items had available units. Selected concrete examples use HDMI Projector (ID 1), Portable PA Speaker (2), DSLR Camera (Canon EOS) (4), Adjustable Tripod (5), Lenovo ThinkPad Laptop (7), USB-C Hub 7-in-1 (8) and Digital Multimeter (13). The guide records the full nine-item availability table and a dated zero-availability example.

The valid date range for that submission date is October 19 through October 25 inclusive; October 18 and October 26 exercise invalid boundaries. The guide labels this as a local snapshot and instructs recalculating after a date/settings change. It does not assert that these stock counts or IDs apply to every teammate's database. No account identities, credentials, private environment values or borrower request contents were queried for the guide.

## Changes and corrections

- Added field/value tables for one, two and three items, exact quantity/date boundaries, and a Pending request for an active zero-availability item.
- Added explicit tables for blank purpose, invalid due dates, excessive/zero quantity, duplicates, empty/incomplete rows, and the critical two-valid-plus-invalid-third-row case. A settings comparison table gives original and changed snapshot inputs.
- Expected outcomes identify the actual `/portal/requests/` redirect and confirmation; saved requests are verified through the existing administrator account history while borrower history remains T12 work.
- Clarified that T11 submits catalog requests without allocating units; maintenance units cannot be allocated, but active catalog items with no available stock can still receive Pending requests. The example quantity 3 for a multimeter is valid under the configured limit despite only two available units.
- Distinguished expected rejection from a failed test, and retained advanced authorization, formset, archival, snapshot and UI checks. Existing completed documentation snapshots and unrelated local edits are preserved.

Relevant contracts/source: [request forms](../borrowing/forms.py), [submission service](../borrowing/services.py), [request view](../borrowing/views.py), [admin history template](../templates/accounts/manage/detail.html) and [HTTP contract](../docs/api_spec.md#new-request-form). Current task status/integration remains in the [backlog](../docs/tasks.md#verified-task-evidence) and [HANDOFF](../HANDOFF.md).

## Verification and next action

Fresh checks pass: **558 local links across 13 changed Markdown files**, including anchors, fences and encoding; command-module paths and read-only Python syntax; whitespace; all **15 main scenario tables and both settings examples** against verified item labels/IDs and existing pure date/quantity/duplicate validators. No HTTP requests were submitted. The prior **181-test PostgreSQL result** remains in the [integration receipt](pr27-t11-main-integration-10-18-2026.md); application tests/builds were not rerun for this documentation-only change. The database inspection used READ ONLY and wrote no rows; no browser scenarios were executed by Codex.

A concurrent local spacing edit adds `mt-5` to the request form's Submit button. It was observed during final scope checking, preserved without modification, and excluded from this task's documentation verification. This task does not claim fresh test/format evidence for that separate edit.

The user can run the tables and record actual results under the guide's result-record section. T11 stays Done and integrated; later tasks and existing review follow-ups retain their own status. This task does not authorize a commit/push or feature implementation; documentation changes remain uncommitted on `jerome`.
