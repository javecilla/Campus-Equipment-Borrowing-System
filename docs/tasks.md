# Project Roadmap and Backlog

## Status and scheduling

This backlog plans future work. DOC-01 through DOC-04 track documentation/standards/handoffs and the execution plan; MCP-01 and MCP-02 track the separately authorized database tooling and developer preparation; GIT-01 tracks repository publication and the team branch workflow. [PLAN.md](../PLAN.md) maps delivery order and member readiness gates; this file owns task status and verified task/integration evidence. No application implementation is authorized yet. Status values are **Not started**, **In progress**, and **Done**. Record blockers in the evidence/next-step column rather than inventing completion. Task IDs remain stable so a member can request, for example, "Implement T06."

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
| DOC-04 | P1 | Jerome; Codex documentation assistance | Central full-system PLAN.md with dependency/member gates, evidence-based next-task selection, distinct acceptance/main-integration records, and routing through existing agent skills and entry points | Done | All 31 application task IDs covered; stage dependencies reviewed against the backlog; relative links/heading anchors and dated naming checked; both changed skills validated; application task rows and source files unchanged; shared credential scan passed. Commit c806458 pushed to jerome with Codex co-author credit and remote SHA verified; not integrated into main. See the [publication handoff](../handoffs/central-system-plan-publication-10-16-2026.md); implementation remains unauthorized |
| GIT-01 | P1 | Jerome; Codex assistance | Connect the private GitHub repository, publish the setup through jerome with Codex co-authorship, initialize main/member branches, protect main for repository-owner integration, and document the member workflow | Done | Baseline 04ecb37 committed on jerome with Codex credit and pushed to all seven branches; Git/REST verified heads, private visibility, default/protected main, and effective owner-only rules. DEV workflow, corrected CODEOWNERS, link/credential checks, and dated handoff complete. Jerome still needs to invite five teammates with write access; GitHub currently reports them as unknown code owners |

## Database tooling and developer preparation

| ID | Priority | Owner | Deliverable and acceptance | Status | Evidence / next step |
| --- | --- | --- | --- | --- | --- |
| MCP-01 | P1 | AI agent; member not specified | Configure a private local Codex PostgreSQL MCP connection to the user-created campus_equipment database and verify read-only querying without changing tables/data | Done | DBHub 1.5.0 initialize/tools-list/SQL calls passed; PostgreSQL 17.5, transaction_read_only on, public table count 0; restart/reload MCP in the client to expose its tools in a new session; details in HANDOFF.md |
| MCP-02 | P1 | AI agent; member not specified | Share a credential-free MCP JSON/policy, document teammate setup in DEV.md, populate the current workstation's ignored .env.local, and verify the shared launch against local PostgreSQL | Done | Shared JSON passed initialize/tools-list/SQL checks with read_only on; private Codex registration matches shared arguments; local DB fields match the MCP URL; credentials absent from shareable files; see DEV.md and HANDOFF.md |

## Foundation and access

| ID | Priority | Owner | Depends on | Deliverable and acceptance | Status |
| --- | --- | --- | --- | --- | --- |
| T01 | P0 | Jerome | DOC-01; explicit implementation request | Review proposed stack/design choices; scaffold only the agreed Django modules; declare compatible tested dependencies, environment parsing, and private-file ignore rules; missing/invalid configuration fails clearly | Not started |
| T02 | P0 | Jerome | T01 | Implement custom User before initial migration and all shared schema/constraints from db_design; migrations run on a fresh PostgreSQL database | Not started |
| T03 | P0 | Jerome | T02 | Shared workflow/locking convention, audit writer, settings singleton, date/limit validation; no generic status bypass; prove critical database constraints against real PostgreSQL | Not started |
| T04 | P0 | Alex | T02 | Shared login/logout, exactly two roles, role redirects, active/admin/ownership enforcement, authorized admin-creation command; direct forged requests and inactive sessions denied | Not started |
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
| — | No application acceptance evidence recorded | No application delivery | No application integration | Jerome / T01 after explicit implementation authorization |

On completion or transfer, use the [project-handoff skill](../.agents/skills/project-handoff/SKILL.md). Save the dated work snapshot in `handoffs/{title-of-work}-{MM-DD-YYYY}.md` and link it from [HANDOFF.md](../HANDOFF.md), which remains the current-state summary/index. This file is the canonical task status list. Mark feature work Done only after its acceptance behavior is verified, not after its documentation is written.
