# Initial Project Setup and Documentation Handoff

## Metadata and scope

- Date: October 16, 2026, Asia/Manila.
- Prepared by: AI agent; member not specified.
- Work: requirements documentation, developer preparation, local read-only database tooling, coding/team standards, and the dated handoff workflow.
- Related tasks: DOC-01, DOC-02, DOC-03, MCP-01, and MCP-02 in [the backlog](../docs/tasks.md).
- Snapshot scope: the initial setup work completed in this conversation. This file records the handover state; read [HANDOFF.md](../HANDOFF.md) for subsequent current state and its dated handoff index.

## Outcome

The project has a documented foundation and verified local AI database inspection, ready for team review and an explicit request to begin implementation. No Django application, migrations, application dependency manifest, configured test/lint suite, or application tables have been implemented by this work.

This is a six-member school project. Feature coordination and repository administration do not make any one member the sole owner of the team's work. Preserve contributor credit and the original course requirements/member assignments.

## Completed deliverables

| Area | Files / result |
| --- | --- |
| Requirements and overview | [README](../README.md), [PRD](../docs/PRD.md), and [SRS](../docs/SRS.md), based on the original [requirements](../docs/Project-Requirements.txt) and [member assignments](../docs/Project-Members.txt) |
| Technical contracts | [Architecture](../docs/architecture.md), [database design](../docs/db_design.md), and [HTTP routes/form contracts](../docs/api_spec.md); these are plans, not implemented modules |
| Work planning | [Prioritized backlog](../docs/tasks.md) with task IDs, owners, dependencies, acceptance criteria, course evidence, and demonstration data requirements |
| Developer preparation | [DEV.md](../DEV.md), [environment template](../.env.example), and [.gitignore](../.gitignore); local private environment populated on this workstation |
| Database MCP | [Shared JSON template](../.agents/mcp.json) and [DBHub policy](../.agents/dbhub.toml), with a matching personal Codex registration and a verified read-only connection |
| Django standards | [Canonical coding/MTV guide](../docs/coding-standards.md), [django-mtv skill](../.agents/skills/django-mtv/SKILL.md), and updated [AGENTS.md](../AGENTS.md) entry-point rules |
| Team participation | [Contributing](../CONTRIBUTING.md), [Code of Conduct](../CODE_OF_CONDUCT.md), and [MIT license](../LICENSE) selected by the user with project-contributors attribution |
| Handoffs | This initial dated snapshot, [current state/index](../HANDOFF.md), and [updated project-handoff skill](../.agents/skills/project-handoff/SKILL.md) defining where future developers/agents write handoffs |

## Decisions to preserve

- Exactly two application roles and a custom admin interface remain required. The proposed architecture is a server-rendered Django MTV monolith; forms, workflow service functions, and query helpers support that structure.
- Proposed application stack: Python 3.13, Django 5.2 LTS, PostgreSQL 17, and Psycopg 3. Application package versions are not yet pinned/tested. Database/workflow conventions identified as proposals still need team review.
- MTV and coding rules are canonical in the coding guide; architecture, schema, SRS, and HTTP contracts keep their separate responsibilities. The Django skill guides design/implementation/review and does not automatically enforce code or authorize implementation.
- MIT applies to original team contributions, with `Campus Equipment Borrowing System project contributors` in its notice. Instructor-supplied/third-party materials retain their own terms. No individual's name is used as sole repository owner.
- Developer setup is documented in DEV.md. The README remains an overview and documentation entry point.
- Future handoffs go in project-root `handoffs/` as `{title-of-work}-{MM-DD-YYYY}.md`, using a lowercase hyphenated title and the current Asia/Manila date. Preserve completed snapshots; choose a distinct work title before the date if a name is taken. HANDOFF.md holds current state and the dated index.

## Local environment and MCP state

On this workstation, the user-created database is `127.0.0.1:5432/campus_equipment`, PostgreSQL 17.5. Earlier setup checks in this conversation confirmed 0 public-schema tables and `transaction_read_only = on` through DBHub 1.5.0's `execute_sql` tool. `search_objects` was also exposed. The wrap-up task does not rerun or modify the database.

Shared MCP files contain no credentials. The private `.env.local` holds this workstation's connection values and generated local Django secret and is excluded by .gitignore. Personal Codex registration is outside the repository and launches Node with the env file, pinned npm package, project working directory, and shared DBHub policy. Each teammate must follow DEV.md, replace machine-specific paths, and provide their own database credentials. Restart/reload the MCP client after registration changes.

The MCP is read-only AI tooling, separate from future Django settings. It does not make Django implemented or configure a teammate's machine automatically. Do not include `.env.local` or private user configuration in a submission ZIP; ZIP tools do not apply .gitignore.

## Verification and limitations

### Checks completed earlier in the setup session

- Both skills passed the bundled `quick_validate.py` during their creation; no validation dependencies were installed.
- JSON/TOML configuration parsed, Node loaded the private environment, and raw DB fields matched the MCP URL without printing credentials.
- The shared MCP launch passed initialize, tools/list, and a read-only SQL query; personal Codex arguments matched the shared template. PostgreSQL returned database campus_equipment, version 17.5, read_only on, and 0 public tables.
- Document links, code fences, and shareable-file credential scans passed. Before this archive change, 128 relative links were checked.

### Checks for this handoff change

- Git is now available: `git status --short` lists shared project files as untracked. No commit, push, or merge was performed by the agent.
- Both updated skills passed the bundled `quick_validate.py`. No validation dependencies or application code were added.
- All 159 relative links across 16 Markdown files resolved; code fences and the archive's `{title-of-work}-{MM-DD-YYYY}.md` filename/date were checked.
- Git check-ignore confirmed .env.local is excluded and the shared environment template, MCP JSON/policy, and dated handoff are not ignored. A shareable-file scan found no local password, encoded password, MCP URL, or Django secret.
- All 31 application tasks remain Not started. DOC-01, DOC-02, DOC-03, MCP-01, and MCP-02 are complete for this setup scope.
- Application tests, migrations, lint, benchmarks, and clean-machine installations were not run. There is no application test configuration yet. Earlier MCP testing covered this Windows workstation, not other clients or operating systems.

## Open work and next steps

1. Team members review the requirements/design and follow DEV.md to prepare their own workstation. Confirm the official instructor deadline and campus policy details; the recorded team target is October 24, 2026.
2. When explicitly asked to implement, begin T01, then the shared schema/authentication dependencies in the backlog. All 31 application tasks currently remain Not started; documentation and MCP readiness do not complete them.
3. Do not use the read-only MCP to create competing application tables. Future Django migrations will own the executable schema.
4. For the next completed task or transfer, use the project-handoff skill to create a distinct dated file under handoffs/, then update the root current state/index and affected task entries. Preserve other members' handoffs and unfinished work.

No technical blocker prevents reviewing this foundation. Remaining application work awaits the user's explicit implementation request, not additional setup approval.
