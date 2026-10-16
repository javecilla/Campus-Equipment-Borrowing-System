# Shared HTTP, styling, and formatting standards

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Task/scope: DOC-07; consistent endpoint/Axios/Tailwind/naming conventions for team agents, appropriate formatters, and explicit third-party disclosure.
- Branch/integration: `jerome`, uncommitted over `8668ff8`; **Not integrated**. Existing UI-01 frontend work is preserved. No commit/push/PR/merge or other member's feature work performed.

## Current outcome

- [Coding standards](../docs/coding-standards.md) now own the server-rendered command/query HTTP pattern, shared Axios transport and page responsibilities, naming, request encodings, CSRF/response/error behavior, Tailwind utilities/components/accessibility, and formatter responsibilities. The HTTP contract still owns paths/statuses/fields; no REST framework, JSON endpoint, generic status setter, or business workflow was added.
- [AGENTS.md](../AGENTS.md) directs agents to those canonical sections; the existing Django skill and member prompts already require reading that guide. The [HTTP contract](../docs/api_spec.md) links implementation/calling conventions. DEV.md's earlier multipart example was aligned to the existing URL-encoded form contract.
- [Prettier config](../.prettierrc.json), [ignore file](../.prettierignore), and package scripts format/check source JS/MJS/CSS and selected project JSON. Prettier 3.9.10 is a pinned local dev dependency. Python remains with Ruff; generated/vendor/private files and Django HTML are excluded from Prettier.
- djLint 1.46.6 is declared in requirements-dev.in and locked with its support packages. pyproject.toml selects its Django profile, four-space indentation, and 100-column wrapping without embedded CSS/JS formatting. The shared base template was reformatted; its rendered behavior is preserved. This config adds template-format checks, not a separate djLint lint gate or an automatic hook/CI job.
- [README](../README.md#third-party-packages-and-assets) owns direct dependency/font/tool purposes, tradeoffs, scope, and license declarations, including djLint's GPL-3.0-or-later and Psycopg's LGPL metadata. [Inventory](../docs/third-party-dependencies.md) lists every locked Python/npm entry, version, parent, scope, optional flag, and license identifier. Architecture links the disclosure instead of retaining a duplicate justification table. Optional DBHub's separate published dependency declaration is disclosed without inventing an application lock for its execution cache.

## Actual verification

- Prettier write/check passes; source JS/CSS files required no formatting changes. djLint reformatted templates/base.html; a second check reports no further changes.
- A real Django template-engine smoke check compared before/after formatter output for inheritance, named URL reversing, CSRF fields, static URL, if/for behavior, and escaped user content. Both conditional branches preserve rendered semantics; the formatted fixture passes another djLint check. Temporary fixture files were removed.
- npm ci initially identified an incomplete nested optional dependency in the evolving lockfile. The lock was regenerated in a fresh temporary directory from the exact declared manifest, without installed dependency state or forced audit fixes. Final npm ci succeeds, source formatting/build pass, and audit reports zero vulnerabilities. Required/optional dependency references resolve throughout the final application lock.
- All 23 real PostgreSQL foundation tests pass (1.784 seconds). Django database/migration drift/applied-migration checks, Ruff lint/format, and pip check pass after the Python dev dependency install. No runtime Python pins changed.
- Complete inventory coverage: 17 pinned Python distributions and 140 npm entries; actual license files were checked where Python metadata lacked an SPDX expression. Existing font notices and generated Axios license handling are preserved. Inventory metadata does not replace the actual third-party notices.
- Final verification passes: relative links/heading anchors and balanced fences/details across 33 Markdown files; private-value scan across 191 shareable files; source TXT, runtime Python pins/source, all 31 application task rows, and their three integration-evidence rows preserved. Exact inventory/version/license coverage matches both locks; Prettier's real file-info API excludes Django HTML/generated assets and accepts source JavaScript; git diff --check passes.
- No new browser UI/workflow or API endpoint was implemented; the earlier UI-01 browser smoke remains in its own historical handoff. No clean-machine/other-OS/CI execution, auto Tailwind class sorting, or automatic architectural enforcement is claimed.

## Next action

Jerome reviews the combined local frontend/standards changes and separately authorizes publication when ready. After integration, teammates install both locked dependency sets, follow DEV.md's formatter/check commands, and have their agents read the expanded coding standards before implementing assigned ready tasks. Dependency changes must refresh README rationale, full inventory, locks, and required redistributed notices together. Existing application task readiness/ownership remains unchanged.
