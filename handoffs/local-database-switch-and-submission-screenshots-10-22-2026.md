# Local/shared database selector and submission screenshots

## Outcome and scope

October 22, 2026, 19:54 Asia/Manila (UTC+08:00). Jerome requested a simple `.env.local` database switch and screenshots for every SUBMISSION.md checklist entry. Codex implemented HOST-02, captured the actual application and updated setup/manual/current-state evidence. **Done locally, uncommitted and Not integrated.** No commit/push is included in this request.

- [Environment parsing](../config/environment.py) requires `IS_LOCAL_DB_CONNECTION` to be exactly `True` or `False`. `True` uses existing local `DB_*` and ignores the retained shared URL; `False` requires/validates the TLS `DATABASE_URL`. Missing/invalid selected configuration fails explicitly. The [.env.example](../.env.example) default is local; existing private files must add the key. No schema, dependency or workflow change.
- [DEV switching](../DEV.md#switch-between-local-and-shared-databases) explains both modes, restart/target verification and independent `MEDIA_STORAGE` selection. This workstation's ignored private file ends with local database/media selected and shared credentials retained. Switching does not synchronize either dataset or photo storage. [README](../README.md#run-locally), isolation commands, architecture, manual cases and Django skill guard are aligned. The T24 recovery helper explicitly selects shared mode when parsing the coordinator's direct URL.
- [SUBMISSION.md](../SUBMISSION.md#screenshots-checklist) links **72 actual PNG screenshots and the real CSV** in `screenshots/`, covering every one of its **39 checklist entries**, plus create/edit/detail/confirmation pages and two mobile views. Desktop viewport 1440 x 1000; mobile 390 x 844; full-page screenshots can be taller and the chart detail is a real element capture. Images were not retouched or synthesized. Browser automation uses stable input IDs/test IDs.
- Screenshot collection is complete as explicitly authorized preparatory evidence. **T30 itself remains Not started:** outstanding prerequisite evidence, final ZIP and clean-machine verification were not bypassed. T27 remains In progress; screenshot artifacts do not establish institutional policy or asset-license clearance.

## Database and artifact safety

Initial read-only local inspection found 9 fictional accounts, 29 catalog items, 46 units, 30 requests, 20 loans, 10 maintenance records and all referenced local photos. Source was local `campus_equipment` on `127.0.0.1:5432`; no fresh seed was needed. A template clone was refused because other sessions used the source; those sessions were not terminated. A read-only PostgreSQL 17 `pg_dump` and restore into the newly created **`campus_screenshots_20261022`** supplied the screenshot copy instead.

The capture server ran only against that copy on loopback port 8030 with local media. One unused item was archived and one fictional account deactivated/reactivated through actual HTTP workflows in the copy. An invalid category submission produced genuine server-rendered inline errors without creating a category. The damaged-return screenshot links an existing maintenance record that was subsequently repaired; it is not presented as newly opened maintenance. Different owner-scoped borrower states use the corresponding fictional accounts.

The CSV was downloaded through the report's real export action and saved: **13 October loan rows plus the matching totals row** (23 issued / 17 returned / 6 outstanding units). The screenshot shows Chrome's actual completed download history; automation assigns its temporary download a generated name. Attempts to change the browser's native download naming were discarded; the delivered evidence uses a fresh browser context with the ordinary successful download/save flow.

Final read-only fingerprints match **all 22 complete original local tables**. Original local photos were retained. Temporary screenshot server and isolated browser sessions are stopped, and the named screenshot database is removed. Temporary credential-bearing capture scripts/logs were removed from the ignored tooling directory. Private database dump, hashes and remaining tooling stay under ignored `output/playwright/submission/`; none is in the screenshot deliverables.

Actual mode checks used explicit read-only transactions: `True` connected to local `campus_equipment` with `transaction_read_only=on`; `False` connected to shared **`neondb` with TLS and `transaction_read_only=on`**. No shared seed, migration, deletion, account change, workflow or cloud-media write occurred.

## Verification

| Check | Actual result |
| --- | --- |
| Full regression suite | **345 tests passed in 128.527s**, including explicit database selection, process override, invalid/missing selector and missing shared-URL errors. Child explicitly set local selector, empty URL and local media; Django created/destroyed **`test_campus_equipment`**. |
| Django checks | System/database check, migration dry-run/check passed against local `campus_equipment`; no model changes or migrations applied. |
| Ruff | Lint passed; changed Python files pass format checking. Whole-repository format check retains the pre-existing unformatted Python block in `handoffs/borrower-portal-ui-improvements-10-20-2026.md`. |
| Frontend/packages | npm build/theme contrast, Prettier source check, npm audit (zero vulnerabilities) and pip check passed. No package changes. |
| Template formatting | djLint retains one pre-existing formatting finding in untouched `templates/inventory/portal/equipment_list.html`; no template/UI styling changed. |
| Browser evidence | Actual role login redirects, authenticated pages, local photos, owner-specific request/loan states, expected HTTP 403, inline validation, inactive-login denial and successful CSV capture. Each bulk-captured page checked expected response/redirect and loaded images. All 72 PNGs decode; contact sheets and representative full-size images were visually inspected. |
| Preservation/cleanup | All 22 original local table fingerprints match; isolated screenshot database/server/browser sessions removed. Shared connection checked read-only only. |
| Documentation/artifacts | **1,322 local links/anchors across eleven affected documents passed**; all 39 checklist entries and 72 referenced/decoded PNGs, balanced fences, skill metadata, source/status consistency and `git diff --check` passed. Changed Python files pass Ruff lint/format checking; the two pre-existing formatting findings above remain outside this scope. |

No new concurrency benchmark, cloud-media import, instructor policy investigation, external message, final ZIP, clean-machine installation or main merge was performed. Previously recorded T24/browser evidence keeps its original limits.

## Git and current readiness

Initial local `jerome` was `fcc238e`. Fresh fetch found user-merged **PR #63 at `d409cfaa96584511905b8bdf8f0c33b17fdc61d0`**, whose tree exactly matches `fcc238e`; source `25e83ef` and its receipt are ancestors. The branch fast-forwarded with this work preserved. T26 is therefore **Done and integrated**; its earlier dated receipts remain historical. HOST-02 and new screenshot artifacts are **local/uncommitted and Not integrated**.

Teammates add the selector to their own private files after obtaining this change and use DEV to verify the target. Jerome reviews the diff and screenshots; publication requires a separate request. Alex/everyone continue T27 while Kenneth/Ellyssa continue T25. Later packaging includes these screenshots after the existing T30 prerequisites are satisfied.
