# Campus Equipment Borrowing System

A planned Python/Django application for requesting and managing campus equipment. Basic users browse equipment, submit borrowing requests, and track their own transactions. Administrators manage accounts, physical inventory, approvals, equipment release, returns, maintenance, reports, and audit history through custom pages.

Private team repository: [javecilla/Campus-Equipment-Borrowing-System](https://github.com/javecilla/Campus-Equipment-Borrowing-System). Member branches and the main integration workflow are documented in [DEV.md](DEV.md#assigned-branches-and-main-integration).

The system tracks individual physical units by asset code, preserves their transaction history, and prevents the same unit from being reserved or issued to multiple borrowers simultaneously.

**Current phase:** Django foundation (T01–T03) integrated into `main` through [PR #3](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/3). Configuration, shared models/migrations, audit/settings services, validation, and PostgreSQL integration tests exist. Login and feature pages remain unimplemented; see [current readiness](HANDOFF.md).

## Run locally

Install Python 3.13 and PostgreSQL 17, open the project root on [your assigned branch](DEV.md#assigned-branches-and-main-integration), and create the local `campus_equipment` database as described in [DEV.md](DEV.md#create-your-local-database).

1. Create the project environment and install the pinned development dependencies:

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
   ```

2. If `.env.local` does not exist, create it from the template, then fill its required `DB_*` and `DJANGO_*` values using [the environment guide](DEV.md#create-and-edit-envlocal). Keep an existing private file.

   ```powershell
   New-Item -Path .env.local -ItemType File -Value (Get-Content -LiteralPath .env.example -Raw) -ErrorAction Stop
   ```

3. Check configuration, apply migrations, run the foundation tests, and start the local server:

   ```powershell
   .\.venv\Scripts\python.exe manage.py check --database default
   .\.venv\Scripts\python.exe manage.py migrate --noinput
   .\.venv\Scripts\python.exe manage.py test --noinput
   .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
   ```

Open <http://127.0.0.1:8000/>. At this foundation stage, Django shows its welcome screen with `DJANGO_DEBUG=True`, or a 404 with `False`; custom login, `/manage/`, and `/portal/` routes are pending. The migration initializes loan limits, but creates no accounts or demonstration data. Stop the server with Ctrl+C (Ctrl+Break on Windows if needed).

See the [expected success screenshot](DEV.md#expected-startup-screen) and [everyday startup commands](DEV.md#everyday-startup) in DEV.md.

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
│   │   └── fonts.css         # Local font declarations and typography
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
├── .env.example              # Shareable configuration template
├── .env.local                # Your private values (local, ignored)
├── .gitignore
├── .python-version
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
├── pyproject.toml            # Ruff configuration
├── requirements.in          # Runtime dependency ranges
├── requirements.txt         # Tested runtime pins
├── requirements-dev.in      # Development dependency inputs
└── requirements-dev.txt     # Tested development pins
```

`assets/` is a valid source directory: Django maps `assets/fonts/...` to `/static/fonts/...`. Load `css/fonts.css` in custom page templates to use DM Sans body text and Poppins headings; see [font setup](DEV.md#fonts-and-static-assets). Keep the font license notices. Shared templates and feature pages will be added in their owners' tasks. Generated `staticfiles/` output is ignored and is not a source folder.

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
| Django test framework | Integration, authorization, and transaction tests |

The foundation uses this stack. Exact tested Python packages are pinned in [requirements.txt](requirements.txt), with Ruff in [requirements-dev.txt](requirements-dev.txt). UI libraries remain unselected. Database options and technical references are in [architecture.md](docs/architecture.md).

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
| [PRD.md](docs/PRD.md) | Product goals, audiences, scope, and success criteria |
| [SRS.md](docs/SRS.md) | Functional requirements, business rules, and acceptance criteria |
| [architecture.md](docs/architecture.md) | Proposed components, responsibilities, and concurrency design |
| [project-folder-architecture.md](docs/project-folder-architecture.md) | Existing/planned folders, feature file locations, and how to add a page |
| [db_design.md](docs/db_design.md) | Proposed entities, fields, relationships, and constraints |
| [api_spec.md](docs/api_spec.md) | Proposed page routes, form inputs, and HTTP behavior |
| [AGENTS.md](AGENTS.md) | Project instructions and AI collaboration rules |
| [coding-standards.md](docs/coding-standards.md) | Canonical Django MTV, coding, and verification standards |
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
