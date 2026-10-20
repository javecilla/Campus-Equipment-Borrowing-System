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
| `static/` | Source CSS, fonts, images, and small JavaScript enhancements; ignored build output | Deciding server permissions, authoritative due dates, or stock availability |
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
- Python modules, functions, variables, and model fields use `snake_case`; classes use `PascalCase`; named constants and enum values use `UPPER_SNAKE_CASE`. Preserve the exact URL names/namespaces in api_spec.md, such as `borrowing_manage:request-approve`. JavaScript identifiers use `camelCase`, browser module filenames use `kebab-case.js`, and project-authored HTML IDs/data attributes use lowercase hyphenated names. Tailwind utilities retain the library's syntax, including responsive/state prefixes.
- Use four spaces in Python, explicit imports, and a consistent standard-library / third-party / project import grouping. Prefer readable expressions to deeply nested or compressed code. Use the configured formatter for each language, as described below.
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

Use the compatible stack in architecture.md and native Django patterns. Add dependencies only to the project environment and declared configuration, never globally. Record tested versions and justify extra packages. Read an installed package's source when behavior is uncertain rather than guessing its API. The Tailwind and page-script build is configured; do not add another frontend framework, generated admin, ORM wrapper, or new deployment target without a task that needs it.

Every dependency change updates the appropriate Python input/pins or npm manifest/lockfile, the [README disclosure](../README.md#third-party-packages-and-assets), and the complete [dependency inventory](third-party-dependencies.md), including indirect/optional packages and license metadata. Explain the need, runtime versus development role, and relevant limitation. Preserve supplied notices, include required notices with any newly authorized browser-bundled packages, rebuild, and run the configured package/build checks; an inventory/lockfile does not replace those notices or the justification.

Do not change a shared field, enum, URL contract, or workflow in one feature without updating its canonical contract and coordinating with affected feature owners. Before the first migration, confirm the custom authentication model. Once migrations exist, preserve shared history and add appropriate migrations rather than independently rewriting another member's schema.

## HTTP endpoint design

The project uses a **server-rendered command/query HTTP pattern**: GET reads or displays a form; a named POST action validates a form and invokes one workflow service. This is the project's API/interface design convention within MTV. [api_spec.md](api_spec.md#common-protocol) owns request encodings, status codes, redirects, fields, pagination, and access rules. Adding calling conventions does not authorize a separate REST backend, Django REST Framework, JWT authentication, or undocumented JSON endpoints.

- Reuse the contracted paths/namespaces. Use integer path converters, noun-based list/detail paths, and explicit action routes such as request approval or maintenance closure. Match the existing kebab-case URL names; Python view/service names remain snake_case. Do not rename routes to impose a second convention.
- Keep one endpoint action and service per business operation. Never introduce a generic status setter, a mode-switching endpoint, or arbitrary model-field updates. HTTP method checks, active/role/owner authorization, form parsing, and rendering belong at their existing MTV boundaries.
- Bind Django forms/formsets with explicit field allowlists; GET filters and path values also require validation. Derive actors, owners, roles, and operational state server-side. Reuse query helpers and workflow services rather than implementing a second AJAX business path.
- Follow the response/status table exactly. In particular, invalid bound forms return 200 HTML, successful mutations return a named 302 redirect, and workflow conflicts return 409. Do not globally change these to 422/JSON or convert failures to successful empty responses. Wrong methods, permissions, missing objects, and unexpected errors retain the documented semantics.
- New programmatic response formats require an explicitly authorized feature and a corresponding HTTP-contract update: document method/name, access, accepted fields, content type, success/error shape, and checks before implementation. Use snake_case for newly agreed JSON field names to match server/form fields; do not add a universal envelope or serializer framework for a hypothetical API.

<a id="axios-calling-pattern"></a>

## Browser interactions

Use native Django form submission and links for the current server-rendered interface, including login and CSRF-protected POST logout. No browser HTTP library or shared JavaScript request client is installed. Do not reintroduce Axios or add a transport abstraction for hypothetical use.

Page modules own browser behavior; domain decisions, validation, authorization, and workflow writes remain on the server. Load actual compiled page modules through the shared shell's scripts block, use stable data-testid values for automation, and keep JavaScript in its feature source file.

If an explicitly authorized feature needs a browser request, use native browser APIs and first document its named route, encoding, response, and access rules in [the HTTP contract](api_spec.md#common-protocol). Preserve same-origin sessions and Django CSRF protection for mutations. Existing HTML redirects, invalid-form responses, and CSV downloads retain their native behavior; HTTP 200 alone does not establish workflow success. Validate any data consumed, report actionable failures, bound requests, and never silently retry mutations. No JSON API or browser request helper is implemented by this guidance.

## Tailwind styling pattern

Use [app.css](../static/css/app.css) as the single Tailwind entry/theme and [base.html](../templates/base.html) as the document/asset shell. The two role layouts extend that shell; feature pages extend their role layout and reuse real navigation/form/table/message components. Do not duplicate complete page shells, create an admin generator, or add a second CSS framework.

Keep both roles and shared error pages in light mode unless an explicit requirement calls for another theme. UI-09 follows the user's modern minimal dashboard reference: white panels, neutral gray canvas, deep slate text, teal active navigation, subtle borders/shadows and compact rounded controls. Shared semantic status roles and elevation/motion tokens remain in use. Use the common page, form, table and button classes below; avoid per-feature palettes, arbitrary narrow page caps, decorative dashboard metrics and unnecessary controls. Feature pages extend `operations/manage/base.html` or `accounts/portal/base.html` and fill `workspace_content`; both inherit shared navigation, messages, and CSRF-protected POST logout from `components/workspace.html`. Pending features may link to the explicitly authorized, protected GET-only placeholders listed in [the HTTP contract](api_spec.md#status-and-interface-choice); keep their pending status visible and do not add pretend forms or metrics. The [backlog](tasks.md) remains canonical for owners, prerequisites, and status. Preserve the role layout when replacing a placeholder with its real module.

At 1024px and wider, the workspace uses a 240px sticky sidebar with brand, line-icon navigation and a red Log out action pinned to the bottom. Log out reuses the navigation row's icon size, spacing and padding through `components/logout.html`, retaining its native CSRF-protected POST form. Smaller screens show Log out beside the brand above scrolling navigation. `components/account_link.html` places the profile image, display name and role in the top workspace bar as one direct link to the signed-in user's profile; there is no dropdown or account-menu script. Profile identity comes from the signed-in account, never a URL-supplied user ID. Display names use uppercase last name plus first initial. Default role avatars are supplied assets, not profile uploads. Below 640px the workspace label is hidden to keep the profile identity visible within the bar.

- Prefer shared `ui-*` component classes for repeated controls/layouts and Tailwind utilities for page-specific composition on semantic, accessible HTML. Reuse established components and spacing/typography decisions before inventing new ones. Use font-sans (DM Sans) for body/control text and font-heading (Poppins) for headings; keep shared design values in the existing theme when a real repeated need appears.
- Write complete literal utility names, including every conditional alternative, in the configured template/Python/JS sources. Never concatenate utility fragments such as bg-{{ color }}-500, and never derive arbitrary classes directly from submitted values. Forms provide `ui-input` or `ui-input ui-textarea` widget classes; keep field IDs, validation attributes and native input types. Visible markup remains in templates.
- Use a stable human grouping: layout/display, positioning/sizing, spacing, typography, colors/borders, effects, then responsive/state variants. Use mobile defaults with explicit breakpoint changes, visible focus-visible styles, disabled/pending states, readable contrast, and text/ARIA feedback in addition to color. Tailwind class sorting is a review convention here; the configured formatters do not automatically sort Django class attributes.
- Project-authored component names, IDs, and data attributes are kebab-case; keep Tailwind's own utility names unchanged. Use explicit data-action-url/data-testid attributes for behavior and automation rather than binding JavaScript to a styling class or visible label.
- Use the standard spacing/color/type scales first. Add arbitrary values or custom selectors only for an actual requirement that the existing scale/component cannot express. Keep necessary reusable CSS in static/css/app.css and use layers so utility overrides remain predictable; do not introduce repeated style attributes, scattered CSS files, or speculative @apply component systems.
- Keep scripts and styles in their source files rather than embedding large blocks in Django HTML. Load compiled modules in the scripts block and compiled CSS through the shared shell. Build output and third-party font/license files are generated/vendor material and must not be hand-formatted.

### Shared M3 roles and components (UI-09)

The shared design system is integrated through PR #39 at `a35e0f1`. [app.css](../static/css/app.css) owns the fixed semantic roles, dashboard utility colors and shared shapes; [base.html](../templates/base.html) loads the compiled stylesheet once. Primary is `#1b5a5a`, canvas `#f8f9fa`, and panel `#ffffff`. Existing `--md-sys-color-*` names are stable CSS tokens, with no Material Color Utilities dependency or palette generator. [The dependency-free contrast check](../scripts/check-theme.mjs) rejects nine text-role pairs below 4.5:1 during CSS builds. Retain DM Sans/Poppins and light mode.

| Component | Shared pattern |
| --- | --- |
| Page canvas | `ui-page` inside the shared `ui-main`; fluid 16–40px gutters beside the desktop sidebar or below compact navigation. Keep paragraph line lengths readable. |
| Page headings and actions | `ui-page-header`; compose title/actions with existing flex utilities where needed; preserve one meaningful h1. |
| Filters and catalog | `ui-filter-grid` and `ui-catalog-grid` adapt tracks to available width; avoid fixed-width filter columns. |
| Edit forms | `ui-form-grid` uses one column below 840px and two above; `ui-span-full` and `ui-actions` span the grid. The request form uses `ui-request-layout` for a 1:2 details/items split from 1280px. |
| Fields | `ui-input`, plus `ui-textarea` for a resizable 8rem text area; 48px minimum controls, persistent labels and native validation/error associations. |
| Buttons | `ui-button` with `--primary`, `--tonal`, `--outline`, `--text`, `--danger` or `--danger-tonal`; retain POST/CSRF and meaningful labels. Do not restyle each feature independently. |
| Surfaces and tables | `ui-surface`, `ui-table-surface`, `ui-data-table`; use shared shadows for depth, consistent cell padding and local horizontal scrolling. Keep table headers positioned so visually hidden labels stay within their scroller. |
| Navigation | `ui-nav-link` uses `aria-current`; primary destinations include shared decorative line icons. `data-scroll-navigation` keeps the current link visible on compact screens. Log out uses `ui-nav-link--danger`; `ui-account-link` is a native profile link in the top bar. |
| Home panels | `ui-dashboard-grid` uses a 1.8:1 split from 1200px; existing feature shortcuts and workspace tools remain real named links. |
| Motion | Shared 160/240ms timing, subtle hover lift and press scale; `prefers-reduced-motion` suppresses transitions and smooth scrolling. Focus rings remain visible without relying on motion. |

Use role tokens for new semantic colors. Slate utilities use the neutral Tailwind scale with readable muted/on-surface text overrides; emerald/rose/amber utilities retain shared primary/error/tertiary roles. Distinct status text remains required. For frontend work, load [campus-ui](../.agents/skills/campus-ui/SKILL.md), which routes agents through this canonical component table and actual source examples rather than maintaining a second design specification. T15 release/date/loan pages and T17 returns are integrated; T18/T19 pages remain pending; home shortcuts link only to existing features. T20's complete cross-workflow acceptance still requires its original prerequisites. See [Module 14](manual-test-guide.md#module-14--shared-m3-layout-and-controls-ui-09) for actual UI checks and remaining limits.

## Formatting ownership

T15's standalone printable borrowing slip extends `base.html`, reuses the loan summary/assets partial and hides its controls for printing. Its active-admin access is checked directly by the print view. Ordinary release/date/loan pages extend the management role shell; this print document does not introduce a second navigation layout or palette.

| Files | Configured formatter | Team rule |
| --- | --- | --- |
| Python | Ruff in pyproject.toml | Four spaces and the existing import/lint rules; Prettier does not format Python |
| JavaScript/MJS, CSS, project JSON | Prettier in .prettierrc.json | Four spaces for JS/CSS, two for JSON, 100-column wrapping, double quotes, semicolons, and LF output |
| Django HTML templates | djLint's Django profile in pyproject.toml | Four spaces and 100-column wrapping; Prettier explicitly ignores HTML to avoid treating Django tags as plain HTML |
| Markdown | Prettier supports explicitly selected files | Preserve prose wrapping; do not reformat archived handoffs, source briefs, or unrelated documents as part of a feature |

Run the [format/check commands in DEV.md](../DEV.md#formatting-and-code-consistency). Use the pinned project tools, not globally installed versions or an editor's generic HTML formatter. Keep large JavaScript/CSS in separate files; djLint does not format embedded scripts/styles in this configuration. Run formatters on owned files and inspect the diff, especially around template tags. Formatting normalizes whitespace; it does not enforce architecture, access control, Tailwind class ordering, runtime types, or workflow correctness. No formatter hook or CI enforcement is installed by these configuration files.

## Minimum verification and review

Use the minimum useful real integration checks for the changed behavior. Django tests, Ruff, Prettier source checks, and djLint template-format checks are configured; follow the commands in [DEV.md](../DEV.md#before-handing-over-work) and applicable project instructions. Do not claim a check ran without its actual result.

| Change | Appropriate evidence |
| --- | --- |
| Protected view, form, export, or portal lookup | Real Django client requests covering valid use, wrong role, inactive account, tampered fields, and owner isolation as relevant |
| Multi-record workflow | Real ORM/database integration covering complete success and relevant rollback, repeat-action, and relationship/state failures |
| Allocation/locking | PostgreSQL `TransactionTestCase` with separate connections demonstrating competing approvals; SQLite-only results are insufficient |
| Return, maintenance, or report | Integration through stored transactions, including partial/damaged returns or correct joined/computed totals as relevant |
| UI change | Smoke/manual or end-to-end checks of the affected flow, useful errors/empty states, keyboard behavior, labels, and responsive layout |

Prefer smoke, integration, and end-to-end checks over tests that mirror implementation. Do not introduce mocks by default where real integrations are practical. Do not test static wording/configuration just to increase a test count. UI automation uses stable IDs, test IDs, or accessibility IDs; no visible-text selectors or fallback clicks.

Reviewers check responsibility placement, explicit trust boundaries, typed inputs, atomic changes/audit, constraint coverage, appropriate query loading, reusable templates, and the relevant SRS acceptance behavior. Avoid unrelated refactoring. Record actual commands/results and unresolved limits; code review and agent instructions are not automatic enforcement.

## Manual testing guide for feature delivery

Every newly implemented feature must have manual testing instructions before its implementation handoff is complete. Update its section in [docs/manual-test-guide.md](manual-test-guide.md), creating that shared guide if it does not exist. Update existing cases whenever a change alters their documented behavior. Keep one consolidated guide rather than a separate manual per feature; documentation-only changes and read-only questions do not require unrelated new test cases.

Base the instructions on actual code, routes, forms, permissions and observable stored results. Identify the task/revision, entry URL, required role and setup. Distinguish a verified member-branch feature from an integrated main feature, and mark later workflow steps as pending until implemented.

- Provide concrete **Field / Value** tables for successful examples, relevant invalid inputs and boundaries, and applicable role/ownership, state-transition or rollback checks. State the expected redirect, error and database effect, with a verification path that exists now. Include a read-only inspection step when the current UI cannot show a required result; do not direct users to a planned page.
- Check permitted local test records and current settings using read-only queries. Select examples whose record relationships, archive/status flags and configured limits match the implemented rules; available stock alone does not determine every action's eligibility. Publish only fictional or non-sensitive values, with exact labels/IDs where useful. Do not create or change database rows merely to author the guide.
- Date verified examples in Asia/Manila and record the relevant revision/settings. Explain how to recalculate date/quantity boundaries and recheck record eligibility when those values change. If the database or required records cannot be inspected, document the missing prerequisite and unverified inputs; never invent records or present stale examples as a current database check.
- Separate **expected results** from actual execution evidence. Supply a place to record real outcomes, known limitations and Not run cases. Writing the guide does not prove that browser, keyboard, mobile or database checks passed, and a correctly rejected invalid submission is a passing validation case.

Check the affected guide links, example inputs and command paths before handoff, then link its feature section and record any missing data or unrun checks in the dated handoff. Reconcile its integration labels after a real main merge. These are required steps for contributors and agents following the project instructions; no background generator or automatic execution hook is installed.

## Applying the AI skill

[The django-mtv skill](../.agents/skills/django-mtv/SKILL.md) routes Django design, implementation, and review work through this guide. Agents follow AGENTS.md first, use the skill for relevant Django work, and finish file-changing work with the existing handoff workflow. Other AI tools that do not discover project instructions must be given the files explicitly. The skill contains no application scaffold, executable hook, or permission to begin implementation.
