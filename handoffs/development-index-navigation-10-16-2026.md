# Development index navigation

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Scope: UI-02 follow-up; root development index to make the existing frontend preview discoverable.
- Branch/integration: `jerome`, uncommitted over `8668ff8`; **Not integrated**. Earlier local frontend/standards/editor work preserved. No commit, push, dependency, schema, or application-data changes.

## Outcome

[config/urls.py](../config/urls.py) maps `/` to `development-index`; the typed handler in [config/views.py](../config/views.py) returns the [index template](../templates/dev/index.html) only with debug enabled. Its navigation card uses the named `/test` URL. The [preview](../templates/dev/frontend-test.html) links back using the named index URL. Both pages use the shared shell and compiled Tailwind styles, and require no account or application data.

[DEV.md](../DEV.md#frontend-preview) owns startup/preview instructions. README, the folder guide, and the HTTP contract reflect the development index. This is a temporary development route: Alex's T04 must replace it with the contracted `accounts:home` behavior rather than adding a competing empty-path route. No authentication or role feature is delivered here.

## Actual verification

- Tailwind CSS build, Prettier source check, full Ruff lint/format checks, all three Django template format checks, and Django system checks pass.
- All 23 real PostgreSQL foundation tests pass (1.663 seconds). The existing root-route test now explicitly tests debug-disabled behavior.
- Real Django client smoke: both development routes return GET/HEAD 200 with debug enabled, POST 405, and GET 404 with debug disabled. Rendering either page makes zero database queries.
- Chrome navigation verified `/` to `/test` and back using stable test IDs. The preview still confirms both local fonts loaded. Index screenshot visually inspected; tab retained at `/`.
- No new permanent test suite or dependency was added. Other members' feature statuses and integration gates remain unchanged.
- Final documentation/integrity checks pass: 521 relative links/anchors across 36 Markdown files, balanced fences/details, credential scan across 200 shareable files, preserved requirement/member source files and application task rows, matching dependency inventory/locks, and Git whitespace checks.

## Next action

Jerome and teammates open [the local index](http://127.0.0.1:8000/) with Django running and `DJANGO_DEBUG=True`, then follow the preview card. Review local changes before separately authorizing publication. Alex/T04 remains ready; Jerome/T06 awaits integrated T04.
