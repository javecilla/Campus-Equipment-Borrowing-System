# Project Instructions for Contributors and AI Agents

## Current authorization and context

The user authorized Jerome's T07 continuation, including optional equipment photos, responsive layouts and audited restoration, then its commit/push with Kenneth and Codex credit. That delivery is integrated through PR #20; Ellyssa's T09 implementation is integrated through PR #21. The user now authorizes staging all current changes with `git add .`, committing and pushing `jerome` with Ellyssa and Codex co-author credit, including the user's minor audit-template changes and documentation review. This does not authorize a PR, main merge, T08 implementation or T09 code correction. See the backlog and current handoff for acceptance findings and integration evidence.

The user authorized implementation of Jerome Avecilla's assigned work on `jerome`, and explicitly allowed T01–T03 as one local, uncommitted batch before main integration. This exception does not unlock tasks requiring other members' features or authorize commits, pushes, PRs, or merges. The user also requested runnable setup steps in README.md and detailed migrations/team guidance in DEV.md. Follow the backlog and current handoff for verified scope; remaining feature designs are contracts, not delivered software.

The user subsequently authorized committing all completed foundation/documentation/assets changes with `Co-authored-by: Codex <codex@openai.com>`, pushing `jerome`, and opening a PR into `main`. This publication request does not authorize merging that PR or starting another member's features.

The user selected Tailwind CSS for styling and authorized the shared frontend setup on `jerome`, then explicitly requested removal of the unused Axios dependency/client. Use ordinary Django forms and links for the current server-rendered interface; do not reintroduce Axios. UI-01 covers the npm build, shared HTML shell, and team guidance; it does not implement authentication, role layouts, product pages, or a separate API. See DEV.md for asset commands and docs/architecture.md for the dependency rationale and required patterns. Later changes stay uncommitted unless separately requested.

The user separately authorized local PostgreSQL MCP tooling, shareable MCP configuration, DEV.md setup guidance, and a private `.env.local` for `campus_equipment`. The connection is read-only; this does not authorize schema changes, seed data, or application implementation. Credentials belong only in ignored private files. Shared configuration and setup instructions are defined in [DEV.md](DEV.md); see [HANDOFF.md](HANDOFF.md) for verified connection state.

Read [PLAN.md](PLAN.md), [HANDOFF.md](HANDOFF.md), the relevant tasks in [docs/tasks.md](docs/tasks.md), and existing files before editing. PLAN.md is the execution map; task status and integration evidence remain canonical in the backlog, while current readiness belongs in HANDOFF.md. Verify prerequisites are accepted and integrated into main before starting dependent work; use the plan's task-selection and handoff gates. The original course brief is [docs/Project-Requirements.txt](docs/Project-Requirements.txt); people/assignments come from [docs/Project-Members.txt](docs/Project-Members.txt). Read the relevant PRD, SRS, architecture, database, and HTTP contract rather than inventing behavior or models. Preserve source requirement/member files.

If a requested change would contradict the course brief, call out the exact conflict before treating it as compliant. Keep implementation choices labeled as proposals until supported by code and checks. Do not claim setup, tests, benchmarks, migrations, Git history, or features exist without inspecting them.

## Product boundaries

- Exactly two roles, `BASIC_USER` and `ADMIN`, through one Django authentication system.
- Custom `/manage/` and `/portal/` views/forms/templates. No Django admin pages, `admin.site.urls`, or packages that generate the admin interface.
- State transitions go through the services and constraints in the design. Never implement generic status updates that bypass reservation, issue, return, maintenance, or audit rules.
- Enforce active-account checks and role/ownership server-side on all protected pages/actions, downloads, and any future AJAX endpoints.
- Keep the approximately 75% custom-admin / 25% basic-user emphasis. Do not add roles, payments, integrations, or hosting as implicit scope.

## Coding standards and Django MTV

