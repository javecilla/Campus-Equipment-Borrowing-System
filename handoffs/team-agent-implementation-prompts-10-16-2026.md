# Team agent implementation prompts

- Owner: Jerome Avecilla (`@javecilla`), with Codex documentation assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Task/scope: DOC-06; provide implementation prompts that each member can send to their coding agent to start assigned ready work.
- Outcome: [Team AI implementation prompts](../docs/team-agent-prompts.md) provides six member prompts and one shared implementation workflow. The prompts authorize implementation when sent by the acting member, select current backlog assignments, verify integrated prerequisites, require checks/handoffs, and leave feature changes uncommitted.
- Entry points: [PLAN.md](../PLAN.md#prompts-for-team-coding-agents), [README.md](../README.md#documentation), and [DEV.md](../DEV.md) link the canonical guide. The readiness-only example remains explicitly optional in PLAN.md.
- Branch/publication: `jerome`, uncommitted changes over `1aebb9f`; **Not integrated**. No commit, push, PR, or main merge performed for this documentation task.

## Decisions and boundaries

Member names, handles, and branches come from the unchanged [source assignments](../docs/Project-Members.txt). Task ownership and acceptance stay in [tasks.md](../docs/tasks.md); the guide does not copy a task roster or replace PLAN.md's gates. Agents read the Django/handoff skills directly when automatic skill discovery is unavailable. No model-specific agent setup is required by the prompt.

Agents may continue independent ready assigned work, but cannot treat a task completed locally during the session as an integrated prerequisite. For example, Alex implements ready T04, then waits for its main integration before T05. Shared/evidence work requires the member's actual contribution; another owner's feature or human participation cannot be fabricated. A branch sync requiring a merge commit needs separate authorization under the existing Git rules.

## Verification

- All six member names, handles, and assigned branches were checked against Project-Members.txt. Workflow scope was reviewed against PLAN.md, DEV.md, AGENTS.md, and both referenced skills, including local Done versus main integration and read-only versus file-changing handoffs.
- All 418 relative Markdown links/heading anchors across 30 Markdown files resolve and code fences/details are balanced. Private credential values are absent from all 180 shareable files scanned. Source assignment/requirements text is unchanged after Git line-ending normalization; all 31 application task rows and three integration-evidence rows match HEAD.
- `git diff --check` passes. Only the prompt guide, PLAN/README/DEV links, DOC-06 backlog entry, current handoff/index, and this new dated handoff changed.
- No application tests or lint were run for this documentation-only task. Application source, migrations, database contents, dependencies, and skill files were unchanged; no coding-agent execution of a future feature is claimed.

## Next action

Jerome reviews the local guide and separately authorizes publication when ready. Once the guide is available in the team's checkout, each member copies their block into their agent. The agent inspects current prerequisites and implements ready assigned work; missing prerequisites retain the plan's normal gates.
