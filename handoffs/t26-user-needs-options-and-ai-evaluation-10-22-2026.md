# T26 user needs, system options and AI-assisted development evaluation

## Scope and outcome

October 22, 2026, Asia/Manila (UTC+08:00). Jerome authorized T26 and selected AI-assisted development for its emerging-technology evaluation. Alex/Jerome coordinate T26; Codex supplied source research and documentation assistance. Existing member, Codex and Kiro credit is preserved.

**T26 In progress; evidence prepared for human review.** The [canonical record](../docs/user-needs-evidence-guide.md) now contains:

- G01: Jerome's report that groupmates tested their assigned modules today and said they worked well. Exact participant count, roles/flows, revision, device and detailed observations are unavailable. This is coordinator-reported classmate/developer proxy feedback, not independent campus interviews or new detailed T23 sessions.
- An explicit mapping of borrower/admin persona needs to SRS requirements, actual source/tests and the limited human evidence. Detailed preferences and campus operating practices remain unvalidated.
- Two alternative transaction-capable Django designs: implemented PostgreSQL and a MySQL 8.4/InnoDB design requiring adapted conditional uniqueness/history protection, configuration and fresh tests. PostgreSQL is recommended; MySQL has not been prototyped or adopted. SQLite remains an earlier screened option, with its row-lock limitation retained.
- Source-based justifications for native authentication/forms, ORM constraints/queries, workflow/audit services, shared templates, Tailwind, Chart.js and photo validation/storage. Version/license inventories remain canonical elsewhere.
- An official-source evaluation recommending supervised AI-assisted development, conditional on actual policy/account protections. Historical attributed contributions and test records are evidence of delivered work, not measured productivity improvement. No runtime AI feature or technical safeguard installation was performed.

Jerome's review of persona interpretation and the recommendations is requested in the active task conversation; no answer, other member approval or adoption vote is assumed. The current evidence does not establish instructor/BulSU policy clearance or account training/retention settings; T27 retains those separate obligations. T25/T28/T29-T31 retain their own acceptance gates.

## Source, integration and files

Fresh fetch verified local `jerome` and `origin/main` at user-merged PR #62, `0c88fcbb34a6a26af2970ff158287b83c9e9491c`, both tree `1a266a47857bc93e78823fb4127d7428a15f52e8`. Initial working tree was clean; no branch merge/reset was needed. DOC-01 is Done and the earlier T26 guide integration `f7c32f8` is an ancestor of main. **These new changes are local, uncommitted and Not integrated.**

Relevant files: [canonical T26 record](../docs/user-needs-evidence-guide.md), [PRD persona status](../docs/PRD.md#users-and-stakeholders), [architecture comparison pointer](../docs/architecture.md#options-comparison), [README evidence index](../README.md#part-6-submission-and-presentation), [submission checklist](../SUBMISSION.md), [backlog evidence](../docs/tasks.md#verified-task-evidence), [current handoff](../HANDOFF.md) and [agent context](../AGENTS.md).

## Verification and limitations

- Read the plan, current handoff, backlog/course brief, existing T26/T23/T24 evidence and package rationale; inspected actual forms/access helpers, workflow locks/services, constraints, ORM reports, shared templates, photo processing and test source references.
- Verified `f3d42bae5d907652e3f0b12b1ec4290321fec08d` has both Codex/Kiro co-author trailers; historical verification remains attributed to its dated record.
- Fetched versioned official Django and MySQL documentation for backend/locking/constraint claims, and official OpenAI documentation for agent execution/security controls. Supporting citations and access date are in the canonical T26 record. Two guessed legacy OpenAI documentation paths failed or redirected to a different topic; those paths are not used as evidence.
- Checked 907 local links/anchors across all nine affected documents, balanced code fences, source/status consistency and `git diff --check`: passed. The link check caught a pre-existing HANDOFF backlog anchor, corrected to `course-evidence-and-delivery`, and a new photo-test link, corrected to the actual filename. Pending handoff links passed after this file was created.
- No Django command or database query was run in this task, so no database target was activated for management/testing. No application, dependency, migration, shared Neon data or media change occurred.
- Application tests, browser sessions, new interviews, MySQL trial, AI productivity benchmark, managed security-control test, clean-machine install and publication were not run. Existing 344-test/T24 results remain historical; this documentation task does not claim a new pass.

## Next action

Jerome/Alex review the persona interpretation and PostgreSQL/supervised-AI recommendations, record actual feedback and reviewer/date in the canonical document, and reconcile T26 status only against that evidence. Preserve limited proxy acceptance rather than inventing detailed interviews, sample sizes or additional mandatory gates. Keep changes uncommitted for review; commit/push/main integration require a separate request.
