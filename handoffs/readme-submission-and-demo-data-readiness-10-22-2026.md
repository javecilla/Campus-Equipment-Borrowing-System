# README, submission and demonstration-data readiness

Date: October 22, 2026, 22:15 Asia/Manila. Owner: Jerome request; Codex documentation/read-only verification. Scope: README/SUBMISSION clarity, Part 5/6 traceability and existing demonstration-data assessment; partial technical documentation supporting T29/T30.

## Outcome

[README](../README.md) now states the system name/overview and gives copyable PowerShell dependency, local database, environment, migration, seed and server steps with their purpose and prerequisites. All six Part 5 rules link actual services/models/tests; Django/ORM/templates/security, PostgreSQL concurrency/portability limitations and isolated verification commands are explained. The course permits a working local demonstration. Neon is voluntarily used for centralized team end-to-end testing; deployment, paid hosting and external integrations are not required. The user's clarification is retained without treating optional infrastructure as a course obligation.

[SUBMISSION](../SUBMISSION.md) maps all six Part 6 evidence groups, private credentials, ZIP contents/exclusions and clean-machine checks. Fixed the malformed borrower/demo row, restored reports/CSV/charts to the demo plan and included the required last-unit race within the proposed 12 minutes. The 3-minute Q&A and every-member evidence remain required; no presenters, rehearsal, policy approval or individual records were invented. Existing 72 screenshot links/checklist results are preserved.

## Actual read-only data result

At October 22, 2026, 22:03 Asia/Manila, explicit local overrides selected `campus_equipment`, PostgreSQL 17.5 and local media. A Django ORM inspection ran inside a transaction confirmed as `transaction_read_only=on`. Totals: **12 categories, 29 catalog items, 46 units, 1 ADMIN, 8 BASIC_USER, 30 requests, 20 issued loans and 10 maintenance records**; all course minimums pass. Also verified: 2 rejected/3 cancelled requests, 1 current partial return, 1 damaged return with linked maintenance, 34 issued units/28 returns, and dashboard 30 Available/3 Pending/4 active/2 overdue. A second explicit read-only local check verified all nine stored usernames, names, emails and roles exactly match the fictional seed roster. No real identity, password or private record was printed into shared documentation.

The 4 active loans are a subset of 20 issued loans (16 fully returned); overdue is a subset of active loans. Unit states sum to 46. [SUBMISSION's data section](../SUBMISSION.md#minimum-demonstration-data) owns this dated explanation.

## Remaining work and state

Source baseline: local `jerome` `36b3835d8a054baf31ae9f770190b4f6054c49ed`; fresh fetched main `bd4d7e36380772a1e2a9285fea0c98614937e299`. Application source `c3fb6bb` is already integrated through PR #64; this documentation update is **uncommitted / Not integrated**. No commit/push is requested by the documentation task. Existing historical publication receipts remain unchanged.

Current data sufficiency does not prove clean-database reproducibility. Inspection of the actual seed commands confirmed: account seed creates accounts only; unit seed requires a catalog; fixed history requires named stock and empty borrowing history and adds only one damaged-return maintenance record. The manual catalog and other maintenance records have no complete reconstruction seed/fixture. T29/T30 owners must provide a reviewed fictional catalog/maintenance fixture or equivalent seed and rehearse the actual ZIP without Neon/private backups. Current records were preserved; no seed, migration, reset or fixture export was performed. T21's previously delivered populated-dataset result is retained, while this packaging gap is explicit.

T25 conversion/review and T27/T28 evidence remain pending under their existing owners. Full T29 verified guides and T30 packaging remain **Not started**; this technical-doc refresh does not close either task or authorize unrelated application work.

## Verification

Source references, environment parser, settings, migrations, named routes, seed commands/plans and dashboard/report queries were inspected. Fresh verification passed: **878 local links/anchors across five affected documents**, Markdown parsing, README/SUBMISSION table widths, **11 PowerShell command blocks** and **3 embedded Python commands** parsed without executing setup commands, all 72 existing PNG paths/counts and `git diff --check`. The proposed demo times sum to 12 minutes, plus the separate 3-minute Q&A. Application tests, asset builds, migrations, seeds, shared Neon queries, clean-machine installation and complete minimum-data replay were **not run**. The prior 345-test isolated local PostgreSQL result remains attributed to the [implementation handoff](local-database-switch-and-submission-screenshots-10-22-2026.md), not this update.

Next: Jerome reviews this uncommitted documentation; T29/T30 owners address reproducible fictional data and verified guides, then follow the remaining submission gates. No credentials, application behavior, database records or shared media changed.
