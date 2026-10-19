# T11 main sync documentation and manual test guide

- Date: October 18, 2026, Asia/Manila (+08:00).
- Work/owner: Jerome with Codex documentation assistance; Ralph's T11 and Ellyssa's T10 source/credit preserved.
- Scope: reconcile current documentation after the user's pull of main, transfer the verified integration receipt from the review worktree, and update the existing local manual-test guide as subsequently requested.
- Outcome: documentation records **T01-T11 Done and integrated**, actual PR #27 merge `6c5ea8f`, and ready-but-Not-started T12/Ralph, T13/Margareth and T16/Kenneth. The user is manually testing T11; no manual-test outcome has been supplied.

## Current interfaces and evidence

Local `jerome` HEAD and `origin/main` are `6c5ea8fcebbcd7dec2099edd66e53148cce2a75b`, preserving Ralph `7477b2b`, resolution `55b0a3b`, T10 and the T09 correction. The transferred [main integration receipt](pr27-t11-main-integration-10-18-2026.md) retains the historical state at the merge. Current readiness is in [HANDOFF](../HANDOFF.md), with canonical acceptance/integration in the [backlog](../docs/tasks.md#verified-task-evidence).

T11 request creation uses [portal URLs](../accounts/portal_urls.py), [forms](../borrowing/forms.py), [submission service](../borrowing/services.py) and [request template](../templates/borrowing/portal/request_form.html). The existing [administrator account history](../templates/accounts/manage/detail.html) displays submitted request IDs, purposes, quantities, status and due date, providing a browser check while borrower history/cancellation remain T12 work. Approval remains T13 work; submission creates only Pending records and no allocation.

Updated [README](../README.md), [DEV](../DEV.md), [AGENTS](../AGENTS.md), [SRS](../docs/SRS.md), [architecture](../docs/architecture.md), [HTTP contract](../docs/api_spec.md), [folder guide](../docs/project-folder-architecture.md), current handoff/backlog and [manual guide](../docs/manual-test-guide.md). PLAN sequencing and completed snapshots are unchanged. Application files, private configuration, databases and generated assets were not modified.

## Manual guide coverage

Module 9 covers the current create/confirmation flow, success with one to three distinct items, third-row atomicity, blank/duplicate/invalid inputs, formset limits, archived and stale selections, permissions/CSRF/forged fields, stored settings snapshots and unchanged inventory counts. It provides a read-only snapshot query and a results template without inventing execution results. It explains known navigation polish, pending T12/T13 and the difference between requesting and reserving units.

Earlier sections now use reproducible seed identities rather than asserting current local account contents, current settings rather than assumed defaults, actual audit reference/action/actor filters, the Manage photo interface, maintenance-history identity locks and the integrated 181-test baseline. The manual guide was already untracked; the user's explicit follow-up authorizes editing it. It remains uncommitted with this documentation batch.

## Checks and remaining work

The existing source comparison confirms local application paths match HEAD and the tested resolution tree. The preceding PR #27 review passed **181 PostgreSQL tests in 28.472s**, plus configured checks; those results are prior evidence. Tests/builds were not rerun for prose changes while the user manually tests. Fresh verification passes: **546 local links across 12 Markdown files**, including heading anchors; balanced fences, encoding, current statuses, whitespace and documentation-only scope. All seven named test-command module paths exist, and the manual guide's read-only Python snippet parses successfully.

Await actual manual findings before recording pass/fail or fixing application behavior. Existing non-blocking T11 navigation/style and T10 photo-test-storage findings remain in the [resolution review](pr27-t11-conflict-resolution-review-10-18-2026.md). Dependent feature implementation and a new commit/push/PR are outside this documentation request; changes remain local on `jerome` for review.
