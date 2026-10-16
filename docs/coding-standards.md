# Coding Standards and Django MTV

## Scope and status

These are the shared implementation and review standards for human developers and AI agents working on the Campus Equipment Borrowing System. They apply when implementation is explicitly requested; they do not authorize scaffolding or database changes during the documentation phase.

Use [AGENTS.md](../AGENTS.md) for current authorization, product boundaries, agent coordination, and Git rules. This file is the canonical coding guide. Component ownership and transaction lock order remain in [architecture.md](architecture.md); business behavior in [SRS.md](SRS.md); fields and constraints in [db_design.md](db_design.md); routes/forms in [api_spec.md](api_spec.md). Link those contracts instead of restating their full contents.

## What MTV means

MTV means **Model–Template–View**, Django's terminology for separating data, presentation, and request handling. A Django view is a Python request handler; it chooses the response and data. A template presents that data. URL routing and Django's request machinery perform the dispatch commonly associated with a controller. See [Django's explanation of MTV](https://docs.djangoproject.com/en/5.2/faq/general/#django-appears-to-be-a-mvc-framework-but-you-call-the-controller-the-view-and-the-view-the-template-how-come-you-don-t-use-the-standard-names).

Forms, service functions, and query functions support this project's MTV structure. They are team conventions for organizing validation and operations, not extra letters in Django's pattern or another architectural framework. The existing [MTV diagram](architecture.md#model-template-view-structure) shows the proposed request flow.

| Component | Owns | Must not own |
| --- | --- | --- |
| `models.py` and migrations | Persistent fields, relationships, enum domains, database constraints, indexes, and small record-level behavior | HTTP responses, template rendering, request/session access, or hidden approval/release/return workflows |
| `templates/` | HTML, template inheritance, rendering prepared data, labels, named links, and CSRF fields | Authorization decisions, inventory allocation, database writes, or business calculations hidden in tags/filters |
| `views.py` | HTTP method/access checks, form binding, calling query/service functions, and producing HTML/redirect/download responses | Repeated ORM reporting logic, multi-record workflow mutations, or copied approval/return rules |
| `forms.py` | Explicit field allowlists, parsing, field/form/formset errors, and permitted choice querysets | Trusting hidden fields for actor/owner/role/status or independently committing operational transitions |
| `services.py` | One named business action, authoritative state validation, explicit ORM writes, transactions, locking, and audit completeness | Template rendering, session-dependent implicit inputs, or one generic operation controlled by mode flags |
| `queries.py` | Read-only ORM selection, owner-scoped data, related-object loading, pagination inputs, and aggregates | State changes, request approval, side-effecting reads, or bypassing view authorization |
| `urls.py` | Named, namespaced routes mapped to views | Queries, mutation logic, or duplicated request-processing code |
| `static/` | CSS and small JavaScript enhancements | Deciding server permissions, authoritative due dates, or stock availability |
| Feature tests | Observable access boundaries, business transitions, transaction behavior, and report correctness | Reimplementing the application or asserting incidental source text |

Do not build a parallel `controllers/` hierarchy, generic repository layer over Django ORM, service-class framework, or separate REST backend just to match another pattern. Use Django's native forms, authentication, ORM, migrations, templates, and named URLs. The course-specific prohibition on Django admin remains in AGENTS.md even when a general Django tutorial demonstrates it.

## File placement and dependencies

The feature apps and ownership in architecture.md are the starting point. Keep each app's models, forms, views, URLs, services, queries, and tests near that feature. These are planned locations: create a file when actual work needs it, not an empty scaffold for every possible responsibility.

Views may import forms, services, and query functions. Services and queries may use models and focused validation helpers; they must not import views or templates. Forms may query allowed choices and call pure validation helpers. Models must not import HTTP-facing code. Shared checks belong in one reusable function at the lowest suitable level; do not duplicate a rule to avoid an import.

Keep one management base template and one portal base template, with shared navigation, form, table, and message components. Use namespaced template paths and URL reversing. Split a growing file by real responsibility when needed, preserving a clear public entry point; do not add speculative packages, base classes, or abstractions.

## How a workflow crosses MTV

For an administrator approving a borrowing request:

1. The named approval route invokes a custom view. The view checks HTTP method, signed-in active ADMIN access, and binds the approval form.
2. The form validates its allowlisted reason field. An inventory/borrowing query function prepares availability for display; rendered availability is not permission to allocate later.
3. The view calls the distinct approval service using server-derived actor ID, target request ID, and validated reason. Client-supplied actor, status, or owner fields are ignored as update inputs.
4. The service re-reads and locks authoritative records, checks current permissions/state, reserves complete quantities, and creates the audit record within the transaction specified in architecture.md. Models/database constraints protect the persisted relationships.
5. On success, the view redirects to the named detail route; its template renders the stored result. A recognized state conflict produces the HTTP behavior defined in api_spec.md, without partial writes.

Apply the same responsibility split to cancellation, release, return, maintenance, and settings. Keep each service action separate. Avoid generic ModelForm saves or status assignments that bypass business transitions. Do not hide workflow writes in signals, template helpers, property access, or `save()` overrides. Account/profile creation is explicit through its service so failures roll back together.

## Style, naming, and types

- Match existing project style and make the smallest useful diff. Inspect existing logic first; preserve unrelated changes. Follow DRY, KISS, and YAGNI.
- Use English comments and docstrings. Prefer clear names and short functions with one purpose. Document non-obvious decisions where the code lives rather than adding parallel explanation files.
- Python modules, functions, variables, and model fields use `snake_case`; classes use `PascalCase`; constants and enum values use `UPPER_SNAKE_CASE`. Preserve the exact URL names/namespaces in api_spec.md, such as `borrowing_manage:request-approve`. JavaScript uses `camelCase`; HTML IDs and CSS classes use lowercase hyphenated names.
- Use four spaces in Python, explicit imports, and a consistent standard-library / third-party / project import grouping. Prefer readable expressions to deeply nested or compressed code. Do not declare a new formatter/linter mandatory until the team configures it.
- Type function parameters, returns, variables, collections, and structured internal data. Use concrete models, enums, typed records, or dataclasses as appropriate. Avoid `Any`, broad `object`, loose dictionary payloads, and untyped collections for domain contracts. A small explicit template context mapping is a presentation boundary, not a substitute for typed business data.
- Runtime-validate forms, formsets, environment configuration, and external input. Type annotations do not validate submitted data. Require needed fields and ignore unrelated extras without assigning them to a model.
- Do not define default values for parameters of project-authored functions. Supply every argument explicitly. This does not prohibit Django model/field configuration defaults required by the schema; those are persistence declarations, not optional function parameters.
- Use separate functions for distinct actions; no flag parameters that turn one function into several workflows. Prefer keyword arguments at call sites where they clarify identifiers or multiple similar values.
- Prefer functions and composition. Classes are for necessary external/framework interfaces: ORM database models, forms, authentication managers, and framework test cases. Avoid OOP service hierarchies. Immutable typed records/dataclasses are data contracts, not service objects.

## Pure calculations and explicit database effects

Calculations and reusable validation helpers should be pure: return a value or raise a specific error without mutating input parameters, caller-owned collections/models, or globals. Pass the current campus date/time explicitly when a calculation depends on it so its behavior is clear.

ORM reads/writes and session changes are integration effects and are not pure functions. Keep them at explicit query/service/view boundaries. Workflow services accept identifiers and validated values, load their own records, and update those internally; they must not mutate a model instance supplied by the caller. Avoid shared mutable module state or import-time database work.

Use one transaction for a complete business operation and its audit record. Validate all request/formset rows before any parent/child persistence, then recheck authoritative state while locked. Follow the single lock order in architecture.md. A database constraint and service validation solve different problems; keep both where the contract requires them.

Read-only queries never repair data or change overdue status. Derive reports/statuses through ORM queries and typed calculations. Use related-object loading and aggregate/annotate queries to avoid repeated reads and multiplied totals. Do not add caches/counters before a measured need and an explicit consistency plan.

## Errors, authorization, and privacy

- Raise specific errors that explain the failing operation and actionable cause. Catch only recognized exceptions at the boundary that can handle them; preserve unexpected root causes. No broad catches that return empty data or false success, silent recovery, fallback configuration, or symptom-masking guards unless explicitly requested.
- Map form, access, missing-record, and workflow-conflict outcomes to api_spec.md. User errors must not disclose another borrower's record or internal technical details.
- Log structured fields such as action, request ID, actor ID, and safe error/status information. For authorized external calls, retain useful request parameters/status/response context internally after redacting credentials and personal data; do not interpolate sensitive values into message strings.
- No external API is required. If one is later authorized, use bounded retries with warning logs for retryable failures, then raise the last error. Establish idempotency before retrying a mutation after an ambiguous result; never blindly replay database workflow writes.
- Apply active-account, role, and object ownership checks on every protected route, including exports/print views and any future AJAX endpoints. Mutating services recheck actor/owner eligibility inside their transaction. Hiding a button does not protect its action.
- Use server-side field allowlists, POST for changes, CSRF, Django password validation/hashing, and normal escaping. Never trust role, status, ownership, actors, timestamps, or allocation IDs submitted as hidden fields. Do not disable escaping to solve a presentation problem.
- Keep live credentials and private data out of source, templates, logs, documentation, and seed data. Configuration keys belong in [.env.example](../.env.example); private loading and MCP setup belong in [DEV.md](../DEV.md). The local MCP remains read-only unless the user authorizes a change.

## Dependencies and compatibility

Use the compatible stack in architecture.md and native Django patterns. Add dependencies only to the project environment and declared configuration, never globally. Record tested versions and justify extra packages. Read an installed package's source when behavior is uncertain rather than guessing its API. Do not create a frontend build system, generated admin, ORM wrapper, or new deployment target without a task that needs it.

Do not change a shared field, enum, URL contract, or workflow in one feature without updating its canonical contract and coordinating with affected feature owners. Before the first migration, confirm the custom authentication model. Once migrations exist, preserve shared history and add appropriate migrations rather than independently rewriting another member's schema.

## Minimum verification and review

Use the minimum useful real integration checks for the changed behavior. The foundation configures Django tests and Ruff; follow the commands in [DEV.md](../DEV.md#application-migrations-checks-and-local-server) and applicable project instructions. Do not claim a check ran without its actual result.

| Change | Appropriate evidence |
| --- | --- |
| Protected view, form, export, or portal lookup | Real Django client requests covering valid use, wrong role, inactive account, tampered fields, and owner isolation as relevant |
| Multi-record workflow | Real ORM/database integration covering complete success and relevant rollback, repeat-action, and relationship/state failures |
| Allocation/locking | PostgreSQL `TransactionTestCase` with separate connections demonstrating competing approvals; SQLite-only results are insufficient |
| Return, maintenance, or report | Integration through stored transactions, including partial/damaged returns or correct joined/computed totals as relevant |
| UI change | Smoke/manual or end-to-end checks of the affected flow, useful errors/empty states, keyboard behavior, labels, and responsive layout |

Prefer smoke, integration, and end-to-end checks over tests that mirror implementation. Do not introduce mocks by default where real integrations are practical. Do not test static wording/configuration just to increase a test count. UI automation uses stable IDs, test IDs, or accessibility IDs; no visible-text selectors or fallback clicks.

Reviewers check responsibility placement, explicit trust boundaries, typed inputs, atomic changes/audit, constraint coverage, appropriate query loading, reusable templates, and the relevant SRS acceptance behavior. Avoid unrelated refactoring. Record actual commands/results and unresolved limits; code review and agent instructions are not automatic enforcement.

## Applying the AI skill

[The django-mtv skill](../.agents/skills/django-mtv/SKILL.md) routes Django design, implementation, and review work through this guide. Agents follow AGENTS.md first, use the skill for relevant Django work, and finish file-changing work with the existing handoff workflow. Other AI tools that do not discover project instructions must be given the files explicitly. The skill contains no application scaffold, executable hook, or permission to begin implementation.
