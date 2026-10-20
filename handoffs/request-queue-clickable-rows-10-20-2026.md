# Request queue clickable rows

- **Owner:** Ralph Andre F. Giga (@dreygigz), with Codex assistance.
- **Date:** October 20, 2026, 17:31 Asia/Manila (UTC+08:00).
- **Task:** UI-10, the explicit request to open request details by clicking the entire table row at `/manage/requests/`.
- **Outcome:** Done locally on `ralph`, **uncommitted and not integrated into main**. No commit, push, PR, merge or teammate notification was performed. Existing uncommitted T17/application/documentation work is preserved.

## Delivered change

[request_list.html](../templates/borrowing/manage/request_list.html) marks populated request rows and their native ID links, supplies pointer/hover/focus feedback and loads the fingerprinted page module. [request-list.js](../static/js/request-list.js) opens the existing detail link when a noninteractive part of its row receives an ordinary click. Links and other interactive controls retain their own behavior; selected text and modified clicks are ignored by the row handler. The request ID remains a native link for keyboard users, Ctrl-click/new-tab actions and operation without JavaScript. Table semantics, filters, pagination, server permissions and all workflows remain unchanged.

The normal asset build includes `build/request-list.js`; no dependency or migration was added. Manual checks are recorded in [T13-01](../docs/manual-test-guide.md#t13-01-queue-filters-and-read-only-detail). The existing module-loading guidance in [DEV.md](../DEV.md#frontend-assets-tailwind-and-page-scripts) applies.

## Checks performed

- Chrome **155.0.8059.84**, using an isolated fictional database: all six cell-padding click targets, original ID link, keyboard Enter, Ctrl-click/new tab, selected-text preservation, pointer cursor, 320px page bounds/row navigation and the ID link with JavaScript disabled **passed**. No JavaScript errors. Desktop screenshot inspected. The browser fixture reuses the local ignored test helper; no live business records were changed. Temporary browser database and session file were removed afterward.
- `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_requests --noinput`: **28 PostgreSQL tests passed in 4.753s**.
- `npm.cmd run build`: **passed**, including all nine contrast checks and the new page bundle.
- `npm.cmd run format:check`: **passed**.
- `.\.venv\Scripts\djlint.exe templates/borrowing/manage/request_list.html --check`: **passed**.
- `.\.venv\Scripts\python.exe manage.py check --database default`: **passed**, no issues.
- Local Markdown links/anchors and `git diff --check`: checked at finalization.

The complete 294-test suite was **not rerun for this localized frontend change**; its prior passing T17 result remains in the [T17 snapshot](ralph-t17-per-unit-returns-and-overdue-10-20-2026.md). No new persistent tests were added for this small reversible enhancement. Firefox/Safari and complete screen-reader testing were not run. Previously documented unrelated repository formatting findings remain unchanged.

## Next action

Refresh `/manage/requests/` and click a Borrower, Items, Submitted, Due date or Status cell to review the behavior. Ralph reviews these uncommitted changes. Publication/integration requires a separate request; Jerome handles authorized main integration. UI-10 does not start or complete T20, which still requires accepted integrated T17/T18/T19. Other task statuses and historical contributor credit are preserved.
