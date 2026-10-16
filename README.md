# Campus Equipment Borrowing System

A planned Python/Django application for requesting and managing campus equipment. Basic users browse equipment, submit borrowing requests, and track their own transactions. Administrators manage accounts, physical inventory, approvals, equipment release, returns, maintenance, reports, and audit history through custom pages.

Private team repository: [javecilla/Campus-Equipment-Borrowing-System](https://github.com/javecilla/Campus-Equipment-Borrowing-System). Member branches and the main integration workflow are documented in [DEV.md](DEV.md#assigned-branches-and-main-integration).

The system tracks individual physical units by asset code, preserves their transaction history, and prevents the same unit from being reserved or issued to multiple borrowers simultaneously.

**Current phase:** requirements and documentation. Application code, migrations, dependencies, and executable setup commands have not been created. The technical documents describe the proposed implementation.

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

These are proposed technology choices, not installed dependencies. Exact tested package versions will be recorded when implementation is authorized. Database options and technical references are in [architecture.md](docs/architecture.md).

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
| [PRD.md](docs/PRD.md) | Product goals, audiences, scope, and success criteria |
| [SRS.md](docs/SRS.md) | Functional requirements, business rules, and acceptance criteria |
| [architecture.md](docs/architecture.md) | Proposed components, responsibilities, and concurrency design |
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

`docs/` contains the requirements and design documents; `.agents/skills/` contains reusable agent instructions. Application directories shown in the architecture are planned and do not exist yet.

The team schedule targets **October 24, 2026**. The official submission date remains subject to the instructor's announcement; presentation and Q&A are scheduled for Week 17.

## Team participation and license

This is a team school project. Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for collaboration. Original team contributions use the [MIT License](LICENSE), with attribution to the project contributors. Instructor-supplied and third-party materials retain their own terms.
