---
name: django-mtv
description: Design, implement, review, or refactor Django features in the Campus Equipment Borrowing project using its MTV coding standards and existing contracts. Use for models, forms, views, templates, ORM queries, workflow services, feature tests and manual testing guides; documentation or MCP setup alone does not authorize application implementation.
---

# Django MTV Project Workflow

Use the project's existing Model–Template–View design and preserve the current task scope. This is an instruction-only skill, not a scaffold or an automatic enforcement tool.

## Establish the contract

Read [AGENTS.md](../../../AGENTS.md), the delivery gates in [PLAN.md](../../../PLAN.md), [coding standards](../../../docs/coding-standards.md), and the relevant task/current state in [tasks.md](../../../docs/tasks.md) and [HANDOFF.md](../../../HANDOFF.md). Verify accepted prerequisites are integrated into main before dependent implementation; do not invent missing upstream interfaces. Resolve paths relative to this skill directory. Respect documentation-only authorization until the user explicitly requests implementation.

For the affected feature, read only the needed [architecture](../../../docs/architecture.md), [SRS](../../../docs/SRS.md), [database design](../../../docs/db_design.md), and [route/form contract](../../../docs/api_spec.md). Inspect actual code before adding anything; planned module names are not evidence that files exist. Identify the acceptance behavior and affected owners before changing shared contracts.

## Place responsibilities

Apply the coding guide's responsibility table. Map the requested change to the necessary model/constraint, form/formset, query, workflow service, view, template, and verification boundaries. Do not create unused layers. Keep dispatch in URLs, HTTP orchestration in views, presentation in templates, and complete workflow writes in distinct transaction services.

Preserve the two-role scope and custom admin requirement. Use server-derived actor/owner identifiers, explicit typed inputs, authoritative locked state checks, and audit completeness. Follow the existing lock order; do not invent a second allocation strategy or generic status setter. Keep pure validation/calculation helpers free of caller/global mutation and keep persistence effects explicit.

## Make and review the smallest change

Reuse existing rules and functions. Follow the guide for naming, strict typing, classes limited to required interfaces/data records, explicit parameters, errors, dependency declarations, and Django-native behavior. Do not duplicate business rules in templates, signals, views, and services. Cross-check any schema/state/URL changes with their canonical document and the affected callers.

When reviewing, identify the concrete violation, file/location, consequence, and smallest correction. Do not claim that a template restriction enforces authorization or that SQLite proves PostgreSQL row-lock behavior. Do not add unrelated security infrastructure or testing machinery.

## Verify and transfer

Use the guide's verification table and actual configured project commands. Prefer meaningful real integration checks for the affected behavior; record unavailable commands or unrun checks honestly. For design/documentation work, check links and consistency without adding application code.

For every newly implemented feature, create or update its section in [docs/manual-test-guide.md](../../../docs/manual-test-guide.md) before completing the implementation handoff. Follow the canonical [manual testing guide requirements](../../../docs/coding-standards.md#manual-testing-guide-for-feature-delivery) for concrete Field / Value cases, read-only local record/settings checks, dated examples and honest expected-versus-executed results. Refresh existing cases when their flow changes; keep pending features and member-branch integration state explicit. Guide creation is part of authorized feature work and does not authorize seeding, database writes or publication.

For file-changing work, follow the [project-handoff skill](../project-handoff/SKILL.md) as required by AGENTS.md: save the work snapshot in project-root `handoffs/{title-of-work}-{MM-DD-YYYY}.md` using the current Asia/Manila date, then update HANDOFF.md's current state/index and affected tasks. Preserve other members' work and leave changes uncommitted unless explicitly requested. Summarize the outcome, relevant checks, and remaining limitations. Using this skill alone does not authorize commits, publishing, unrelated dependencies, or database changes beyond the user's requested scope.
