# Campus Equipment Borrowing System

A planned Python/Django application for requesting and managing campus equipment. Basic users browse equipment, submit borrowing requests, and track their own transactions. Administrators manage accounts, physical inventory, approvals, equipment release, returns, maintenance, reports, and audit history through custom pages.

Private team repository: [javecilla/Campus-Equipment-Borrowing-System](https://github.com/javecilla/Campus-Equipment-Borrowing-System). Member branches and the main integration workflow are documented in [DEV.md](DEV.md#assigned-branches-and-main-integration).

The system tracks individual physical units by asset code, preserves their transaction history, and prevents the same unit from being reserved or issued to multiple borrowers simultaneously.

**Current phase:** Django foundation (T01–T03) integrated into `main` through [PR #3](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/3). Configuration, shared models/migrations, audit/settings services, validation, and PostgreSQL integration tests exist. Login and feature pages remain unimplemented; see [current readiness](HANDOFF.md).

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

4. Check configuration, apply migrations, run the foundation tests, and start the local server:

   ```powershell
   .\.venv\Scripts\python.exe manage.py check --database default
   .\.venv\Scripts\python.exe manage.py migrate --noinput
   .\.venv\Scripts\python.exe manage.py test --noinput
   .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
   ```

Open <http://127.0.0.1:8000/> with `DJANGO_DEBUG=True` for the development index, which links to the Tailwind/font preview at `/test`. See [the frontend preview](DEV.md#frontend-preview) for expected behavior. The account home behavior, custom login, `/manage/`, and `/portal/` routes are pending. The migration initializes loan limits, but creates no accounts or demonstration data. Stop the server with Ctrl+C (Ctrl+Break on Windows if needed).

See the [expected success screenshot](DEV.md#expected-startup-screen) and [everyday startup commands](DEV.md#everyday-startup) in DEV.md. During frontend work, keep `npm.cmd run dev` running in a second terminal to rebuild CSS/JavaScript after edits.

For migration changes, test-database permissions, dependency updates, checks, and team synchronization, follow [DEV.md](DEV.md#application-migrations-checks-and-local-server). No clean-machine or complete product demonstration is claimed yet.

## Project folder structure

Main paths currently present in the project:

For the detailed app layout, planned `views.py`/`forms.py`/`urls.py` files, and where to add page HTML, read [Project Folder Architecture](docs/project-folder-architecture.md).

```text
Campus-Equipment-Borrowing-System/
├── .agents/                  # Shared MCP configuration and project skills
├── accounts/                 # Custom User/Profile models and migrations
├── assets/                   # Source files discovered by Django staticfiles
│   ├── css/
│   │   ├── app.css           # Tailwind entry point and font theme
│   │   └── fonts.css         # Local font declarations and typography
│   ├── js/http.js            # Shared Axios client; source bundled by esbuild
│   ├── build/                # Generated CSS/ES modules (local, ignored)
│   ├── fonts/
│   │   ├── DM_Sans/          # Variable/static fonts and OFL license
│   │   └── Poppins/          # Font weights/styles and OFL license
│   └── images/
│       └── inital-setup-running-success-screen.png
├── borrowing/                # Requests, allocations, loans, returns, migrations
├── config/                   # Environment parsing, settings, URLs, WSGI/ASGI
├── docs/                     # Requirements, design contracts, and task backlog
├── handoffs/                 # Dated developer/AI work snapshots
├── inventory/                # Catalog, units, maintenance models and migrations
├── operations/
│   ├── migrations/
│   ├── tests/                # PostgreSQL schema/service/locking integration tests
│   ├── audit.py
│   ├── locking.py
│   ├── models.py
│   ├── queries.py
│   ├── services.py
│   └── validation.py
├── templates/base.html       # Shared document/asset shell; role layouts follow
├── scripts/copy-licenses.mjs  # Retains the Axios MIT notice in generated assets
├── .env.example              # Shareable configuration template
├── .env.local                # Your private values (local, ignored)
├── .gitignore
├── .python-version
├── .prettierrc.json           # Shared JS/CSS/JSON formatting options
├── .prettierignore            # Leaves Django HTML/Python to their own formatters
├── .venv/                    # Your Python environment (local, ignored)
├── AGENTS.md
├── CODEOWNERS
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DEV.md                    # Setup, daily work, migrations, checks, and assets
├── HANDOFF.md                # Current readiness and dated handoff index
├── LICENSE
├── PLAN.md
├── README.md
├── manage.py
├── package.json              # JavaScript dependencies and build/watch commands
├── package-lock.json         # Reproducible JavaScript dependency versions
├── pyproject.toml            # Ruff and Django-template djLint configuration
├── requirements.in          # Runtime dependency ranges
├── requirements.txt         # Tested runtime pins
├── requirements-dev.in      # Development dependency inputs
└── requirements-dev.txt     # Tested development pins
```

`assets/` is a valid source directory: Django maps `assets/fonts/...` to `/static/fonts/...`. The shared `base.html` loads compiled Tailwind CSS with DM Sans body text and Poppins headings; see [frontend setup](DEV.md#frontend-assets-tailwind-and-axios). Keep the font license notices. Role templates and feature pages will be added in their owners' tasks. Generated `assets/build/`, `node_modules/`, and `staticfiles/` remain ignored; build assets before collecting static files or preparing a runnable submission.

## Project scope

The application has exactly two roles: `BASIC_USER` and `ADMIN`. Development emphasizes the custom administration side, approximately 75% of the work, with approximately 25% for basic-user features. Django's generated admin interface is prohibited.

The principal workflow is request submission, review, reservation, release, and return. Partial returns, damaged equipment, overdue monitoring, and maintenance are included. Payments, fines, procurement, supplier portals, and third-party integrations are outside the required scope.

## Technology

| Technology | Planned purpose |
| --- | --- |
| Python 3.13 | Application language |
| Django 5.2 LTS | Model-template-view application, authentication, forms, ORM, and migrations |
| PostgreSQL 17 | Relational storage, database constraints, and transactional row locking |
| Psycopg 3 | Django's PostgreSQL database driver |
| Django templates, HTML, and CSS | Server-rendered pages and reusable role layouts |
| JavaScript | Small progressive enhancements and database-backed charts |
| Tailwind CSS | Compiled utility styling for handwritten Django templates |
| Axios | Shared HTTP client for optional same-origin enhancements |
| Node.js/npm | Locked local CSS/JavaScript build and watch tools |
| Django test framework | Integration, authorization, and transaction tests |

The foundation uses this stack. Exact tested Python packages are pinned in [requirements.txt](requirements.txt), with Ruff in [requirements-dev.txt](requirements-dev.txt). JavaScript packages and their lockfile are declared separately in [package.json](package.json). Library rationale, required architectural patterns, database options, and references are in [architecture.md](docs/architecture.md#required-patterns-and-selected-libraries).

## Third-party packages and assets

The [course brief](docs/Project-Requirements.txt), Part 5, permits third-party packages when declared and justified, and prohibits generating the custom admin interface. These packages support our handwritten Django views/forms/templates; none supplies the required admin pages. The team selected Tailwind and Axios under that general permission; the brief does not name them specifically.

| Package / asset | Used for / why selected | Scope and tradeoff | License |
| --- | --- | --- | --- |
| Django | MTV, ORM, migrations, forms, sessions/authentication, and tests required by the brief | Application runtime; custom role pages remain team-authored | BSD-3-Clause |
| psycopg and psycopg-binary (`psycopg[binary]`) | PostgreSQL driver for the selected real locking/constraint strategy; binary wheels simplify local installation | Application runtime; depends on a running PostgreSQL service | LGPL-3.0-only; retain wheel notices |
| python-dotenv | Parse each workstation's ignored private environment file using a maintained parser | Application runtime; our strict configuration validation remains authoritative | BSD-3-Clause |
| Ruff | Fast Python lint/import checks and formatting in one existing tool | Development only; checks style, not workflow correctness | MIT |
| djLint | Format Django template tags/HTML with a Django-aware profile | Development only; GPL-3.0-or-later tool, not bundled into application assets; Python remains Ruff's responsibility | GPL-3.0-or-later |
| tailwindcss and @tailwindcss/cli | Compile responsive utility styling for handwritten Django templates | Build only; more custom markup/component work than Bootstrap; adds a local CSS build | MIT |
| Axios | Shared optional browser HTTP client, Django CSRF names, and finite timeout | Browser runtime; native fetch could avoid a dependency, but the team selected one consistent transport; ordinary forms remain valid | MIT |
| esbuild | Bundle Axios and feature modules into browser-ready ES modules | Build only; needed to resolve npm imports; adds no separate frontend server | MIT |
| concurrently | Run CSS and JS watchers through one cross-platform command | Development only; keeps Django in its own terminal and stops sibling watchers on exit | MIT |
| Prettier | Consistent JS/MJS, CSS, and JSON formatting; supports deliberately selected Markdown too | Development only; no built-in Python/Django-template formatting is used; separate formatters handle those languages | MIT |
| [Tailwind CSS IntelliSense](https://github.com/tailwindlabs/tailwindcss-intellisense) (`bradlc.vscode-tailwindcss`) | Tailwind-aware VS Code language mode, completions, and diagnostics for custom CSS syntax | Optional editor extension recommended by the workspace; installed separately from npm; see [editor setup](DEV.md#tailwind-css-in-vs-code) | MIT |
| DM Sans and Poppins fonts | Locally served body/heading typography without a font CDN | Runtime assets; supplied OFL notices remain with the font files | SIL OFL-1.1 |
| @bytebase/dbhub 1.5.0 | Optional, separately authorized read-only PostgreSQL inspection through MCP | Developer tooling through npm's execution cache; not a Django dependency or application HTTP integration | MIT |

Exact application/tool pins and all indirect Python/npm packages, their parent dependencies, optional platform binaries, and license metadata are disclosed in the [complete third-party inventory](docs/third-party-dependencies.md). The inventory includes the indirect support packages (for example asgiref/sqlparse/tzdata and djLint's CLI/parsing dependencies), rather than implying only the direct packages exist. Python pins live in [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt); npm pins live in [package-lock.json](package-lock.json). Optional DBHub's own dependency declaration is linked separately in the inventory because its execution-cache dependencies are not part of the application's lockfile.

The root [MIT license](LICENSE) applies to original team contributions; dependency, font, instructor, and upstream notices keep their own terms. The browser build copies the complete Axios MIT notice beside its bundle. Refresh declarations, rationale, inventory, and relevant notices together whenever dependencies change; [DEV.md](DEV.md#updating-dependencies) owns the commands. No Django admin generator, Django REST Framework, frontend SPA framework, or chart library is installed by this setup.

## Project members

| Member | GitHub | Assigned responsibility |
| --- | --- | --- |
| Avecilla, Jerome S. | [@javecilla](https://github.com/javecilla) | Database and backend foundation; audit logs and settings |
| Cayanan, Alex Enrico | [@AlexCayanan](https://github.com/AlexCayanan) | Login, user accounts, security, dashboard, and reports |
| Cortez, Kenneth T. | [@corkenneth](https://github.com/corkenneth) | Equipment inventory and maintenance |
| Ignacio, Margareth Raine H. | [@raifun](https://github.com/raifun) | Approval, release, and returns |
| Regodon, Ma. Ellyssa Bianca | [@ellieebeann](https://github.com/ellieebeann) | Basic-user account, profile, browsing, and layout |
| Giga, Ralph Andre F. | [@dreygigz](https://github.com/dreygigz) | Basic-user requests, tracking, cancellation, and UI integration |

Assignments come from [Project-Members.txt](docs/Project-Members.txt). All members also contribute documentation, testing, and an individual presentation segment. The shared authentication system is owned by Alex; Ellyssa's registration and profile pages use it.

## Documentation

| File | Purpose |
| --- | --- |
| [Project-Requirements.txt](docs/Project-Requirements.txt) | Original course requirements |
| [Project-Members.txt](docs/Project-Members.txt) | Original team assignments and schedule |
| [PLAN.md](PLAN.md) | Full-system delivery order, member handoff gates, and agent task selection |
| [team-agent-prompts.md](docs/team-agent-prompts.md) | Copy-and-paste implementation prompts for each member's coding agent |
| [PRD.md](docs/PRD.md) | Product goals, audiences, scope, and success criteria |
| [SRS.md](docs/SRS.md) | Functional requirements, business rules, and acceptance criteria |
| [architecture.md](docs/architecture.md) | Proposed components, responsibilities, and concurrency design |
| [project-folder-architecture.md](docs/project-folder-architecture.md) | Existing/planned folders, feature file locations, and how to add a page |
| [db_design.md](docs/db_design.md) | Proposed entities, fields, relationships, and constraints |
| [api_spec.md](docs/api_spec.md) | Proposed page routes, form inputs, and HTTP behavior |
| [AGENTS.md](AGENTS.md) | Project instructions and AI collaboration rules |
| [coding-standards.md](docs/coding-standards.md) | Canonical Django MTV, coding, and verification standards |
| [third-party-dependencies.md](docs/third-party-dependencies.md) | All locked Python/npm packages, parent dependencies, optional entries, and license metadata |
| [django-mtv skill](.agents/skills/django-mtv/SKILL.md) | Reusable Django design, implementation, and review workflow |
| [DEV.md](DEV.md) | Workstation, private environment, local PostgreSQL, and MCP setup |
| [.env.example](.env.example) | Shared application/MCP configuration keys with empty secret values |
| [.agents/mcp.json](.agents/mcp.json) | Credential-free MCP client template for teammates |
| [tasks.md](docs/tasks.md) | Prioritized implementation and submission backlog |
| [HANDOFF.md](HANDOFF.md) | Current project state, next work, and dated handoff index |
| [handoffs/](handoffs/) | Developer/AI work snapshots named `{title-of-work}-{MM-DD-YYYY}.md` |
| [project-handoff skill](.agents/skills/project-handoff/SKILL.md) | Reusable task-completion and context-transfer workflow |

`docs/` contains the requirements and design documents; `.agents/skills/` contains reusable agent instructions. `config/`, `accounts/`, `inventory/`, `borrowing/`, and `operations/` now contain the foundation; feature views, forms, and templates follow their owners' tasks.

The team schedule targets **October 24, 2026**. The official submission date remains subject to the instructor's announcement; presentation and Q&A are scheduled for Week 17.

## Team participation and license

This is a team school project. Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for collaboration. Original team contributions use the [MIT License](LICENSE), with attribution to the project contributors. Instructor-supplied and third-party materials retain their own terms.
