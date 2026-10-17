# Remove unused Axios

- Owner: Jerome Avecilla, with Codex assistance; explicit user request to retire the unused browser HTTP dependency.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00).
- Task: UI-06; updates the UI-01/DOC-07 tooling and guidance without starting another member's feature.
- Delivery: local, uncommitted on `jerome`, based on `024cf34`; **Not integrated**. No commit, push, PR, or main merge requested or performed for this change.

## Current outcome

Removed Axios from [package.json](../package.json) and [package-lock.json](../package-lock.json), along with the unused `static/js/http.js` and `scripts/copy-licenses.mjs`. The JavaScript build no longer runs the removed notice-copy script. Formatter commands no longer include the now-empty scripts glob. Existing Tailwind/page-script build and watchers remain configured; no new HTTP wrapper or dependency was added.

The lockfile now contains 113 build/development entries instead of 140. Exactly 27 unused production dependency entries were removed; retained versions are unchanged. npm uninstall also pruned two unrelated optional bundled Tailwind WASM metadata entries; their exact original lock metadata was preserved to keep the optional graph complete. A fresh npm ci succeeds against that lock. [The inventory](../docs/third-party-dependencies.md) was refreshed from the actual dependency paths, parents, versions, roles, and licenses; Python pins and supplied font notices are unchanged.

Obsolete generated `static/build/http.js` and `static/build/axios-LICENSE.txt` were removed locally; a rebuilt output contains only `app.css` and `frontend-test.js`. Build metadata confirms that the page bundle includes only the project font-preview source. No third-party JavaScript runtime package is bundled. Tailwind remains the styling tool; Django, local fonts, Python dependencies, and npm build/development tools still require their own disclosures.

[DEV.md](../DEV.md#frontend-assets-tailwind-and-page-scripts), [README](../README.md#third-party-packages-and-assets), [architecture](../docs/architecture.md), [HTTP contract](../docs/api_spec.md), [coding guide](../docs/coding-standards.md#browser-interactions), [folder guide](../docs/project-folder-architecture.md), and [AGENTS](../AGENTS.md) now direct developers to native Django forms/links. Native browser APIs may support a future explicitly authorized enhancement under its documented contract; no such request feature was implemented. Legacy document anchors preserve archived handoff links, while historical snapshots remain unchanged. DEV also tells upgrading teammates to remove the two stale generated files before static collection.

## Verification performed

| Check | Actual result |
| --- | --- |
| Clean dependency install | npm ci completed, installing 50 packages; manifest/lock no longer declares Axios |
| Build/source format | Full npm build passed; font-preview output 639 bytes; Prettier source checks passed |
| Runtime bundle | esbuild metadata contains only `static/js/frontend-test.js`; removed Axios bundle/notice are absent |
| Dependency audit | Zero npm vulnerabilities; pip check found no broken requirements |
| PostgreSQL suite | 44 tests passed in 17.558 seconds; separate test database created and destroyed |
| Django/schema | Database system check passed; no migration drift; applied-migration check passed |
| Python/templates | Ruff lint passed; 113 Python files already formatted; djLint checked 11 templates with zero updates |
| Documentation/preservation | 445 relative links/anchors across 11 documents passed, including legacy anchors; all 113 npm inventory rows match metadata; exactly the 27 unused production entries removed; retained lock metadata/versions, 18 feature task rows, historical snapshots, private configuration, existing app/templates/page script, and empty index preserved; diff whitespace passed |

No browser rerun was needed: no view, form, URL, template, font, styling source, or existing page-script implementation changed, the removed module had no page consumers, the bundle input was verified, and the full authentication/role/CSRF suite passed. This does not claim a new acceptance run for pending workflows or other platform binaries.

## Next action

Jerome reviews this uncommitted cleanup before separately authorizing publication. Teammates receiving it run npm ci and rebuild using [DEV.md](../DEV.md); remove obsolete generated files from older workstations before collecting static assets. Preserve native Django CSRF-protected POST actions and the existing feature owners/dependencies. Do not reintroduce the removed library. Full T20 layouts, workflow features, and T21 demonstration data retain their current status.
