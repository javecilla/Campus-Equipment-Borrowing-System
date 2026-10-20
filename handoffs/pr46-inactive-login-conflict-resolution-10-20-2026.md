# PR #46 inactive-login conflict resolution

- **Owner:** Jerome with Codex review/integration assistance; Alex Enrico Cayanan retains implementation credit.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** AUTH-02, PR #46, issue #18; reconcile Alex `4a1cda3` with main `9d67fab` (user-merged PR #48).
- **Outcome:** The sole HANDOFF.md conflict is resolved, retaining Alex's authentication evidence and current dashboard/workspace records. Authentication source is unchanged from Alex; dashboard/UI source is unchanged from main. Resolution merge `14d3a27c15f280445e0a22bdceb0e90ac0b79740` is committed/pushed to `alex` with Codex co-author credit. PR #46 is merged into main at `c0529009cacd3e234f04cc07b4fc5c4c70261522` on October 20, 23:09:04 Asia/Manila. Issue #18 closed as completed at 23:09:06.

## Verification

- Full PostgreSQL suite: **304 passed in 74.818s**; focused authentication: **20 passed in 19.358s**. Test databases were removed.
- Django database check, migration drift/applied checks, Ruff lint and changed-auth formatting, pip consistency, npm format/build (nine contrast pairs), audit (zero vulnerabilities) and diff checks pass.
- Full Ruff format retains unrelated findings in accounts/views.py, inventory/tests/test_portal_equipment.py and the Python example in handoffs/borrower-portal-ui-improvements-10-20-2026.md. Full djLint retains the unrelated equipment-list long tag. Those files were preserved.
- Chromium 153.0.8010.12: correct inactive username and uppercase email show the specific message; wrong/unknown credentials remain generic; failed attempts create no session. Actual admin deactivation invalidates an existing borrower session with 403; reactivation restores unchanged credentials. The 320px page has no horizontal overflow; no JavaScript errors. Disposable fixtures only; browser/server closed and test_pr46_auth_review database explicitly removed and absence verified.
- Current read-only development lookup found neither historical example localadmin nor basicdemo. No live accounts or other business data changed. [Manual cases](../docs/manual-test-guide.md#17-block-an-inactive-account-requires-creating-one-first) now distinguish prerequisites from actual isolated execution.
- Documentation checks: 485 local relative links, balanced Markdown code fences, conflict-marker absence, diff whitespace, and exact authentication/UI source preservation pass.
- PR #48 preserves dashboard source f3d42ba and publication receipt 5fb8236; main merge tree equals the published receipt tree. Codex/Kiro credit is preserved. Earlier dated handoffs remain historical snapshots.

## Files and next action

The merged authentication files are [LoginForm](../accounts/forms.py), [authentication tests](../accounts/tests/test_authentication.py) and [HTTP contract](../docs/api_spec.md). Current evidence is in [HANDOFF](../HANDOFF.md), [tasks](../docs/tasks.md), [manual guide](../docs/manual-test-guide.md) and [AGENTS](../AGENTS.md).

GitHub merged PR #46 using the pinned tested head and merge strategy. Fetched main contains both parents and exactly equals the tested resolution tree; issue #18 is verified closed as completed. Local jerome was fast-forwarded to fetched main. This final documentation receipt updates current integration evidence and is published on jerome; no further application change or test rerun was needed. Alex / T19 remains ready from integrated T18; T20 still waits for integrated T19. Diagrams remain on standby.
