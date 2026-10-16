# Frontend and standards publication

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Scope: explicitly authorized commit/push of all completed local changes, separated by concern, with `Co-authored-by: Codex <codex@openai.com>` on every commit.
- Branch/integration: `jerome`, publication target `origin/jerome`; **Not integrated into main**. No merge, new PR, or another member's feature work is part of this request.

## Commit groups

| Commit | Concern |
| --- | --- |
| `c670bd9` | Tailwind/Axios build pipeline, shared asset shell, and generated-output exclusions |
| `ab5abb4` | Prettier and djLint dependencies/configuration, preserving Ruff for Python |
| `3806bb9` | Global theme, scrolling, selection, reduced-motion, and scrollbar styles |
| `76f19db` | Supplied logo/favicon assets, corrected manifest paths, and shared metadata |
| `6622e28` | Debug-only index/preview navigation, font-load status, and supplied startup screenshot |
| `6b0fc91` | Tailwind-aware VS Code language mode and extension recommendation |
| This documentation commit | Team standards, complete dependency disclosure, setup/folder/HTTP guidance, and current publication records |

The build and formatter changes were staged separately, including matching manifest/lock versions. Working files retained their verified final contents. Earlier completed handoffs retain their historical uncommitted observations; [HANDOFF.md](../HANDOFF.md) and [tasks.md](../docs/tasks.md) record current member-branch status. The user's supplied logo and favicon images are included unchanged.

## Verification for this publication

- Full npm build, source formatting, all three Django template format checks, workspace JSON checks, and manifest formatting pass. npm audit reports zero vulnerabilities.
- Full Ruff lint/format checks, pip dependency validation, Django database/system checks, migration drift check, and applied-migration check pass. All 23 real PostgreSQL foundation tests pass (1.972 seconds).
- Earlier browser/font/CSRF/static-byte/responsive/navigation/style checks are preserved in their linked work handoffs; browser scenarios were not repeated solely for committing unchanged source.
- Before creating commits, fetched origin/jerome and main; origin/jerome matched the starting local head 8668ff8. Existing main protection and other member branches are unchanged. Private environment files, generated builds, node_modules, and virtual environments remain excluded.
- Final integrity checks pass: 541 relative links/anchors across 40 Markdown files, balanced fences/details, private-value scan across 213 shareable files, preserved course/member source files and all application task rows, exact inventory coverage of 17 Python pins and 140 npm entries, and unchanged runtime Python pins. Staged commit whitespace checks pass. No dependency, schema, or feature changes were introduced during the commit split.

## Next owner/action

Jerome reviews the published member-branch batch and separately decides PR/main integration. T04/Alex remains ready from the previously integrated T02 foundation. T06/Jerome still requires integrated T04. Shared UI/standards work does not close another member's tasks or relax those gates.
