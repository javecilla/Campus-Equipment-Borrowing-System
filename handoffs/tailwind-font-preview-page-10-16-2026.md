# Tailwind and font preview page

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Task/scope: UI-02; explicitly requested local `/test` page to inspect Tailwind styling and font loading.
- Branch/integration: `jerome`, uncommitted over `8668ff8`; **Not integrated**. Existing local frontend/standards/editor work preserved. No commit, push, PR, merge, dependency, schema, or application-data changes.

## Delivered interfaces

- [config/urls.py](../config/urls.py) maps exact `/test` (no trailing slash), named `frontend-test`, to the typed [view](../config/views.py). It permits GET/HEAD and returns 404 with `DEBUG=False`. It reads no application data and requires no account.
- [Template](../templates/dev/frontend-test.html) extends the shared shell with DM Sans/Poppins specimens, utility color swatches, rounded cards, and responsive grids. [Browser module](../assets/js/frontend-test.js) uses the native Font Loading API to require real matching font faces and display explicit success/failure status; unexpected failures remain visible in the browser console.
- [DEV.md](../DEV.md#frontend-preview) owns preview instructions; README startup now points there. The original startup screenshot remains as the pre-route reference. Adding a route ends Django's automatic welcome screen; `/` remains 404 until the account home route exists. The [HTTP contract](../docs/api_spec.md#development-preview) and [folder guide](../docs/project-folder-architecture.md) describe the utility's placement and access.

## Actual verification

- npm build and source formatting checks pass; both template files pass djLint; full Ruff lint/format checks pass; Django system check reports no issues.
- All 23 existing real PostgreSQL foundation tests pass (1.919 seconds); the seven configuration tests also pass independently. No test framework/dependencies added.
- Real Django client smoke: GET and HEAD return 200 with debug enabled, POST returns 405, GET returns 404 with debug disabled, and rendering performs zero database queries.
- Real Chrome smoke at the existing local server: page shows successful local DM Sans/Poppins loading; computed font families match both theme choices; swatch has the emerald color and 24px padding. At desktop width 1704px the color grid has three columns; at mobile width 390px both grids have one column and no horizontal overflow. Screenshots inspected at both sizes. Temporary viewport override reset; preview tab retained as a deliverable.
- Final documentation/integrity checks pass: 514 relative links/anchors across 35 Markdown files, balanced fences/details, private-value scan across 198 shareable files, unchanged source requirements/member files and application task rows, and complete dependency inventory matching the existing locks. Git whitespace check passes.
- No failure was simulated by removing font files. Failure feedback exists but was not end-to-end exercised. No other member's feature implementation or main integration is claimed.

## Next action

Jerome can open [the local preview](http://127.0.0.1:8000/test) while Django runs and `DJANGO_DEBUG=True`; rebuild assets or keep watchers running after source changes. Review combined local changes before separately authorizing publication. Alex/T04 remains ready from the integrated foundation; Jerome/T06 still awaits integrated T04. The preview does not relax those gates.
