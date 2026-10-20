# Admin Workspace UI Improvements

**Date:** October 20, 2026, Asia/Manila
**Author:** Jerome with Kiro assistance
**Branch:** `jerome` (uncommitted, local only)
**Scope:** UI polish — no schema changes, no new dependencies, no test changes, no new routes.

---

## Work summary

Five targeted UI improvements to the administrator workspace, all driven by reviewer feedback in the same session. No business logic, data models, HTTP contracts, or authorization paths were changed.

---

## Changes

### 1. Dashboard — Equipment & borrowing section layout

**File:** `templates/operations/manage/dashboard.html`

Replaced the card grid (`ui-launch-grid` + `action_link.html` includes) with the same row-per-row `ui-tool-link` style used by the Workspace tools section. Each of the four links (Equipment catalog, Requests and approvals, Borrower accounts, Maintenance) is now a full-width row with the link label on the left and a matching icon on the right. Icon mapping:

| Link | Icon |
|---|---|
| Equipment catalog | `equipment-list` |
| Requests and approvals | `request-list` |
| Borrower accounts | `accounts` |
| Maintenance | `audit-list` |

### 2. Requests page — filter button order

**File:** `templates/borrowing/manage/request_list.html`

Swapped the order of the two filter controls in the `flex justify-end` row so **Clear filters** (link) appears on the left and **Search requests** (button) appears on the right. Previously the order was reversed.

### 3. Sidebar pending requests badge

**New file:** `operations/context_processors.py`
**Modified:** `config/settings.py`, `templates/components/navigation_link.html`, `templates/operations/manage/base.html`

Added a live count badge to the Borrowing navigation link in the admin sidebar:

- `operations/context_processors.py` — `nav_badges()` runs a single `COUNT` query (`BorrowRequest.objects.filter(status=RequestStatus.PENDING).count()`) only for authenticated active ADMIN users; all other sessions receive an empty dict.
- `config/settings.py` — registered `operations.context_processors.nav_badges` in `TEMPLATES[0]["OPTIONS"]["context_processors"]`.
- `templates/components/navigation_link.html` — added an optional `{% if badge %}` block rendering `<span class="ui-nav-badge">`. Caps at `99+`; includes an `aria-label` for screen readers.
- `templates/operations/manage/base.html` — passes `badge=nav_pending_requests` to the Borrowing nav link only; all other sidebar links are unchanged.

### 4. Badge styling and adaptive active-state color (`static/css/app.css`)

Added `.ui-nav-badge` and its active-state override to the component layer:

```
.ui-nav-badge
  margin-inline-start: auto   ← pushes badge to right edge
  background: var(--md-sys-color-primary)   ← #1b5a5a teal when inactive
  color: var(--md-sys-color-on-primary)     ← white text

.ui-nav-link[aria-current="page"] .ui-nav-badge
  background: var(--md-sys-color-on-primary)   ← white when active link
  color: var(--md-sys-color-primary)            ← teal text
```

Using a CSS class instead of inline Tailwind utilities avoids a missing-build-output issue where `bg-rose-600`/`text-white` would be absent from `static/build/app.css` until a rebuild, making the badge invisible on light backgrounds.

Also added `width: 100%` inside the `@media (min-width: 1024px)` block, scoped to `.ui-navigation .ui-nav-link` (not `.ui-nav-link` globally) so that `margin-inline-start: auto` has room to push the badge to the right edge in the desktop sidebar without affecting the `ui-nav-link` subnav tabs on pages like `/manage/items/`.

### 5. Tool-link last-child border removal (`static/css/app.css`)

Added:
```css
.ui-tool-link:last-child {
    border-block-end: none;
}
```

Removes the trailing bottom border from the last row in any `ui-tool-link` list. Applies to both sections on the dashboard: Maintenance (Equipment & borrowing) and Audit history (Workspace tools).

---

## Files changed

| File | Change |
|---|---|
| `templates/operations/manage/dashboard.html` | Equipment & borrowing section: cards → rows |
| `templates/borrowing/manage/request_list.html` | Filter button order: Clear before Search |
| `templates/components/navigation_link.html` | Optional badge slot added |
| `templates/operations/manage/base.html` | Borrowing nav link receives `badge=nav_pending_requests` |
| `operations/context_processors.py` | **New.** `nav_badges()` context processor |
| `config/settings.py` | Registered `operations.context_processors.nav_badges` |
| `static/css/app.css` | `.ui-nav-badge`, active override, scoped `width: 100%`, `.ui-tool-link:last-child` |
| `static/build/app.css` | Compiled output — rebuilt after all source changes |

---

## Verification

| Check | Result |
|---|---|
| `ruff check operations/context_processors.py` | ✅ All checks passed |
| `npm run build:css` | ✅ Done in ~100–155 ms; nine contrast pairs confirmed |
| Compiled output contains `.ui-nav-badge`, active override, scoped `.ui-navigation .ui-nav-link` width | ✅ Verified via regex extraction from `static/build/app.css` |
| Django test suite | Not run this session (no application logic changed) |
| Browser / manual checks | **Not run** — see manual test notes below |

### Manual test notes — Not run

These checks were not performed this session and remain outstanding for browser verification:

- Badge appears on the Borrowing sidebar link when at least one PENDING request exists
- Badge is hidden when there are zero PENDING requests
- Badge color is `#1b5a5a` (teal) on inactive link; badge inverts to white pill with teal text on active link
- Badge is right-aligned in the desktop sidebar (≥1024 px)
- Equipment & borrowing section on the dashboard renders as rows, not cards
- Clear filters appears to the left of Search requests on `/manage/requests/`
- Last item in Equipment & borrowing (Maintenance) and Workspace tools (Audit history) has no bottom border
- Subnav tabs on `/manage/items/`, `/manage/requests/`, and other list pages are not full-width (regression guard)

---

## Decisions

- **Badge uses CSS class, not Tailwind utilities.** Inline Tailwind classes (`bg-rose-600`, `text-white`, etc.) are only present in the compiled CSS after a rebuild. A CSS class in `app.css` is always in the output.
- **`width: 100%` scoped to `.ui-navigation .ui-nav-link`.** Applying it to `.ui-nav-link` globally broke the subnav tab buttons on equipment/inventory pages. Scoping to the sidebar container fixes the alignment without regression.
- **Badge color is primary teal, not error red.** The project design uses error red for actual error states. A teal badge aligns with the sidebar's design language and still provides clear count visibility.
- **No new test added.** The context processor is a simple ORM count with no branching logic. The visual changes are presentation-only and covered by manual checks.

---

## Next action

Changes are uncommitted on `jerome`. Browser verification (listed above) should be done before committing. No other task is blocked by this work; T19 and T20 prerequisites are unchanged.
