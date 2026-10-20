# Administrator Dashboard Chart.js Improvement

## Work, authorization and publication

- **Date/time zone:** October 20, 2026, Asia/Manila.
- **Owner:** Jerome Avecilla with Codex assistance; Alex Enrico Cayanan's original T18 implementation credit is preserved.
- **Scope:** Publish the completed T18 integration-review documentation, then implement the explicitly requested dashboard improvement with Chart.js. UI-11 records this follow-up without reopening accepted T18 or starting T19/T20.
- **Publication completed first:** `55274321fc08cac147bb7293b2fd0a523c748088`, `docs: verify T18 integration and T19 readiness`, pushed normally to `origin/jerome`. The commit contains `Co-authored-by: Codex <codex@openai.com>`; local/remote equality was verified after push and again with `ls-remote`.
- **Subsequent user integration:** PR #47 merged the documentation at `0e05ed6ea7bbd8f2994cd4e793ca2717a6c534ab`. Fetched main preserves `5527432` and has exactly the same tree. This agent did not create that PR or merge it. Local `jerome` HEAD remains `5527432`; the UI-11 working diff is preserved.
- **UI-11 outcome:** Done locally, **uncommitted and not integrated**. No UI-11 commit/push/PR/main merge, teammate message or diagram work was performed. T19 remains ready from integrated T17/T18; T20 still requires integrated T19.

## Result and useful scope

