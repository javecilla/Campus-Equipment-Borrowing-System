# Request queue text alignment

- **Owner:** Ralph Andre F. Giga (@dreygigz), with Codex assistance.
- **Date:** October 20, 2026, Asia/Manila (UTC+08:00).
- **Task:** UI-10 follow-up; fix text alignment in the clickable management request table.
- **Outcome:** Done locally on `ralph`, **uncommitted and not integrated into main**. Existing T17 and other local changes are preserved; no commit, push, PR, merge or external message was performed.

## Cause and correction

The shared table style gives direct cell links a 44px minimum click area and centers the link text within it. The request cells were top-aligned, which placed ordinary text above the request ID. [request_list.html](../templates/borrowing/manage/request_list.html) now vertically centers all six body cells. Item counts and status labels stay on one line, avoiding compact-screen wrapping while the existing table scroller handles width. The shared link click area, table semantics and [whole-row navigation](request-queue-clickable-rows-10-20-2026.md) are preserved; no shared CSS or JavaScript behavior was changed.

## Checks

- Chrome **155.0.8059.84**, isolated fictional test database: measured text positions across all six columns at **1440px and 320px**, with **0px vertical spread** at both widths. Desktop and compact screenshots inspected. Rechecked all six cell-padding click targets, ID navigation, keyboard Enter, Ctrl-click/new tab, selected text, pointer cursor, compact page bounds/navigation and JavaScript-disabled native-link fallback; passed with no JavaScript errors.
- `npm.cmd run build`: passed, including all nine fixed palette contrast checks.
- `.\.venv\Scripts\djlint.exe templates/borrowing/manage/request_list.html --check`: passed.
- Local Markdown links/anchors and `git diff --check`: passed at finalization.
- No new persistent tests were added for this small presentation correction. Django/backend tests, full repository formatting, Firefox/Safari and complete screen-reader testing were not rerun. The earlier 28 request tests and 294 T17 suite results remain historical evidence in their own snapshots.

The first compact check found `1 item` wrapping onto two lines; adding no-wrap to counts/status resolved it, and the rerun passed at both widths. Browser helpers used only the disposable test database, which was removed along with the temporary session file. No live business data was changed.

## Handoff

The [manual row checks](../docs/manual-test-guide.md#t13-01-queue-filters-and-read-only-detail), UI-10 backlog evidence and current handoff identify the corrected presentation. Ralph reviews by refreshing `/manage/requests/` and checking the ID, borrower, count, dates and status on the same line. Publication requires a separate request, with Jerome responsible for authorized main integration. T20 and all other dependency gates remain unchanged.
