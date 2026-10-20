# Ralph T17 per-unit returns and overdue

- **Owner:** Ralph Andre F. Giga (@dreygigz), branch `ralph`, with Codex implementation/testing/documentation assistance. Earlier member implementations and contributor credit are preserved.
- **Date:** October 20, 2026, Asia/Manila (UTC+08:00).
- **Outcome:** T17 Done locally, **uncommitted and not integrated into main**. Shared T27/T28 are In progress for this member's actual technical/session evidence only. T20 remains Not started.
- **Review baseline:** `ralph` HEAD and fetched `origin/main` are `744bc3995f310fe365d7e00d8b187d765df326a8`. The checkout was clean before this work. No commit, push, PR, merge or teammate notification was performed.

## Prerequisites and integration correction

The previous current-state documents still described T15 as awaiting integration. `git fetch origin` and actual history established that [PR #42](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/42) merged at `744bc39` on October 20, 2026, 16:21:01 Asia/Manila. T15 source `74924dd09e950d491f9ab9b3780220b03a395851`, published tip `1b8c2e4` and T16 corrections `d68d7f7` are ancestors of fetched main. `git diff 1b8c2e4 744bc39` is empty: the merge preserves the published source tree. Both T17 prerequisites were therefore integrated before implementation; no local-batch exception was used.

The T15/T16 implementations and earlier [implementation](t15-release-due-date-revision-and-borrowing-slip-10-20-2026.md), [publication](t15-documentation-review-publication-and-t17-readiness-10-20-2026.md) and [maintenance](t16-maintenance-integrity-and-conflict-fixes-10-19-2026.md) snapshots remain preserved. Current readiness and integration records were reconciled without altering those historical files.

## Implemented behavior and interfaces

| Source | Delivered interface / behavior |
| --- | --- |
| [return_services.py](../borrowing/return_services.py) | `return_units(actor_id, loan_id, rows)` receives immutable `ReturnInput(loan_unit_id, returned_condition, notes, maintenance_problem)` values. It validates every input, checks active ADMIN authority inside the transaction and uses shared borrower/request/loan/unit locks followed by allocation/LoanUnit locks. Returns reject duplicate, foreign, ended, inconsistent or non-Issued units. Server timestamps cannot precede issue/release. |
| Same service | GOOD/FAIR returns end their allocation and become Available with the returned condition. DAMAGED returns become Maintenance/Damaged and create exactly matching ReturnRecord/MaintenanceRecord relationships. Each return and maintenance opening is audited inside the same atomic transaction. A failure rolls back the complete selection. |
| Same service | Outstanding units keep the request Partially returned and the loan open. The final return sets Returned and `closed_at`. Existing issued equipment remains recoverable after borrower deactivation or catalog archival; the receiving administrator must be active. T16 manual maintenance services are unchanged. |
| [return_forms.py](../borrowing/return_forms.py), [return_views.py](../borrowing/return_views.py), [manage_urls.py](../borrowing/manage_urls.py) | `borrowing_manage:return-create`, GET/POST `/manage/loans/<loan_id>/returns/new/`. Native `returns` formset with a selection checkbox, loan-scoped unit choices, condition/notes/problem, whole-formset validation and a confirmation submit. GET/Cancel never write; success redirects to loan detail, input errors return 200, workflow conflicts 409, unauthorized access 403/sign-in redirect and wrong methods 405. |
| [queries.py](../borrowing/queries.py) | `with_loan_progress(loans, today)` derives issued/returned/outstanding counts, `is_active`, `is_overdue` and calendar `overdue_days`. Call before adding other to-many joins that could multiply counts. Existing administrator/owner loan queries consume it. No stored overdue state or read-side writes. |
| [Return form](../templates/borrowing/manage/return_form.html), management [detail](../templates/borrowing/manage/loan_detail.html)/[list](../templates/borrowing/manage/loan_list.html), portal [detail](../templates/accounts/portal/loan_detail.html)/[list](../templates/accounts/portal/loan_list.html) | Existing role shells/components, responsive two-column return fields, explicit confirmation/errors, unit progress and overdue labels. Closed loans lose the return action. Borrower pages retain ownership scoping and omit return notes/maintenance details. |
| [Tests](../borrowing/tests/test_returns.py), [concurrency tests](../borrowing/tests/test_return_concurrency.py) | Real approval/release-to-return integration, active-role/CSRF/ownership checks, partial/final/damaged transitions, inventory reconciliation/repair, foreign/duplicate/stale rejection, real audit-constraint rollback, overdue boundaries and observed overlapping duplicate/disjoint returns on separate PostgreSQL connections. |

No models, migrations, dependencies, generated admin, API client or live business records were added or changed. Canonical HTTP/architecture/schema descriptions, README/DEV setup/readiness, the folder guide, backlog and current handoff were updated for the delivered interfaces and verified integration state. [Module 16](../docs/manual-test-guide.md#module-16--per-unit-returns-and-overdue-t17) supplies concrete inputs, expected results and actual execution evidence; [Module 15](../docs/manual-test-guide.md#module-15--release-due-date-revision-and-borrowing-slip-t15) now identifies its main integration.

## Verification performed

| Command / check | Actual result |
| --- | --- |
| `python manage.py test borrowing.tests.test_returns borrowing.tests.test_return_concurrency --noinput` | **21 passed in 6.283s** on PostgreSQL. Both race tests observe lock waits on three distinct backend connections; only expected domain conflicts count as the losing outcome. |
| `python manage.py test --noinput` | **294 passed in 109.763s** on the final source, including all previous borrowing/maintenance/access regressions. An earlier full run also passed 294 in 92.808s. The final rerun covers related-record loading without repeated request-item queries while keeping locks limited to allocation rows. |
| Final layout follow-up: `python manage.py test borrowing.tests.test_returns.ReturnHttpTests --noinput` | **5 passed in 4.723s** after the final template layout refinement; these also pass within the subsequent final full-suite run. |
| Chrome 155.0.8059.84 via existing local Playwright Core | Passed at 1440/390/320px: labels, page bounds, keyboard focus, Cancel without writes, blank damaged-problem error, Fair partial return, damaged final return, closure, stale URL 409 and owner request/loan privacy. Passed again after the final layout refinement. Desktop/compact screenshots inspected. No unexpected console or JavaScript errors. |
| `npm.cmd run build` | Passed; all nine fixed theme text-role contrast pairs passed. Rebuilt again after final template layout. |
| `npm.cmd run format:check` | Passed. |
| `npm.cmd audit` | Passed with **0 vulnerabilities** after the sandbox-blocked registry request was rerun with approved network access. |
| `python manage.py check --database default` | Passed, no issues. |
| `python manage.py makemigrations --check --dry-run --noinput` | Passed, no changes detected. |
| `python manage.py migrate --check` | Passed, no unapplied migrations. |
| `ruff check .` | Passed. |
| `ruff format --check .` | Existing failure in a Python code block of untouched `handoffs/borrower-portal-ui-improvements-10-20-2026.md`. Changed Python files pass formatting. |
| `djlint templates --check` | Existing formatting failure in untouched `templates/inventory/portal/equipment_list.html`; checked 77 templates. Changed templates pass. |
| `python -m pip check` | Passed, no broken requirements. |
| Documentation / Git review | **708 local links/anchors across 11 Markdown files pass**. Current-state/integration consistency, task/status/owner checks and `git diff --check` pass. No source requirement/member record or archived handoff was modified. |

The first pre-build regression run hit missing compiled `workspace-navigation.js`; building the existing assets resolved it. A first T17 HTTP assertion expected a redirect for an inactive session; the established middleware correctly returns 403 and terminates that session. The assertion was corrected to that contract and both subsequent focused/full runs passed. Neither was an application workflow defect.

The read-only local database check found **0 loans / 0 outstanding loan units**, with limits **7 days / 3 units per item**, on October 20, 2026. Browser checks used only `test_campus_ralph_t17_browser`, with fictional assets `TEST-CAM-001` and `T17-CAM-002`. That database and temporary session-token file were removed after each run; the development database received no business-data writes. Local screenshots/helper scripts remain only under ignored `output/` and are not deliverable dependencies.

## Ralph's T27 technical contribution

This is the implemented technical portion of the shared professional-judgment task; Alex retains security/privacy coordination. It records choices and available evidence without claiming the team's policy/legal review is complete.

| Stakeholder / duty | Implemented decision and evidence | Remaining decision / accountable owner |
| --- | --- | --- |
| Borrower confidentiality and fair handling | Return notes and maintenance problems stay out of borrower HTML; owner-scoped request/loan lookup returns 404 for another borrower. The T17 HTTP tests and isolated browser checks verify these boundaries. Overdue days follow the same campus-calendar rule for all borrowers and disappear on final return; no fine or payment flow is added. | Ralph reviews the code and explains the rule; Alex coordinates review of actual institutional requirements and privacy notices before real-data use. No approved notice or retention period was supplied in this session. |
| Administrator accountability and reliable equipment records | Active ADMIN checks apply at the route and inside the return transaction. Actor/time come from the server; each unit return and damaged maintenance opening has an audit target. Whole-operation rollback and duplicate/disjoint-return races protect stock/history accuracy. Existing equipment remains returnable after borrower deactivation, without reopening borrowing privileges. | Ralph owns return correctness and defect follow-up; administrators must avoid entering unnecessary personal information in free-text observations. The team must agree operational access and retention rules before using real identities. |
| Accessibility and public welfare | Shared light-mode shell, labeled controls, visible state/error text, keyboard focus and three viewport widths were checked. Partial returns keep unreceived equipment outstanding rather than incorrectly releasing stock. | Ralph's T20 work requires integrated T17/T18/T19; complete screen-reader and real-user evaluation remain unrun. These smoke checks do not complete T23. |
| Intellectual property, AI assistance and conflicts of interest | Existing member source/credit, MIT terms and third-party notices were preserved. Codex assistance is identified in this handoff; no original requirement/member files were rewritten. No publication or teammate message occurred, and Jerome's integration responsibility remains distinct from team authorship. See [CONTRIBUTING](../CONTRIBUTING.md), [conduct](../CODE_OF_CONDUCT.md) and [license](../LICENSE). | Ralph must review, understand and defend the contribution. Actual BulSU AI Policy/instructor disclosure requirements and permission must be obtained and checked by the team; no policy text or approval was supplied here. |
| Safe development evidence | Read-only development inspection plus separate fictional test databases avoided business-data writes. Temporary browser database and session-token file were removed; private environment values were neither printed nor committed. | Alex coordinates current primary legal/code/policy sources and applicable safeguards; the team must supply genuine consent-appropriate feedback and define data handling for any real deployment. No legal compliance certification is claimed. |

T27 remains In progress. Missing work includes identifying actual applicable codes/laws/campus policies with current sources, team-reviewed decisions on notices/access/retention, and member review/defense. These institutional and team decisions were not invented. This record is available for Alex's review; no external message was sent.

## Ralph's T28 contribution record and remaining work

Ralph supplied the assigned-member implementation request and left publication unauthorized. This session selected T17 after verifying dependency/main evidence, implemented and tested it, monitored failures against actual contracts, updated the manual/readiness documents and prepared this review handoff. This is evidence of Ralph's current work with Codex assistance. It does **not** establish a meeting, peer feedback, rotated team leadership, another member's participation or a feedback-driven enhancement. T28 stays In progress until the team supplies the remaining genuine collaboration/individual-performance evidence.

Known limits: Firefox/Safari, full screen-reader evaluation, live populated loan examples, complete maintenance browser lifecycle, T20-wide accessibility, real user acceptance, performance and backup/restore were not run. The two pre-existing formatting findings and older T10/T11/T12/T13 cleanup/manual follow-ups remain recorded; no unrelated fixes were folded into T17. Diagram conversion remains on standby.

Ralph reviews these local changes. Any commit/push/PR needs a separate request; Jerome handles authorized main integration. After **accepted T17 main integration**, Alex can implement **T18** and Jerome can implement **T21**. Alex's **T19** then requires integrated T18 as well as T17. Ralph's **T20** requires accepted integrated **T10/T12/T17/T18/T19**: T10/T12 are satisfied, T17 is local only and T18/T19 are Not started. T22/T23/T25/T29/T30/T31 retain their own gates. No further Ralph feature is ready in this session.