The dashboard keeps four live cards and exactly the two charts required by [Part 5/A7](../docs/Project-Requirements.txt) and [SRS A7/A7-CHART](../docs/SRS.md#functional-requirements):

- Monthly vertical columns count each issued Loan once. Months with no releases are present from the first stored release through the current campus month, so gaps remain visible. The page labels the date range and all-history total; long histories scroll within the chart region.
- Horizontal category bars compare issued LoanUnit occurrences, ranked highest first with alphabetical ties. Returned units and repeat issues remain counted. The axis names physical units issued; full category names and exact counts remain in tooltips and data tables. Many categories have a bounded vertical chart region.
- Both value axes start at zero with whole-number ticks. Exact-value tooltips respond to hover/tap and wrap long labels. Animation is disabled, including for reduced-motion users. Colors come from existing shared CSS roles and fonts; no unrelated palette, chart or trend metric was added.
- Card links use existing Available/Pending filters and issued-loan records. The loan list has no active/overdue filter; its links are labeled to inspect loan records/due dates rather than imply a new filtered view.
- The protected Django view still derives the campus date, queries real records and embeds data with `json_script`. Native disclosure tables remain usable by keyboard and with JavaScript disabled. Empty data produces honest messages rather than manufactured charts.

No model, migration, workflow service, authorization rule, report endpoint or live business record changed. The dashboard updates on page load; no automatic polling or realtime subscription was added.

## Files and dependencies

- [Query](../operations/queries.py): `monthly_issued_loans(today)` includes idle months; `dashboard_snapshot(today)` preserves card definitions and ranks category counts. [View](../operations/views.py) adds date and all-history presentation totals. [Tests](../operations/tests/test_dashboard.py) add one real-ORM history/ranking integration case and retain live-return/access/JSON coverage.
- [Template](../templates/operations/manage/dashboard.html) and [page module](../static/js/dashboard-charts.js): responsive cards, two canvas charts, scoped scrolling, table disclosures, exact tooltips and existing named action links. The module registers only needed Chart.js bar/scales/tooltip components through the existing esbuild build.
- [Manifest](../package.json)/[lock](../package-lock.json): runtime Chart.js **4.5.1**, indirect `@kurkle/color` **0.3.4**, both MIT. No Python package or global tool was installed. The dashboard module builds to approximately 151.3 kB minified before compression; other pages do not load it.
- Complete installed MIT notices are retained in [static/licenses/chartjs-MIT.txt](../static/licenses/chartjs-MIT.txt), included in normal static collection/submission. README rationale, the complete dependency inventory, setup/architecture/HTTP/folder guidance and [Module 17](../docs/manual-test-guide.md#module-17--live-administration-dashboard-t18) are updated. All 115 npm lock entries match the inventory.
- `npm install` initially pruned two existing bundled optional Tailwind WASI peer records, causing plain `npm ci` to reject a missing indirect dependency. Restored those exact existing records from the reviewed baseline; the final lock diff only adds Chart.js/color. A subsequent unmodified `npm ci` succeeds; no omit/legacy/force flags or dependency upgrades were used to bypass the failure.

## Verification

| Check | Actual result |
| --- | --- |
| Full PostgreSQL suite | **299 tests passed in 56.043s**; test database created/destroyed |
| Focused dashboard suite | Initial 5 passed in 0.419s; final post-build/render run 5 passed in 0.390s |
| Plain `npm.cmd ci` | Passed; installed 52 packages, audited 53 |
| `npm.cmd run build` | Passed; all nine contrast pairs meet 4.5:1; chart module generated |
| `npm.cmd run format:check` and `npm.cmd audit` | Passed; zero vulnerabilities |
| Ruff lint and changed-Python format | Passed; three changed Python files formatted |
| Changed dashboard djLint format | Passed; zero updates |
| Django database check / migration drift / applied migrations | Passed; no issues, new migrations or unapplied migrations |
| `python -m pip check` | Passed; no broken requirements |
| Documentation and dependency integrity | 11 changed Markdown files checked: 762 relative targets and 187 heading fragments resolve; code fences balanced. All 115 npm inventory entries match the lock, both complete installed MIT license texts are retained, and all original package lock records are unchanged |
| Diff/scope | `git --no-pager diff --check` passes. Original requirement/member files, Python pins, workflow/model/access code and skill files are unchanged; UI-11 stays uncommitted |
| Required repository-wide formatting | Same four unrelated existing findings: Ruff line endings in `accounts/views.py` and `inventory/tests/test_portal_equipment.py`, archived borrower-portal handoff Python example; djLint long tag in `templates/inventory/portal/equipment_list.html`. These files were not changed |

### Browser QA inventory and actual execution

Chromium **153.0.8010.12**, local isolated PostgreSQL database, October 20 Asia/Manila. The browser logged in through the real form using fictional disposable accounts. QA covered requested chart usefulness, implemented controls and intended delivery claims:

| Claim/control/state | Executed result |
| --- | --- |
| Exactly two meaningful charts, actual ORM counts | Populated fixture: cards 11/1/3/1; May–October 2026 loan counts 1/3/0/2/0/2; category counts 6/6/4 including returned units; totals 8 loans and 16 issued-unit occurrences |
| Readable zero-based counts, honest gaps/ranking | Desktop screenshots visually reviewed; integer ticks, zero month gaps and ranked horizontal bars match table values |
| Four card links | Clicked each; correct existing unit/request filters or loan-list URL reached, then returned to dashboard |
| Native table controls and keyboard | Monthly disclosure opened/closed with Enter; category disclosure opened/closed; full labels/counts match data. Horizontal chart scroller focused and scrolled by arrow keys |
| Desktop/compact layout | 1440px, 390px and 320px screenshots reviewed; document width matches viewport, charts stay inside their panels; compact chart history scroll is local |
| Long label / hover / tap | Exploratory case with `Classroom audio and presentation equipment`: full label/exact count shown; mobile tooltip wrapping inspected and corrected |
| JavaScript disabled | Both native disclosures expose exact tables; blank canvas regions remain hidden |
| Empty-state exploratory case | Separate empty-loan fixture shows real Available count 1, other cards 0, two useful empty messages and no canvases |
| Runtime failures | No JavaScript errors observed |

Screenshots are retained locally under ignored `output/playwright/`, including `chartjs-desktop-final.png`, compact chart/tooltip/scroll images, JavaScript-disabled and empty-state images. These are browser evidence artifacts, not committed source. Browser contexts and temporary servers were closed; the explicitly named disposable database was checked and removed. The development database was inspected only in a transaction verified `transaction_read_only = on`; its snapshot remains 11 Available, 2 Pending, 0 active/overdue, one October loan/category point.

Not run: Firefox/Safari, complete screen-reader review, many-category vertical scrolling, live transaction mutations in a browser, performance benchmarking, clean-machine setup or full-system acceptance. The real-service automated suite covers transaction-driven card/chart updates; browser checks do not claim those live mutations were executed.

## Documentation verification and next action

Link, scope, lock/license and diff verification passed as recorded above. Original requirements/member files and completed handoffs remain preserved. No skill metadata changed, so skill validation was not rerun. Remote HTTP link checks were not run. User reviews the UI-11 diff and preview; any later publication/main integration needs a separate explicit request. Alex can continue authorized T19 work from accepted integrated T18; this enhancement does not change that prerequisite. Diagram work remains on standby under the existing completion/go-signal gate.
