# Current Project Handoff

## Current state

- Last updated: October 16, 2026, Asia/Manila.
- Phase: documentation and requirements preparation, with separately authorized shared read-only MCP tooling, developer setup documentation, and private local configuration. Application implementation and schema/data changes require an explicit user request.
- Product: Campus Equipment Borrowing System; see [README.md](README.md).
- The folder contains source requirements/member files and planning documentation. No Django application, migrations, dependency manifest, or configured test/lint commands is present. The user's local PostgreSQL 17.5 database `campus_equipment` is running and was verified through a read-only MCP query; its public schema currently has 0 tables.
- Git origin is connected to the private [team repository](https://github.com/javecilla/Campus-Equipment-Borrowing-System), and the initial publication is being prepared on `jerome`. The active main-owner-only GitHub ruleset allows only `javecilla` to bypass its main update restrictions. Commit/push verification remains pending for GIT-01.
- The team target is October 24, 2026; the official deadline remains instructor-controlled.

## Dated handoff files

Developers and AI agents write work snapshots in the project-root `handoffs/` folder as `{title-of-work}-{MM-DD-YYYY}.md`. Use a lowercase hyphenated title and the current date in Asia/Manila. Example: `initial-project-setup-documentation-10-16-2026.md`. Preserve completed handoffs; if a title/date is taken, choose a distinct work title before the date. Follow the [project-handoff skill](.agents/skills/project-handoff/SKILL.md) for required content and update this index after creating a snapshot.

| Date | Work | Author | Handoff |
| --- | --- | --- | --- |
| October 16, 2026 | Initial setup, documentation, local MCP, standards, and team files | AI agent; member not specified | [Initial project setup documentation](handoffs/initial-project-setup-documentation-10-16-2026.md) |
| October 16, 2026 | GitHub publication, member branches, main protection, and shared review assignments | Jerome with Codex assistance | [GitHub repository and member branch workflow](handoffs/github-repository-and-member-branch-workflow-10-16-2026.md) |

This root file summarizes current state. Dated files retain the state and checks at handover; canonical technical rules remain in their own documents.

## Work at handover

Task statuses are canonical in [docs/tasks.md](docs/tasks.md). Keep the table below focused on current work/next-owner context rather than copying the entire backlog.

| Task / owner | Current outcome | Relevant files | Next action |
| --- | --- | --- | --- |
| DOC-01 / AI agent; member not specified; review by the team | Documentation baseline complete and checked; application work remains unimplemented | [README](README.md), [PRD](docs/PRD.md), [SRS](docs/SRS.md), [architecture](docs/architecture.md), [database](docs/db_design.md), [HTTP contracts](docs/api_spec.md), [AGENTS](AGENTS.md), [environment template](.env.example), [backlog](docs/tasks.md), [handoff skill](.agents/skills/project-handoff/SKILL.md) | Team review of proposed design choices; implementation requires a separate explicit request |
| DOC-02 / AI agent; member not specified | Canonical MTV coding guide, Django skill, team contribution/conduct rules, and selected MIT license complete and checked | [Coding standards](docs/coding-standards.md), [Django skill](.agents/skills/django-mtv/SKILL.md), [Contributing](CONTRIBUTING.md), [Code of Conduct](CODE_OF_CONDUCT.md), [MIT license](LICENSE) | Developers/agents follow the guide and skill for authorized Django work; preserve accurate team attribution |
| DOC-03 / AI agent; member not specified | Initial dated handoff and matching archive-folder/filename instructions complete; skill/link/Git-exclusion checks passed | [Dated handoff](handoffs/initial-project-setup-documentation-10-16-2026.md), [handoff skill](.agents/skills/project-handoff/SKILL.md), [AGENTS](AGENTS.md) | Future work writes a distinct dated snapshot and updates this current state/index and the affected task |
| GIT-01 / Jerome with Codex assistance | Origin connected, initial branch jerome selected, owner-only main ruleset active; DEV workflow and CODEOWNERS prepared | [Developer Git workflow](DEV.md#assigned-branches-and-main-integration), [Contributing](CONTRIBUTING.md), [CODEOWNERS](CODEOWNERS), [GitHub handoff](handoffs/github-repository-and-member-branch-workflow-10-16-2026.md) | Complete secret/link checks, publish commits with Codex credit, and verify main/member remote branches |
| MCP-01 and MCP-02 / AI agent; member not specified | Shareable JSON/policy and DEV.md complete; ignored .env.local populated; personal Codex registration uses them; MCP checks passed without schema/data changes | [Developer guide](DEV.md), [MCP JSON](.agents/mcp.json), [DBHub policy](.agents/dbhub.toml), [environment template](.env.example); personal `~/.codex/config.toml` | Teammates follow DEV.md using their own project paths and credentials; restart/reload the MCP client after registration changes |
| T01–T31 / assigned members in backlog | Application, operational validation, and course evidence work remain Not started | [Backlog](docs/tasks.md) | Wait for explicit implementation authorization; then start with T01 and its prerequisites |

## Decisions and assumptions to preserve

- README covers purpose, proposed technology, team, and documentation links. [DEV.md](DEV.md) owns developer setup; application installation/start commands remain deferred until implementation.
- Proposed implementation: server-rendered Django monolith, Python 3.13, Django 5.2 LTS, PostgreSQL 17, and Psycopg 3. Exact tested patch versions are not selected or installed.
- PostgreSQL is proposed for the row-lock/constraint strategy. SQLite is permitted by the brief but cannot validate this design's row-lock behavior.
- No separate REST API is planned. [api_spec.md](docs/api_spec.md) defines HTML routes/forms and CSV/print interfaces; no OpenAPI or JSON backend has been implemented.
- Snapshotting limits, normalization through LoanUnit, serviceable-count definition, and pre-issue due-date revision limits are proposed design decisions. Review them against the SRS before implementation.
- Source requirement/member files remain authoritative and have not been rewritten. No user research, performance measurement, legal review, or completed feature is claimed.
- Current state/index belongs in HANDOFF.md, dated developer/AI snapshots in `handoffs/{title-of-work}-{MM-DD-YYYY}.md`, and task status in the backlog. [AGENTS.md](AGENTS.md) requires completion updates and links the handoff skill. This is an instruction-based workflow, with no executable hook or background automation.
- Coding standards are canonical in docs/coding-standards.md. AGENTS.md directs Django design/implementation/review through the django-mtv skill, while architecture/SRS/schema/HTTP documents retain their own contracts. The skill provides instructions and review criteria, not automatic code enforcement or permission to implement.
- The user selected MIT licensing, including commercial reuse with the license notice retained. LICENSE uses `Copyright (c) 2026 Campus Equipment Borrowing System project contributors`; no individual repository account holder is named as sole owner. Contribution/conduct rules describe team participation, and instructor/third-party material retains its own terms.

## Local PostgreSQL MCP connection

- Codex server name: `campus_equipment`; target: `127.0.0.1:5432/campus_equipment`, using the user-supplied `postgres` account. No additional database roles were created.
- Runtime: pinned `@bytebase/dbhub@1.5.0`, obtained through npm's per-user execution cache. Native Node loads `.env.local` explicitly and invokes npm's `npx-cli.js` entry point to avoid Windows batch-shell quoting issues. No custom MCP server or application code was written.
- Shared files are `.agents/mcp.json` and `.agents/dbhub.toml`; teammate installation, client-specific import, path changes, and credential instructions belong in DEV.md. The JSON's working-directory placeholder must be replaced in each member's local client copy. JSON files are not automatically discovered by Codex.
- Personal Codex registration remains in `~/.codex/config.toml` and now points to this project's working directory and shared launch arguments. Its live connection is loaded from the ignored `.env.local`, with a generated local Django secret and DB_* values prepared for future application settings. Existing unrelated Codex settings were preserved. The older private `~/.codex/dbhub-campus-equipment.toml` file remains on this machine but is not used by the active registration.
- Only `.env.example` is shared; `.env.local` is explicitly excluded by .gitignore. Do not copy private environment/source files into the submission ZIP, because ZIP tools do not apply .gitignore. Each member supplies their own local database and credentials.
- DBHub exposes `execute_sql` and `search_objects`. Its SQL tool is configured with `readonly = true`; the verified query reported PostgreSQL transaction_read_only = on. This tool setting does not change the underlying postgres account's privileges.
- This is optional AI development tooling, separate from the application's future Django database configuration. The JSON `mcpServers` format supplied by the user is not Codex's TOML format. Connection URLs must include `/campus_equipment`.
- The original `@modelcontextprotocol/server-postgres` example is archived; use the configured DBHub connection. References: [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp#connect-codex-to-an-mcp-server), [DBHub configuration](https://dbhub.ai/config/toml), and [archived PostgreSQL reference server](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/postgres).
- The external test client verified the shared JSON command with its working-directory placeholder resolved to this project and confirmed that personal Codex arguments match. Tools are not claimed to be loaded into the current conversation; restart/reload the client's MCP connection first. Update .env.local when connection details change; no shared files should contain real credentials.

## Verification

| Check | Actual result |
| --- | --- |
| Source and workspace inspection | Read both source TXT files and the original empty README; no application files found |
| Existing Git checkout | `git status --short` now succeeds and shows shared files as untracked; no agent commit/push/merge |
| Framework/discovery references | Checked official Django version/database/locking documentation and official OpenAI AGENTS/skill documentation |
| Local document links and configuration integrity | Relative targets and code fences checked; shared MCP JSON and DBHub TOML parsed; environment template/private file have 10 matching unique keys; private connection values validated through Node's env-file loading |
| Handoff skill frontmatter | Passed bundled `quick_validate.py` using an existing cached PyYAML package; no dependencies installed and no validator code changed |
| Dated handoff archive | Initial filename/date checked; both updated skills passed the bundled validator; 159 relative links across 16 Markdown files resolved; Git excludes .env.local while shared MCP/environment/handoff files remain trackable |
| Django MTV skill and team documents | Bundled skill validator passed; guide/skill/entry-point links and document consistency checked; MIT terms use project-contributor attribution; no application code added |
| Private MCP configuration | TOML parsed; existing Codex configuration preserved; `codex mcp get campus_equipment` recognized the enabled stdio registration |
| Direct PostgreSQL query | Passed against PostgreSQL 17.5, database campus_equipment, read-only transaction; public schema has 0 tables |
| MCP protocol and query | Shared JSON launch passed initialize, tools/list, and execute_sql; DBHub 1.5.0 returned database campus_equipment and read_only on; public table count remains 0; no database writes performed |
| Project credential scan and scope | No supplied password or encoded password found in shareable text/configuration files; credentials are intentionally stored in ignored .env.local; all 31 application tasks remain Not started |
| Platform coverage | Shared launch verified on this Windows workstation; clean-machine installations, other clients, and macOS/Linux have not been executed |
| Application tests, migrations, lint, benchmarks | Not run; no application or configured project commands exist |

## Open review items and next actions

1. Review the completed documentation, coding standards, and team collaboration files. DOC-01/DOC-02 completion means files exist and were checked, not that the proposed architecture has been implemented. The MIT choice was explicitly supplied by the user.
2. Team review: confirm proposed stack, serviceable-count definition, immutable identity rules, and limit/date conventions. Do not change instructor requirements without identifying a conflict.
3. Confirm the official submission date and campus policies when supplied. Course evidence tasks cover privacy/retention, licenses, AI disclosure, feedback, leadership, and presentation records; none is fabricated here.
4. Teammates follow DEV.md, copy the shared MCP entry into their supported client configuration, replace machine-specific paths, and supply their own .env.local. Restart/reload the client to load campus_equipment tools.
5. Future developers/agents create a dated handoff in handoffs/ after file-changing work or transfer, then link it in this file's dated index and update affected tasks. Follow the skill for the exact naming/content rules.
6. When explicitly asked to implement, start T01, then the shared schema and authentication dependencies. Preserve all source documents and keep changes uncommitted unless a commit is requested.

## Maintaining this handoff

Follow [.agents/skills/project-handoff/SKILL.md](.agents/skills/project-handoff/SKILL.md). Save work snapshots to `handoffs/{title-of-work}-{MM-DD-YYYY}.md`, then update this current-state summary and dated index. Read the latest shared files before writing and preserve other owners' work and completed handoffs. Link durable decisions to their canonical documents and record actual checks/blockers. Do not include transcripts or credentials or duplicate the backlog.
