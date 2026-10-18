# Catalog layout, preview and asset refresh

- Date/time zone: October 18, 2026, Asia/Manila (UTC+08:00).
- Work/owner: T07 manual-testing feedback; Kenneth Cortez's catalog, continued by Jerome Avecilla with Codex assistance under the user's explicit request.
- Branch/base: `jerome`, HEAD `20c4452` / Kenneth baseline PR #19. This follow-up and the preceding T07 batch remain **uncommitted / Not integrated**. No commit, push, PR, merge, migration or dependency change in this follow-up.

## Result

- [Category detail](../templates/inventory/manage/category_detail.html) and [catalog list](../templates/inventory/manage/item_list.html) reuse an [item identity component](../templates/inventory/manage/item_identity.html) with thumbnail/name. Child items display the effective archived-category label where applicable.
- [Item detail](../templates/inventory/manage/item_detail.html) places photo and description/metadata beside each other on wider screens. Live counts use two columns on mobile, four on small screens and seven on desktop.
- Catalog search/category/status/button share one row from the medium breakpoint. [The view](../inventory/views.py) now paginates catalog items at **10 per page**; category pages retain 25. Search and filters remain encoded/preserved across page links; malformed pages still return 404. The [HTTP](../docs/api_spec.md) and [SRS](../docs/SRS.md) pagination contracts match the user's requested change.
- [New-item form](../templates/inventory/manage/item_form.html) uses metadata on the left and a full-width image/selection panel on the right on desktop, stacking on mobile. The separate [photo action form](../templates/inventory/manage/photo_form.html) shares the [preview panel](../templates/inventory/manage/photo_preview.html).
- [Native JavaScript](../static/js/equipment-photo.js) previews a selected file using an object URL, exposes **Remove selected image**, clears the pending file without a POST, restores the original/default preview, reports decode failures and releases obsolete object URLs. A selected file is uploaded only when the form is submitted. Existing saved-photo removal remains the separate confirmed, audited action.
- The invisible archive button and one-column count grid were reproduced in Chrome despite the current generated CSS containing the correct utilities. Chrome's loaded stylesheet omitted those rules. [The compiled_asset tag](../operations/templatetags/assets.py) now versions built CSS/JS URLs by their content through the [shared shell](../templates/base.html), [workspace](../templates/components/workspace.html), preview page and photo forms. Chrome then fetched the current CSS and displayed the archive button's red background and the intended grids. Missing bundles fail explicitly with the build command; no silent style substitute was added. [DEV.md](../DEV.md) documents the build/refresh and photo behavior.

## Requirements answers

- [Part 5 of the original brief](../docs/Project-Requirements.txt) expressly allows HTML/CSS, JavaScript, Bootstrap styling and a chart library; AJAX is optional. This enhancement uses native DOM events and local object URLs, with validation and authorization still on Django.
- Part 2 A2 requires create/view/update/archive and preserving referenced records. It does **not** require restoration or state that archives must be permanent. The current forms/services/routes implement archive only; no unarchive route exists. An audited ADMIN-only restoration action could be separately designed as an optional enhancement. It was not requested for implementation by the user's requirements question and was not added here.

## Verification performed

| Check | Actual result |
| --- | --- |
| Full PostgreSQL suite | **104 tests passed**. The existing filtered-pagination integration test now checks category size 25 and catalog size 10; the added real-filesystem [asset integration check](../operations/tests/test_assets.py) proves unchanged content keeps its URL, changed content changes it, and a missing bundle raises the build instruction |
| Build/style/dependencies | npm format/build/audit passed, zero vulnerabilities; Ruff lint/format passed; all 46 templates passed djLint; Node syntax check passed; pip check passed |
| Django/schema | Database check passed, no migration drift, no unapplied migrations; no schema/dependency change needed |
| Documentation/Git | 514 local Markdown links resolve; fences, dated handoff paths and Git whitespace checked. The asset integration check passed again after making its single-result finder argument explicit |
| Real Chrome, localhost:8000 | Category 4 loads three protected item thumbnails; item 2 uses photo/details columns and seven desktop count columns; filters align at the same vertical position; catalog pages 1/2 each contain ten items. Category 9 archive confirmation is visibly red with white text; no archive action submitted |
| Responsive/browser scripts | Desktop new-item metadata/preview columns verified at 528px each; mobile creation stacks at 375px, counts have two columns, and catalog/category pages stay within the viewport. At 768px all four filter controls share one row. Screenshots inspected; the preview module loads with its versioned URL, clear control initially hidden, and no browser console errors. Viewport restored; updated creation page left open for review |

An initial full run failed only the old pagination expectation (one item on page 2 of a 26-item catalog). The test was updated to the requested ten-row contract; the final full suite passes. The browser extension still denies file selection because file-URL access is disabled. Actual selection/preview/clear behavior could not be exercised end to end through the chooser and remains a manual check; implementation, module load, syntax/build and server-side multipart behavior are verified. No browser permission was changed or restriction bypassed.

## Transfer

Refresh the live pages to obtain the versioned assets. Manually choose an image on the creation screen, confirm the preview changes, clear it and choose another; this is the remaining browser coverage gap. Review the full uncommitted T07 diff before separately authorized publication/integration. Existing user data, supplied assets, historical handoffs and unrelated pending changes are preserved. No catalog writes were made during these live-browser checks.

Kenneth / T08 still consumes the integrated T07 batch before unit work; future portal/T20 acceptance is not claimed. Category restoration remains a separate optional design decision. No CI, full borrower workflow, T14 race, performance, backup or restore run was performed.
