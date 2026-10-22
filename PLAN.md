# Full-System Delivery Plan

## Start here

This is the shared execution map for developers and their AI agents. It explains which part of the Campus Equipment Borrowing System comes next, which member coordinates it, and what must be available before another member starts. It does not authorize implementation or claim that planned features exist.

Read [AGENTS.md](AGENTS.md), this plan, [HANDOFF.md](HANDOFF.md), and the relevant entries in [docs/tasks.md](docs/tasks.md) at the start of each session. Then read the linked work handoff and actual code for the selected task. A fresh agent must establish state from those files and Git, rather than relying on another agent's conversation.

## Where information belongs

| Source | Responsibility |
| --- | --- |
| [Original requirements](docs/Project-Requirements.txt) and [original member assignments](docs/Project-Members.txt) | Course scope, people, original responsibilities, branch assignments and target schedule; current responsibility changes are in the backlog |
| [PRD](docs/PRD.md) and [SRS](docs/SRS.md) | Product purpose, required behavior, rules, and acceptance scenarios |
| [Architecture](docs/architecture.md), [database design](docs/db_design.md), and [HTTP contracts](docs/api_spec.md) | Technical boundaries and shared interfaces; proposed until implemented and verified |
| This plan | Delivery order, handoff gates, and how an agent chooses the next task |
| [Backlog](docs/tasks.md) | Canonical task IDs, priorities, owners, prerequisites, acceptance, statuses, and verified task/integration evidence |
| [Current handoff](HANDOFF.md) | Current readiness, blockers, next task/member, and links to relevant work snapshots |
| [Dated handoffs](handoffs/) | Evidence and remaining work for a specific completed scope or transfer |
| [Coding standards](docs/coding-standards.md) and [DEV.md](DEV.md) | Django MTV rules, verification strategy, workstation preparation, and Git/PR commands |

Keep task status in the backlog and current readiness in HANDOFF.md. Update this plan when sequencing, responsibilities, or handoff contracts change; do not copy the task checklist or routine progress into a second status board. If files disagree, inspect the relevant code, checks, and integration evidence, and reconcile the current records before proceeding. A plan or status label cannot override course requirements or prove completion.

## Current starting point

