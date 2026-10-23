# Campus Equipment Borrowing System

A Python/Django system for borrowing and managing campus equipment. Basic users browse equipment, submit requests and track their own requests and loans. Administrators manage accounts, categories, catalog items, individual physical units, approvals, release, partial/damaged returns, maintenance, reports and audit history through custom pages.

Private team repository: [javecilla/Campus-Equipment-Borrowing-System](https://github.com/javecilla/Campus-Equipment-Borrowing-System). Member branches and the main integration workflow are documented in [DEV.md](DEV.md#assigned-branches-and-main-integration).

The system tracks individual physical units by asset code, preserves their transaction history, and prevents the same unit from being reserved or issued to multiple borrowers simultaneously.

**A working local demonstration is sufficient for assessment. Online deployment, paid hosting and external integrations are not required by the course brief.** The team uses Neon voluntarily as a centralized database so members can see the same records during end-to-end workflow testing. Evaluators can run the application entirely with local PostgreSQL and local file storage, without a Neon account or shared credentials. Application workflows, the database switch and [72 system screenshots](docs/system-screenshots.md) are integrated. Final diagrams, professional/team evidence, verified guides, packaging and rehearsal remain incomplete; [SUBMISSION.md](SUBMISSION.md) is the delivery checklist and [the backlog](docs/tasks.md#course-evidence-and-delivery) owns status.

## Run locally

Run these PowerShell commands from the extracted project root. They start the application with your own local database. The final ZIP has **not yet passed a clean-machine rehearsal**; reconstructing the complete current dataset also needs the catalog/maintenance fixture described under [seed setup](#5-seed-the-demonstration-data).

### 1. Install dependencies

> **Team members** who have received the Neon credentials from Jerome: follow the [step-by-step Neon setup](DEV.md#shared-neon-database-and-photos) in DEV.md to connect to the shared centralized database. Use [the connection switch](DEV.md#switch-between-local-and-shared-databases) to select local or shared data; the template defaults to local.

**For professors, evaluators, or anyone running the app independently** — no Neon account or credentials are required. The steps below use your own local PostgreSQL database and Django's built-in file storage. The app works fully; the only difference from the team's shared environment is that equipment photos uploaded to the team's private cloud will not transfer via Git. Items without local uploads show a built-in placeholder image. After migrating, follow [seed setup](#5-seed-the-demonstration-data): account creation and borrowing-history import are separate commands with different prerequisites.

Install Python 3.13, PostgreSQL 17, and Node.js 22+/npm 10+. Runtime versions are pinned in [requirements.txt](requirements.txt), including Django 5.2.18, Psycopg 3.3.6, python-dotenv 1.2.4 and Pillow 13.0.0. npm packages are locked in [package-lock.json](package-lock.json). Use the supplied files rather than unpinned installs.

Create the environment, install runtime dependencies and compile the local CSS/JavaScript assets:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd ci
npm.cmd run build
```

Python runs Django; npm builds Tailwind CSS and bundled Chart.js/page scripts. No separate frontend server is needed. See [package justifications](#third-party-packages-and-assets) for their purpose and licenses.

### 2. Create a local PostgreSQL database

Start PostgreSQL. In pgAdmin, create `campus_equipment`, owned by your local account. Alternatively, with PostgreSQL's `bin` directory on PATH, run this once; `-W` prompts for the database password:

```powershell
psql -h 127.0.0.1 -p 5432 -U postgres -W -d postgres -c "CREATE DATABASE campus_equipment;"
```

Use your account if its name differs from `postgres`. Skip creation when the database already exists; keep its records. Migrations create the tables, so do not create tables manually from the design. See [database limitations](#database-choice-and-limitations) for why this application uses PostgreSQL.

### 3. Create and edit the environment

If `.env.local` does not exist, create it from the template. This command deliberately fails if the file exists, preserving private values. Generate a secret and paste it into the private file:

```powershell
New-Item -Path .env.local -ItemType File -Value (Get-Content -LiteralPath .env.example -Raw) -ErrorAction Stop
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```

Edit these values in `.env.local`; never put their actual secrets in README or Git:

| Variable                                                             | Local value / purpose                                                                                                |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `IS_LOCAL_DB_CONNECTION`                                             | `True` selects local `DB_*`; accepts exactly `True` or `False`                                                       |
| `DB_NAME`                                                            | `campus_equipment`                                                                                                   |
| `DB_USER`, `DB_PASSWORD`                                             | Your local PostgreSQL username and raw password                                                                      |
| `DB_HOST`, `DB_PORT`                                                 | Normally `127.0.0.1`, `5432`                                                                                         |
| `DJANGO_SECRET_KEY`                                                  | Generated private secret; at least 50 characters and 5 distinct characters                                           |
| `DJANGO_DEBUG`                                                       | Change the template's `False` to `True` for local development/static-file serving                                    |
| `DJANGO_ALLOWED_HOSTS`                                               | Keep `localhost,127.0.0.1`                                                                                           |
| `DJANGO_CSRF_TRUSTED_ORIGINS`                                        | Keep `http://localhost:8000,http://127.0.0.1:8000`                                                                   |
| `MEDIA_STORAGE`                                                      | `local` uses this machine's ignored `media/` directory                                                               |
| `SEED_ACCOUNT_PASSWORD`                                              | Choose a private Django-valid password before account seeding; no password ships in the repository                   |
| `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, `AWS_*`, `MCP_DATABASE_URL` | No cloud/MCP credentials needed locally; leave private credential fields blank and other template defaults unchanged |

Django loads `.env.local`; explicit process values override it. Quote passwords containing `#` or whitespace. Booleans are case-sensitive; missing/invalid required settings fail clearly. Restart Django after editing configuration. [DEV.md](DEV.md#create-and-edit-envlocal) owns the full key rules.

**Switch to shared Neon:** set `IS_LOCAL_DB_CONNECTION=False` and retain Jerome's privately supplied TLS `DATABASE_URL`. Set `MEDIA_STORAGE=neon` only with the separately supplied storage keys. Return to local with `IS_LOCAL_DB_CONNECTION=True` and `MEDIA_STORAGE=local`; local mode ignores the retained shared URL. Switching selects records; it does not copy/synchronize databases or photos. See [DEV switching instructions](DEV.md#switch-between-local-and-shared-databases).

### 4. Check the target and run migrations

Migrations create/update tables and constraints and initialize default limits to **7 calendar days and 3 units per request item**. They create no accounts, equipment or borrowing history. Apply the committed migrations; do not generate new migration files during installation.

First verify the target:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database:', connection.settings_dict['NAME'])"
```

Expect `campus_equipment` for these local setup commands. If it prints `neondb`, stop: shared migrations/seeds/resets require Jerome's separate coordination. Then run:

```powershell
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py showmigrations
.\.venv\Scripts\python.exe manage.py migrate --check
```

Successful commands exit without errors; applied migrations show `[X]`. Rerunning `migrate` applies only outstanding migrations. Development/migration ownership guidance is in [DEV.md](DEV.md#application-migrations-checks-and-local-server).

### 5. Seed the demonstration data

Seeding supplies fictional sign-in and workflow records. **The existing populated demo database needs no reseeding.** On a fresh local database, after migrations and the target check above:

1. Set `SEED_ACCOUNT_PASSWORD` privately, then create accounts:

    ```powershell
    .\.venv\Scripts\python.exe manage.py seed_demo_data
    ```

    This creates **one admin and eight basic users only**. Sign in as `andrea.mendoza` (admin), `miguel.santos` or `sofia.reyes` (basic users), using the password selected when seeding. [DEV.md](DEV.md#seed-the-t21-demonstration-dataset) lists all nine fictional identities. Changing the environment password later does not change stored passwords; use `manage.py changepassword USERNAME` to reset an existing account.

2. Start the server using step 6, sign in as admin, then prepare active categories/items through `/manage/categories/new/` and `/manage/items/new/`. The fixed history importer needs the **nine exact equipment names** in [the transaction plan](operations/demo_transaction_plan.py). Photos are optional. Stop the server before continuing CLI setup.

3. With the required catalog prepared, register stock dated before the historical transactions:

    ```powershell
    .\.venv\Scripts\python.exe manage.py seed_demo_units --admin-username andrea.mendoza --quantity-per-item 2 --acquired-on 2026-07-01
    ```

    This tops up each active catalog item to at least two total units; it creates no categories/items. Existing damaged/retired units count toward that total, so check sufficient serviceable stock before importing history.

4. On an empty borrowing history, import the fixed fictional August-October 22, 2026 scenarios:

    ```powershell
    .\.venv\Scripts\python.exe manage.py seed_demo_transactions
    ```

    This creates **30 requests and 20 issued loans**, including rejected/cancelled requests, partial/damaged returns and overdue scenarios. It requires the actual campus date on/after October 22, 2026 and rejects existing history rather than overwriting it. Ordinary forms still enforce current date rules. It creates one linked damaged-return maintenance record; the populated demo's other nine maintenance records pre-exist the import.

**Remaining packaging gap:** these commands do not rebuild the manually entered catalog or pre-existing maintenance/photos. A repeatable sanitized catalog/maintenance fixture or equivalent seed is still needed for a complete minimum-data replay from the ZIP. Starting the app from this README must not be claimed as reproducing all current records. [SUBMISSION.md](SUBMISSION.md#minimum-demonstration-data) records the verified totals and this gap; [DEV's seed runbook](DEV.md#demo-command-runbook) owns detailed preconditions, repeat behavior and cleanup procedures.

### 6. Run the server / application

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open <http://127.0.0.1:8000/accounts/login/>. An active admin reaches `/manage/`; a basic user reaches `/portal/`. Stop with Ctrl+C (Ctrl+Break on Windows if needed). For everyday restarts, run only this command; migrations/seeds are not needed on every launch. During frontend development, optionally run `npm.cmd run dev` in a second terminal to rebuild changed assets. This is a local development server, not a production deployment configuration.

Equipment photos are stored as relative paths in PostgreSQL and as image bytes in the configured storage backend. For standalone/local evaluation (`MEDIA_STORAGE=local`, the default), photos you upload through the admin go to the ignored `media/equipment/` folder on your machine. The team's existing 23 catalog photos live in private Neon Object Storage and require the shared credentials to appear; without them, items show a built-in placeholder instead of an error. Pulling Git alone does not transfer images. See [photo storage and controls](DEV.md#equipment-photos-and-local-media). Local `.idea/` settings are ignored and are no longer tracked.

## Part 5: business rules and technical implementation

The [course brief](docs/Project-Requirements.txt), [SRS](docs/SRS.md) and implementation define these rules. This table explains what happens, why it matters and where to verify it.

| Rule                                                   | What happens and why                                                                                                                                                                                                                                                                                                        | Source / verification                                                                                                                                                                                           |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Atomic approval; cancellation releases reservations | Approval locks stock and checks all quantities before reserving the complete set in one transaction. A shortage rolls everything back. Approved cancellation ends allocations and frees reserved units, preventing partial promises or stranded stock.                                                                      | [Approval/cancellation services](borrowing/services.py), [rollback tests](borrowing/tests/test_requests.py)                                                                                                     |
| 2. One effective unit status                           | Each unit stores Available, Reserved, Issued, Maintenance or Retired. Release, per-unit returns and repair/retirement services maintain valid transitions; damaged returns open maintenance. This keeps unavailable equipment out of allocation.                                                                            | [Inventory models](inventory/models.py), [return services](borrowing/return_services.py), [maintenance services](inventory/services.py), [return tests](borrowing/tests/test_returns.py)                        |
| 3. Transactions and competing approvals                | PostgreSQL transactions, ordered row locks and a conditional unique active-allocation constraint prevent simultaneous ownership. Two real connections competing for the last unit produce one approval and one conflict, with no partial loser allocation.                                                                  | [Lock helpers](operations/locking.py), [allocation constraints](borrowing/models.py), [competing-approval tests](borrowing/tests/test_approval_concurrency.py)                                                  |
| 4. No duplicate catalog item or partial request        | A unique `(request, catalog_item)` constraint rejects duplicates. The server validates all formset rows before an atomic save; an invalid row in a three-item request saves nothing.                                                                                                                                        | [Forms](borrowing/forms.py), [submission service](borrowing/services.py), [constraints](borrowing/models.py), [submission tests](borrowing/tests/test_request_submission.py)                                    |
| 5. Duration, quantity and issue dates                  | Migrations initialize 7 calendar days and 3 units per item. Submission checks due date after submission and within configured duration; requests snapshot applied limits. Issue after the agreed date is rejected until a valid admin revision is recorded and audited. This prevents stale approvals bypassing date rules. | [Initial settings](operations/migrations/0002_initial_settings.py), [validation](operations/validation.py), [revision/release](borrowing/release_services.py), [release tests](borrowing/tests/test_release.py) |
| 6. Calculated overdue days                             | Outstanding loans show zero before/on the due date; otherwise days overdue are the calendar-day difference in Asia/Manila. Closed loans do not remain overdue. Overdue is calculated rather than manually selected. Payments, fines, procurement and supplier portals are outside scope.                                    | [Loan progress](borrowing/queries.py), [report queries](operations/queries.py), [report tests](operations/tests/test_reports.py)                                                                                |

### Required Django implementation

| Requirement                                                   | How the system implements it                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ORM, migrations, authentication and forms                     | [Settings](config/settings.py), app `models.py`/`migrations/`, [account forms](accounts/forms.py) and [request forms](borrowing/forms.py) use Django's native facilities. Django authentication hashes passwords.                                                                                                                                    |
| Templates, inheritance, named URLs and reuse                  | [Admin base](templates/operations/manage/base.html), [borrower base](templates/accounts/portal/base.html) and [shared components](templates/components/) reuse navigation, fields, messages, statuses and pagination. App URL modules define namespaced routes.                                                                                      |
| Custom workflow-aware operations                              | Handwritten `/manage/` pages provide list/detail/create/update/archive where allowed. Borrowing updates call explicit services; no generated Django admin or unrestricted CRUD bypasses allocation/issue/return rules.                                                                                                                               |
| Relationships, filtering, ordering, pagination and aggregates | [Inventory](inventory/queries.py), [borrowing](borrowing/queries.py) and [operations](operations/queries.py) query helpers use the ORM. Loan/overdue reports and CSV combine loans, borrowers, units and returns with issued/returned/outstanding totals.                                                                                            |
| Validation, CSRF, POST, escaping and ownership                | Forms/services validate input and authoritative state. CSRF middleware/tokens protect POST writes; GET confirmations do not mutate data. [Access checks](accounts/access.py) and [active-account middleware](accounts/middleware.py) enforce roles/ownership. Templates escape ordinary user content; secrets stay in ignored private configuration. |
| Declared tools supporting custom pages                        | [Package justifications](#third-party-packages-and-assets) explain Tailwind, Chart.js and Python/build packages; the [dependency inventory](docs/third-party-dependencies.md) records notices. These tools do not generate the required custom admin interface.                                                                                      |

### Database choice and limitations

PostgreSQL supplies real `select_for_update()` locks, transactional allocation and conditional unique constraints. Evaluation requires a running local PostgreSQL service and valid credentials. PostgreSQL-specific date expressions/constraints are also used; changing the Django engine to SQLite/MySQL without adapting and re-verifying these contracts is unsupported. SQLite's allowance in the brief does not establish equivalent concurrency behavior for this implementation. Optional shared Neon adds network/service dependencies; local PostgreSQL avoids those during demonstration.

### Run the verification

The preceding implementation passed **345 tests on isolated local PostgreSQL**; the [implementation handoff](handoffs/local-database-switch-and-submission-screenshots-10-22-2026.md) records the run and limitations. This documentation update does not claim a new test run. To run the suite yourself, install development requirements and use an explicit local child-process override. The local database account needs permission to create/drop the separate test database:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -c "import os, subprocess, sys; sys.exit(subprocess.call([sys.executable, 'manage.py', 'test', '--noinput'], env={**os.environ, 'IS_LOCAL_DB_CONNECTION': 'True', 'DATABASE_URL': '', 'MEDIA_STORAGE': 'local'}))"
```

For the two competing approvals for the last unit, use the same isolation pattern with its module:

```powershell
.\.venv\Scripts\python.exe -c "import os, subprocess, sys; sys.exit(subprocess.call([sys.executable, 'manage.py', 'test', 'borrowing.tests.test_approval_concurrency', '--noinput'], env={**os.environ, 'IS_LOCAL_DB_CONNECTION': 'True', 'DATABASE_URL': '', 'MEDIA_STORAGE': 'local'}))"
```

These commands create/destroy `test_campus_equipment`, leaving demonstration records intact. Expected result: all tests pass; each last-unit race yields exactly one success and one workflow conflict. [DEV.md](DEV.md#before-handing-over-work) owns further checks and [the manual guide](docs/manual-test-guide.md) provides human walkthroughs.

## Project folder structure

See [Project Folder Architecture](docs/project-folder-architecture.md) for the full tree, existing versus planned files, and where to add models, views, forms, services, templates, and static files.

## Part 6: submission and presentation

Use this as an evidence index for [Part 6 of the course brief](docs/Project-Requirements.txt). **The project is not submission-ready yet.** Application acceptance evidence is available; editable diagrams, professional/team evidence, verified guides and the submission package still require their own completed tasks. See **[SUBMISSION.md](SUBMISSION.md)** for the team's actionable submission and demo-day checklist. [The backlog](docs/tasks.md#course-evidence-and-delivery) owns task status and [HANDOFF.md](HANDOFF.md) owns current readiness.

| Status                 | Required evidence                                                 | Where to look                                                                                                                                                                                         | Current coverage / remaining work                                                                                                                                                                                                                                                                                                                                      |
| ---------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ✅ Done                | Working system, constraints, tests, limitations, and enhancements | [System requirements](docs/SRS.md), [database constraints](docs/db_design.md), [verified task evidence](docs/tasks.md#verified-task-evidence), [test/check commands](DEV.md#before-handing-over-work) | T01-T24 integrated. T25 reference audit In progress; final traceability/editable diagrams and team review remain pending                                                                                                                                                                                                                                               |
| 🔄 In Progress         | MTV, database, and workflow diagrams                              | [MTV diagram](docs/architecture.md#model-template-view-structure), [database ERD](docs/db_design.md#relationships), [workflow diagram](docs/architecture.md#workflow-view)                            | Code-reconciled references and drawing notes ready for Kenneth/Ellyssa; editable tool sources/exports and team review pending under T25                                                                                                                                                                                                                                |
| ✅ Done                | User needs and options                                            | [Requirements](docs/SRS.md), [stakeholders/personas](docs/PRD.md#users-and-stakeholders), [T26 needs/options evidence](docs/user-needs-evidence-guide.md)                                             | T23 limited acceptance/feedback/fix is Done/integrated; T24 performance/recovery is integrated with its lab limits. T26 is Done on Jerome-accepted limited proxy evidence and source research; source `25e83ef`/receipt `fcc238e` are integrated through PR #63 at `d409cfa`                                                                                           |
| ✅ Done                | Technology choices and development records                        | [Tool justifications](#third-party-packages-and-assets), [dependency inventory](docs/third-party-dependencies.md), [coding standards](docs/coding-standards.md), [work records](handoffs/)            | Tool/reuse examples and the conditional supervised-AI recommendation are accepted in [T26](docs/user-needs-evidence-guide.md#evaluate-one-emerging-technology); policy/account clearance remains T27                                                                                                                                                                   |
| 🔄 In Progress         | Professional judgment, standards, ethics, and legal requirements  | [T27 professional-judgment record](docs/professional-judgment-and-ethics.md), [security/privacy requirements](docs/SRS.md#non-functional-requirements), [contribution/licensing guidance](CONTRIBUTING.md) | Source-backed stakeholders/duties, privacy lifecycle, risk/safeguard decisions, IP, accessibility, bias, conflicts and public-welfare boundaries are recorded. T27 still requires institutional privacy/records decisions, policy/instructor evidence, asset resolution, accessibility evidence and all-member review |
| 🔄 In Progress         | Reuse, third-party assets, and AI disclosure                      | [AI/reuse disclosure](docs/professional-judgment-and-ethics.md#ai-and-reuse-disclosure), [package/asset disclosures](#third-party-packages-and-assets), [licensing boundaries](CONTRIBUTING.md)       | The application has no AI feature; dependency notices and Codex records exist. Default image provenance, actual account/service controls, the BulSU AI Policy/instructor instructions and final member disclosure review remain unresolved under T27 |
| 🔄 In Progress         | Team and individual participation                                 | [Assignments](docs/Project-Members.txt), [collaboration guidance](CONTRIBUTING.md), [work handoffs](handoffs/)                                                                                        | Allocation/history exists; every member still needs leadership rotation with goal-setting, task assignment, coordination and monitoring, contributions, peer feedback, individual/team evaluations and improvements after feedback: T28                                                                                                                                |
| ⏳ Not Started         | Technical, basic-user, and admin guides                           | [Technical setup/development guide](DEV.md), [guide task](docs/tasks.md#course-evidence-and-delivery)                                                                                                 | Technical setup exists; verified user/admin guides and complete maintenance guidance remain pending: T29                                                                                                                                                                                                                                                               |
| ✅ Done and integrated | Screenshots of the system                                         | [Captured-page checklist](SUBMISSION.md#screenshots-checklist)                                                                                                                                        | 72 actual PNGs and verified CSV cover all 39 checklist entries plus additional forms/details/mobile views; captured using a disposable local copy with original data retained. Published in `c3fb6bb`; [integration receipt](handoffs/database-switch-and-screenshot-main-integration-10-22-2026.md); user-merged PR #64 at `8dda8c9`                                  |
| ⏳ Not Started         | ZIP, seed, and demonstration access                               | [Packaging checklist](SUBMISSION.md#t30--submission-zip-checklist), [fictional dataset](docs/tasks.md#required-fictional-demonstration-dataset)                                                       | Existing seeds integrated and screenshots collected; complete catalog/maintenance replay, private instructor credential delivery, final ZIP (named `IT401W_ProjectA_BSIT4EG1_Group2.zip`) and clean-machine verification remain pending: T30                                                                                                                           |
| ⏳ Not Started         | Week 17 demonstration and Q&A                                     | [Demo checklist](SUBMISSION.md#t31--demo-day-checklist)                                                                                                                                               | T31: 12-minute demo + 3-minute Q&A; no PPT/slides needed (instructor-confirmed); bring printed project rubric × 2; every member presents an identifiable segment and records feedback/actions                                                                                                                                                                          |

The final package must be named `IT401W_ProjectA_BSIT4EG1_Group2.zip`. Submit demonstration credentials for **one admin and two basic users** through the instructor-designated channel; exclude secrets and private data from the ZIP/repository. Individual evidence must address all four indicators under PO-d, PO-e, PO-g, PO-h, PO-j, and PO-n using the actual course rubric. See **[SUBMISSION.md](SUBMISSION.md)** for the complete team checklist.

## Project scope

The application has exactly two roles: `BASIC_USER` and `ADMIN`. Development emphasizes the custom administration side, approximately 75% of the work, with approximately 25% for basic-user features. Django's generated admin interface is prohibited.

The principal workflow is request submission, review, reservation, release, and return. Partial returns, damaged equipment, overdue monitoring, and maintenance are included. Payments, fines, procurement, supplier portals, and third-party integrations are outside the required scope.

## Technology

| Technology                                 | Implemented purpose                                                                                        |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| Python 3.13                                | Application language                                                                                       |
| Django 5.2 LTS                             | Model-template-view application, authentication, forms, ORM, and migrations                                |
| PostgreSQL 17 locally / Neon PostgreSQL 18 | Relational storage, database constraints, and transactional row locking; Neon centralizes team development |
| Neon Object Storage                        | Private shared equipment images; Django authenticates and streams access                                   |
| Psycopg 3                                  | Django's PostgreSQL database driver                                                                        |
| Django templates, HTML, and CSS            | Server-rendered pages and reusable role layouts                                                            |
| JavaScript                                 | Small progressive enhancements and database-backed charts                                                  |
| Tailwind CSS                               | Compiled utility styling for handwritten Django templates                                                  |
| Node.js/npm                                | Locked local CSS/JavaScript build and watch tools                                                          |
| Django test framework                      | Integration, authorization, and transaction tests                                                          |

The application uses this stack. Exact tested Python packages are pinned in [requirements.txt](requirements.txt), with Ruff in [requirements-dev.txt](requirements-dev.txt). JavaScript packages and their lockfile are declared separately in [package.json](package.json). Library rationale, required architectural patterns, database options, and references are in [architecture.md](docs/architecture.md#required-patterns-and-selected-libraries).

## Third-party packages and assets

The [course brief](docs/Project-Requirements.txt), Part 5, permits third-party packages when declared and justified, and prohibits generating the custom admin interface. These packages support our handwritten Django views/forms/templates; none supplies the required admin pages. The team selected Tailwind under that general permission; the brief does not name it specifically. HTTP interactions use native Django forms and links without a browser request library.

| Package / asset                                                                                                     | Used for / why selected                                                                                        | Scope and tradeoff                                                                                                                                   | License                                                       |
| ------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Django                                                                                                              | MTV, ORM, migrations, forms, sessions/authentication, and tests required by the brief                          | Application runtime; custom role pages remain team-authored                                                                                          | BSD-3-Clause                                                  |
| psycopg and psycopg-binary (`psycopg[binary]`)                                                                      | PostgreSQL driver for the selected real locking/constraint strategy; binary wheels simplify local installation | Application runtime; depends on a running PostgreSQL service                                                                                         | LGPL-3.0-only; retain wheel notices                           |
| python-dotenv                                                                                                       | Parse each workstation's ignored private environment file using a maintained parser                            | Application runtime; our strict configuration validation remains authoritative                                                                       | BSD-3-Clause                                                  |
| Pillow                                                                                                              | Validate, orient, resize and re-encode optional equipment photos                                               | Runtime; local image processing, no external service or generated admin; retain wheel/native-library notices                                         | MIT-CMU and bundled library notices                           |
| django-storages[s3] / boto3                                                                                         | Connect Django's storage API to private Neon S3-compatible equipment media                                     | Python runtime; adds a network/storage dependency while retaining existing upload validation, Django authentication and custom pages                 | BSD-3-Clause / Apache-2.0; indirect licenses in the inventory |
| Ruff                                                                                                                | Fast Python lint/import checks and formatting in one existing tool                                             | Development only; checks style, not workflow correctness                                                                                             | MIT                                                           |
| djLint                                                                                                              | Format Django template tags/HTML with a Django-aware profile                                                   | Development only; GPL-3.0-or-later tool, not bundled into application assets; Python remains Ruff's responsibility                                   | GPL-3.0-or-later                                              |
| tailwindcss and @tailwindcss/cli                                                                                    | Compile responsive utility styling for handwritten Django templates                                            | Build only; more custom markup/component work than Bootstrap; adds a local CSS build                                                                 | MIT                                                           |
| Chart.js 4.5.1                                                                                                      | Render the two required dashboard charts with meaningful axes, exact-value tooltips and shared colors          | Browser runtime, bundled locally; retains server-rendered data tables for accessible/non-JavaScript access; adds a canvas bundle                     | MIT; [bundled notices](static/licenses/chartjs-MIT.txt)       |
| esbuild                                                                                                             | Compile/minify page JavaScript into browser-ready ES modules                                                   | Build only; keeps page scripts minified and supports the existing watcher; adds no separate frontend server                                          | MIT                                                           |
| concurrently                                                                                                        | Run CSS and JS watchers through one cross-platform command                                                     | Development only; keeps Django in its own terminal and stops sibling watchers on exit                                                                | MIT                                                           |
| Prettier                                                                                                            | Consistent JS/MJS, CSS, and JSON formatting; supports deliberately selected Markdown too                       | Development only; no built-in Python/Django-template formatting is used; separate formatters handle those languages                                  | MIT                                                           |
| [Tailwind CSS IntelliSense](https://github.com/tailwindlabs/tailwindcss-intellisense) (`bradlc.vscode-tailwindcss`) | Tailwind-aware VS Code language mode, completions, and diagnostics for custom CSS syntax                       | Optional editor extension recommended by the workspace; installed separately from npm; see [editor setup](DEV.md#tailwind-css-in-vs-code)            | MIT                                                           |
| DM Sans and Poppins fonts                                                                                           | Locally served body/heading typography without a font CDN                                                      | Runtime assets; supplied OFL notices remain with the font files                                                                                      | SIL OFL-1.1                                                   |
| Default admin/basic-user profile illustrations                                                                      | User-supplied role avatars for the account dropdown and My profile                                             | Local runtime images; provenance recorded in the [asset inventory](docs/third-party-dependencies.md#supplied-assets-and-optional-inspection-tooling) | Source/license not supplied                                   |
| Default equipment photo                                                                                             | User-supplied WebP placeholder when a catalog item has no uploaded photo                                       | Local runtime asset; [photo/storage setup](DEV.md#equipment-photos-and-local-media) and provenance in the asset inventory                            | Source/license not supplied                                   |
| @bytebase/dbhub 1.5.0                                                                                               | Optional, separately authorized read-only PostgreSQL inspection through MCP                                    | Developer tooling through npm's execution cache; not a Django dependency or application HTTP integration                                             | MIT                                                           |

Exact application/tool pins and all indirect Python/npm packages, their parent dependencies, optional platform binaries, and license metadata are disclosed in the [complete third-party inventory](docs/third-party-dependencies.md). The inventory includes the indirect support packages (for example asgiref/sqlparse/tzdata and djLint's CLI/parsing dependencies), rather than implying only the direct packages exist. Python pins live in [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt); npm pins live in [package-lock.json](package-lock.json). Optional DBHub's own dependency declaration is linked separately in the inventory because its execution-cache dependencies are not part of the application's lockfile.

The root [MIT license](LICENSE) applies to original team contributions; dependency, font, instructor, and upstream notices keep their own terms. The dashboard bundle includes Chart.js and its indirect color dependency; their full MIT notices are retained in [static/licenses/chartjs-MIT.txt](static/licenses/chartjs-MIT.txt). Supplied font notices remain with the assets. Refresh declarations, rationale, inventory, and relevant notices together whenever dependencies change; [DEV.md](DEV.md#updating-dependencies) owns the commands. No Django admin generator, Django REST Framework or frontend SPA framework is installed.

## Project members

| Member                      | GitHub                                         | Assigned responsibility                                                     |
| --------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------- |
| Avecilla, Jerome S.         | [@javecilla](https://github.com/javecilla)     | T15 release/slips; T16 maintenance; system completion and diagram go signal |
| Cayanan, Alex Enrico        | [@AlexCayanan](https://github.com/AlexCayanan) | T18 dashboard; T19 reports                                                  |
| Cortez, Kenneth T.          | [@corkenneth](https://github.com/corkenneth)   | Validation, documentation, manual testing; editable conversion pending      |
| Ignacio, Margareth Raine H. | [@raifun](https://github.com/raifun)           | Validation, documentation, manual testing; diagram review support           |
| Regodon, Ma. Ellyssa Bianca | [@ellieebeann](https://github.com/ellieebeann) | Validation, documentation, manual testing; editable conversion pending      |
| Giga, Ralph Andre F.        | [@dreygigz](https://github.com/dreygigz)       | T17 returns; T20 UI integration                                             |

Current assignments follow the October 20 [ownership and support responsibilities](docs/tasks.md#current-ownership-and-support-responsibilities); [Project-Members.txt](docs/Project-Members.txt) preserves original assignments and branches. Existing contributor credit remains intact, including Kenneth's completed T16 baseline. All members still contribute code, documentation, testing and an individual presentation segment. Jerome authorized preparing accurate diagram references for Kenneth and Ellyssa to convert into an editable tool such as Lucidchart; Margareth retains validation/documentation support. Follow [T25 consumer guidance](DEV.md#t25-readiness-and-consumer-handoff) for conversion, exports and review.

## Documentation

| File                                                                  | Purpose                                                                                                         |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| [Project-Requirements.txt](docs/Project-Requirements.txt)             | Original course requirements                                                                                    |
| [Project-Members.txt](docs/Project-Members.txt)                       | Original team assignments and schedule                                                                          |
| [PLAN.md](PLAN.md)                                                    | Full-system delivery order, member handoff gates, and agent task selection                                      |
| [team-agent-prompts.md](docs/team-agent-prompts.md)                   | Copy-and-paste feature or validation/documentation/manual-testing prompts for each member                       |
| [PRD.md](docs/PRD.md)                                                 | Product goals, audiences, scope, and success criteria                                                           |
| [SRS.md](docs/SRS.md)                                                 | Functional requirements, business rules, and acceptance criteria                                                |
| [System screenshots](docs/system-screenshots.md)                      | All 72 system screenshots displayed with short descriptions, grouped by role and workflow                       |
| [architecture.md](docs/architecture.md)                               | Code-reconciled MTV, workflow and concurrency references                                                        |
| [project-folder-architecture.md](docs/project-folder-architecture.md) | Existing/planned folders, feature file locations, and how to add a page                                         |
| [db_design.md](docs/db_design.md)                                     | Code-reconciled entities, relationships and constraints                                                         |
| [api_spec.md](docs/api_spec.md)                                       | Page routes, form inputs and HTTP contracts                                                                     |
| [AGENTS.md](AGENTS.md)                                                | Project instructions and AI collaboration rules                                                                 |
| [coding-standards.md](docs/coding-standards.md)                       | Canonical Django MTV, coding, and verification standards                                                        |
| [third-party-dependencies.md](docs/third-party-dependencies.md)       | All locked Python/npm packages, parent dependencies, optional entries, and license metadata                     |
| [User-needs evidence guide](docs/user-needs-evidence-guide.md)        | T26 proxy feedback/persona assessment, system options, implemented reuse and AI-assisted-development evaluation |
| [django-mtv skill](.agents/skills/django-mtv/SKILL.md)                | Reusable Django design, implementation, and review workflow                                                     |
| [DEV.md](DEV.md)                                                      | Workstation, private environment, local PostgreSQL, and MCP setup                                               |
| [.env.example](.env.example)                                          | Shared application/MCP configuration keys with empty secret values                                              |
| [.agents/mcp.json](.agents/mcp.json)                                  | Credential-free MCP client template for teammates                                                               |
| [tasks.md](docs/tasks.md)                                             | Prioritized implementation and submission backlog                                                               |
| [HANDOFF.md](HANDOFF.md)                                              | Current project state, next work, and dated handoff index                                                       |
| [SUBMISSION.md](SUBMISSION.md)                                        | Team submission and demo-day checklist with status tracking                                                     |
| [handoffs/](handoffs/)                                                | Developer/AI work snapshots named `{title-of-work}-{MM-DD-YYYY}.md`                                             |
| [project-handoff skill](.agents/skills/project-handoff/SKILL.md)      | Reusable task-completion and context-transfer workflow                                                          |

`docs/` contains the requirements and design documents; `.agents/skills/` contains reusable agent instructions. `config/`, `accounts/`, `inventory/`, `borrowing/`, and `operations/` contain the implemented application; feature responsibilities follow their owners' tasks.

The team schedule targets **October 24, 2026**. The official submission date remains subject to the instructor's announcement; presentation and Q&A are scheduled for Week 17.

## Team participation and license

This is a team school project. Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for collaboration. Original team contributions use the [MIT License](LICENSE), with attribution to the project contributors. Instructor-supplied and third-party materials retain their own terms.

---

_Developed for the Final Project in IT 401W WEB PROGRAMMING AND FRAMEWORKS._
