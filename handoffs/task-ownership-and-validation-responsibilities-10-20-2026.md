# Task Ownership and Validation Responsibilities

- **Owner/author:** Team allocation decision supplied by the user; Codex documentation assistance.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** Current ownership for T15–T20, supporting validation/documentation/manual testing and the T25 diagram standby gate. Documentation only on `jerome`, uncommitted and not integrated.
- **Outcome:** T15/T16 belong to Jerome, T17/T20 to Ralph and T18/T19 to Alex. Kenneth, Margareth and Ellyssa focus on validation, documentation and manual testing. T16 remains Done/integrated; Kenneth's baseline and Jerome's corrections retain their credit. All other task statuses remain unchanged.

## Current decisions and files

[The backlog ownership section](../docs/tasks.md#current-ownership-and-support-responsibilities) is canonical for the revised allocation and support responsibilities. [PLAN.md](../PLAN.md) reflects the delivery responsibilities; [README.md](../README.md), [CONTRIBUTING.md](../CONTRIBUTING.md), [AGENTS.md](../AGENTS.md), [DEV.md](../DEV.md) and [HANDOFF.md](../HANDOFF.md) route members and agents to those current assignments. [Architecture ownership](../docs/architecture.md), [SRS readiness](../docs/SRS.md), [folder guidance](../docs/project-folder-architecture.md), [manual testing](../docs/manual-test-guide.md) and [member prompts](../docs/team-agent-prompts.md) now use the new feature owners. Support prompts authorize available validation/documentation/manual testing rather than reassigned feature implementation.

Kenneth, Margareth and Ellyssa keep diagram work on standby until Jerome confirms the system is fully finished and explicitly gives the go signal; T25's existing T22/T23/T24 prerequisites also apply. Existing MTV/database/workflow diagrams are partial drafts to reconcile with the final system and convert into editable diagrams in an actual tool such as Lucidchart. Canonical design documents will link editable sources and readable exports. No tool selection, diagram creation or go signal is claimed.

Original requirement/member TXT files, existing branches, completed handoffs, acceptance behavior and integration evidence are preserved. Reassignment does not restart completed work or authorize implementation, publication or main integration.

## Verification and limitations

- Checked 13 changed/new Markdown files and 740 relative links/anchors: no newly broken links; code fences are balanced. The existing README link to `DEV.md#expected-startup-screen` is already broken in HEAD because the heading is now “Earlier startup screen”; it is preserved outside this allocation scope.
- Compared the canonical backlog with HEAD: all 31 task statuses are unchanged, all six T15–T20 owners match the requested assignments, and existing prerequisites are preserved with the explicit T25 diagram go-signal gate added.
- Checked all three support prompts for validation/documentation/manual-testing scope and the diagram gate. Original requirement/member records and historical handoffs are unchanged; the diff contains documentation only.
- `git diff --check` passed. No dependency, skill metadata, application code, schema or live data changed.
- Application tests and browser/manual execution were not run for this documentation-only task; earlier recorded application results are historical evidence. No diagram tool was opened or artifact created.

## Next action and owner

Jerome reviews this uncommitted allocation update. T15 is his next ready feature with integrated T13/T14; it remains Not started until authorized implementation. Ralph's T17 waits for T15 with T16 already integrated; Alex's T18/T19 and Ralph's T20 retain their dependency gates. Kenneth, Margareth and Ellyssa can validate available implemented flows, document actual results and report defects to feature owners now. They wait for Jerome's explicit go signal and T25 prerequisites before diagram conversion. No task completion or manual-test result is fabricated by this allocation update.
