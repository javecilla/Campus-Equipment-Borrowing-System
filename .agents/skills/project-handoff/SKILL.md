---
name: project-handoff
description: Create a dated work handoff in the Campus Equipment Borrowing project's handoffs folder and update the current handoff index and affected backlog entries. Use after file-changing tasks, session wrap-up, or transfer of unfinished work; read-only questions do not require artificial handoff files.
---

# Project Handoff

Maintain current, verifiable context for the next member or agent. This skill writes documentation only; it does not authorize implementation, commits, pushes, dependency installation, or external messages.

1. Read the latest [AGENTS.md](../../../AGENTS.md), [HANDOFF.md](../../../HANDOFF.md), relevant existing [handoffs](../../../handoffs/), and affected entries in [tasks.md](../../../docs/tasks.md). Resolve links from this skill directory. Inspect actual changed files and available verification results. Use Git status/diff only when this checkout has Git metadata.
2. Create one work handoff in the project-root `handoffs/` folder. Name it `{title-of-work}-{MM-DD-YYYY}.md`, using a descriptive lowercase hyphenated title and the current date in Asia/Manila. Example: `handoffs/initial-project-setup-documentation-10-16-2026.md`. Create the folder if missing. If a completed handoff already has that title/date, choose a distinct work title before the date, such as `initial-project-setup-documentation-follow-up-10-16-2026.md`; do not overwrite another handoff.
3. Write a concise snapshot of the work: date/time zone, known author/member, task IDs and scope, outcome, relevant file links, decisions, actual checks/results, unrun checks/limitations, blockers, and the next action/owner. Distinguish previous session verification from checks run for this handoff. If the author/member is unidentified, write "AI agent; member not specified" rather than guessing. Link canonical requirements/design/setup rules instead of copying them into the snapshot.
4. Update only affected backlog entries. Keep application tasks Not started when only their design was documented. Mark Done only when stated acceptance checks actually pass. Update HANDOFF.md's relevant current-state sections and add a link to the new file in its dated handoff index; keep the root file useful as the entry point for the next agent.
5. Preserve earlier completed handoffs and other members' rows/active work. Re-read shared files before the final write and reconcile intervening edits. Finalize your in-progress handoff after verification; do not replace another person's historical snapshot. Current-state summaries may change as work progresses, while dated handoffs retain the state at transfer.
6. Check filename/date, links, and statuses, then summarize the outcome and material limitations to the user with the handoff path. Do not store transcripts, real credentials, private borrower data, or unsupported claims. Leave changes uncommitted unless the user explicitly requested a commit.

Use `handoffs/` for both developer and AI work handoffs, with one file per completed work scope or transfer of unfinished work. Do not create separate per-person folders or a duplicate changelog. If a task ends partially complete, state exactly what remains and the smallest next step. A missing tool or interrupted run is not proof of a completed check.

The AGENTS.md completion rule requests this workflow after file changes. Skill discovery or implicit invocation alone does not guarantee execution; agents that do not load repository instructions need this file supplied explicitly.
