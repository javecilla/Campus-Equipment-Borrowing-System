# Static directory rename

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Task/scope: UI-03; explicitly requested rename of shared source files from `assets/` to Django's conventional `static/` directory.
- Branch/integration: `jerome`, uncommitted over `45dd055`; **Not integrated**. No commit, push, PR, merge, dependency, schema, or application-data changes.

## Current outcome

All 109 tracked source files moved to [static/](../static/) without content changes, including fonts, notices, screenshots, icons, CSS, and JavaScript. Local ignored build output moved with the directory and was rebuilt. There is no remaining source directory at the old location.

[Django settings](../config/settings.py) now discover `BASE_DIR / "static"`. Browser URLs and template static paths retain their existing behavior; `STATIC_ROOT` remains separate at `staticfiles/`. The [npm scripts](../package.json), [license copying](../scripts/copy-licenses.mjs), ignore files, editor language association, and current README/DEV/architecture/standards/folder/license guidance use the new paths. [DEV.md](../DEV.md#everyday-startup) explains stopping/restarting watchers around directory-moving updates.

All 21 existing handoffs remain byte-for-byte unchanged. Eight historical file links refer to the old source paths and were verified against Git revision `45dd055`; [HANDOFF.md](../HANDOFF.md) explains how to inspect those original snapshots. They are historical references, not current file-placement instructions.

## Actual verification

- Both npm build stages and source formatting checks pass. Both development watchers start successfully against the new paths; the verification watcher process was stopped afterward. All three template format checks and workspace JSON checks pass.
- Full Ruff lint/format checks, Django database/system checks, migration drift/applied checks, and all 23 real PostgreSQL foundation tests pass (1.750 seconds).
- SHA-256 comparison confirms all 109 moved source files and all 21 earlier handoffs preserve their bytes.
- All 113 source/generated static files are found by Django, served with exact source bytes, and copied unchanged by `collectstatic` into a checked temporary directory; temporary collection output was removed. The 20 compiled font URLs and both manifest image paths resolve. Axios's generated license notice still matches its installed source.
- Real Chrome navigation verifies index to preview and back. The preview confirms local DM Sans/Poppins loading, computed font families, smooth scrolling, and the unchanged compiled stylesheet URL. Static HTTP checks cover all icon files; native browser tab-strip icon rendering was not separately inspected.
- No extra tests or dependencies added. Other members' feature tasks and normal integration gates remain unchanged.
- Final integrity checks pass: 550 relative links/anchors across 41 Markdown files (including eight historical targets verified at `45dd055`), balanced fences/details, private-value scan across 214 shareable files, preserved source requirements/member files and application task rows, exact locked dependency/license coverage, and Git whitespace checks. Generated output and private environment files remain ignored.

## Next action

Jerome reviews the rename and updated guidance before separately authorizing publication. Teammates stop old watchers before syncing the rename, then rebuild or restart `npm.cmd run dev` using the updated scripts. Alex/T04 remains ready from the integrated foundation; Jerome/T06 still requires integrated T04.
