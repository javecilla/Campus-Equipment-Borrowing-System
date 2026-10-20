---
name: campus-ui
description: Build, edit, or review Campus Equipment Borrowing templates, form widget styling, navigation, and shared CSS using the established minimal design system. Use for this repository's frontend work; do not redesign unrelated applications or implement pending workflows.
---

# Campus UI

Keep new and AI-generated feature pages consistent with the existing equipment application. This skill guides authorized frontend work; it does not authorize a new feature, dependency, commit or publication.

## Start from the implemented design

Read [AGENTS.md](../../../AGENTS.md), current scope in [HANDOFF.md](../../../HANDOFF.md) and the affected [task](../../../docs/tasks.md). Use [django-mtv](../django-mtv/SKILL.md) for Django responsibility/access contracts. Read the [canonical styling rules and component table](../../../docs/coding-standards.md#tailwind-styling-pattern); that guide owns the palette, typography, spacing, breakpoints and component contracts. Do not maintain a second copy here.

Inspect the nearest existing page for the requested feature and its actual widget classes before editing. Compare [the administrator home](../../../templates/operations/manage/dashboard.html), [catalog list](../../../templates/inventory/manage/item_list.html) or [borrower request form](../../../templates/borrowing/portal/request_form.html) as relevant. These illustrate different content layouts, not mandatory sections to copy into every page.

## Reuse the shared shell and components

- Extend the appropriate [management](../../../templates/operations/manage/base.html) or [portal](../../../templates/accounts/portal/base.html) base and fill `workspace_content`; preserve the shared [workspace](../../../templates/components/workspace.html).
- Map the requested content to existing `ui-*` page/surface/grid/field/button/table classes from the canonical table. Use complete literal Tailwind utilities for feature-specific composition. Add shared CSS only when existing patterns cannot express an actual repeated need.
- Keep tokens in [app.css](../../../static/css/app.css), local fonts in its existing import, and compiled asset loading in [base.html](../../../templates/base.html). Do not introduce per-page palettes, remote fonts or another styling framework.
- Preserve the [direct top-bar profile link](../../../templates/components/account_link.html), the [red native POST logout row](../../../templates/components/logout.html) and shared [line icons](../../../templates/components/icon.html). A feature page must not recreate or override their navigation behavior.
- Render only implemented actions and real supplied data. A visual reference does not authorize fake metrics, decorative filters, new workflow controls or removal of pending-feature status.

## Search and filter form layout

Every admin and portal list page uses the same two-row filter pattern. Do not place the submit button inside the field grid.

**Required structure:**

```html
<section class="border-t border-slate-200 py-6">
    <form method="get" action="..." data-testid="..." class="space-y-4">

        <!-- Row 1: filter fields only -->
        <div class="ui-filter-grid">
            <div>
                <label for="{{ form.FIELD.id_for_label }}"
                       class="mb-2 block text-sm font-medium">{{ form.FIELD.label }}</label>
                {{ form.FIELD }}
                {{ form.FIELD.errors }}
            </div>
            <!-- repeat for each additional field -->
        </div>

        <!-- Row 2: actions right-aligned -->
        <div class="flex items-center justify-end gap-4">
            <a href="{% url 'namespace:list-route' %}"
               data-testid="...-clear"
               class="text-sm font-semibold text-accent underline underline-offset-4
                      focus-visible:outline-2 focus-visible:outline-offset-4
                      focus-visible:outline-accent">Clear filters</a>
            <button type="submit"
                    data-testid="...-submit"
                    class="ui-button ui-button--tonal">Search</button>
        </div>

    </form>
</section>
```

**Rules:**
- `ui-filter-grid` goes on a wrapper `<div>`, never on the `<form>` tag itself.
- `space-y-4` on the form separates the field row from the action row.
- `justify-end` on the action row aligns Search and Clear to the right edge.
- **Clear filters is always visible** — do not make it conditional on `request.GET` values.
- Clear filters is a plain text link (`text-sm font-semibold text-accent underline`), not a `ui-button`.
- Submit button label matches the page context: `Search`, `Search requests`, `Filter`, etc.
- Both the submit button and the clear link must have `data-testid` attributes.
- The `border-t border-slate-200 py-6` section wrapper provides the visual separator from the page header above; add `mt-8` if the section follows a page header directly (no outer `space-y-*` gap).

**Implemented examples:** [`/manage/requests/`](../../../templates/borrowing/manage/request_list.html), [`/manage/items/`](../../../templates/inventory/manage/item_list.html), [`/manage/categories/`](../../../templates/inventory/manage/category_list.html), [`/manage/units/`](../../../templates/inventory/manage/unit_list.html), [`/manage/maintenance/`](../../../templates/inventory/manage/maintenance_list.html), [`/manage/accounts/`](../../../templates/accounts/manage/list.html), [`/manage/audit/`](../../../templates/operations/manage/audit_list.html), [`/portal/equipment/`](../../../templates/inventory/portal/equipment_list.html), [`/portal/requests/`](../../../templates/accounts/portal/request_list.html).

**What not to do:**
```html
<!-- WRONG: button inside ui-filter-grid, no Clear, conditional Clear -->
<form class="ui-filter-grid">
    <div>{{ form.q }}</div>
    <button type="submit">Search</button>  <!-- grid cell, not a separate row -->
</form>

<!-- WRONG: Clear is conditional -->
{% if request.GET.q %}<a href="...">Clear</a>{% endif %}
```

## Verify the resulting page

Run the applicable [project checks](../../../DEV.md#before-handing-over-work). A build runs the dependency-free palette contrast check; it does not validate every UI behavior. Use existing test IDs or accessibility IDs to check the affected real routes and controls in a browser. Inspect desktop and compact screenshots, including the sidebar breakpoint and 320px when changing shared navigation. Check focus, visible names/roles, labels/errors, local table scrolling and page bounds as relevant. Keep access checks, CSRF and server validation intact.

Update the affected [manual test cases](../../../docs/manual-test-guide.md), then follow [project-handoff](../project-handoff/SKILL.md). Report actual checks and limitations. This is an instruction-based team convention, not a background enforcement service; agents that do not discover repository skills must be given this file and AGENTS.md explicitly.
