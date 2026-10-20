# PR #46 inactive-login conflict resolution

- **Owner:** Jerome with Codex review/integration assistance; Alex Enrico Cayanan retains implementation credit.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** AUTH-02, PR #46, issue #18; reconcile Alex `4a1cda3` with main `9d67fab` (user-merged PR #48).
- **Outcome:** The sole HANDOFF.md conflict is resolved, retaining Alex's authentication evidence and current dashboard/workspace records. Authentication source is unchanged from Alex; dashboard/UI source is unchanged from main. Main integration and issue closure are authorized and pending.

## Verification

- Full PostgreSQL suite: **304 passed in 74.818s**; focused authentication: **20 passed in 19.358s**. Test databases were removed.
- Django database check, migration drift/applied checks, Ruff lint and changed-auth formatting, pip consistency, npm format/build (nine contrast pairs), audit (zero vulnerabilities) and diff checks pass.
- Full Ruff format retains unrelated findings in accounts/views.py, inventory/tests/test_portal_equipment.py and the Python example in handoffs/borrower-portal-ui-improvements-10-20-2026.md. Full djLint retains the unrelated equipment-list long tag. Those files were preserved.
- Chromium 153.0.8010.12: correct inactive username and uppercase email show the specific message; wrong/unknown credentials remain generic; failed attempts create no session. Actual admin deactivation invalidates an existing borrower session with 403; reactivation restores unchanged credentials. The 320px page has no horizontal overflow; no JavaScript errors. Disposable fixtures only; browser/server closed and test_pr46_auth_review database explicitly removed and absence verified.
- Current read-only development lookup found neither historical example localadmin nor basicdemo. No live accounts or other business data changed. [Manual cases](../docs/manual-test-guide.md#17-block-an-inactive-account-requires-creating-one-first) now distinguish prerequisites from actual isolated execution.
- PR #48 preserves dashboard source f3d42ba and publication receipt 5fb8236; main merge tree equals the published receipt tree. Codex/Kiro credit is preserved. Earlier dated handoffs remain historical snapshots.

## Files and next action

The merged authentication files are [LoginForm](../accounts/forms.py), [authentication tests](../accounts/tests/test_authentication.py) and [HTTP contract](../docs/api_spec.md). Current evidence is in [HANDOFF](../HANDOFF.md), [tasks](../docs/tasks.md), [manual guide](../docs/manual-test-guide.md) and [AGENTS](../AGENTS.md).

Commit the reconciliation as a merge, push normally to alex, merge PR #46 using the tested head, verify main ancestry/tree equality and close issue #18. Refresh current integration evidence after the authorized merge. T19/T20 and diagrams remain separately gated.
