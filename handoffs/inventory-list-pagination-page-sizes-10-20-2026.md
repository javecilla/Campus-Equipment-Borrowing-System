# Inventory List Pagination Page Sizes

- **Author:** Jerome with Kiro assistance.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** Adjust per-page row counts for three inventory list views and align their tests and manual guide. No model, service, URL, or form change. Not a new task; adjusts existing Done T07, T08, and T16 list behavior.

## Changes

| View | URL | Old page size | New page size |
|---|---|---|---|
| `category_list` | `/manage/categories/` | 25 | **5** |
| `unit_list` | `/manage/units/` | 25 | **10** |
| `maintenance_list` | `/manage/maintenance/` | 25 | **5** |
| `item_list` | `/manage/items/` | 10 | 10 (unchanged) |

## Relevant files

- [`inventory/views.py`](../inventory/views.py) — three `Paginator(…, N)` calls updated.
- [`inventory/tests/test_catalog_management.py`](../inventory/tests/test_catalog_management.py) — two assertions updated: `test_category_list_pagination_and_invalid_page` (25 → 5) and `test_pagination_preserves_special_character_searches_and_filters` category tuple (25 → 5).
- [`templates/inventory/manage/maintenance_list.html`](../templates/inventory/manage/maintenance_list.html) — `{% for record in page.object_list %}` corrected to `{% for record in page %}` to match the other three templates (same session, no functional change).
- [`docs/manual-test-guide.md`](../docs/manual-test-guide.md) — updated the T16 local-snapshot note from "more-than-25-row pagination" to "more-than-5-row pagination".

## Actual verification

- `.\.venv\Scripts\python.exe manage.py test --noinput` — **254 PostgreSQL tests passed in 39.457s** after updating both test assertions. No new tests were added; existing pagination tests cover page-size enforcement, filter-preserving URLs, and invalid-page 404 behavior.
- `.\.venv\Scripts\python.exe manage.py check --database default` — 0 issues (0 silenced).
- Pagination controls appear automatically when record count exceeds the new page size (6+ categories or maintenance records, 11+ units). With current local data (4 maintenance records, fewer than 5 categories), the nav block remains hidden until that threshold is reached — this is expected behavior.

## Not run

- Browser verification of the new page boundaries (Previous/Next appearing at 6/11 records). Existing automated tests cover the pagination logic.
- Unit and maintenance list manual browser checks remain Not run as documented in the manual guide.

## Decisions

- Items page size (10) was not changed — user did not request it.
- No template structure or CSS change was needed; the `{% if page.has_other_pages %}` nav block already handles all four lists uniformly.

## Next action

No dependent task is affected. These are self-contained view configuration changes. T15 remains the next task requiring implementation (Margareth, after accepted T13/T14).
