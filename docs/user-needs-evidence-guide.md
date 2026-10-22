# User-needs and technology evidence

## Current state and responsibility

This is the team's collection and recording guide for **T26**, coordinated by Alex and Jerome with contributions from every member. The user confirmed that student/admin feedback, interview notes, and a team technology evaluation are not available yet. **T26 remains In progress; this guide is not completed research or acceptance evidence.** Replace pending entries with verified findings as work proceeds, keeping this file as the canonical record for this topic.

Use the [course brief, Part 6](Project-Requirements.txt), [T26 acceptance](tasks.md#course-evidence-and-delivery), and [PRD personas](PRD.md#users-and-stakeholders) as the starting points. The personas are assumptions until checked with intended users. Follow [PLAN.md](../PLAN.md) for implementation prerequisites; collecting feedback does not authorize additional product scope.

## What the team needs to collect

| Required material | How to obtain and record it | Current evidence |
| --- | --- | --- |
| Borrower and administrator needs | Invite intended users from both groups. Record participant codes, role/context, date in Asia/Manila, interviewer, consent, questions, and anonymized notes. Distinguish actual campus users from classmates acting as proxies. | Pending |
| Validated personas and requirements | Compare findings with the PRD assumptions. Record which needs were supported, contradicted, or remain untested, with links to source notes and SRS requirement IDs. | Pending |
| Two suitable system options and a recommendation | Compare both options against the same needs and course constraints using the worksheet below. Record evidence, tradeoffs, decision makers, decision date, and unresolved assumptions. | Pending |
| Selected tools and reusable components | Inspect actual code, pins, and check results. Link the existing package rationale and examples of Django authentication/forms, ORM relationships/queries, transactions, shared services, and reusable templates. Explain their benefit and limits for the observed needs. | Existing technical sources linked below; team evaluation pending |
| One emerging technology evaluation | Select a specific technology, investigate current authoritative sources, and record effectiveness, compatibility, security, user value, and an adopt/defer decision. Separate research from any prototype actually run. | Pending |
| Usability/acceptance results | With T23's coordinators, run available workflows with intended users and link their canonical [T23 session/results record](usability-acceptance.md). Do not duplicate private notes or report unattempted flows as tested. | T23 Done/integrated through PR #56/#57: R01 both-role self-report, attributed R02/F02 feedback and verified E01; limited sample/metadata and Not-run human recheck retained |
| Resolved issue and feedback-driven enhancement | Link an actual feedback record to the [T23 findings/enhancement register](usability-acceptance.md#feedback-driven-enhancement), implemented change, owner, verification, and participant recheck. Record unresolved concerns honestly. | E01 startup asset check integrated and technically verified; original R02 source/session metadata unavailable and human recheck Not run |
| Maintenance and configuration guidance | Link verified setup/maintenance guidance and relevant test/operational evidence. Record missing guidance for T24/T29 rather than claiming backup or performance results. | [DEV.md](../DEV.md) and [T24 operational results](operational-verification.md) now include measured performance and a current database/media restore; T24 is integrated through PR #58; broader T29 guidance still requires its own delivery |

Collect a mix of borrower and administrator perspectives sufficient to explain the decision. The brief does not specify an interview count; agree the sample and explain its limitations. Do not invent a minimum, participant statements, signatures, or dates.

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

Start from the existing [architecture options comparison](architecture.md#options-comparison), which compares Django with SQLite and PostgreSQL and records the proposed PostgreSQL baseline. Validate those design tradeoffs against actual user needs and evidence; this guide does not change the selected stack. If the team chooses different candidates, research and justify them under the same constraints. Do not build an additional system merely to complete the comparison.

| Criterion | Option A: name/version and evidence | Option B: name/version and evidence |
| --- | --- | --- |
| Intended users and supported needs, linked to findings | Pending | Pending |
| Course constraints and required workflows | Pending | Pending |
| Availability integrity, authorization, privacy, and auditability | Pending | Pending |
| Usability, accessibility, and local/device suitability | Pending | Pending |
| Django/ORM compatibility and reusable components | Pending | Pending |
| Team effort, setup, maintenance, licensing, and cost | Pending | Pending |
| Verification actually performed and known limitations | Pending | Pending |

Write the recommendation after comparison: chosen option, reasons tied to user findings, significant tradeoffs, remaining risks, reviewer names/date, and evidence links. If scores are used, explain the weights and who agreed them; unmeasured judgments must remain labeled as judgments.

## Explain the implemented tools and reuse

Extend the existing [package rationale](../README.md#third-party-packages-and-assets) and [dependency inventory](third-party-dependencies.md) by referencing them, not copying their version/license tables. Useful source examples include:

| Source | What the team should demonstrate and explain |
| --- | --- |
| [Account forms](../accounts/forms.py) and [access helpers](../accounts/access.py) | Native authentication/form validation and reusable active-role checks; show the relevant real access-test evidence |
| [Borrowing models](../borrowing/models.py) and [account queries](../accounts/queries.py) | Relationships, constraints, filtering, ordering, and related-object loading; distinguish schema from implemented workflows |
| [Settings service](../operations/services.py) and [audit writer](../operations/audit.py) | Explicit transaction, row locking, authoritative role checks, and audit completeness |
| [Operational queries](../operations/queries.py) and [views](../operations/views.py) | Read-only search, filtered pagination, and thin HTTP orchestration |
| [Shared workspace](../templates/components/workspace.html) and [admin layout](../templates/operations/manage/base.html) | Template reuse, named navigation, CSRF-protected forms, responsive Tailwind styling |
| [DEV verification commands](../DEV.md#before-handing-over-work) and [dated handoffs](../handoffs/) | Actual tested commands/revisions and limitations; do not treat historical results as current results |

For each selected example, record the user need it serves, the native component reused, the team's custom code, test evidence, and the tradeoff. Explain outcomes rather than just listing packages. Reports and full borrowing flows require their own accepted implementations before being demonstrated.

## Evaluate one emerging technology

Select the technology with the team and instructor context. Define whether it is being considered for development, testing, or the runtime product. For example, evaluating AI-assisted development does not authorize adding an AI feature to the borrowing application. Research alone can support a defer decision; do not claim a prototype ran unless it did.

| Evaluation field | Required record |
| --- | --- |
| Technology and scope | Specific name/version, why it qualifies for evaluation, intended use, evaluator/date |
| User need | Observed need or team problem, linked to the evidence above |
| Effectiveness | What it might improve; source-supported claims; measured results only if an actual prototype was run |
| Compatibility | Django/Python/PostgreSQL/browser compatibility as relevant, setup effort, dependencies, licensing, and local demonstration constraints |
| Security and privacy | Data sent/stored, access permissions, retention, exposed credentials, failure modes, and mitigations; verify with current primary documentation |
| Accessibility, bias, and user impact | Potential barriers or affected groups, human review needs, and unresolved risks |
| Comparison | Simpler existing/native approach and its tradeoffs |
| Sources and verification | Official documentation or research links with access dates; prototype command/revision/environment/results if performed |
| Decision | Adopt or defer, scope, reasons, reviewers/date, conditions for reconsideration, and remaining unknowns |

Fetch current authoritative sources when carrying out the evaluation. Adoption still follows the project's dependency disclosure, product scope, and implementation authorization rules. No technology adoption or security review is completed by this worksheet.

## Review and completion

Alex and Jerome consolidate the real findings here, link related T23/T25/T27/T28/T29 evidence, and have the contributing members review the interpretation. Update the PRD's persona status only when evidence supports it; preserve course requirements and identify any requested change that conflicts with them.

T26 can be marked Done only after the needs/persona findings, two-option recommendation, tool/reuse justification, and emerging-technology decision have actual evidence and team review. Record what remains untested. Usability execution, feedback-driven implementation, operational measurements, and guides keep their separate backlog acceptance gates. Follow the [handoff skill](../.agents/skills/project-handoff/SKILL.md) when updating project files.
