# T19 and T20 manual testing guide simplification

- Date: October 21, 2026, Asia/Manila.
- Owner: Jerome Avecilla with Codex documentation assistance. Alex retains T19 implementation credit; Ralph retains T20 implementation credit.
- Scope: make the existing manual guide easier to follow. Documentation only; preserve the earlier uncommitted T20 integration-review changes and historical handoffs.

## Outcome

Rewrote [Module 18 / T19](../docs/manual-test-guide.md#module-18--administrator-loan-and-overdue-reporting-t19) and [Module 19 / T20](../docs/manual-test-guide.md#module-19--integrated-role-workspaces-t20) around setup, numbered browser actions and observable expected results. T19 now has five short cases; T20 has three. Developer checks and cases requiring more records are separate, with missing data explicitly recorded as Not run. A shared checklist records the tester's own results without replacing historical passes.

The T19 example identifies issue dates, quantities and why an empty Overdue report is currently correct. T20 explains per-owner counts, full history versus active-loan counts, the overdue preview shortcut, separate login sessions and one controlled request-submission/cancellation walkthrough. Existing implementation/verification handoffs supply detailed historical evidence instead of long command histories inside the walkthrough.

## Actual checks and limits

- Read-only local PostgreSQL transaction at October 21, 16:38 Asia/Manila confirmed `transaction_read_only = on`. Two loans exist: #1 issued October 20, due October 24, quantities 1 issued / 1 returned / 0 outstanding; #2 issued October 20, due October 23, quantities 3 / 0 / 3. Neither is overdue on October 21. Aggregate quantities are 4 / 1 / 3. No borrower identities or credentials are published.
- The same read-only check found three active basic users and one active administrator; settings are seven maximum loan days and three units per item. These are dated examples, not a promise that records remain unchanged or that every user's home has the same counts.
- Checked actual report forms/views/templates, borrower submission redirect, status filter/pagination, cancellation labels and owner-scoped workspace queries. Valid submission redirects to My requests; it does not directly open request detail.
- Checked Markdown links/anchors, code references, table structure, paired fences and whitespace after the edits. No application code changed.
- No browser scenarios, request submissions, cancellations, spreadsheet opening, schema changes or seed commands were executed. This task did not rerun application tests; the prior review's 322 PostgreSQL passes remain separately attributed in its [receipt](t20-main-integration-review-and-documentation-10-21-2026.md).

## Next action

Jerome/team testers follow the basic cases first and record actual results in the guide's checklist, including Not run where setup is missing. T21 remains Not started; T22/T23, screen-reader/extra-browser/spreadsheet checks and diagram gates retain their existing status. No new feature work or publication was performed. Leave changes uncommitted for review.
