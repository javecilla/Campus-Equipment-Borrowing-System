# Project folder architecture guide

- Owner: Jerome Avecilla (`@javecilla`), with Codex documentation assistance.
- Date/time: October 16, 2026, 15:59 Asia/Manila (UTC+08:00).
- Task: DOC-05; dedicated Markdown folder architecture guide requested under `docs/`.
- Delivery: `jerome`, local/uncommitted, **Not integrated**. No commit, push, PR, or merge. Earlier uncommitted foundation and assets work is preserved.

## Outcome and relevant files

[docs/project-folder-architecture.md](../docs/project-folder-architecture.md) shows where each app's models, views, forms, URLs, services, queries, migrations, commands, and tests belong. It marks actual versus planned paths, shows shared role layouts and feature template locations, traces a planned page through its files, and provides page-placement examples using existing HTTP contract names. Existing coding and workflow rules are linked rather than copied in full.

[README.md](../README.md#project-folder-structure), [DEV.md](../DEV.md), and [docs/architecture.md](../docs/architecture.md#proposed-modules-and-ownership) link to the dedicated guide. [docs/tasks.md](../docs/tasks.md) records DOC-05; [HANDOFF.md](../HANDOFF.md) links this snapshot. No application files, placeholder views/templates, settings, migrations, dependencies, or feature task statuses were changed in this task.

## Checks and limitations

- Inspected actual app files, root routing/settings, the coding guide, system architecture, and the HTTP contracts.
- Checked all **71** existing/planned annotations in the directory tree against the filesystem; every annotation matches the checkout.
- All 10 example route names match `docs/api_spec.md`. All 379 local links/anchors across 27 Markdown files resolve; code fences and collapsible sections are balanced. Git whitespace checks pass.
- The credential scan found no private environment values across 177 shareable paths.
- Source requirement/member files, private environment, MCP configuration, skills, and prior dated handoffs are preserved.
- No application tests, lint, migration commands, browser session, or server startup were run for this documentation-only task. The earlier foundation/assets handoffs retain their actual application verification results.

## Next action

Jerome reviews the documentation together with the pending local foundation work. Feature owners use the guide when their assigned tasks and integration prerequisites are ready. Planned page/template names are placement examples, not delivered routes or new service/authentication interfaces. The normal T04/T06 and later-task gates remain unchanged; main integration still requires separate authorization.
