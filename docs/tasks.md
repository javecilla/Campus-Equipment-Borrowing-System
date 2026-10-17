# Project Roadmap and Backlog

## Status and scheduling

This backlog tracks planned and accepted work. DOC-01 through DOC-08 track documentation/standards/handoffs, the execution plan, folder architecture, team agent prompts, and shared HTTP/styling/formatting conventions; MCP-01 and MCP-02 track separately authorized database tooling/developer preparation; UI-01 tracks the selected frontend setup; GIT-01 tracks repository publication and the team branch workflow. [PLAN.md](../PLAN.md) maps delivery order and member readiness gates; this file owns task status and verified task/integration evidence. The user authorized Jerome's implementation and explicitly allowed T01–T03 as one local, uncommitted batch before main integration; other dependencies retain their gates. Status values are **Not started**, **In progress**, and **Done**. Record blockers in evidence rather than inventing completion. Task IDs remain stable so a member can request, for example, "Implement T06."

Requirements come from [Project-Requirements.txt](Project-Requirements.txt). The source member schedule in [Project-Members.txt](Project-Members.txt) targets **Saturday, October 24, 2026**; the instructor still controls the official submission date. The planned starts below are dependencies, not evidence that work has begun or been merged.

| Planned start | Owner | Dependency / handover |
| --- | --- | --- |
| October 15 | Jerome | Schema targeted for shared integration by end of October 16; shared helpers/locking follow |
| October 16 | Alex | Shared tables available; authentication, roles, admin/active checks |
| October 17 | Kenneth | Login exists; catalog, physical units, maintenance |
| October 17 | Ellyssa | Login and units exist; portal account/profile/browsing and layout |
| October 17 | Ralph | Units and Ellyssa's layout available; request form, history, cancellation |
| October 19 | Margareth | Users can submit requests; approval, release, slips, returns |
| October 21 | Alex | Issued loans exist; real dashboard/charts/reports |
| October 22 | Everyone | Integrated workflows; cross-testing, fixes, guides, practice |

Calendar starts do not override incomplete dependencies. Maintain the approximately 75% admin-side emphasis described in the PRD. Every member contributes code, documentation, testing, and an identifiable presentation segment; ownership below identifies the coordinator, not an exemption for others. Feature owners follow the source assignments; coordinators for cross-team/evidence tasks are proposed for team review.

## Documentation baseline