Before designing, writing, reviewing, or refactoring a Django feature, read [docs/coding-standards.md](docs/coding-standards.md) and use [.agents/skills/django-mtv/SKILL.md](.agents/skills/django-mtv/SKILL.md). The guide is the canonical source for MTV responsibility placement, HTTP endpoint/browser interaction patterns, Tailwind styling, naming/types, functional style, explicit parameters, errors, authorization, dependency disclosure, formatting ownership, and feature verification. Do not duplicate it into another AI/style file.

Follow the existing architecture, SRS, database, and HTTP contracts for the affected feature. Use the guide's Model–Template–View split with forms, distinct workflow service functions, and read-only query helpers. Read actual code before changing it; the skill does not authorize implementation or install an automatic enforcement hook.

## Verification and documentation

Follow the coding guide's verification table and actual commands recorded in DEV.md/project configuration. Run applicable required checks after code changes and report unrun checks honestly. Django integration tests and Ruff checks are configured for the foundation.

For documentation-only work, check links, internal consistency, source coverage, and skill metadata where relevant. Do not install a test suite or add code just to validate prose. Report exactly what was checked and what was not run.

Keep function-level explanations in code/docstrings once implementation exists. Separate documents cover concepts such as requirements, architecture, and workflow, with one canonical file per topic. Link instead of duplicating full rules. Maintain current-state documentation; dated work handoffs under `handoffs/` are the explicitly requested historical snapshots. Do not add a duplicate changelog of routine edits. No `AI.md` or `.cursorrules` duplicates are required.

## Team participation and licensing

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). This is a team school project; do not identify the repository account holder or any one member as the sole author/owner. Preserve accurate contributor credit. [LICENSE](LICENSE) contains the team's selected MIT terms for original contributions, with a project-contributors notice; preserve third-party/instructor material's separate rights and notices.

## Team coordination and required handoff

At the end of every task that changes project files, or before transferring unfinished work, follow [.agents/skills/project-handoff/SKILL.md](.agents/skills/project-handoff/SKILL.md). Developers and agents write the work handoff in the project-root `handoffs/` folder as `{title-of-work}-{MM-DD-YYYY}.md`, with a lowercase hyphenated title and the current Asia/Manila date; for example, `initial-project-setup-documentation-10-16-2026.md`. Preserve completed handoffs; if a filename is taken, use a distinct work title before the date. Update only the affected task status/evidence in [docs/tasks.md](docs/tasks.md), the relevant current-state section in [HANDOFF.md](HANDOFF.md), and its dated handoff index. Read their latest contents before writing so other members' work is preserved. Read-only questions do not need artificial handoff files.

The dated handoff must identify work/owner, date/time zone, current outcome, relevant files, checks with actual results, unresolved issues/decisions, and the next action. No transcripts, secrets, or invented results. Keep historical snapshots in `handoffs/`, current state/index in HANDOFF.md, and canonical rules in their own documents. Do not overwrite unrelated task entries or close another owner's work without evidence. If concurrent edits conflict, reconcile the latest file before accepting the update. Finalize the handoff after the task's actual verification, before the final response.

This is an instruction-based completion convention, not an installed background hook or enforcement service. Codex supports repository AGENTS guidance and local skills; other tools may require explicit loading. Ask those agents to read this file and the handoff skill when they do not discover them themselves. See [official AGENTS guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md) and [official skill discovery](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

## Git and review

Never create a commit unless the user explicitly asks. Keep changes uncommitted for review; do not push, open a PR, initialize Git, or merge simply because a task is done. Prefer merge over squash when a merge is actually authorized. Use non-interactive commands and `git --no-pager diff`; preserve unrelated edits. If the folder has no Git metadata, report that fact instead of claiming a clean working tree.

Use the member branch assigned in docs/Project-Members.txt and follow [DEV.md's Git workflow](DEV.md#assigned-branches-and-main-integration). Ordinary member work is committed/pushed on that branch and proposed to main through a PR. Only `javecilla` handles main integration; do not push main or another member's branch without an explicit repository-owner instruction for that operation. GitHub's owner-only main ruleset is separate from team authorship. The current user explicitly authorized initial publication from `jerome`, main bootstrap/integration, and a Codex co-author trailer; that does not authorize application implementation or future automatic commits.
