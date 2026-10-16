# Static directory publication

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Scope: user-authorized commit and push of all UI-03 source-directory rename changes on `jerome`, with Codex co-author credit preserved.
- Branch/integration: `jerome`, based on `45dd055`; publication target `origin/jerome`. **Not integrated into main**. No PR creation, merge, dependency, schema, or new feature work is part of this request.

## Outcome and verification

The rename, active configuration/documentation updates, and this publication record form one commit: `refactor: rename shared assets directory to static`. All 109 source files preserve their bytes. Existing dated handoffs are retained; current status is recorded in [HANDOFF.md](../HANDOFF.md) and [the backlog](../docs/tasks.md).

- Fetched origin/jerome before committing; it matches local starting head `45dd055`, with zero commits ahead/behind.
- Rechecked source-file hashes and original handoff preservation, current document links (including historical paths against `45dd055`), credential exclusion, source/task preservation, and dependency inventory/lock consistency.
- The [rename handoff](static-directory-rename-10-16-2026.md) records the completed build/watch, formatting, Django/migration checks, 23 real PostgreSQL tests, 113-file static discovery/serving/collection, and browser font/navigation verification. Application code/content did not change during publication; those runtime checks were not repeated solely to commit it.
- Private environment files and generated output remain excluded. The commit uses `Co-authored-by: Codex <codex@openai.com>`.
- Final documentation checks pass: 556 relative links/anchors across 42 Markdown files, eight archived paths verified in `45dd055`, private-value scan across 215 shareable files, matching locked dependency/license inventory, and Git whitespace checks. Git identifies all 109 moved files as exact renames.

## Next action

Jerome reviews the member-branch rename before separately deciding main integration. Teammates stop old asset watchers before syncing the rename, then rebuild or restart the updated npm scripts. Alex/T04 and Jerome/T06 readiness is unchanged.
