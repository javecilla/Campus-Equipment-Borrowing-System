# Campus Equipment Borrowing System

A Python/Django application under development for requesting and managing campus equipment. The intended system lets basic users browse equipment, submit borrowing requests, and track their own transactions. Administrators manage accounts, physical inventory, approvals, equipment release, returns, maintenance, reports, and audit history through custom pages.

Private team repository: [javecilla/Campus-Equipment-Borrowing-System](https://github.com/javecilla/Campus-Equipment-Borrowing-System). Member branches and the main integration workflow are documented in [DEV.md](DEV.md#assigned-branches-and-main-integration).

The system tracks individual physical units by asset code, preserves their transaction history, and prevents the same unit from being reserved or issued to multiple borrowers simultaneously.

**Current phase: T01–T19 are Done and integrated.** Alex's T19 reports reached main through PR #49 at `e8f2a19`, source `16e1d4c`; source/merge tree equality and the five T20 prerequisite integrations are verified. The combined application passes **315 PostgreSQL tests in 57.317s**. Ralph / T20 has all prerequisites satisfied and remains Not started. Browser/mobile/keyboard/spreadsheet checks remain pending. See [current readiness](HANDOFF.md), [task evidence](docs/tasks.md#verified-task-evidence), [T20 consumer handoff](DEV.md#t20-readiness-and-consumer-handoff) and [T19 review](handoffs/t19-main-review-and-local-merge-conflict-resolution-10-21-2026.md).

**Dashboard/workspace enhancement (UI-11/UI-12, integrated through PR #48 at `9d67fab`):** Chart.js 4.5.1 renders monthly loan columns with zero-issue months and category usage bars ranked by issued units. Live card links, exact-value tooltips and accessible tables retain real Django transaction data. Kiro-assisted improvements add shortcut rows, an active-ADMIN Pending-request badge and consistent filter/sidebar styling. All **301 PostgreSQL tests pass**; combined desktop/mobile, keyboard, badge and no-JavaScript checks pass. Run `npm.cmd ci` and `npm.cmd run build` after syncing. See [publication review](handoffs/dashboard-and-workspace-publication-review-10-20-2026.md).

**Shared UI refresh (UI-09):** integrated through PR #39 at `a35e0f1` (source `043822e`), preserved in main `866eb7e`. Existing pages follow the supplied minimal dashboard reference with teal navigation, white panels, a neutral canvas, a desktop sidebar, adaptive grids and consistent controls. The fixed palette no longer needs Material Color Utilities. Run `npm.cmd ci` and `npm.cmd run build` after syncing this work; see [styling conventions](docs/coding-standards.md#shared-m3-roles-and-components-ui-09) and [UI checks](docs/manual-test-guide.md#module-14--shared-m3-layout-and-controls-ui-09). Frontend agents use the shared [campus-ui skill](.agents/skills/campus-ui/SKILL.md), explicitly invoked as `$campus-ui` when needed.

## Run locally

Install Python 3.13, PostgreSQL 17, and Node.js 22+/npm 10+, open the project root on [your assigned branch](DEV.md#assigned-branches-and-main-integration), and create the local `campus_equipment` database as described in [DEV.md](DEV.md#create-your-local-database).

1. Create the project environment and install the pinned development dependencies:

    ```powershell
    py -3.13 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    ```

2. If `.env.local` does not exist, create it from the template, then fill its required `DB_*` and `DJANGO_*` values using [the environment guide](DEV.md#create-and-edit-envlocal). Keep an existing private file.

    ```powershell
    New-Item -Path .env.local -ItemType File -Value (Get-Content -LiteralPath .env.example -Raw) -ErrorAction Stop
    ```

3. Install the locked frontend packages and build Tailwind CSS/browser modules:

    ```powershell
    npm.cmd ci
    npm.cmd run build
    ```

4. Check configuration, apply migrations, run the integration tests, and start the local server:

    ```powershell
    .\.venv\Scripts\python.exe manage.py check --database default
    .\.venv\Scripts\python.exe manage.py migrate --noinput
    .\.venv\Scripts\python.exe manage.py test --noinput
    .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
    ```

Open <http://127.0.0.1:8000/> for the custom sign-in route. The debug-only Tailwind/font preview remains at <http://127.0.0.1:8000/test>; see [the frontend preview](DEV.md#frontend-preview). Migrations initialize loan limits but create no accounts; use [`seed_auth_accounts`](DEV.md#seed-authentication-test-accounts) for one fictional account per role with a shared private environment password, or [`create_admin`](DEV.md#create-an-administrator-account) for a local administrator. Stop the server with Ctrl+C (Ctrl+Break on Windows if needed).

See the [earlier startup screenshot](DEV.md#earlier-startup-screen) and [everyday startup commands](DEV.md#everyday-startup) in DEV.md. During frontend work, keep `npm.cmd run dev` running in a second terminal to rebuild CSS/JavaScript after edits.

For migration changes, test-database permissions, dependency updates, checks, and team synchronization, follow [DEV.md](DEV.md#application-migrations-checks-and-local-server). No clean-machine or complete product demonstration is claimed yet.

After receiving the T07 continuation, reinstall the pinned Python dependencies (including Pillow), apply migrations and rebuild assets. Equipment photos are optional and stored in local `media/equipment/`; the database stores their relative paths. Each teammate supplies their own uploads. See [photo storage and controls](DEV.md#equipment-photos-and-local-media) and [T08 preparation](DEV.md#continuing-with-t08). Local `.idea/` settings are ignored and are no longer tracked.

## Project folder structure

See [Project Folder Architecture](docs/project-folder-architecture.md) for the full tree, existing versus planned files, and where to add models, views, forms, services, templates, and static files.

## Part 6: submission and presentation

Use this as an evidence index for [Part 6 of the course brief](docs/Project-Requirements.txt). **The project is not submission-ready yet.** Existing design documents and feature integration tests provide partial evidence; they do not prove completed workflows or full-system acceptance. [The backlog](docs/tasks.md#course-evidence-and-delivery) owns task status, and [HANDOFF.md](HANDOFF.md) owns current readiness.

| Required evidence                                                 | Where to look                                                                                                                                                                                               | Current coverage / remaining work                                                                                                                                                                                |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| User needs and options                                            | [Requirements](docs/SRS.md), [stakeholders/personas](docs/PRD.md#users-and-stakeholders), [two-option comparison](docs/architecture.md#options-comparison)                                                  | Design evidence exists; actual acceptance findings, resolved issues, feedback-driven enhancement, and maintenance evidence remain pending: T23, T24, T26                                                         |
| MTV, database, and workflow diagrams                              | [MTV diagram](docs/architecture.md#model-template-view-structure), [database ERD](docs/db_design.md#relationships), [workflow diagram](docs/architecture.md#workflow-view)                                  | Partial drafts exist; tool-based conversion under T25 is on standby until Jerome confirms system completion and gives the go signal; see [current responsibilities](docs/tasks.md#current-ownership-and-support-responsibilities) |
| Working system, constraints, tests, limitations, and enhancements | [System requirements](docs/SRS.md), [database constraints](docs/db_design.md), [verified task evidence](docs/tasks.md#verified-task-evidence), [test/check commands](DEV.md#before-handing-over-work) | T01–T18 integrated. Reporting, full acceptance and final system evidence remain pending |
| Technology choices and development records                        | [Tool justifications](#third-party-packages-and-assets), [dependency inventory](docs/third-party-dependencies.md), [coding standards](docs/coding-standards.md), [work records](handoffs/)                  | Selected tools and foundation records exist; emerging-technology evaluation and adopt/defer recommendation remain pending: T26                                                                                   |
| Professional judgment, standards, ethics, and legal requirements  | [Security/privacy requirements](docs/SRS.md#non-functional-requirements), [contribution/licensing guidance](CONTRIBUTING.md), [evidence task](docs/tasks.md#course-evidence-and-delivery)                   | Design safeguards exist; applicable codes/policies, stakeholder duties, risks, decisions, and accountability need actual supported evidence: T27                                                                 |
| Team and individual participation                                 | [Assignments](docs/Project-Members.txt), [collaboration guidance](CONTRIBUTING.md), [work handoffs](handoffs/)                                                                                              | Allocation/history exists; every member still needs leadership-rotation, contribution, peer-feedback, individual/team evaluation, and improvement evidence: T28                                                  |
| Technical, basic-user, and admin guides                           | [Technical setup/development guide](DEV.md), [guide task](docs/tasks.md#course-evidence-and-delivery)                                                                                                       | Technical setup exists; verified user/admin guides and complete maintenance guidance remain pending: T24, T29                                                                                                    |
| ZIP, seed, and demonstration access                               | [Required fictional dataset](docs/tasks.md#required-fictional-demonstration-dataset), [packaging task](docs/tasks.md#course-evidence-and-delivery)                                                          | Source/migrations/requirements and a two-account authentication seed exist; the full demonstration dataset, final ZIP, and clean-machine verification remain pending: T21, T30                                                                           |
| Week 17 demonstration and Q&A                                     | [Presentation task](docs/tasks.md#course-evidence-and-delivery)                                                                                                                                             | T31: rehearse a 12-minute demo plus 3-minute Q&A covering both roles, workflows, validation, access restrictions, conflicts, and reports; every member presents and participates, with feedback/actions recorded |
| Reuse, third-party assets, and AI disclosure                      | [Package/asset disclosures](#third-party-packages-and-assets), [licensing boundaries](CONTRIBUTING.md), [professional evidence task](docs/tasks.md#course-evidence-and-delivery)                            | Dependency notices and Codex co-author records exist; the formal AI/reuse declaration must follow the BulSU AI Policy and instructor instructions: T27                                                           |

The final package must be named `IT401W_ProjectA_Section_Group.zip`. Submit demonstration credentials for **one admin and two basic users** through the instructor-designated channel; exclude secrets and private data from the ZIP/repository. Individual evidence must address all four indicators under PO-d, PO-e, PO-g, PO-h, PO-j, and PO-n using the actual course rubric.

## Project scope

The application has exactly two roles: `BASIC_USER` and `ADMIN`. Development emphasizes the custom administration side, approximately 75% of the work, with approximately 25% for basic-user features. Django's generated admin interface is prohibited.

The principal workflow is request submission, review, reservation, release, and return. Partial returns, damaged equipment, overdue monitoring, and maintenance are included. Payments, fines, procurement, supplier portals, and third-party integrations are outside the required scope.

## Technology

| Technology                      | Planned purpose                                                             |
| ------------------------------- | --------------------------------------------------------------------------- |
| Python 3.13                     | Application language                                                        |
| Django 5.2 LTS                  | Model-template-view application, authentication, forms, ORM, and migrations |
| PostgreSQL 17                   | Relational storage, database constraints, and transactional row locking     |
| Psycopg 3                       | Django's PostgreSQL database driver                                         |
| Django templates, HTML, and CSS | Server-rendered pages and reusable role layouts                             |
| JavaScript                      | Small progressive enhancements and database-backed charts                   |
| Tailwind CSS                    | Compiled utility styling for handwritten Django templates                   |
| Node.js/npm                     | Locked local CSS/JavaScript build and watch tools                           |
| Django test framework           | Integration, authorization, and transaction tests                           |

The foundation uses this stack. Exact tested Python packages are pinned in [requirements.txt](requirements.txt), with Ruff in [requirements-dev.txt](requirements-dev.txt). JavaScript packages and their lockfile are declared separately in [package.json](package.json). Library rationale, required architectural patterns, database options, and references are in [architecture.md](docs/architecture.md#required-patterns-and-selected-libraries).

## Third-party packages and assets

The [course brief](docs/Project-Requirements.txt), Part 5, permits third-party packages when declared and justified, and prohibits generating the custom admin interface. These packages support our handwritten Django views/forms/templates; none supplies the required admin pages. The team selected Tailwind under that general permission; the brief does not name it specifically. HTTP interactions use native Django forms and links without a browser request library.

| Package / asset                                                                                                     | Used for / why selected                                                                                        | Scope and tradeoff                                                                                                                        | License                             |
| ------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Django                                                                                                              | MTV, ORM, migrations, forms, sessions/authentication, and tests required by the brief                          | Application runtime; custom role pages remain team-authored                                                                               | BSD-3-Clause                        |
| psycopg and psycopg-binary (`psycopg[binary]`)                                                                      | PostgreSQL driver for the selected real locking/constraint strategy; binary wheels simplify local installation | Application runtime; depends on a running PostgreSQL service                                                                              | LGPL-3.0-only; retain wheel notices |
| python-dotenv                                                                                                       | Parse each workstation's ignored private environment file using a maintained parser                            | Application runtime; our strict configuration validation remains authoritative                                                            | BSD-3-Clause                        |
| Pillow | Validate, orient, resize and re-encode optional equipment photos | Runtime; local image processing, no external service or generated admin; retain wheel/native-library notices | MIT-CMU and bundled library notices |
| Ruff                                                                                                                | Fast Python lint/import checks and formatting in one existing tool                                             | Development only; checks style, not workflow correctness                                                                                  | MIT                                 |
| djLint                                                                                                              | Format Django template tags/HTML with a Django-aware profile                                                   | Development only; GPL-3.0-or-later tool, not bundled into application assets; Python remains Ruff's responsibility                        | GPL-3.0-or-later                    |
| tailwindcss and @tailwindcss/cli                                                                                    | Compile responsive utility styling for handwritten Django templates                                            | Build only; more custom markup/component work than Bootstrap; adds a local CSS build                                                      | MIT                                 |
| Chart.js 4.5.1 | Render the two required dashboard charts with meaningful axes, exact-value tooltips and shared colors | Browser runtime, bundled locally; retains server-rendered data tables for accessible/non-JavaScript access; adds a canvas bundle | MIT; [bundled notices](static/licenses/chartjs-MIT.txt) |
| esbuild                                                                                                             | Compile/minify page JavaScript into browser-ready ES modules                                                 | Build only; keeps page scripts minified and supports the existing watcher; adds no separate frontend server                                                               | MIT                                 |
| concurrently                                                                                                        | Run CSS and JS watchers through one cross-platform command                                                     | Development only; keeps Django in its own terminal and stops sibling watchers on exit                                                     | MIT                                 |
| Prettier                                                                                                            | Consistent JS/MJS, CSS, and JSON formatting; supports deliberately selected Markdown too                       | Development only; no built-in Python/Django-template formatting is used; separate formatters handle those languages                       | MIT                                 |
| [Tailwind CSS IntelliSense](https://github.com/tailwindlabs/tailwindcss-intellisense) (`bradlc.vscode-tailwindcss`) | Tailwind-aware VS Code language mode, completions, and diagnostics for custom CSS syntax                       | Optional editor extension recommended by the workspace; installed separately from npm; see [editor setup](DEV.md#tailwind-css-in-vs-code) | MIT                                 |
| DM Sans and Poppins fonts                                                                                           | Locally served body/heading typography without a font CDN                                                      | Runtime assets; supplied OFL notices remain with the font files                                                                           | SIL OFL-1.1                         |
| Default admin/basic-user profile illustrations | User-supplied role avatars for the account dropdown and My profile | Local runtime images; provenance recorded in the [asset inventory](docs/third-party-dependencies.md#supplied-assets-and-optional-inspection-tooling) | Source/license not supplied |
| Default equipment photo | User-supplied WebP placeholder when a catalog item has no uploaded photo | Local runtime asset; [photo/storage setup](DEV.md#equipment-photos-and-local-media) and provenance in the asset inventory | Source/license not supplied |
| @bytebase/dbhub 1.5.0                                                                                               | Optional, separately authorized read-only PostgreSQL inspection through MCP                                    | Developer tooling through npm's execution cache; not a Django dependency or application HTTP integration                                  | MIT                                 |

Exact application/tool pins and all indirect Python/npm packages, their parent dependencies, optional platform binaries, and license metadata are disclosed in the [complete third-party inventory](docs/third-party-dependencies.md). The inventory includes the indirect support packages (for example asgiref/sqlparse/tzdata and djLint's CLI/parsing dependencies), rather than implying only the direct packages exist. Python pins live in [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt); npm pins live in [package-lock.json](package-lock.json). Optional DBHub's own dependency declaration is linked separately in the inventory because its execution-cache dependencies are not part of the application's lockfile.

The root [MIT license](LICENSE) applies to original team contributions; dependency, font, instructor, and upstream notices keep their own terms. The dashboard bundle includes Chart.js and its indirect color dependency; their full MIT notices are retained in [static/licenses/chartjs-MIT.txt](static/licenses/chartjs-MIT.txt). Supplied font notices remain with the assets. Refresh declarations, rationale, inventory, and relevant notices together whenever dependencies change; [DEV.md](DEV.md#updating-dependencies) owns the commands. No Django admin generator, Django REST Framework or frontend SPA framework is installed.

## Project members

| Member                      | GitHub                                         | Assigned responsibility                                         |
| --------------------------- | ---------------------------------------------- | --------------------------------------------------------------- |
| Avecilla, Jerome S.         | [@javecilla](https://github.com/javecilla)     | T15 release/slips; T16 maintenance; system completion and diagram go signal |
| Cayanan, Alex Enrico        | [@AlexCayanan](https://github.com/AlexCayanan) | T18 dashboard; T19 reports |
| Cortez, Kenneth T.          | [@corkenneth](https://github.com/corkenneth)   | Validation, documentation, manual testing; diagrams on standby |
| Ignacio, Margareth Raine H. | [@raifun](https://github.com/raifun)           | Validation, documentation, manual testing; diagrams on standby |
| Regodon, Ma. Ellyssa Bianca | [@ellieebeann](https://github.com/ellieebeann) | Validation, documentation, manual testing; diagrams on standby |
| Giga, Ralph Andre F.        | [@dreygigz](https://github.com/dreygigz)       | T17 returns; T20 UI integration |

Current assignments follow the October 20 [ownership and support responsibilities](docs/tasks.md#current-ownership-and-support-responsibilities); [Project-Members.txt](docs/Project-Members.txt) preserves original assignments and branches. Existing contributor credit remains intact, including Kenneth's completed T16 baseline. All members still contribute code, documentation, testing and an individual presentation segment. Kenneth, Margareth and Ellyssa will convert the partial MTV/database/workflow drafts into editable diagrams in an actual tool such as Lucidchart after system completion and Jerome's explicit go signal, subject to T25's prerequisites.

## Documentation

| File                                                                  | Purpose                                                                                     |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [Project-Requirements.txt](docs/Project-Requirements.txt)             | Original course requirements                                                                |
| [Project-Members.txt](docs/Project-Members.txt)                       | Original team assignments and schedule                                                      |
| [PLAN.md](PLAN.md)                                                    | Full-system delivery order, member handoff gates, and agent task selection                  |
| [team-agent-prompts.md](docs/team-agent-prompts.md)                   | Copy-and-paste feature or validation/documentation/manual-testing prompts for each member                        |
| [PRD.md](docs/PRD.md)                                                 | Product goals, audiences, scope, and success criteria                                       |
| [SRS.md](docs/SRS.md)                                                 | Functional requirements, business rules, and acceptance criteria                            |
| [architecture.md](docs/architecture.md)                               | Proposed components, responsibilities, and concurrency design                               |
| [project-folder-architecture.md](docs/project-folder-architecture.md) | Existing/planned folders, feature file locations, and how to add a page                     |
| [db_design.md](docs/db_design.md)                                     | Proposed entities, fields, relationships, and constraints                                   |
| [api_spec.md](docs/api_spec.md)                                       | Proposed page routes, form inputs, and HTTP behavior                                        |
| [AGENTS.md](AGENTS.md)                                                | Project instructions and AI collaboration rules                                             |
| [coding-standards.md](docs/coding-standards.md)                       | Canonical Django MTV, coding, and verification standards                                    |
| [third-party-dependencies.md](docs/third-party-dependencies.md)       | All locked Python/npm packages, parent dependencies, optional entries, and license metadata |
| [User-needs evidence guide](docs/user-needs-evidence-guide.md)       | T26 collection questions, recording worksheets, option comparison, and technology evaluation |
| [django-mtv skill](.agents/skills/django-mtv/SKILL.md)                | Reusable Django design, implementation, and review workflow                                 |
| [DEV.md](DEV.md)                                                      | Workstation, private environment, local PostgreSQL, and MCP setup                           |
| [.env.example](.env.example)                                          | Shared application/MCP configuration keys with empty secret values                          |
| [.agents/mcp.json](.agents/mcp.json)                                  | Credential-free MCP client template for teammates                                           |
| [tasks.md](docs/tasks.md)                                             | Prioritized implementation and submission backlog                                           |
| [HANDOFF.md](HANDOFF.md)                                              | Current project state, next work, and dated handoff index                                   |
| [handoffs/](handoffs/)                                                | Developer/AI work snapshots named `{title-of-work}-{MM-DD-YYYY}.md`                         |
| [project-handoff skill](.agents/skills/project-handoff/SKILL.md)      | Reusable task-completion and context-transfer workflow                                      |

`docs/` contains the requirements and design documents; `.agents/skills/` contains reusable agent instructions. `config/`, `accounts/`, `inventory/`, `borrowing/`, and `operations/` now contain the foundation; feature views, forms, and templates follow their owners' tasks.

The team schedule targets **October 24, 2026**. The official submission date remains subject to the instructor's announcement; presentation and Q&A are scheduled for Week 17.

## Team participation and license

This is a team school project. Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for collaboration. Original team contributions use the [MIT License](LICENSE), with attribution to the project contributors. Instructor-supplied and third-party materials retain their own terms.

---

_Developed for the Final Project in IT 401W WEB PROGRAMMING AND FRAMEWORKS._
