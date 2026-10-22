# User-needs and technology evidence (T26)

## Current state and responsibility

This is the canonical **T26** evidence record, coordinated by Alex and Jerome with contributions from every member. Jerome authorized this work on October 22, 2026 and selected AI-assisted development for the emerging-technology evaluation. Codex prepared the source review and recommendations against local `jerome` and freshly fetched main `0c88fcb` (PR #62), whose trees matched at review. DOC-01 is Done; the earlier T26 guide source `c3d2c01`/integration `f7c32f8` is retained in main. T26 does not depend on T25 completion.

**Done on the documented limited evidence; Not integrated.** On October 22, 2026, Jerome accepted this prepared record for commit/push and requested T27 readiness. That is coordinator acceptance of the role-level persona assessment, PostgreSQL recommendation, tool/reuse justification and supervised-AI recommendation below. It is not an all-member vote or additional participant feedback. Detailed needs, campus processes and device/accessibility preferences remain untested; those limits do not imply that new interviews or an outside sample are required by T26.

Use the [course brief, Part 6](Project-Requirements.txt), [T26 acceptance](tasks.md#course-evidence-and-delivery), and [PRD personas](PRD.md#users-and-stakeholders) as authority. These notes describe feedback about the application; they are not the purpose, remarks, descriptions or maintenance notes stored in its database. Follow [PLAN.md](../PLAN.md) for implementation prerequisites.

**Publication:** source `25e83ef45036f0a0541b74daa7fffbb57972a4b7` is pushed to `origin/jerome` with fetched remote equality and Codex co-author credit verified. Main integration remains pending; see the [publication/T27-readiness receipt](../handoffs/t26-evidence-publication-and-t27-readiness-10-22-2026.md).

## What the team needs to collect

| Required material | How to obtain and record it | Current evidence |
| --- | --- | --- |
| Borrower and administrator needs | Retain real feedback, distinguish intended users from classmates acting as proxies, and record available context without inventing missing details. | G01 below: coordinator-reported groupmate testing today; only general positive feedback supplied |
| Validated personas and requirements | Compare findings with PRD assumptions and SRS IDs; distinguish role-level acceptance from detailed needs research. | Persona assessment below; detailed preferences, device/accessibility needs and campus processes remain untested |
| Two suitable system options and a recommendation | Compare against the same course constraints and role needs, including adaptation and verification limits. | PostgreSQL versus a MySQL/InnoDB design; recommendation to retain PostgreSQL accepted by Jerome on October 22 |
| Selected tools and reusable components | Explain real source examples, the need served, custom implementation, evidence and tradeoff. | Source review completed below; versions/licenses remain in the existing inventory |
| One emerging technology evaluation | Investigate authoritative sources and distinguish research from an actual experiment. | AI-assisted development selected by Jerome; conditional supervised-use recommendation accepted for T26; policy/account clearance remains T27 |
| Usability/acceptance results | With T23's coordinators, run available workflows with intended users and link their canonical [T23 session/results record](usability-acceptance.md). Do not duplicate private notes or report unattempted flows as tested. | T23 Done/integrated through PR #56/#57: R01 both-role self-report, attributed R02/F02 feedback and verified E01; limited sample/metadata and Not-run human recheck retained |
| Resolved issue and feedback-driven enhancement | Link an actual feedback record to the [T23 findings/enhancement register](usability-acceptance.md#feedback-driven-enhancement), implemented change, owner, verification, and participant recheck. Record unresolved concerns honestly. | E01 startup asset check integrated and technically verified; original R02 source/session metadata unavailable and human recheck Not run |
| Maintenance and configuration guidance | Link verified setup/maintenance guidance and relevant test/operational evidence. Record missing guidance for T24/T29 rather than claiming backup or performance results. | [DEV.md](../DEV.md) and [T24 operational results](operational-verification.md) now include measured performance and a current database/media restore; T24 is integrated through PR #58; broader T29 guidance still requires its own delivery |

Collect a mix of borrower and administrator perspectives sufficient to explain the decision. The brief does not specify an interview count; agree the sample and explain its limitations. Do not invent a minimum, participant statements, signatures, or dates.

## Recorded feedback and persona assessment

### G01: Coordinator-reported groupmate module testing

| Field | Actual record |
| --- | --- |
| Report/test date | Report received October 22, 2026, Asia/Manila; Jerome says testing happened today. Exact time not supplied. |
| Source and reporter | Jerome's T26 task conversation; coordinator summary of groupmates' feedback, not independently observed sessions |
| Participants/context | Groupmates tested modules assigned to them, including administrator/basic-user work as examples. Treat this as classmate/developer proxy feedback. Number of participants, individual identities and exact role coverage not supplied. |
| Findings supplied | Jerome reports that members said their assigned modules worked well. No specific difficulty, requested change, preference, rating or measured task outcome supplied. |
| Revision/device/dataset | Not supplied for the actual sessions. The documentation review baseline is main `0c88fcb`; do not assign that revision to the human testing. |
| Retained material | Only the coordinator's nonidentifying summary; no participant interview transcript, recording or identifying data retained. Individual permission for additional notes/recordings was not supplied. |
| Interpretation and limit | Supports limited acceptance of assigned functionality. It does not prove every workflow was tested, validate every PRD assumption or represent actual campus equipment administrators. No separate T23 participant session or enhancement is claimed. |

Classmate testing is usable proxy evidence. Its limits must travel with the conclusion. The existing [T23 R01/R02/F02/E01 record](usability-acceptance.md#session-register) remains canonical for the earlier both-role working report, startup issue and verified enhancement; G01 must not be counted as a known independent sample of those reports.

| PRD persona / need | Requirement and implementation evidence | Assessment from human evidence | Remaining question |
| --- | --- | --- | --- |
| Borrower: find available equipment and request a suitable quantity | U2/U3; [portal queries](../inventory/queries.py), [submission service](../borrowing/services.py), [submission tests](../borrowing/tests/test_request_submission.py) | T23 R01 reports the borrower flow works; G01 is consistent with basic-user module acceptance. Specific search/quantity needs remain brief-derived assumptions. | Does the item information and availability display let a proxy borrower choose confidently? |
| Borrower: understand decisions, due dates and cancellation | U4; [tracking tests](../borrowing/tests/test_request_tracking.py) | General acceptance only; no feature-level preference or cancellation observation supplied. | Can the tester explain the displayed status, next action and cancellation limit? |
| Administrator: prevent double issue and preserve unit history | A2-A6, BR-04/BR-07/BR-09; [locking helpers](../operations/locking.py), [concurrency tests](../borrowing/tests/test_approval_concurrency.py), [returns](../borrowing/return_services.py) | T23 R01 reports the admin flow works; G01 supports assigned-module acceptance. Actual campus operating practices remain unvalidated. | Does asset-level reservation/return handling match the tester's expected responsibilities? |
| Administrator: reports, audit and configurable limits | A7/A8; [report queries](../operations/queries.py), [report tests](../operations/tests/test_reports.py), [settings/audit tests](../operations/tests/test_settings_audit.py) | Implemented and technically verified historically; no specific human report/CSV/audit feedback supplied. | Are the report fields/date meanings and limits useful and understandable? |
| Both roles: clear errors, accessible device use and reliable startup | NFR-04/NFR-08; [T23 E01](usability-acceptance.md#feedback-driven-enhancement), [shared workspace](../templates/components/workspace.html) | The missing-build issue has a verified technical fix; a human recheck remains Not run. G01 supplies no device/accessibility finding. | What needed explanation or assistance, and on which device? |

The two-role persona structure is consistent with the brief and available proxy acceptance. Jerome accepted this role-level assessment for publication on October 22. This is limited validation of role suitability, not a completed needs interview study. No contradictory needs were reported; absence of a complaint is not proof that all needs are met. Instructor/evaluator and development-team entries remain stakeholders, not additional application roles. Detailed persona assumptions retain their limits in the PRD.

## Collecting feedback

Before a session, explain the school-project purpose, participation choice, how anonymized notes will be used, and who may access them. Ask permission before recording audio, video, or identifiable details. Use fictional borrowing examples and avoid collecting passwords, student numbers, private transaction histories, or unnecessary contact information. Confirm applicable campus/instructor requirements through T27; this guide makes no compliance claim.

Suggested borrower questions:

1. How do you currently find and request campus equipment? Describe a recent difficulty without naming other people.
2. What information helps you choose an item and quantity?
3. How do you know whether a request was approved, when to collect it, and when it is due?
4. When would you need to cancel or check a return? What would clear feedback look like?
5. What device, access, or accessibility needs affect this task?

Suggested administrator questions:

1. How do you identify physical units and confirm which are available?
2. What information do you need before approving or rejecting a request?
3. How do you handle release, partial returns, damage, repairs, and overdue equipment?
4. Which account, audit, settings, and report information do you need for daily work?
5. Which errors would cause the most disruption, and how should the application explain them?

Ask users to describe their needs before showing the proposed solution. Distinguish a participant's words from the interviewer's interpretation. For a usability session, let the participant attempt an available task before helping, then record where help was needed. Proposed tasks must match the implemented revision; the [SRS acceptance scenarios](SRS.md#minimum-acceptance-scenarios) supply the system behavior to check.

Record each session here using these fields:

| Field | To fill after the session |
| --- | --- |
| Session ID, date/time zone, interviewer | Pending |
| Participant code, role/context, intended user or proxy | Pending |
| Consent and permitted use of notes/recordings | Pending |
| Interview questions or attempted task; tested revision/device if applicable | Pending |
| Anonymized observation or approved short quotation | Pending |
| Interpretation, linked PRD assumption/SRS requirement, priority and reason | Pending |
| Source location and access restriction for any private notes | Pending |
| Follow-up, responsible member, and participant recheck | Pending |

Keep private source material in the instructor-approved restricted location; Git should contain anonymized findings and references only. Never commit private participant records. Preserve unresolved disagreements and the limits of proxy feedback.

## Compare two suitable options

First screen options against the brief: Django, ORM, exactly two roles, a handwritten custom administration interface, required borrowing workflows, and a runnable local demonstration. A candidate that cannot meet those constraints is not a compliant replacement. Explain why it was excluded and identify a suitable second option. Different UI sketches alone do not establish two system options.

The [architecture screening comparison](architecture.md#options-comparison) explains why SQLite was not selected: Django's `select_for_update()` has no effect on SQLite. It is permitted by the brief, but swapping it into this application would not preserve the verified concurrency design. The comparison here therefore uses two transaction-capable Django system designs. Option B is a feasible alternative requiring adaptation, not a tested replacement for the current checkout. No second system needs to be built to research the options.

Research performed October 22, 2026, using the versioned [Django 5.2 database guidance](https://docs.djangoproject.com/en/5.2/ref/databases/), [locking API](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update), [constraint reference](https://docs.djangoproject.com/en/5.2/ref/models/constraints/#uniqueconstraint) and [MySQL 8.4 InnoDB locking guidance](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html).

| Criterion | Option A: Django 5.2 monolith with PostgreSQL | Option B: Django 5.2 monolith with MySQL 8.4/InnoDB |
| --- | --- | --- |
| Role needs | Current portal/custom management views serve the borrower and administrator needs above; G01/T23 give limited proxy acceptance. | Could use the same server-rendered role journeys; no MySQL user test or evidence of a better experience. |
| Course fit | Django authentication, ORM, migrations, custom pages and exactly two roles are implemented. | Django/MySQL is permitted; these same contracts could be implemented without generated administration pages. |
| Concurrent allocation | Actual row locks, atomic services and conditional uniqueness protect units; T14 and later integration evidence cover competing approvals. | InnoDB supports locking reads in transactions. The allocation model needs an alternative database-enforced active-unit uniqueness design, such as a unique current-allocation relation separate from history, with atomic service/constraint tests. This is a design proposal, not implemented code. |
| Portability and integrity | Existing [allocation constraints](../borrowing/models.py) and [maintenance constraints](../inventory/models.py) are already exercised on PostgreSQL. | Django [conditional index restrictions](https://docs.djangoproject.com/en/5.2/ref/models/indexes/#condition) also apply to conditional uniqueness; current active-allocation/open-maintenance constraints cannot simply be retained unchanged. Review date/regex expressions, case-insensitive uniqueness and migrations too. |
| Access, privacy and audit | Native authentication plus custom role/ownership checks and same-transaction audit; database choice alone does not provide these controls. | The same application protections are required. A different database does not remove their implementation or test obligations. |
| Usability and local demonstration | Native forms/templates; local PostgreSQL/media setup is documented without requiring Neon. | Comparable browser interface is possible; needs a MySQL service, driver/configuration, fixtures and revised evaluator setup. Accessibility is a UI concern in either option. |
| Reuse and maintenance | Existing Psycopg dependency, ORM queries, services, backup procedures and test environment are reusable now. | Would retain Django components but add a compatible driver and MySQL-specific backup/recovery guidance; strict mode and transaction settings require review under Django's database guidance. |
| Effort and cost | Retains working dependencies and measured operations. A database service remains a setup responsibility; no cost/productivity comparison was measured. Licenses/notices are recorded in the [inventory](third-party-dependencies.md). | Adds migration/constraint/service adaptation and fresh tests before equal confidence is possible. Driver/server licensing and distribution terms would require review before adoption; no installation, purchase or price claim made. |
| Actual verification | Existing [T22 acceptance](../handoffs/t22-automated-system-acceptance-10-22-2026.md), [T24 operations](operational-verification.md) and [latest requirements audit](../handoffs/course-requirements-audit-before-t26-10-22-2026.md) establish PostgreSQL results with their original dates/environments. | Official-source feasibility review only. No MySQL prototype, migration, benchmark, restore or concurrency proof performed. |

**Recommendation: retain Option A, PostgreSQL.** This is Codex's source-based recommendation prepared for Alex/Jerome review on October 22. It preserves the implemented protection for scarce physical units, reliable histories and role workflows that received limited positive proxy feedback. It also retains demonstrated recovery and existing local setup. There is no human finding requiring a database change or evidence that Option B would improve usability. Those are judgments based on available evidence, not weighted scores or a comparative benchmark.

Option B is suitable as an alternative system design because Django and InnoDB can implement transactional allocation, provided equivalent uniqueness/history protections are designed and verified. It is not suitable as an immediate configuration-only switch. Reconsider it if a real institutional requirement calls for MySQL and the team can fund the adaptation/verification effort. Jerome accepted the PostgreSQL recommendation for publication on October 22; detailed persona findings remain limited. This document does not change the selected stack.

## Explain the implemented tools and reuse

The existing [package rationale](../README.md#third-party-packages-and-assets) and [dependency inventory](third-party-dependencies.md) own purposes, exact pins and license tables. This source review connects the implemented choices to the role needs above; it does not claim G01 validated each component separately.

| Need and selected tool/reuse | Native component and team's custom implementation | Verification and tradeoff |
| --- | --- | --- |
| Safe access for both roles: Django authentication/forms | [LoginForm](../accounts/forms.py) extends Django's AuthenticationForm; [access helpers](../accounts/access.py) enforce stored role, active state and ownership. Custom views/forms define allowed fields. | [Authentication/access tests](../accounts/tests/test_authentication.py) cover denial paths; built-in authentication avoids custom password/session protocols, while application role rules still need explicit checks. |
| Reliable quantities/history: Django ORM and PostgreSQL | [Models](../borrowing/models.py) relate requests/items, allocations, loans/units and returns; [locking helpers](../operations/locking.py) reuse `select_for_update()`; [services](../borrowing/services.py) reuse `transaction.atomic()` and validation. | [Submission](../borrowing/tests/test_request_submission.py), [approval concurrency](../borrowing/tests/test_approval_concurrency.py) and [return tests](../borrowing/tests/test_returns.py) cover invariants. The stronger database contract adds PostgreSQL setup and backend dependence. |
| Traceable decisions/settings: reusable services | [Settings service](../operations/services.py) and [audit writer](../operations/audit.py) reuse Django transactions and shared actor checks, with explicit custom audit actions and before/after values. | [Settings/audit tests](../operations/tests/test_settings_audit.py); audit failure must roll back the business change. Reuse centralizes behavior but every new workflow must call it correctly. |
| Useful reports: ORM relationships and aggregates | [Operational queries](../operations/queries.py) use filtering, ordering, `select_related`, `annotate` and `Count`; report totals use the filtered loan set and count issued/returned/outstanding units. | [Report tests](../operations/tests/test_reports.py) check filters, totals, CSV and access. ORM reuse avoids duplicating SQL in views; careless joins can still multiply counts, requiring integrated checks. |
| Consistent navigation/errors: Django templates, native forms and Tailwind | [Workspace](../templates/components/workspace.html), [admin base](../templates/operations/manage/base.html), [portal base](../templates/accounts/portal/base.html) and [form field](../templates/components/form_field.html) reuse inheritance/includes, named links, CSRF and shared styles. Required role pages are handwritten. | [Workspace tests](../accounts/tests/test_workspace.py), T20's retained browser evidence and [manual guide](manual-test-guide.md). Shared structure reduces repeated markup; npm asset builds and manual device/accessibility review remain necessary. |
| Understandable operational summaries: Chart.js | [Dashboard](../templates/operations/manage/dashboard.html) renders the two required charts from server ORM results, with accessible data tables; Chart.js supplies rendering rather than management pages. | [Dashboard tests](../operations/tests/test_dashboard.py) and the [attributed UI-11/UI-12 record](../handoffs/dashboard-and-workspace-publication-review-10-20-2026.md). Adds JavaScript/build/notices; table data remains available without charts. |
| Equipment recognition: Pillow and configured photo storage | [Photo validation](../inventory/photos.py) uses Pillow; the storage adapter is selected through existing configuration, with protected application photo views. Local evaluation can use local media and placeholders. | [Photo tests](../inventory/tests/test_equipment_photos.py) and HOST-01 evidence in the [backlog](tasks.md#verified-task-evidence). Images help recognition but require validation, storage permissions and provenance; unresolved asset provenance stays with T27. |

Version-control receipts, actual test results and configuration/maintenance instructions remain in [DEV.md](../DEV.md#before-handing-over-work), [dated handoffs](../handoffs/), [T24](operational-verification.md) and the backlog. Historical results are not rerun results for this documentation task. [T23](usability-acceptance.md) supplies acceptance, the resolved startup issue and feedback-driven E01; [DEV](../DEV.md) supplies current maintenance commands. T29 still owns complete audience guides. These references connect Part 6 evidence without duplicating their records.

## Evaluate one emerging technology

**Selected by Jerome: AI-assisted development, evaluated October 22, 2026 by Codex for Alex/Jerome review.** The specific reference product is Codex as a repository coding assistant. Historical Kiro work remains credited, but its product/security behavior is not evaluated by OpenAI documentation. No exact client/model version was retained for the historical contributions, so this is a workflow/product evaluation rather than a reproducible version benchmark. The emerging aspect is agentic assistance that can inspect source, draft changes and invoke development tools.

| Evaluation field | Finding and evidence |
| --- | --- |
| Intended use and user need | Development/review/documentation support for the team's tested workflows and consistent handoffs. Borrower/admin value is indirect through correctness and maintainability; G01 contains no request for an AI application feature. |
| Effectiveness observed | Git source `f3d42bae5d907652e3f0b12b1ec4290321fec08d` has both Codex and Kiro co-author trailers; its [delivery record](../handoffs/dashboard-and-workspace-publication-review-10-20-2026.md) attributes dashboard/workspace work and records 301 passing PostgreSQL tests plus scoped browser checks. This establishes attributed assistance and checked deliverables, not that AI caused the passing results or improved speed. No controlled unassisted comparison, time saving, cost saving or defect-rate measurement exists. |
| Compatibility | Historical work is present in this Python/Django, template, JavaScript and PostgreSQL repository. Assistance uses the project's existing commands; the application requires no AI SDK/API key/inference service to run. A student can develop/review manually and the evaluator can demonstrate locally without an AI account. A fresh supported client/platform/account combination was not tested in this task. |
| Security: permissions and execution | Official [agent approvals/security guidance](https://learn.chatgpt.com/docs/agent-approvals-security) distinguishes sandbox boundaries, approval policy and network access, and warns about untrusted instructions. An assistant with shell/database access can cause real writes or disclose source/secrets. AGENTS instructions and ignored files are not technical access controls. This task's environment permits unrestricted filesystem/network access; no enforced restrictive sandbox is claimed. |
| Privacy and retention | Repository context/prompts and tool outputs can reach the assistant service; connected tools add separate destinations and permissions. Actual account plan, training controls, retention, residency and all teammates' configurations are unverified. Do not assert zero retention or no training for this project. Alex/Jerome must verify applicable account/service terms and T27 policy before approving sensitive-data use. |
| Safeguards proposed | Use sanitized source and fictional examples, a least-privileged disposable local database and reviewed diffs/checks. Limit tool/file/network access using enforced controls appropriate to the chosen client. The official [security cookbook](https://learn.chatgpt.com/docs/enterprise/security-cookbook) covers protecting secrets and production systems and verifying allowed/blocked actions. No managed policy or blocking test was installed/performed here; existing shared-data restrictions remain authoritative. |
| Accessibility, bias and accountability | Generated wording may assume an unfamiliar campus process, device or ability; code may be incorrect despite a confident explanation. Human reviewers must compare changes to the brief, test role/ownership/integrity paths and check errors/device/keyboard use. Each member must understand and explain their contribution. AI credit is not evidence of instructor/BulSU permission or individual participation; T27/T28 own those records. |
| Simpler alternative | Manual implementation/review using official Django documentation, native forms/ORM, Git and existing tests avoids assistant context sharing and service dependence. It still needs human time and may miss defects. No measured evidence ranks either process for productivity here. |
| Experiment and verification limits | This evaluation used source/history/record inspection and current official documentation. No new AI prototype, model comparison, security scan, retention inspection or productivity experiment was run. Existing development use is disclosed rather than presented as a new trial. |

**Recommendation: adopt supervised AI assistance for development, subject to the actual instructor/BulSU rules and verified account/data controls.** Keep a named human responsible for reviewing the diff, running appropriate checks and explaining the result. Defer unsupervised shared-data operations, sensitive participant-data use and any runtime AI feature: no observed need or verified benefit justifies them here. Jerome accepted this conditional recommendation for publication on October 22; that acceptance is not policy clearance, a service installation or an all-member adoption vote. Reconsider if policy prohibits the use, required data protections cannot be demonstrated, or a supervised trial shows unacceptable review effort/errors.

The cited official OpenAI pages were fetched on October 22, 2026. They establish available controls and their limits, not that this workstation or every teammate has configured them. T27 remains responsible for the applicable policy, privacy and AI/reuse disclosure evidence; this evaluation does not close it.

## Review and completion

**Coordinator review: Jerome, October 22, 2026, Asia/Manila.** After the record and its pending review were presented, Jerome accepted the changes for commit/push and requested readiness for T27. This closes the coordinator review of the documented scope; it does not supply answers to individual research questions or claim Alex/other members reviewed the record. Further voluntary findings can refine it without inventing retrospective activity. Formal interviews, recordings, ratings and outside participants are not additional course requirements.

| Review item | Current result / next action |
| --- | --- |
| Groupmate feedback and persona validation | G01 and the role-level assessment accepted for publication by Jerome; exact role/flow detail and detailed preferences remain evidence limits. No new participant result inferred. |
| Options recommendation | Source/official comparison complete; Jerome accepted retaining PostgreSQL. MySQL remains an unimplemented alternative design. |
| Tool/reuse justification | Actual source and historical checks linked; Jerome accepted the explanation for publication. Members still explain their own work under T28/T31. |
| Emerging technology | Evaluation complete; Jerome accepted the conditional supervised-use recommendation. T27 account/policy questions remain open and do not become an AI clearance claim. |
| Related deliverables | T23 acceptance/enhancement and T24 operational evidence remain as recorded; T25 diagrams, T27 professional judgment, T28 participation and T29 guides retain separate acceptance gates. |

An anonymized summary means retaining useful observations without names or other identifying details. Before adding another person's quotation, recording or private source, explain its school-report use and record their permission. The current G01 entry retains only Jerome's general nonidentifying coordinator report; it does not invent individual consent forms or participant statements.

T26 is Done on the retained proxy feedback/role assessment, sourced comparison, tool/reuse explanation, emerging-technology evaluation and coordinator acceptance. Publication and main integration are separate facts recorded in the [backlog](tasks.md#verified-task-evidence). Usability execution, feedback-driven implementation, operational measurements, policy clearance and guides keep their separate backlog acceptance gates. T27 can continue independently; use its [consumer handoff](../DEV.md#t27-readiness-and-consumer-handoff). Follow the [handoff skill](../.agents/skills/project-handoff/SKILL.md) when updating project files.
