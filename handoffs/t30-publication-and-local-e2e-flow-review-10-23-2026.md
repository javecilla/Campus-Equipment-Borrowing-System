# T30 Publication and Local E2E Flow Review

- **Date:** October 23, 2026, Asia/Manila.
- **Owner:** Jerome authorized publication and supplied the E2E guide; Codex reviewed documentation and database/source alignment. Existing member credit remains intact.
- **Scope:** Publish T30 ownership/date documentation and the supplied [E2E flow guide](../docs/e2eflow.md), corrected for Jerome's local presentation environment. No application implementation or workflow execution.

## T30 publication

Source `edb2f916606e6d550bba641aafd415b59b0eb6d2` was committed/pushed on `origin/jerome` with
`Co-authored-by: Codex <codex@openai.com>`. A fresh fetch matched local HEAD to that exact remote hash;
the trailer was verified. Fetched main was `94fd49d7f134cfa6dba782982b1bcf7ec10047c5` (PR #80).
This T30 update is **Not integrated**. The [original ownership snapshot](t30-submission-ownership-and-october-26-presentation-10-23-2026.md)
preserves its pre-publication state. Ownership handoff is Done; actual T30 package delivery remains In progress.
Jerome packages/uploads/invites Alex, who submits through the professor's channel; presentation is Monday, October 26.
The [submission checklist](../SUBMISSION.md#t30--submission-zip-checklist) retains actual verification/delivery steps.

## Local E2E guide review

Jerome subsequently authorized including `docs/e2eflow.md` and asked for database review, then clarified that the
presentation uses **local PostgreSQL and local media**. The guide now uses that environment and separate browser profiles
on one presentation machine. Teammates' independent local databases do not share transactions.

At **21:55 Asia/Manila**, a Django shell query with explicit child-process local/media overrides verified
`current_database() = campus_equipment` and `transaction_read_only = on` inside a read-only transaction. No private
configuration was modified. Results: 12 categories, 29 items, 46 units, 30 requests, 20 loans, 10 maintenance records;
all four initial personas active with correct roles, 7-day/3-unit limits, and all 23 referenced local photo files present.
Student Loan Laptop was separately verified active with three Available units. Fourteen critical guide routes resolved
through Django's URL resolver, without HTTP requests. Photo HTTP delivery and password authentication were not rerun.

The initial MCP target was also confirmed local/read-only. Before Jerome clarified local presentation use, a separate
read-only `neondb` inspection found different stock/history; that shared snapshot is not the guide's presentation baseline.
Every database review transaction was read-only; no data was changed on either database.

Corrections include unavailable tripod/Lenovo examples, a three-valid-item request, reason-required automatic allocation,
Pending rejection semantics, borrower-only cancellation and exact ownership 404s, pre-issue date revision ordering,
Issued/Partially returned/Returned request states versus Active/Overdue/Closed loan badges, a new three-unit return
sequence, actual maintenance closure fields, a real overdue borrower, date-only report filters/CSV scope, audit references,
and local photo/browser setup. Manual contention and browser-only validation are not presented as controlled server tests.
Retirement is explicit and conditional because no restore workflow exists; expired issue remains Not run without an eligible request.

The guide retains an unfilled result table. Its expected checkmarks are not proof that those steps ran; Jerome's prior
[T28 confirmation](t28-team-participation-completion-10-23-2026.md) remains separately attributed. The
[canonical manual guide](../docs/manual-test-guide.md) and [automated acceptance section](../docs/manual-test-guide.md#module-21--automated-system-acceptance-t22)
remain the full coverage references. No additional SRS acceptance or T30/T31 completion is claimed.

## Verification and next action

Reviewed guide/source alignment, local database preconditions, relative links/anchors, Markdown fences and staged/working
`git diff --check`. No tests, HTTP/browser workflow, migration, seed, purge, backup/restore or media/database write ran.
No ZIP/upload/invitation/external message/submission was performed.

This publication includes the reviewed guide and current handoff/backlog/index reconciliation. Jerome uses the guide on
the local presentation machine, rechecks stock/dates, and records actual outcomes if run. Keep the existing local dataset
and media. Jerome/Alex retain their final package/submission responsibilities; main integration remains a separate action.
