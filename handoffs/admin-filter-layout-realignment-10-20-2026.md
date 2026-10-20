# Admin Filter Layout Realignment

- **Author:** Jerome with Kiro assistance.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** Consistent filter/search form layout across all seven admin list pages. No model, service, URL, form logic, or query change. Not a new task; visual/UX improvement to existing Done feature pages (T05, T06, T07, T08, T13, T16).

## Problem

All admin list pages had the Search button as the last cell inside `ui-filter-grid` on the `<form>` tag. This made the button sit inline with the filter fields in the same responsive grid row. There was no consistent placement and no Clear filters link on several pages.

## Pattern applied

Every affected page now follows a two-row filter section:

```
Row 1 — ui-filter-grid div:   [field]  [field]  [field]  ...
Row 2 — flex justify-end div:               [Clear filters]  [Search]
```

- Form tag: `class="space-y-4"` (was `class="ui-filter-grid"`)
- Fields only inside `<div class="ui-filter-grid">`
- Actions in `<div class="flex items-center justify-end gap-4">` below the grid

## Changed templates

| Page | Template | Changes |
|---|---|---|
| `/manage/requests/` | `templates/borrowing/manage/request_list.html` | Applied two-row layout; `justify-end` added (replaced no-op `position-right` class) |
| `/manage/items/` | `templates/inventory/manage/item_list.html` | Extracted button from grid into separate row; added `Clear filters` link (`data-testid="item-search-clear"`) |
| `/manage/categories/` | `templates/inventory/manage/category_list.html` | Extracted button from grid into separate row; added `Clear filters` link (`data-testid="category-search-clear"`) |
| `/manage/units/` | `templates/inventory/manage/unit_list.html` | Extracted button/clear from grid into separate row; `justify-end`; restyled Clear from `ui-button--outline` to text link matching other pages |
| `/manage/maintenance/` | `templates/inventory/manage/maintenance_list.html` | Extracted button/clear from grid into separate row; `justify-end`; Clear was conditional (`{% if request.GET.q or request.GET.status %}`), now always visible; added `data-testid="maintenance-search-submit"` and `data-testid="maintenance-search-clear"` |
| `/manage/accounts/` | `templates/accounts/manage/list.html` | Extracted button from grid into separate row; added `Clear filters` link (`data-testid="account-search-clear"`); added `data-testid="account-search-submit"` to button (was missing) |
| `/manage/audit/` | `templates/operations/manage/audit_list.html` | Pulled button/clear `<div>` out of `ui-filter-grid` into sibling row; added `justify-end`; swapped order so Clear precedes Search (consistent with other pages) |

## Actual verification

- `manage.py test borrowing.tests.test_requests --noinput` — **28 passed**.
- `manage.py test inventory.tests.test_catalog_management --noinput` — **28 passed**.
- `manage.py test inventory.tests.test_unit_management inventory.tests.test_maintenance --noinput` — **49 passed**.
- `manage.py test accounts.tests.test_account_management --noinput` — **13 passed**.
- `manage.py test operations.tests --noinput` — **28 passed**.
- `npm.cmd run build` passed for each change; CSS rebuilt with `justify-end` and `space-y-4` emitted.
- `manage.py check --database default` — 0 issues (0 silenced) after all changes.

## Not run

- Browser visual confirmation of the two-row layout on each page. Expected: fields fill the grid row, Search and Clear sit right-aligned below them.
- Mobile layout confirmation (fields stack to single column via `ui-filter-grid` auto-fit; actions remain right-aligned).

## Side notes

- The same session also changed the inventory list page sizes (separate handoff: [inventory-list-pagination-page-sizes-10-20-2026.md](inventory-list-pagination-page-sizes-10-20-2026.md)) and fixed `maintenance_list.html` iteration from `page.object_list` to `page`.
- No test asserts button position; all existing form-submit and filter tests pass unmodified.

## Next action

No dependent task is blocked. All seven pages are visual-only changes. T15 remains the next application feature (Margareth).
