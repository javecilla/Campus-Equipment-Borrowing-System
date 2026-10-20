# Borrower Portal UI Improvements

- **Author:** Jerome with Kiro assistance.
- **Date:** October 20, 2026, Asia/Manila.
- **Scope:** Visual and UX improvements to the borrower portal — placeholder home, equipment catalog layout and pagination, request list layout and pagination, filter alignment, and navigation icon. No model, service, URL, or business logic change. Adjusts existing Done feature pages (T09, T10, T11, T12) and replaces AI-generated home content with a proper placeholder for T20.

---

## 1. Portal home (`/portal/`) — placeholder for T20

**File:** `accounts/views.py`

`portal_home` now renders `accounts/portal/pending.html` with T20 context instead of `home.html` (which contained AI-generated navigation links). Mirrors the admin dashboard treatment (T18 placeholder).

```python
# before
return render(request, "accounts/portal/home.html")

# after
return render(request, "accounts/portal/pending.html", {
    "heading": "Borrower workspace",
    "module": "T20 · Ralph with Ellyssa",
    "description": "...",
    "next_work": "...",
})
```

`home.html` is preserved for Ralph and Ellyssa to build out when T20 is authorized.

---

## 2. Equipment list (`/portal/equipment/`) — filter, grid, pagination

**Files changed:**
- `templates/inventory/portal/equipment_list.html`
- `inventory/portal_views.py`
- `inventory/tests/test_portal_equipment.py`

| Change | Before | After |
|---|---|---|
| Filter form structure | `ui-filter-grid` on `<form>` tag; button inline in grid; conditional Clear | `space-y-4` on form; fields in `ui-filter-grid` div; `justify-end` actions row; Clear always visible |
| Filter wrapper | `rounded-lg border bg-white p-4 sm:p-5` card | `border-t border-slate-200 py-6` section (matches admin pattern) |
| Grid columns | `ui-catalog-grid` (auto-fill ~4 at lg) | `grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5` |
| Items per page | 25 | **10** |
| Clear filters visibility | Conditional on `request.GET.q or request.GET.category` | Always visible |

Test assertions updated in `test_portal_equipment.py`: `test_pagination_at_twenty_five_items` — page 1 and page 2 assertions changed from 25/5 to 10/10 (30 test items across 3 pages of 10).

---

## 3. Request list (`/portal/requests/`) — filter, grid, pagination, spacing

**Files changed:**
- `templates/accounts/portal/request_list.html`
- `borrowing/views.py`

| Change | Before | After |
|---|---|---|
| Filter form structure | `mt-7 flex flex-col gap-3 sm:flex-row sm:items-end`; button inline; no Clear | `border-t mt-8 py-6` section; `space-y-4` form; `ui-filter-grid` for fields; `justify-end` actions; Clear filters added |
| Clear filters | Absent | `data-testid="request-filter-clear"` text link |
| Submit button testid | None | `data-testid="request-filter-submit"` |
| Card layout | `space-y-3` (1 per row, stacked) | `grid grid-cols-1 sm:grid-cols-2 gap-4` (2 per row) |
| Filter–header spacing | `mt-7` only | `mt-8 border-t` (consistent gap between description and horizontal rule) |
| Requests per page | 25 | **6** |

---

## 4. Navigation icon — My loans (`loan-list`)

**File:** `templates/components/icon.html`

`loan-list` icon replaced: the previous icon was a clipboard variant nearly identical to `request-list`. New icon is a **calendar with checkmark** — semantically accurate (loans have return due dates) and visually distinct.

```html
<!-- before — clipboard variant, indistinguishable from request-list -->
<path d="M8 3h8v4H8zM8 5H5v16h14V5h-3M8 12h8M8 16h5" />

<!-- after — calendar with checkmark -->
<rect x="3" y="4" width="18" height="18" rx="2" />
<path d="M16 2v4M8 2v4M3 10h18M9 16l2 2 4-4" />
```

---

## Actual verification

| Test module | Result |
|---|---|
| `accounts.tests.test_authentication accounts.tests.test_borrower_portal` | **33 passed** |
| `inventory.tests.test_portal_equipment` | **25 passed** |
| `borrowing.tests.test_request_tracking` | **10 passed** |

- `manage.py check --database default` — 0 issues (0 silenced).
- `npm.cmd run build` — CSS rebuilt after each change; zero vulnerabilities.

## Not run

- Browser verification of 5-column equipment grid, 2-column request cards, filter alignment, and calendar icon rendering.
- Mobile layout checks (single-column equipment grid, single-column request cards).

## Next action

No dependent task is blocked. T20 (Ralph with Ellyssa) is the owner of the full portal layout integration; these changes remove AI placeholder content and provide clean starting points. T15 remains the next application feature (Margareth).
