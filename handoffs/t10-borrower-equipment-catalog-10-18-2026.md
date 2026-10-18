# T10 Borrower Equipment Catalog Browsing and Detail Handoff

## Summary

- **Task**: T10 (Borrower equipment catalog search and item detail)
- **Owner**: Ma. Ellyssa Bianca Regodon (Ellie, `@ellieebeann`), with Antigravity pair programming assistance
- **Date**: October 18, 2026, Asia/Manila (`+08:00`)
- **Status**: **Done** (locally verified; uncommitted for review per team instructions)
- **Branch**: `elly` (local working tree based on `origin/main` at `f29bd91`)
- **Main integration**: **Not integrated** (local changes awaiting user review, commit authorization, and PR)

## Implemented Work

1. **Borrower catalog search and filtering (`/portal/equipment/`)**:
   - Replaced placeholder in [accounts/portal_urls.py](../accounts/portal_urls.py) and [accounts/portal_views.py](../accounts/portal_views.py) with real basic-user views in [inventory/portal_views.py](../inventory/portal_views.py).
   - Created [PortalItemSearchForm](../inventory/forms.py) filtering by item name/description query `q` and active category `category`. Category choices strictly evaluate non-archived categories (`is_archived=False`).
   - Created [list_active_catalog_items](../inventory/queries.py) returning only non-archived items under active categories (`CatalogItem.is_archived=False` and `Category.is_archived=False`), annotated with `serviceable_units` (Available + Reserved + Issued per BR-12) and `available_units`.
   - Paginated at 25 items per page per `NFR-06`, using Django's `{% querystring %}` to preserve search parameters across page navigation.

2. **Borrower item detail (`/portal/equipment/<id>/`)**:
   - Created `equipment_detail` in [inventory/portal_views.py](../inventory/portal_views.py) backed by [get_active_catalog_item_or_404](../inventory/queries.py).
   - Shows item name, category badge, description, photo (or shared static default), live available count, and total serviceable units.
   - Enforces confidentiality per SRS `U2`: strictly hides internal administrative notes, physical unit asset codes, serial numbers, maintenance records, and other borrower allocations.
   - Excludes archived records per BR-13: attempting to view an archived item or an item under an archived category returns 404.

3. **Borrower equipment photo delivery (`/portal/equipment/<id>/photo/`)**:
   - Implemented `equipment_photo` in [inventory/portal_views.py](../inventory/portal_views.py) delivering uploaded WebP media across the active `BASIC_USER` security boundary.
   - Sets `X-Content-Type-Options: nosniff` and `Cache-Control: private, no-store`.
   - Returns 404 for missing photos, archived items, or archived categories, falling back cleanly to the shared default static asset in templates.

4. **Templates and UI Presentation**:
   - Created [templates/inventory/portal/equipment_list.html](../templates/inventory/portal/equipment_list.html) and [templates/inventory/portal/equipment_detail.html](../templates/inventory/portal/equipment_detail.html) extending `accounts/portal/base.html`.
   - Maintained light mode, responsive grid/stacking layout, accessible form labels, visible focus rings, and explicit empty states with filter reset options.
   - Updated [templates/accounts/portal/base.html](../templates/accounts/portal/base.html) with `active_portal_tab` support so the "Equipment" tab stays highlighted when viewing detail pages.

## Verification Evidence

| Check | Command | Result |
| --- | --- | --- |
| Focused portal equipment test suite | `python manage.py test inventory.tests.test_portal_equipment --noinput` | **25 tests passed in 3.591s** covering anonymous redirects, admin/deactivated 403, method 405, active catalog search, category filtering, archival exclusion, BR-12 math, SRS U2 confidentiality, photo delivery, and navigation |
| Full system test suite | `python manage.py test --noinput` | **174 tests passed in 63.781s** across the entire PostgreSQL test database |
| Django system check | `python manage.py check --database default` | Passed: `System check identified no issues (0 silenced)` |
| Migration drift check | `python manage.py makemigrations --check --dry-run --noinput` | Passed: `No changes detected` |
| Applied migrations check | `python manage.py migrate --check` | Passed: all migrations up to date |
| Python linting | `ruff check .` | Passed: `All checks passed!` |
| Python formatting | `ruff format --check .` | Passed: `176 files already formatted` |
| Template formatting | `djlint templates/inventory/portal/ --check` | Passed: `0 files would be updated` |
| Frontend asset build | `npm run build` | Passed: Tailwind v4 and esbuild bundles built |
| Frontend code style | `npm run format:check` | Passed: Prettier formatting verified |
| Dependency vulnerabilities | `npm audit` | Passed: `found 0 vulnerabilities` |
| Python dependencies | `pip check` | Passed: `No broken requirements found` |
| Git whitespace check | `git --no-pager diff --check` | Passed: clean diff |

## Affected Files

- [inventory/portal_views.py](../inventory/portal_views.py) (new: portal equipment list, detail, and photo streaming views)
- [inventory/forms.py](../inventory/forms.py) (added `PortalItemSearchForm`)
- [inventory/queries.py](../inventory/queries.py) (added `list_active_catalog_items` and `get_active_catalog_item_or_404`)
- [inventory/tests/test_portal_equipment.py](../inventory/tests/test_portal_equipment.py) (new: 25 integration tests)
- [accounts/portal_urls.py](../accounts/portal_urls.py) (mounted equipment routes to `inventory.portal_views`)
- [accounts/portal_views.py](../accounts/portal_views.py) (removed superseded placeholder)
- [templates/accounts/portal/base.html](../templates/accounts/portal/base.html) (supported `active_portal_tab` for detail views)
- [templates/inventory/portal/equipment_list.html](../templates/inventory/portal/equipment_list.html) (new: portal catalog search template)
- [templates/inventory/portal/equipment_detail.html](../templates/inventory/portal/equipment_detail.html) (new: portal item detail template)

## Decisions and Constraints

- **Confidentiality (SRS U2)**: Basic users have no access to physical asset codes, acquisition dates, internal notes, maintenance histories, or loan allocations.
- **Serviceable definition (BR-12)**: `serviceable_units = Available + Reserved + Issued`. Units in `MAINTENANCE` or `RETIRED` are excluded from serviceable and available counts.
- **Archival behavior (BR-13)**: Items marked `is_archived=True` or belonging to an archived category (`category.is_archived=True`) are excluded from queries and return HTTP 404 on direct access.
- **Photo delivery**: Uploaded photos are served only via the protected `/portal/equipment/<id>/photo/` route for authenticated active basic users; templates fall back to the static default photo when no photo is uploaded.

## Next Actions and Consumers

- **Ralph / T11 (Borrower request submission)**: T10 catalog browsing is verified and ready to be linked to request form creation once T11 is authorized.
- **User Review**: Ellie's T10 changes remain uncommitted on branch `elly` awaiting user inspection and commit authorization.