Select the next task from the [backlog](docs/tasks.md#verified-task-evidence) and [current handoff](HANDOFF.md), which own current status, blockers and integration evidence. For the existing UI interfaces and prerequisite checks consumed by T20, use [DEV.md's consumer handoff](DEV.md#t20-readiness-and-consumer-handoff). For the course-evidence stage, use [DEV.md's T25 consumer/source checklist](DEV.md#t25-readiness-and-consumer-handoff) to verify the integration and diagram authorization gates. This plan defines sequencing and handoff gates rather than maintaining a second status board.

The original T01–T03 local-batch exception is completed and does not relax later integration gates. A merged implementation with an unresolved acceptance failure does not satisfy a prerequisite. Branch and private-repository access instructions remain in DEV.md. Documentation review does not authorize implementation or publication.

## Delivery stages and handoff gates

The task links below lead to canonical acceptance criteria. A stage can hand over a completed prerequisite before every task in that stage is finished. Calendar dates in the member schedule are targets; verified dependencies determine readiness.

| Stage | Coordinating members and tasks | Entry gate | Output needed by the next member |
| --- | --- | --- | --- |
| 1. Application and shared data foundation | Jerome: [T01, T02](docs/tasks.md#foundation-and-access) | Explicit implementation request; review proposed choices against existing contracts | Agreed modules and tested dependency/configuration setup; custom User defined before initial migration; full shared schema/constraints; fresh PostgreSQL migration evidence. T02 integrated into main unlocks Alex's T04. |
| 2. Shared workflow rules and access | Jerome: T03, then T06; Alex: T04, then T05 in [foundation and access](docs/tasks.md#foundation-and-access) | T03 and T04 each require T02; T05 and T06 each require both T03 and T04 | One lock/audit/settings convention and one authentication/authorization contract. T03 and T04 may proceed in parallel after T02; T04 unlocks Ellyssa's account/layout work, and T03 plus T04 unlock Kenneth's catalog work. |
| 3. Equipment inventory | Kenneth: [T07, T08](docs/tasks.md#inventory-and-borrower-portal) | T07 requires T03 and T04; T08 requires T07 | Custom catalog and physical-unit operations, stable asset identities, availability queries, derived counts, and protected history. T08 enables browsing and request submission when their other prerequisites are met. |
| 4. Borrower account and discovery | Ellyssa: [T09, T10](docs/tasks.md#inventory-and-borrower-portal) | T09 requires T04; T10 requires T08 and T09 | Registration/profile that reuse Alex's authentication, portal base/components, and privacy-safe equipment browsing. T09 can progress while Kenneth implements inventory. |
| 5. Borrower requests and tracking | Ralph: [T11, T12](docs/tasks.md#inventory-and-borrower-portal) | T11 requires T03, T08, and T09; T12 requires T11 | Atomic validated request submission, own history/detail, and eligible cancellation using the shared contracts. T11 unlocks administrator review; T12's full cancellation/history paths must also be exercised once approval and issue exist. |
| 6. Approval and concurrency proof | Margareth: T13; Jerome with Margareth: T14 in [administrator operations](docs/tasks.md#administrator-operations) | T13 requires T03 and T11; T14 requires T13 | Audited approval/rejection and exact reservations. Competing PostgreSQL approvals for the last unit produce exactly one success and one conflict, with no partial allocation. T14 is required before T15. |
| 7. Maintenance and release | Jerome: T16 and T15 in [administrator operations](docs/tasks.md#administrator-operations) | T16 requires T08 and T03; T15 requires T13 and T14 | Maintenance repair/retirement rules and audited one-time issue/LoanUnit/slip behavior. T16's completed implementation and contributor credit are preserved; both T15 and T16 are prerequisites for complete returns. |
| 8. Returns and overdue behavior | Ralph: [T17](docs/tasks.md#administrator-operations) | T15 and T16 | Per-unit/partial returns, duplicate prevention, damaged-return maintenance, final closure, and derived overdue behavior, with transactional audit evidence. |
| 9. Live administration reporting | Alex: [T18, T19](docs/tasks.md#administrator-operations) | T18 requires T15 and T17; T19 requires T17 and T18 | Live cards/charts and filtered reports/CSV with consistent totals and access checks. Alex returns to this work after borrowing operations exist; static numbers do not complete these tasks. |
| 10. Integrated UI and demonstration data | Ralph: T20; Jerome with all owners: T21 in [operations](docs/tasks.md#administrator-operations) and [validation](docs/tasks.md#validation-and-demonstration-data) | T20 requires T10, T12, T17, T18, T19; T21 requires T17 | Integrated role layouts, navigation, errors, confirmations, and accessibility; coherent fictional data meeting the backlog's dataset. Keep seed credentials and real identities out of Git. |
| 11. System validation and operational evidence | Everyone: T22, T23; Jerome with owners: T24 in [validation](docs/tasks.md#validation-and-demonstration-data) | T22 requires T14, T19, T20, T21; T23 requires T20, T21; T24 requires T22 | Real SRS acceptance/security/concurrency results, actual user feedback and a verified enhancement, measured performance, and demonstrated backup/restore. Fix failures before claiming acceptance. |
| 12. Course evidence and delivery | Everyone under the [T25–T31 owners](docs/tasks.md#course-evidence-and-delivery) | T25 requires T22–T24; T29 requires T22 and T24; T30 requires T22, T23, T25–T29; T31 requires T30 | Evidence matching the implementation, verified guides, clean-machine submission ZIP, and a rehearsed demo/Q&A with individual participation. T26 starts after DOC-01, T27 precedes real-data use, and T28 runs every work period; do not defer those records until submission. |

Within each stage, follow each task's exact prerequisites and acceptance in the backlog. This table groups work for coordination; it does not relax those dependencies, reassign feature ownership, or make a shared module exclusively owned by one member.

Follow the October 20 [current ownership and support responsibilities](docs/tasks.md#current-ownership-and-support-responsibilities): Kenneth, Margareth and Ellyssa now focus on validation, documentation and manual testing. They can check available implemented flows now without closing gated system-acceptance tasks. Their T25 MTV/database/workflow diagram conversion into an actual diagramming tool remains on standby until the system is fully finished and Jerome explicitly gives the go signal; T25's backlog prerequisites also remain required. Preserve earlier contributions and original member/branch records.

## Select the next task in a new session

1. Establish the acting member, assigned branch, requested scope, and implementation/commit permissions. Follow DEV.md to obtain current main and sync the member branch without discarding local work. Read-only review is possible without authorizing implementation.
2. Read the member's unfinished task entries and the current handoff. Resume that member's In progress task before starting another unrelated one. Choose a Not started task only when its prerequisites and scope are satisfied; do not take another member's task without coordination.
3. Verify every prerequisite's acceptance evidence and **integration into main**. Check the referenced handoff, real source, actual configured checks, and commit/PR identity. A Done task on an unmerged member branch is not yet an integrated dependency. A PR that is only open, a schema diagram, an agent's claim, or a passing check on an old commit is insufficient.
4. If a prerequisite is missing, keep the dependent task Not started and record the specific missing output, responsible member, and unblock action in HANDOFF.md. Do not invent models, auth helpers, signatures, routes, or temporary implementations to bypass it. Continue only independently authorized work with satisfied dependencies.
5. For a ready and authorized task, agree the smallest acceptance scope, mark that task In progress, read its contracts and actual code, and use the [Django MTV skill](.agents/skills/django-mtv/SKILL.md). Work only that scope and run the meaningful checks required by the coding guide and configured project commands.

An agent can assess readiness and report the next task without changing files. Agents that do not discover AGENTS.md must be given that file and this plan explicitly. These are shared instructions, not background automation.

## Complete work and hand it to the next member

Use the [project-handoff skill](.agents/skills/project-handoff/SKILL.md) after file-changing work. The evidence must let another member establish all of the following:

| Question | Required evidence |
| --- | --- |
| What was accepted? | Task IDs, implemented behavior, relevant source/contract paths, actual checks and results, and known gaps. Keep a partially satisfied task In progress. |
| What interface may the next agent use? | Actual model/migration, service/query/form/access helper, named URL, or template/component paths and important signatures/constraints. Link their canonical source instead of copying code. If an interface changed, identify affected consumers. |
| Where is the work? | Member branch and commit/PR when they actually exist; otherwise explicitly say uncommitted or local only. Never invent a SHA or mark a pending PR merged. |
| Is it available on main? | Actual merged PR/main commit and relevant checks for that revision, or an explicit Not integrated result with the remaining reviewer/integration action. |
| Who can continue? | Named member, exact next task IDs, each satisfied prerequisite, remaining blockers, and the immediate next action. Readiness does not authorize that member's agent to start coding automatically. |

Store the work snapshot in `handoffs/{title-of-work}-{MM-DD-YYYY}.md` using the current Asia/Manila date. Preserve previous snapshots. Update the affected backlog status and [verified task evidence](docs/tasks.md#verified-task-evidence), then HANDOFF.md's current readiness and dated index. Update this plan only if the execution map or handoff rules changed. Preserve concurrent edits and unrelated task rows.

**Done** means the task's acceptance was verified; **integrated into main** is a separate fact recorded with evidence. Until integration is verified, its dependent member remains waiting for that output. Once Jerome integrates an authorized PR, update the current handoff and backlog integration evidence with the actual main reference and newly ready task/member; the consumer syncs main and rechecks the dependency before implementation. A real failed check reopens the affected task and readiness; do not erase the earlier dated snapshot.

Follow [DEV.md's Git workflow](DEV.md#assigned-branches-and-main-integration): member branch, authorized commit/push, PR, Jerome's integration, then consumer sync. Agents still require an explicit commit/push/merge request for the operation concerned. Do not push main, notify teammates, or start the next member's task merely because a handoff is complete.

## Example: Jerome hands the foundation to Alex

This is a future example, not completed work. Jerome implements and verifies T01 and T02 after authorization. His handoff identifies the actual custom User, migrations, PostgreSQL checks, branch, and any delivery reference. T02 can be Done locally while its integration record still says Not integrated; Alex's T04 remains waiting.

After Jerome integrates T02 into main, the current handoff points to the actual main revision and says **Alex / T04 is ready**, provided Alex has requested that implementation. Alex's agent syncs `alex` with main, reads T02's evidence and real user model, and implements only T04. Jerome can work on T03 alongside that task. Ellyssa's T09 can start after T04 integrates; Kenneth's T07 needs both T03 and T04 integrated. Jerome's later settings/audit UI task T06 does not hold up Alex's initial authentication work.

## Prompts for team coding agents

To start implementation, copy your member's complete prompt from [Team AI work prompts](docs/team-agent-prompts.md). Implementation prompts authorize ready assigned feature work; support prompts authorize validation, documentation and manual testing. Both require verification and handoff while preserving prerequisite, diagram and main-integration gates. Send it again after integration to continue with newly ready work. The prompt guide owns the reusable templates; task ownership and acceptance remain in the backlog.

For a readiness-only session, a member can instead use:

> I am Alex, assigned branch alex. Read AGENTS.md, PLAN.md, HANDOFF.md, and my backlog entries. Inspect integrated prerequisite evidence and tell me my next ready task and blockers. Do not implement anything yet.