| ID | Priority | Owner | Deliverable and acceptance | Status | Evidence / next step |
| --- | --- | --- | --- | --- | --- |
| DOC-01 | P0 | Team; AI documentation assistance | README without setup instructions; PRD/SRS; architecture/schema/HTTP contracts; AGENTS/environment template; backlog; current handoff and instruction-only handoff skill | Done | Documentation created; 63 relative links and file integrity checked; bundled skill validator passed using existing cached tooling; proposed choices await team review |
| DOC-02 | P1 | AI agent; member not specified | Canonical MTV/coding standards, reusable Django skill, contribution/conduct guides, and the user-selected MIT license with project-contributor attribution | Done | Guide and skill linked from AGENTS/README/DEV; bundled skill validator passed; document links, scope, and credential scan checked; no application implementation |
| DOC-03 | P1 | AI agent; member not specified | Dated developer/AI handoff archive, initial setup snapshot, and matching folder/filename instructions in the handoff skill and project entry points | Done | Both skills validated; 159 relative links and archive naming checked; Git excludes private env and keeps shared files trackable; initial snapshot linked from HANDOFF.md |
| DOC-04 | P1 | Jerome; Codex documentation assistance | Central full-system PLAN.md with dependency/member gates, evidence-based next-task selection, distinct acceptance/main-integration records, and routing through existing agent skills and entry points | Done | All 31 application task IDs covered; stage dependencies reviewed against the backlog; relative links/heading anchors and dated naming checked; both changed skills validated; application task rows and source files unchanged; shared credential scan passed. Commit c806458 and publication follow-up 636f832 were integrated into main by [PR #1](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/1), merge 96f383b, verified through fetched main history and ancestry. See the [publication handoff](../handoffs/central-system-plan-publication-10-16-2026.md) for the earlier publication state; implementation remains unauthorized |
| DOC-05 | P1 | Jerome; Codex documentation assistance | Dedicated docs/project-folder-architecture.md showing existing/planned paths, feature file locations, page/template examples, and links from project entry points | Done | All 71 annotated paths and route examples checked; links/fences/credential scan passed. Integrated by [PR #3](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/3), merge d122518, preserving commit f1fefbb and Codex credit. See the [folder architecture handoff](../handoffs/project-folder-architecture-guide-10-16-2026.md) and [publication evidence](../handoffs/jerome-foundation-publication-10-16-2026.md) |
| DOC-06 | P1 | Jerome; Codex documentation assistance | Reusable implementation prompts for all six members, linked from PLAN/README/DEV, that select assigned ready work and require verification/handoff while preserving integration and Git authorization gates | Done | Six identities/branches checked against source assignments; relative links/anchors, fences/details, credential scan, and whitespace checks pass. Application task/evidence rows and source files preserved. Committed/pushed on jerome as 8668ff8, Not integrated; see the [prompt guide handoff](../handoffs/team-agent-implementation-prompts-10-16-2026.md) |
| DOC-07 | P1 | Jerome; Codex assistance | Canonical endpoint/Axios/Tailwind/naming conventions, language-specific formatter configs/commands, README package justifications, and complete locked dependency/license inventory | Done | Prettier/djLint/Ruff and real Django template semantics checks pass; locked npm install/build/audit and all 23 PostgreSQL tests pass; complete 17-Python/140-npm inventory, links, credentials, and source/task preservation checked. Committed on jerome, Not integrated; see [standards handoff](../handoffs/shared-http-styling-and-formatting-standards-10-16-2026.md) |
| DOC-08 | P1 | Jerome; Codex documentation assistance | Compact README Part 6 evidence index with direct diagram links, honest existing/pending coverage, submission reminders, and a canonical folder-guide link replacing the duplicate tree | Done | Source coverage and documentation checks pass; no application/evidence task marked complete. Committed on jerome, Not integrated; see [README handoff](../handoffs/readme-part-six-evidence-index-10-16-2026.md); see [publication handoff](../handoffs/readme-evidence-publication-10-16-2026.md) for the authorized commit/push |
| GIT-01 | P1 | Jerome; Codex assistance | Connect the private GitHub repository, publish the setup through jerome with Codex co-authorship, initialize main/member branches, protect main for repository-owner integration, and document the member workflow | Done | Baseline 04ecb37 committed on jerome with Codex credit and pushed to all seven branches; Git/REST verified heads, private visibility, default/protected main, and effective owner-only rules. Current access check: javecilla plus corkenneth, ellieebeann, and dreygigz have write access; AlexCayanan and raifun have pending write invitations. GIT-02 tracks the requested reviewer-routing adjustment |
| GIT-02 | P1 | Jerome; Codex documentation assistance | Prepare CODEOWNERS with only javecilla as the default reviewer, align developer guidance, and explain base-branch activation and self-review restrictions while preserving shared team authorship | Done | Guidance and checks passed; commits 40e35cc/0bd14a1 integrated into main by [PR #2](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/2), merge f4e9b6d, with Codex co-author credit and original commits preserved. GitHub confirms merged/closed, main rule * @javecilla, zero CODEOWNERS errors, and unchanged active owner-only main rules. See the [integration handoff](../handoffs/owner-review-routing-main-integration-10-16-2026.md) |

## Shared frontend tooling

| ID | Priority | Owner | Depends on | Deliverable and acceptance | Status | Evidence / next step |
| --- | --- | --- | --- | --- | --- | --- |
| UI-01 | P1 | Jerome; Codex assistance | Integrated T01; explicit frontend setup request | Declare/justify Tailwind and Axios; lock npm dependencies; build/watch local CSS and browser modules; shared template asset shell; Django-compatible CSRF client; document setup and required patterns without implementing another member's pages | Done | npm ci/build/audit pass with zero findings; watcher rebuilds, real browser CSRF/error/font/Tailwind smoke, static discovery/bytes, license notice, and 23 PostgreSQL tests verified. Committed on jerome, Not integrated; feature statuses unchanged. See [frontend handoff](../handoffs/tailwind-axios-frontend-foundation-10-16-2026.md). [Editor follow-up](../handoffs/tailwind-css-editor-language-mode-10-16-2026.md): scoped Tailwind language mode/recommendation added; CSS build/format checks pass; live IDE reload verification pending; [favicon/metadata follow-up](../handoffs/shared-favicon-and-page-metadata-10-16-2026.md) verifies shared head metadata, manifest paths, and exact static responses; [global base styles](../handoffs/global-base-styles-10-16-2026.md) adds requested scrolling/selection/reduced-motion/scrollbar CSS with passing build, format, and browser computed-style checks |
| UI-02 | P2 | Jerome; Codex assistance | Explicit preview request; local UI-01 assets | `/test` with shared shell, Tailwind samples, real font-load status, no application data, and debug-only access | Done | Browser verifies local DM Sans/Poppins loading, computed Tailwind styles and desktop/mobile grids without overflow; GET/HEAD 200, POST 405, DEBUG=False 404, no page queries; build/format/Django checks and 23 foundation tests pass. Committed on jerome, Not integrated; see [preview handoff](../handoffs/tailwind-font-preview-page-10-16-2026.md); [index follow-up](../handoffs/development-index-navigation-10-16-2026.md) adds debug-only root navigation and return link, verified in Chrome with all 23 tests passing; [updated startup screenshot](../handoffs/updated-startup-screenshot-10-16-2026.md) documents the current index below the original screenshot in DEV.md |
| UI-03 | P2 | Jerome; Codex assistance | Explicit shared-source rename request; existing UI-01/UI-02 work | Rename source directory to static/, update active configuration/docs, preserve file contents and historical handoffs, and verify build/watch/discovery/collection/browser behavior | Done | All 109 moved files and 21 historical handoffs unchanged; build/watch/format/Django/migration checks and 23 tests pass; 113 files discovered, served, and collected with exact bytes; browser fonts/navigation verified. Committed on jerome, Not integrated; see [static directory handoff](../handoffs/static-directory-rename-10-16-2026.md); see [publication handoff](../handoffs/static-directory-publication-10-16-2026.md) for the authorized member-branch commit/push |

## Database tooling and developer preparation

| ID | Priority | Owner | Deliverable and acceptance | Status | Evidence / next step |
| --- | --- | --- | --- | --- | --- |
| MCP-01 | P1 | AI agent; member not specified | Configure a private local Codex PostgreSQL MCP connection to the user-created campus_equipment database and verify read-only querying without changing tables/data | Done | DBHub 1.5.0 initialize/tools-list/SQL calls passed; PostgreSQL 17.5, transaction_read_only on, public table count 0; restart/reload MCP in the client to expose its tools in a new session; details in HANDOFF.md |
| MCP-02 | P1 | AI agent; member not specified | Share a credential-free MCP JSON/policy, document teammate setup in DEV.md, populate the current workstation's ignored .env.local, and verify the shared launch against local PostgreSQL | Done | Shared JSON passed initialize/tools-list/SQL checks with read_only on; private Codex registration matches shared arguments; local DB fields match the MCP URL; credentials absent from shareable files; see DEV.md and HANDOFF.md |

## Foundation and access

| ID | Priority | Owner | Depends on | Deliverable and acceptance | Status |
| --- | --- | --- | --- | --- | --- |
| T01 | P0 | Jerome | DOC-01; explicit implementation request | Review proposed stack/design choices; scaffold only the agreed Django modules; declare compatible tested dependencies, environment parsing, and private-file ignore rules; missing/invalid configuration fails clearly | Done |
| T02 | P0 | Jerome | T01 | Implement custom User before initial migration and all shared schema/constraints from db_design; migrations run on a fresh PostgreSQL database | Done |
| T03 | P0 | Jerome | T02 | Shared workflow/locking convention, audit writer, settings singleton, date/limit validation; no generic status bypass; prove critical database constraints against real PostgreSQL | Done |
| T04 | P0 | Alex | T02 | Shared login/logout, exactly two roles, role redirects, active/admin/ownership enforcement, authorized admin-creation command; direct forged requests and inactive sessions denied | Done |
| T05 | P1 | Alex | T04, T03 | Custom basic-user account search/detail/history and separate activation/deactivation actions; audit changes and preserve transactions | Not started |
| T06 | P1 | Jerome | T03, T04 | Custom validated settings form and searchable admin-only audit page; settings affect newly submitted requests and audit is not user-accessible | Not started |

## Inventory and borrower portal

| ID | Priority | Owner | Depends on | Deliverable and acceptance | Status |
| --- | --- | --- | --- | --- | --- |
| T07 | P0 | Kenneth | T03, T04 | Category/catalog custom list/detail/create/update/archive; server validation, search/pagination, protected transactional references | Not started |
| T08 | P0 | Kenneth | T07 | Physical-unit registration/update/history and category/item/status filters; unique asset codes, valid conditions, derived inventory totals; workflow status cannot be edited directly | Not started |
| T09 | P1 | Ellyssa | T04 | Registration/profile using Alex's auth contract; portal base template/components; reject self-promotion and protected-field edits | Not started |
| T10 | P1 | Ellyssa | T08, T09 | Active catalog search/detail with serviceable/available quantities; hide private and maintenance data; verify empty/mobile/keyboard states | Not started |
| T11 | P0 | Ralph | T03, T08, T09 | Submit 1–3 distinct item rows atomically with purpose/date/quantity validation and snapshotted limits; an invalid third row leaves no request/items | Not started |
| T12 | P1 | Ralph | T11 | Own request/loan lists and details, due dates and issued/returned units; owner-only Pending/Approved cancellation frees reservations atomically; cross-user/after-issue cancellation denied | Not started |

## Administrator operations

| ID | Priority | Owner | Depends on | Deliverable and acceptance | Status |
| --- | --- | --- | --- | --- | --- |
| T13 | P0 | Margareth | T03, T11 | Searchable/filterable/paginated queue, request review, approval/rejection with reasons; exact atomic reservation and audit; use shared locking helpers | Not started |
| T14 | P0 | Jerome with Margareth | T13 | PostgreSQL competing-approval integration scenario with separate connections; last unit has exactly one successful approval and one conflict, no partial allocations | Not started |
| T15 | P0 | Margareth | T13, T14 | Audited pre-issue due-date revision, release once, Loan/LoanUnits, printable slip; reject expired, rejected, cancelled, already issued, or incomplete requests | Not started |
| T16 | P0 | Kenneth | T08, T03 | Maintenance open/close, repair/retirement, history and inventory reconciliation; reject Reserved/Issued units and duplicate open maintenance | Not started |
| T17 | P0 | Margareth with Kenneth | T15, T16 | Per-unit/partial returns, duplicate prevention, damaged-return maintenance in one transaction, final loan closure, derived overdue behavior and audit | Not started |
| T18 | P1 | Alex | T15, T17 | Four live dashboard cards, monthly issued-loan chart, category issued-unit chart; database changes update all values; no static demonstration data | Not started |
| T19 | P1 | Alex | T17, T18 | Date-filtered loan/overdue reports and CSV with matching totals and spreadsheet-safe cells; verify joins/computed outstanding quantities and all export access checks | Not started |
| T20 | P1 | Ralph with Ellyssa and admin feature owners | T10, T12, T17, T18, T19 | Integrate role layouts/navigation, reusable tables/forms/messages, confirmations, status text, responsive behavior, stable test IDs, useful errors/empty states | Not started |

## Validation and demonstration data

| ID | Priority | Owner | Depends on | Deliverable and acceptance | Status |
| --- | --- | --- | --- | --- | --- |
| T21 | P0 | Jerome; all owners verify | T17 | Controlled seed command/fixture meets the dataset below, uses fictional people and coherent history, and preserves all constraints | Not started |
| T22 | P0 | Everyone; Alex coordinates security, Jerome concurrency | T14, T19, T20, T21 | Execute SRS acceptance scenarios on PostgreSQL; record real commands/results, access tests, rollback/concurrency/returns/report evidence, bugs and resolutions | Not started |
| T23 | P1 | Everyone; Ellyssa and Ralph coordinate usability | T20, T21 | Conduct actual basic-user/admin acceptance sessions, record consent-appropriate findings, resolve issues, and implement/verify at least one feedback-driven enhancement within scope | Not started |
| T24 | P1 | Jerome with feature owners | T22 | Measure proposed performance targets on recorded hardware/dataset, inspect slow queries, demonstrate backup/restore, document limitations and maintenance | Not started |

### Required fictional demonstration dataset

| Record | Minimum |
| --- | --- |
| Categories | 3 |
| Catalog items | 6 |
| Physical units | 18 |
| Admin accounts | 1 |
| Basic-user accounts | 8 |
| Borrowing requests | 20 |
| Issued loans, including any subsequently returned | 8 |
| Maintenance records | 4 |

Include rejected and cancelled requests, an Approved cancellation that releases units, partial returns, damaged returns, overdue outstanding loans, repaired units, and retired units. Use historical dates consistent with the current demonstration date. Supply safe demonstration credentials for one admin and two basic users only through the instructor-designated channel; never commit them or real campus identities.

## Course evidence and delivery

Do not fabricate meetings, interviews, leadership, tests, compliance, or individual contributions. Create each evidence document only when its real records exist, with one canonical file per topic and references to source/tests/records. The planned evidence below does not mean the files exist today.

| ID | Priority | Owner | Depends on | Deliverable and acceptance | Status |
| --- | --- | --- | --- | --- | --- |
| T25 | P1 | Jerome coordinates; everyone reviews | T22, T23, T24 | System evidence: link requirements to source/tests, update MTV/database/workflow diagrams to match implementation, include resolved issues, constraints, limitations, and verified enhancements; use existing design files rather than duplicate them | Not started |
| T26 | P1 | Alex and Jerome coordinate; everyone contributes | DOC-01; complete before submission | User-needs evidence: validate personas/options recommendation; justify chosen tools and reusable Django/ORM components; evaluate one emerging technology for effectiveness, compatibility, security, and user needs with an adopt/defer recommendation | Not started |
| T27 | P1 | Everyone; Alex coordinates security/privacy | Before using real data and before submission | Professional-judgment evidence: stakeholders/duties, actual applicable codes/laws/campus policies, privacy/retention, intellectual property, accessibility, bias, conflicts of interest, public welfare, risks, safeguards, accountability, and AI/reuse disclosure under the BulSU AI Policy and instructor instructions; obtain current sources and avoid unsupported compliance claims | Not started |
| T28 | P1 | Everyone; rotate leadership | Every work period | Evidence of task allocation, collaboration, individual code/docs/tests, peer feedback, goal-setting/task assignment/coordination/progress monitoring by every member, and performance improvements; record actual dates and contributions | Not started |
| T29 | P1 | Ellyssa/Ralph for user guide; Margareth/Kenneth for admin guide; Jerome/Alex for technical guide | T22, T24; implementation authorized | Write verified basic-user/admin guides, maintenance/configuration guidance, tested dependency versions, and migration/seed/start steps; extend the existing DEV.md workstation/MCP guide with verified application setup after implementation | Not started |
| T30 | P0 | Everyone | T22, T23, T25–T29 | Assemble IT401W_ProjectA_Section_Group.zip with source, migrations, requirements, README, seed, and evidence; exclude virtual environments, caches, secrets, and private data; verify a clean-machine local demonstration | Not started |
| T31 | P1 | Everyone | T30 | Rehearse 12-minute demo + 3-minute Q&A for Week 17; demonstrate both roles, validation, access controls, concurrency, operations, and reports; each member has an identifiable segment and records feedback/agreed actions | Not started |

## Completion rules

P0 means foundational correctness or required delivery; P1 means remaining required functionality/evidence, not optional work. Dependencies determine execution order. Additional enhancements follow required functionality and must not displace the course brief.

## Verified task evidence

Record actual accepted task evidence here, linking its dated handoff rather than copying test output. Replace the no-evidence row when the first application task is verified; add/update only affected task records. A Done task on a member branch is not an integrated prerequisite. Record main integration separately with the actual merged PR/main revision and relevant check result; use Not integrated while local/uncommitted or awaiting review. See [PLAN.md](../PLAN.md#complete-work-and-hand-it-to-the-next-member) for the handoff gate. Documentation completion evidence remains in the documentation rows above.

| Task | Checked result and work handoff | Branch / commit / PR | Main integration evidence | Next consumer |
| --- | --- | --- | --- | --- |
| T01 | Agreed Python/Django/PostgreSQL scaffold, pinned compatible dependencies, strict private configuration, WSGI/ASGI boot, and README/DEV setup steps; seven configuration/bootstrap tests plus Ruff pass. See [foundation handoff](../handoffs/jerome-django-foundation-10-16-2026.md). [Setup/assets follow-up](../handoffs/team-dev-guide-and-local-fonts-10-16-2026.md) simplifies the guide, embeds the supplied screenshot, records the folder tree, and verifies shared local fonts through Django staticfiles | jerome; f1fefbb; [PR #3](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/3) | Integrated into main at d122518; GitHub merge and fetched ancestry verified; publication checks pass, no CI configured. See [publication handoff](../handoffs/jerome-foundation-publication-10-16-2026.md) | T02 completed and integrated; teammates sync main for the foundation |
| T02 | All 14 shared models and constraints; custom user selected before migration; fresh PostgreSQL 17.5 schema migrated successfully; all 22 migrations applied; constraint tests pass. See [foundation handoff](../handoffs/jerome-django-foundation-10-16-2026.md) | jerome; f1fefbb; [PR #3](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/3) | Integrated into main at d122518; full 23-test PostgreSQL suite passed before publication; original implementation tree preserved | Alex / T04 is locally complete against this schema; dependent consumers still need T04 main integration evidence |
| T03 | Transaction-only shared locks, audit writer, initialized singleton, audited settings service, immutable limit snapshots, and pure date/item validation. Full 23-test suite passes against PostgreSQL, including real audit failure rollback and separate-connection lock behavior. See [foundation handoff](../handoffs/jerome-django-foundation-10-16-2026.md) | jerome; f1fefbb; [PR #3](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/3) | Integrated into main at d122518; GitHub merge/fetched ancestry verified; publication checks pass | T04 is locally accepted but not integrated; T06/T07 retain that gate. T14 approval race is not implemented or claimed |
| T04 | Shared home/login/logout routes; stored-role redirects; active-session middleware; reusable active/admin/basic-user and owner-scoped 404 helpers; CLI-only atomic ADMIN/Profile creation; custom login/403 and protected role destinations. Full 35-test PostgreSQL suite passes, including 12 authentication/access/command tests. A separate follow-up restores the isolated candidate's extension-scoped LF policy; see the [T04 handoff](../handoffs/alex-t04-authentication-and-access-10-17-2026.md) and [scope-correction handoff](../handoffs/t04-gitattributes-scope-correction-10-17-2026.md) | alex; `7ae5e87`; [PR #9](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/9); separate correction commit on `alex` | Integrated into main at `cb96319`; fetched ancestry and zero tree delta from `7ae5e87` verified. The LF-scope correction is not integrated and requires a new PR | T04's integration gate is satisfied; dependent owners sync and recheck main before authorized work. T05 remains Not started in this follow-up |

On completion or transfer, use the [project-handoff skill](../.agents/skills/project-handoff/SKILL.md). Save the dated work snapshot in `handoffs/{title-of-work}-{MM-DD-YYYY}.md` and link it from [HANDOFF.md](../HANDOFF.md), which remains the current-state summary/index. This file is the canonical task status list. Mark feature work Done only after its acceptance behavior is verified, not after its documentation is written.
