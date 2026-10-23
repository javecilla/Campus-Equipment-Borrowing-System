# Team Development Guide

[First-time setup](#first-time-setup) | [Shared Neon setup](#shared-neon-database-and-photos) | [Everyday startup](#everyday-startup) | [Error pages](#preview-custom-error-pages) | [Reset local data](#reset-local-development-data) | [Frontend assets](#frontend-assets-tailwind-and-page-scripts) | [Formatting](#formatting-and-code-consistency) | [Migrations](#working-with-migrations) | [Checks](#before-handing-over-work) | [Manual browser tests](docs/manual-test-guide.md) | [Fonts](#fonts-and-static-assets) | [Team Git](#assigned-branches-and-main-integration) | [Optional MCP](#configure-your-mcp-client) | [Troubleshooting](#troubleshooting)

Run commands in **PowerShell from the project root**, where `manage.py` lives. Every member uses their own `.venv` and ignored `.env.local`. The template selects local PostgreSQL; use [the connection switch](#switch-between-local-and-shared-databases) to choose local development or the shared Neon database/photos. Isolated development and automated tests use a separate local PostgreSQL database. Git shares source and migrations, not credentials, database contents or uploaded images.

For current implementation, verification and main-integration status, read [HANDOFF.md](HANDOFF.md) and [verified task evidence](docs/tasks.md#verified-task-evidence). Shared Neon setup is locally implemented on `jerome` and awaits publication/review; it is not yet available by pulling main.

**UI-09 is Done and integrated through PR #39 at `a35e0f1`, source `043822e`, preserved in main `866eb7e`.** Its shared M3 presentation does not change workflow APIs or T15 ownership. Read the [canonical component rules](docs/coding-standards.md#shared-m3-roles-and-components-ui-09) before adding feature templates.

For where to add views, models, forms, URLs, and page templates, use [Project Folder Architecture](docs/project-folder-architecture.md).

Copy your member prompt from [Team AI work prompts](docs/team-agent-prompts.md) for your current assignment. Alex, Ralph and Jerome use implementation prompts; Kenneth, Margareth and Ellyssa focus on validation, documentation and manual testing. Follow the [current ownership and diagram delivery guidance](docs/tasks.md#current-ownership-and-support-responsibilities); all changes stay uncommitted for review.

## First-time setup

Follow these steps once, in order. Keep an existing environment, database, or private configuration. For shared Neon development, prepare Python/frontend dependencies below, then use [the Neon steps](#shared-neon-database-and-photos); skip local database creation unless you also need isolated tests.

### Tools to download

| Required tool    | Version                                                  | Download                                                          |
| ---------------- | -------------------------------------------------------- | ----------------------------------------------------------------- |
| Git              | Git for Windows                                          | [Install Git](https://git-scm.com/install/windows)                |
| Python           | Python 3.13                                              | [Windows downloads](https://www.python.org/downloads/windows/)    |
| PostgreSQL       | PostgreSQL 17, including pgAdmin                         | [Windows installer](https://www.postgresql.org/download/windows/) |
| Node.js with npm | Node 22+ and npm 10+; tested with Node 24.5.0/npm 11.6.2 | [Node.js downloads](https://nodejs.org/en/download)               |

Open a new terminal after installation. Check `git --version`, `py -3.13 --version`, `node --version`, and `npm.cmd --version`. Node/npm now build the shared frontend assets as well as supporting optional MCP tooling. On PowerShell, `npm.cmd` avoids execution-policy blocks affecting the npm PowerShell shim.

### Open your copy of the project

Accept your invitation to the private team repository, then clone it:

```powershell
git clone https://github.com/javecilla/Campus-Equipment-Borrowing-System.git
Set-Location Campus-Equipment-Borrowing-System
```

Already cloned? Open that folder instead. Choose your [assigned branch](#assigned-branches-and-main-integration) using the [first-checkout steps](#first-checkout-of-your-member-branch) before editing. Read [PLAN.md](PLAN.md), [HANDOFF.md](HANDOFF.md), and your [task](docs/tasks.md) to check prerequisites.

### Prepare the Python environment

Create `.venv` once, then install the pinned development dependencies:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Use the explicit `.venv` interpreter below; activation is unnecessary. If `.venv` already exists, run only the install command.

### Install and build frontend assets

From the project root, install exactly the locked JavaScript dependencies and compile the CSS/browser modules:

```powershell
npm.cmd ci
npm.cmd run build
```

Commit `package.json` and `package-lock.json` when dependencies change. `node_modules/` and `static/build/` are local generated files and remain ignored. Rebuild them on each workstation; do not copy them from another member. Python dependencies remain in the requirements files. See [frontend usage](#frontend-assets-tailwind-and-page-scripts) for watch mode and template integration.

<details>
<summary>Using uv, or fixing a missing pip command</summary>

This workstation uses Python 3.13.12 through an existing uv installation. With uv installed, create a new environment using `uv venv --python 3.13 --seed .venv`. If an existing environment has no pip, run `.\.venv\Scripts\python.exe -m ensurepip --upgrade`, then install `requirements-dev.txt`.

</details>

### Create your local database

1. Start PostgreSQL 17 and connect in pgAdmin using your own local account.
2. Under **Databases**, create **campus_equipment**, owned by that account.
3. If the database already exists, keep it. Django will apply missing migrations later.

To check the connection, run this in pgAdmin's Query Tool for that database:

```sql
SELECT current_database(), current_user, current_setting('server_version');
```

Expect `campus_equipment` and PostgreSQL 17.x. This workstation was verified with 17.5. Django migrations create the tables; do not create them manually from the design document.

### Create and edit .env.local

Create the private file **only if it does not exist**:

```powershell
New-Item -Path .env.local -ItemType File -Value (Get-Content -LiteralPath .env.example -Raw) -ErrorAction Stop
```

Open `.env.local` in your editor. The command above deliberately fails if the file already exists, preserving your values.

| Setting                                                   | What to enter                                                                                                                                   |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `IS_LOCAL_DB_CONNECTION` | Required `True` for local PostgreSQL (template default), or `False` for the shared URL; restart Django after editing |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Your database name, account, raw password, host, and port. Usual local values are `campus_equipment`, your account, `127.0.0.1`, and `5432`     |
| `DJANGO_SECRET_KEY`                                       | A unique secret generated with the command below                                                                                                |
| `DJANGO_DEBUG`                                            | `True` for normal local debugging and static serving; use the [error-page preview steps](#preview-custom-error-pages) to inspect the custom 404 |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`     | Keep the template's localhost entries when using port 8000                                                                                      |
| `MCP_DATABASE_URL`                                        | Leave blank unless using optional MCP tooling                                                                                                   |
| `SEED_ACCOUNT_PASSWORD`                                   | Your private default password when running `seed_auth_accounts` or `seed_demo_data`; existing account passwords are not changed                             |

Generate a secret locally, then paste the result into `.env.local`:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```

[.env.example](.env.example) is the full key inventory. Django requires all `DJANGO_*` values, `IS_LOCAL_DB_CONNECTION`, and the selected database configuration: all `DB_*` for `True`, or a nonblank TLS `DATABASE_URL` for `False`. `DJANGO_DEBUG` accepts exactly `True` or `False`; quote passwords containing `#` or whitespace. Django reads literal values without variable expansion, and explicit process environment values override the file. Missing, blank, malformed, or duplicate configuration fails clearly. Keep `.env.local` private and out of Git.

## Switch between local and shared databases

Set `IS_LOCAL_DB_CONNECTION` in your ignored `.env.local`, then restart Django. The template defaults to `True`; existing private files must add this required key explicitly. Only the selected database configuration is used, and a failed connection never switches to the other database.

| Database mode | `.env.local` | Required connection values | Photos for the same environment |
| --- | --- | --- | --- |
| Local PostgreSQL | `IS_LOCAL_DB_CONNECTION=True` | Your local `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | `MEDIA_STORAGE=local` uses your existing `media/` files |
| Shared Neon | `IS_LOCAL_DB_CONNECTION=False` | Private TLS `DATABASE_URL` from Jerome | `MEDIA_STORAGE=neon` uses the existing private storage credentials |

Keep both sets of credentials in the private file; there is no need to erase/retype the shared URL when switching. The flag accepts exactly `True` or `False`. `MEDIA_STORAGE` controls photos separately and does not select the database. Switching does not copy/synchronize records or photos: local and shared datasets can differ, and Git carries neither. Configure each teammate's own local database before selecting local mode.

Verify the actual target before migrations, seeds, cleanup or tests:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database:', connection.settings_dict['NAME'])"
```

`campus_equipment` is the ordinary local database; `neondb` is shared. Keep the [shared-database restrictions](AGENTS.md#shared-database-and-media-safety) when using Neon, and use the [explicit local child-process command](#isolated-tests-while-using-neon) for tests. A local mode value does not make arbitrary `DB_*` values safe: check the real host/database. Process environment values override `.env.local`; restart a shell with no conflicting override if the selected target differs from the file.

## Shared Neon database and photos

Neon supplies PostgreSQL and private S3-compatible Object Storage for shared team development. The project is `Campus-Equipment-Borrowing-System`, branch `production`, region Singapore (`ap-southeast-1`), database `neondb`, bucket `assets`. Each developer still runs the existing Django app locally. PostgreSQL stores records and photo paths; Object Storage stores image bytes. Django retains authentication, authorization, ORM, migrations, workflow services and all custom pages. Neon Auth, Functions, AI Gateway and Realtime are not wired into this app. Internet access and the Neon services are required in this configuration; local static assets still come from the npm build.

### Teammate setup, step by step

1. Clone the repository, select [your assigned member branch](#first-checkout-of-your-member-branch), and bring in the reviewed shared-Neon source using [the team Git workflow](#bring-main-into-your-work-before-starting). Until that source reaches main, use the reviewed `jerome` delivery by team agreement. Older source does not understand `DATABASE_URL` or shared media.
2. Install Python 3.13 and Node/npm, then run these commands from the project root. Create `.venv` only once:

    ```powershell
    py -3.13 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    npm.cmd ci
    npm.cmd run build
    ```

    This installs `django-storages[s3]`/boto3 alongside the existing Django/Psycopg stack. Local PostgreSQL is unnecessary just to use the shared app; install it separately for [isolated automated tests](#isolated-tests-while-using-neon).
3. Ask Jerome for the **pooled database connection URL, storage endpoint, storage access key ID and secret, region, bucket name, and seeded application login password**. Jerome sends these privately by email. A database password, storage secret and Django user's login password have different purposes. Do not put that email, screenshots of credentials, or populated environment files in Git, issues, handoffs or the submission ZIP.
4. If `.env.local` does not exist, create it without overwriting an existing file:

    ```powershell
    New-Item -Path .env.local -ItemType File -Value (Get-Content -LiteralPath .env.example -Raw) -ErrorAction Stop
    ```

    Generate your own `DJANGO_SECRET_KEY` using [the command above](#create-and-edit-envlocal). Edit each existing key once, replacing the placeholders below with the private emailed values:

    ```dotenv
    DJANGO_SECRET_KEY="<your own generated secret>"
    DJANGO_DEBUG=True
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
    DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
    IS_LOCAL_DB_CONNECTION=False
    DATABASE_URL="<pooled PostgreSQL URL from Jerome, including sslmode=require&channel_binding=require>"
    MEDIA_STORAGE=neon
    AWS_ENDPOINT_URL_S3="<storage HTTPS endpoint from Jerome>"
    AWS_ACCESS_KEY_ID="<private storage access key ID>"
    AWS_SECRET_ACCESS_KEY="<private storage secret>"
    AWS_REGION=ap-southeast-1
    AWS_STORAGE_BUCKET_NAME=assets
    ```

    Keep the supplied URL intact, including its encoded password and TLS parameters. `IS_LOCAL_DB_CONNECTION=False` selects `DATABASE_URL`; a missing/invalid URL fails rather than using local data. `True` selects `DB_*` even while the shared URL remains populated. Keep `DB_*` for your own local test database if you have one. `DATABASE_URL_UNPOOLED` is an optional direct URL for coordinator backup/import tools; Django uses `DATABASE_URL`. Leave optional `MCP_DATABASE_URL` blank unless independently configuring read-only MCP; it does not configure Django. `SEED_ACCOUNT_PASSWORD` is only an input to account creation, so teammates do not need it to sign in to already stored accounts.
5. Check the configured connection and existing migrations without changing shared records:

    ```powershell
    .\.venv\Scripts\python.exe manage.py check --database default
    .\.venv\Scripts\python.exe manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database:', connection.settings_dict['NAME']); print('Client TLS:', connection.connection.pgconn.ssl_in_use)"
    .\.venv\Scripts\python.exe manage.py migrate --check
    ```

    Expect database `neondb`, `Client TLS: True`, and exit code 0 from the migration check. An unapplied migration means the coordinator needs to review/apply it; joining members do not initialize a second dataset.
6. Start your local app:

    ```powershell
    .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
    ```

    Open <http://127.0.0.1:8000/accounts/login/>. Use a username/email in [the nine-account table](#seed-the-t21-demonstration-dataset) and the application password emailed by Jerome. Andrea Mendoza (`andrea.mendoza`) is the admin; Miguel Santos (`miguel.santos`) and the other seven listed users are basic users. Changing your local `SEED_ACCOUNT_PASSWORD` does not change these stored passwords. Confirm the catalog and photos appear; restart Django after environment changes.

All members now see the same records, including each other's submitted requests, approvals, returns and image updates. The October 22 migration copied **9 accounts, 12 categories, 29 catalog items, 46 units, 10 maintenance records, 30 requests, 20 loans, 28 returns and 23 referenced images**. Those are migration counts, not permanent dashboard totals.

Do **not** rerun seeds, `upload_catalog_photos`, `flush`, transaction/unit cleanup or database recreation as part of teammate onboarding. These commands target the configured database, which is now shared. Coordinate schema changes, resets and fixture imports with Jerome; use a local database for destructive professor-demo rehearsals. There is one central dataset, so concurrent manual edits affect everyone.

### Isolated tests while using Neon

Create your own local PostgreSQL 17 `campus_equipment` database and fill the existing `DB_*` keys with its credentials. The local account needs permission to create/drop the separate `test_campus_equipment` database. Run the complete suite through a child process that explicitly selects local PostgreSQL and local media:

```powershell
.\.venv\Scripts\python.exe -c "import os, subprocess, sys; sys.exit(subprocess.call([sys.executable, 'manage.py', 'test', '--noinput'], env={**os.environ, 'IS_LOCAL_DB_CONNECTION': 'True', 'DATABASE_URL': '', 'MEDIA_STORAGE': 'local'}))"
```

This leaves `.env.local` pointing at Neon for ordinary startup. The child explicitly sets `IS_LOCAL_DB_CONNECTION=True`; clearing its URL is an additional explicit isolation setting, without removing credentials from the private file. Do not use an unqualified `manage.py test --noinput` with the shared Neon configuration: it selects `test_neondb`, which other members could also use. Tests create their own fixtures and do not require seeding or clearing the populated development database. Never store valuable data in a `test_*` database.

### Coordinator import and maintenance

The existing local PostgreSQL database and `media/` originals are retained. The initial import used a private custom-format `pg_dump`, restored into an empty Neon database with `pg_restore --no-owner --no-acl --single-transaction --exit-on-error`. Both services were checked before switching `.env.local`; all 14 domain-model datasets matched the source field for field. Backups belong in ignored `output/private-backups/`, with credentials supplied privately rather than in command history. Use the direct connection URL for native backup/import tools, and a PostgreSQL client compatible with the server version (Neon was verified at 18.6; local test server at 17.5).

For a future approved media import, place the matching originals under `MEDIA_ROOT` with their stored relative paths, configure Neon media and the matching database, then run:

```powershell
.\.venv\Scripts\python.exe manage.py upload_catalog_photos
```

This copies only referenced catalog photos, compares SHA-256 bytes for existing objects, verifies uploads, and leaves source files and database paths unchanged. Missing local files or mismatched destination bytes fail explicitly; it never overwrites an existing mismatched object. The initial import uploaded 23 photos; repeating it verified 23 matching objects and uploaded zero. Interrupted imports can be rerun after resolving the reported failure. New app uploads go directly to the selected storage backend; this command is not a routine synchronization job.

Keep database and media backups together: PostgreSQL dumps contain paths, not image bytes, and current Neon media must be backed up from Object Storage, not an old local folder. The bucket remains private; the app streams photos through its existing role-protected routes. The pooled connection disables server-side cursors for PgBouncer compatibility. This setup moves data services only; Django application hosting, measured performance and a complete operational recovery rehearsal remain separate work. Provider references: [Neon Django](https://neon.com/docs/guides/django), [private S3-compatible storage](https://neon.com/docs/storage/s3-compatibility), and [django-storages S3 backend](https://django-storages.readthedocs.io/en/stable/backends/amazon-S3.html).

## Application migrations, checks, and local server

For an isolated local database, check configuration and apply the shared migrations. With Neon active, follow [teammate setup](#teammate-setup-step-by-step) instead; the coordinator applies approved shared migrations once.

```powershell
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py migrate --noinput
```

Then start the server:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open **<http://127.0.0.1:8000/>** for the custom sign-in route. With `DJANGO_DEBUG=True`, the Tailwind/font preview remains available directly at **<http://127.0.0.1:8000/test>**. The terminal should report no system-check errors or unapplied migrations. Keep that terminal open while working; stop with Ctrl+C, or Ctrl+Break on Windows.

### Earlier startup screen

The supplied screenshot below records the earlier minimal sign-in page. Local UI-09 now uses a responsive M3 layout with the existing brand logo/wave, a contextual desktop panel and stacked compact-screen form; the authentication flow is unchanged:

![Campus Equipment sign-in page with username or email, password, and the green bottom wave](static/images/login-screen.png)

The current root is `accounts:home`: anonymous visitors go to the custom login page and active users go to `/portal/` or `/manage/` from their stored role. `/test` remains a separate debug-only preview and returns 404 when debug is disabled. Role workspaces display stored data; migrations alone supply no demonstration transactions.

<details>
<summary>Earlier setup screens (historical)</summary>

The screenshot below records Django's initial startup before custom routes were added:

![Django initial installation success page with DEBUG=True, before custom routes are added](static/images/inital-setup-running-success-screen.png)

The screenshot below records the temporary development index that preceded T04:

![Earlier development index at / with a Tailwind and font preview link to /test](static/images/new-inital-setup-running-success-screen.png)

</details>

Migrations initialize the settings row (7 days and 3 units per item) and its system audit. They create no accounts or equipment. Use the commands below for local account setup or the [T21 demonstration dataset](#seed-the-t21-demonstration-dataset).

### Create an administrator account

Run the CLI-only setup command from a trusted local shell after migrations:

```powershell
.\.venv\Scripts\python.exe manage.py create_admin --username campus_admin --first-name Campus --last-name Administrator --email admin@example.invalid
```

The command prompts for the password twice without accepting it as a command-line argument. Django password validators run before one atomic write creates the active `ADMIN` and its Profile. The command fixes `is_staff` and `is_superuser` to false because runtime management access uses the two-role contract. Treat shell and database access as the authorization boundary; there is no public administrator-creation or promotion endpoint. Replace the fictional values above with approved local demonstration details and never commit credentials.

### Seed authentication test accounts

After migrations, run this command in a trusted local terminal:

```powershell
.\.venv\Scripts\python.exe manage.py seed_auth_accounts
```

Set `SEED_ACCOUNT_PASSWORD` in your ignored `.env.local` first. The command uses that same private password for both accounts without prompting or printing it; explicit process environment values override the file. Only the two seed commands require this setting. Keep its value out of shared files and Git.

It creates the fictional `auth_demo_admin` (`ADMIN`) and `auth_demo_user` (`BASIC_USER`), both active with Profiles and Django staff/superuser flags false. Django validates and hashes the configured password. Both accounts are created in one transaction; a missing/blank/invalid password or either username already existing causes a clear error without changing accounts. Reuse existing accounts or run `manage.py changepassword USERNAME` if needed. Changing the environment value does not reset existing accounts.

Open `/accounts/login/` and sign in with each account separately using the "Username or email" field:

| Role       | Username          | Email                        |
| ---------- | ----------------- | ---------------------------- |
| Admin      | `auth_demo_admin` | `auth-admin@example.invalid` |
| Basic user | `auth_demo_user`  | `auth-user@example.invalid`  |

Both accounts use your private `SEED_ACCOUNT_PASSWORD`; there is no password shipped in the repository. Choose your own value in `.env.local`. To replace the password on existing accounts, follow [password changes](#change-seed-passwords-while-keeping-records); changing the environment value alone does not update them. Email matching ignores letter case; shared or otherwise ambiguous email addresses require an unambiguous username instead.

The admin should reach `/manage/` and receive 403 at `/portal/`; the basic user should reach `/portal/` and receive 403 at `/manage/`. Sign out using the page's logout button, then reopen the protected destination and confirm it redirects to login. These are the integrated role workspaces; use the feature navigation for existing workflows. This two-account development seed does not satisfy T21's full fictional demonstration dataset.

### Seed the T21 demonstration dataset

The demonstration commands have separate purposes: `seed_demo_data` creates the accounts below; [`seed_demo_units`](#seed-physical-units-for-existing-equipment) tops up stock in an existing catalog; [`seed_demo_transactions`](#seed-august-october-2026-transactions) imports the user-requested August-October history using existing equipment. The account command creates no inventory, requests, allocations, loans or returns. Equipment and photos remain in the configured database/storage; shared Neon already contains the migrated dataset. The [demo command runbook](#demo-command-runbook) lists the preparation order and cleanup choices.

After existing migrations, set a Django-valid `SEED_ACCOUNT_PASSWORD` privately in ignored `.env.local`, then run once:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_data
```

The command atomically creates one ADMIN and eight BASIC_USER accounts with Profiles. All identities below are realistic fictional examples, with `username@example.invalid` emails and blank contact numbers. Each account has a usable password hashed from the private seed value; the password is neither shipped nor printed.

| Full name | Username | Email | Role | Default password source |
| --- | --- | --- | --- | --- |
| Andrea Mendoza | `andrea.mendoza` | `andrea.mendoza@example.invalid` | ADMIN | `.env.local` → `SEED_ACCOUNT_PASSWORD` |
| Miguel Santos | `miguel.santos` | `miguel.santos@example.invalid` | BASIC_USER | `.env.local` → `SEED_ACCOUNT_PASSWORD` |
| Sofia Reyes | `sofia.reyes` | `sofia.reyes@example.invalid` | BASIC_USER | `.env.local` → `SEED_ACCOUNT_PASSWORD` |
| Gabriel Cruz | `gabriel.cruz` | `gabriel.cruz@example.invalid` | BASIC_USER | `.env.local` → `SEED_ACCOUNT_PASSWORD` |
| Isabella Garcia | `isabella.garcia` | `isabella.garcia@example.invalid` | BASIC_USER | `.env.local` → `SEED_ACCOUNT_PASSWORD` |
| Daniel Navarro | `daniel.navarro` | `daniel.navarro@example.invalid` | BASIC_USER | `.env.local` → `SEED_ACCOUNT_PASSWORD` |
| Camille Torres | `camille.torres` | `camille.torres@example.invalid` | BASIC_USER | `.env.local` → `SEED_ACCOUNT_PASSWORD` |
| Rafael Ramos | `rafael.ramos` | `rafael.ramos@example.invalid` | BASIC_USER | `.env.local` → `SEED_ACCOUNT_PASSWORD` |
| Alyssa Flores | `alyssa.flores` | `alyssa.flores@example.invalid` | BASIC_USER | `.env.local` → `SEED_ACCOUNT_PASSWORD` |

Sign in at <http://127.0.0.1:8000/accounts/login/> with any listed username or email. For the password, enter the actual value of `SEED_ACCOUNT_PASSWORD` from your private `.env.local` when you created the accounts. Explicit process environment values override the file during seeding. The admin reaches `/manage/`; basic users reach `/portal/`. For an isolated local database, each developer supplies their own private seed value. For shared Neon, use the existing accounts and application password emailed by Jerome; do not reseed. Changing that environment value later does not change stored passwords; use `manage.py changepassword USERNAME` to reset an existing account. Share instructor demonstration credentials only through the designated private channel. This table documents the environment key; live passwords stay in private configuration.

Existing unrelated accounts, equipment, images, maintenance, settings and transactions remain unchanged by this seed. Case-insensitive username/email collisions fail before writes; invalid passwords or audit/database errors roll back all nine new accounts. There is no destructive reset mode. The one-time user-authorized local cleanup is recorded in [the cleanup handoff](handoffs/clean-demonstration-accounts-and-equipment-preservation-10-22-2026.md); it is separate from this safe account-creation command. Old sessions were cleared, so sign in again using the new accounts. The former `auth_demo_*` and `t21_*` accounts no longer exist in this local database.

See [implementation](operations/demo_seed.py) and [Module 20](docs/manual-test-guide.md#module-20--fictional-demonstration-dataset-t21) for current examples and verification. Run the focused PostgreSQL checks with:

```powershell
.\.venv\Scripts\python.exe manage.py test operations.tests.test_demo_seed --noinput
```

### Physical units for the current local catalog

On October 22, 2026, one Good/Available demonstration unit was registered for each of the eleven catalog items that had none. Audio Cassette Duplicator was restored from archive with the user's approval before its unit was added. All 29 catalog items have at least one physical unit: **46 units total**. The registration snapshot, before transaction import, had 39 Available, 5 Maintenance and 2 Retired units. Existing units, maintenance history and all 23 uploaded photos were preserved. Current borrowing counts belong to the [transaction snapshot](#seed-august-october-2026-transactions).

| Equipment | Added asset code |
| --- | --- |
| TP-Link Wi-Fi Router | `CEL-NET-RTR-001` |
| 5-Port Network Switch | `CEL-NET-SWT-001` |
| Cat6 Ethernet Cable (10m) | `CEL-NET-CAT6-001` |
| Wireless Presentation Clicker | `CEL-PRA-CLK-001` |
| Portable Whiteboard | `CEL-PRA-WBD-001` |
| Desktop PC (Core 2 Duo) | `CEL-LGC-PC-001` |
| CRT Monitor 17-inch | `CEL-LGC-CRT-001` |
| PS/2 Keyboard | `CEL-LGC-KBD-001` |
| Cassette Tape Recorder | `CEL-ANR-CTR-001` |
| VHS Player | `CEL-ANR-VHS-001` |
| Audio Cassette Duplicator | `CEL-ANR-DUP-001` |

These are fictional demonstration inventory entries, with registration date October 22 as their acquisition date and practical handling notes. They were added locally through the existing audited unit-registration service; the account seed command does not create this equipment or copy uploaded images to another developer's database. Other developers can use the [physical-unit seed](#seed-physical-units-for-existing-equipment) for bulk registration or `/manage/units/new/` for individual stock. See the [unit-registration follow-up](handoffs/seed-account-access-table-and-missing-physical-units-10-22-2026.md) and [Module 20](docs/manual-test-guide.md#module-20--fictional-demonstration-dataset-t21) for the verified local state.

### Seed physical units for existing equipment

After creating the nine demonstration accounts and adding equipment to the catalog, run:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_units --admin-username andrea.mendoza --quantity-per-item 2 --acquired-on 2026-07-01
```

This tops up each active catalog item under an active category to **at least two total physical units**, counting all existing units regardless of state. An item with two or more units receives none; an item with one receives one. Repeat runs at the same quantity add no duplicates. Use `--quantity-per-item 1` if you only need one unit per item. All three options are required; change the administrator username when using another active ADMIN.

New units are Good/Available, with unique `DEMO-<catalog-id>-<sequence>` asset codes, practical accessory/inspection notes and the supplied acquisition date. They are registered through the existing audited service in one transaction. Existing asset codes, conditions, statuses, acquisition dates, maintenance and photos remain unchanged. Archived items/categories are excluded and reported as such; restore them in the management UI first if they need stock. Invalid arguments, unavailable administrators or asset-code collisions fail without partial registration. No catalog records or photos are bundled with this command.

For the fixed August-October history, July 1 is a fictional acquisition date before its first reservation. Use an accurate acquisition date for your own records; the importer rejects stock acquired after its historical allocation. Retired/damaged/reserved stock counts toward the top-up target, so a successful top-up alone does not guarantee sufficient serviceable equipment for the history. The current populated database already has units and transactions; running this command there may add extra stock and change dashboard counts.

### Seed August-October 2026 transactions

This command imports realistic **fictional** campus borrowing history from August through **October 22, 2026**, with most activity in October. It reuses the documented accounts and the existing named equipment from the manually entered catalog; it creates no accounts, catalog items or physical units, and does not replace photos. Prepare the equipment named in [the plan](operations/demo_transaction_plan.py), including enough serviceable stock with acquisition dates no later than each historical reservation. The current local inventory satisfies these prerequisites, and the history was imported successfully on October 22; do not rerun it to refresh dates.

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_transactions
```

The importer requires an empty borrowing history and the active seeded accounts. Missing/archived equipment, insufficient stock, acquisition/maintenance conflicts and database errors fail the whole transaction. An existing borrowing history produces an explicit error; there is no overwrite, reset or duplicate-import mode. Existing acquisition dates, master records, old maintenance records and old audits remain intact; stock states change only through the existing approval, issue, cancellation, return and repair services.

Each workflow runs through the actual services, then only its newly created transaction/audit records are assigned the historical dates. Original database registration times on equipment/accounts remain the actual entry/import times, which can be later than the imported events. Server time is not patched, constraints remain enabled, and no historical dates are accepted through ordinary application endpoints. The importer checks acquisition dates, reservation exclusivity and maintenance windows before committing. New event dates end October 22; outstanding due dates extend through October 26, still inside the requested October scope.

| Demonstration metric, as of October 22 | Count |
| --- | --- |
| Requests | 30: 3 submitted in August, 4 in September, 23 in October |
| Issued loans | 20: August 3, September 4, October 13 |
| Loan units / returned / outstanding | 34 / 28 / 6 |
| Request states | 16 Returned, 1 Partially returned, 3 Issued, 2 Approved, 2 Rejected, 3 Cancelled, 3 Pending |
| Dashboard Available / Pending / active / overdue | 30 / 3 / 4 / 2 |
| Current inventory states | 30 Available, 3 Reserved, 6 Issued, 5 Maintenance, 2 Retired |
| Maintenance | 9 existing records preserved; 1 new damaged-return record repaired and closed |

The plan includes real equipment names, course/event purposes, practical decision/return notes, an Approved cancellation releasing reservations, partial return, overdue outstanding loans and damaged-return repair. These are demonstration scenarios, not evidence of actual campus borrowing or technician work. Overdue counts naturally change after October 22; the command does not freeze the clock or refresh dates on repeat execution. [Module 20](docs/manual-test-guide.md#module-20--fictional-demonstration-dataset-t21) supplies current local examples and expected checks.

Run the focused real PostgreSQL integration tests with:

```powershell
.\.venv\Scripts\python.exe manage.py test operations.tests.test_demo_transactions --noinput
```

### Demo command runbook

**Shared Neon is already populated.** This runbook is for an isolated local database or an explicitly coordinated central reset/import. Seeds and purges use whichever database is configured; setting `DB_NAME` alone does not select local data while `IS_LOCAL_DB_CONNECTION=False`.

Run from the project root using your private `.env.local`. Every command targets its configured database; explicit process environment variables override that file. Run commands one at a time and stop if one fails. Seeds require migrations first. Your current populated local data does **not** need these commands rerun for an ordinary server restart.

| Need | Command / procedure | Result |
| --- | --- | --- |
| Default admin + eight basic users | `manage.py seed_demo_data` | Nine accounts from the table above; password from `SEED_ACCOUNT_PASSWORD` |
| Small authentication-only test | `manage.py seed_auth_accounts` | Two separate `auth_demo_*` accounts; choose this instead of the nine-account seed when only testing sign-in |
| Physical stock for existing equipment | `manage.py seed_demo_units --admin-username andrea.mendoza --quantity-per-item 2 --acquired-on 2026-07-01` | Tops up active items; preserves existing units/catalog/photos |
| Borrow, issue, return and repair history | `manage.py seed_demo_transactions` | Imports the fixed 30 requests / 20 loans; requires empty history and the named equipment/stock |
| Professor wants empty transaction history | `manage.py clear_borrowing_data` | Deletes all borrowing history; keeps accounts, catalog/photos, stock and maintenance |
| Professor also wants no physical stock or maintenance | `manage.py clear_equipment_units` after clearing borrowing | Deletes all units and maintenance; keeps accounts and catalog/photos |
| Professor wants absolutely no existing database records | [Recreate the database](#delete-all-local-records-and-seed-again) | Deletes accounts, catalog/photo references, units, transactions, audits and settings; migrations restore required system rows |

The table abbreviates the executable; use `.\.venv\Scripts\python.exe manage.py ...` in PowerShell. Cleanup commands delete **all records in their stated scope**, including manually entered records, rather than identifying only fictional seed rows. They are trusted local CLI tools, not application workflow actions. They do not prompt. Stop Django and other database writers before cleanup, check the target database, and take a private backup if you need to restore the current demonstration later.

For a new database **with the required catalog already prepared**, use this order. Skip the account seed if these users already exist:

```powershell
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py seed_demo_data
.\.venv\Scripts\python.exe manage.py seed_demo_units --admin-username andrea.mendoza --quantity-per-item 2 --acquired-on 2026-07-01
.\.venv\Scripts\python.exe manage.py seed_demo_transactions
.\.venv\Scripts\python.exe manage.py check --database default
```

An empty database has no catalog. Register the equipment named in [the transaction plan](operations/demo_transaction_plan.py) at `/manage/items/new/` before unit/history seeding, or restore your private database backup. These commands cannot reconstruct manually uploaded equipment/photos after a full database deletion. A different stock count changes Available totals; the current 46-unit dashboard snapshot is not a universal seed result.

### Preview custom error pages

The custom [403](templates/403.html) and [404](templates/404.html) share the project's minimal light design. Django shows its diagnostic 404 instead of our template while `DJANGO_DEBUG=True`.

1. Stop the server, set `DJANGO_DEBUG=False` in your ignored `.env.local`, and save it. An explicit `DJANGO_DEBUG` process environment variable overrides this file; remove or update that override if one is set.
2. Start the local preview with static serving enabled:

    ```powershell
    .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --insecure
    ```

3. Visit <http://localhost:8000/accounts/login/s> to see the custom 404. For a 403, sign in as the basic user and open `/manage/`, or as the admin and open `/portal/`. The home action returns to the appropriate role destination, or sign-in when anonymous. `/test` also returns 404 with debug disabled.
4. After inspection, stop the server, restore `DJANGO_DEBUG=True`, and restart with the normal [startup command](#everyday-startup).

`--insecure` serves local development assets when debug is disabled. Use it only for this local preview; it is not a production server or deployment configuration.

### Reset local development data

If your `.env.local` uses Neon, first switch to your own local database and media (`IS_LOCAL_DB_CONNECTION=True`, `MEDIA_STORAGE=local`, valid local `DB_*`) and restart Django. Run the connection check in [teammate setup](#teammate-setup-step-by-step) to verify the actual target before cleanup. A centralized reset requires Jerome's coordination and current database/Object Storage backups; the local examples below are not teammate onboarding steps.

Choose the smallest scope requested by your professor using the [command table](#demo-command-runbook). Cleanup is destructive and is **not part of everyday startup**. The cleanup commands below have been exercised in a separate PostgreSQL test database; the current local demonstration records have not been cleared for this runbook.

#### Back up the populated demonstration before cleanup

Use pgAdmin's **Backup** action on the database named by `DB_NAME`, selecting **Custom** format, and save it privately under `output/private-backups/`. Also copy the uploaded files from `media/`; a database dump contains photo paths, not image bytes. Both directories are ignored by Git. For example, choose a new destination for each media backup:

```powershell
New-Item -ItemType Directory -Path output/private-backups -Force
Copy-Item -LiteralPath media -Destination output/private-backups/media-before-professor-demo -Recurse -ErrorAction Stop
```

To recover the original demonstration, restore the custom dump into a newly recreated empty database using pgAdmin **Restore**, and restore its matching `media/` files. A full dump already includes accounts, units, history, settings and migration records: do not run the seed commands after a full restore. Keep the private password used by those stored accounts; editing the seed environment value does not update restored passwords. The [T24 recovery record](docs/operational-verification.md#backup-and-recovery-demonstration) now documents a separate current-Neon-to-local rehearsal; the preserved development database was not overwritten.

#### Clear transactions while retaining equipment and maintenance

For “fresh transaction history, keep my equipment and pictures,” stop the server and run:

```powershell
.\.venv\Scripts\python.exe manage.py clear_borrowing_data
```

This atomically deletes all requests/items, allocations, loans/loan units, returns and audits targeting requests, loans or returns. Reserved/Issued units become Available; other unit states and conditions remain unchanged. Accounts, Profiles, sessions, categories, catalog/photo references, units, maintenance and settings remain. Maintenance records keep their repair history but their `source_return` links are detached because the returns no longer exist. Their existing audit text can still mention the deleted return. There are no borrowing rows left for charts/reports; Pending, active and overdue counts become zero.

You can now demonstrate new manual borrowing through the portal. Reimporting the fixed history still requires valid stock/acquisition/maintenance windows. Preserved maintenance can conflict with its historic dates; restoring the pre-history backup preserves the original equipment setup exactly. If you instead want entirely new demonstration stock, use the next procedure.

#### Clear physical units and maintenance while retaining the catalog and photos

For “keep the equipment list and pictures, but delete transactions, physical units and maintenance,” stop the server and run:

```powershell
.\.venv\Scripts\python.exe manage.py clear_borrowing_data
.\.venv\Scripts\python.exe manage.py clear_equipment_units
```

The second command refuses to proceed while any borrowing request remains. It removes **all** physical units, maintenance records and audits targeting those units/maintenance. Categories, catalog items and their photo references, accounts/Profiles/sessions, settings and unrelated audits remain. Uploaded files are untouched. The catalog now has zero stock; you can register units manually or rebuild demonstration stock/history:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_units --admin-username andrea.mendoza --quantity-per-item 2 --acquired-on 2026-07-01
.\.venv\Scripts\python.exe manage.py seed_demo_transactions
```

This creates new asset identities and fresh maintenance from the history, rather than restoring the previous 46 units and ten maintenance records. Existing users keep their passwords; do not rerun `seed_demo_data` for this procedure.

An existing-username error from either account seed means those accounts already exist. Use their login or change their passwords below; seeds deliberately refuse to overwrite identities.

#### Change seed passwords while keeping records

Run these commands and follow their hidden password/confirmation prompts:

```powershell
.\.venv\Scripts\python.exe manage.py changepassword auth_demo_admin
.\.venv\Scripts\python.exe manage.py changepassword auth_demo_user
```

For the nine-account demonstration, use the username from the table, for example:

```powershell
.\.venv\Scripts\python.exe manage.py changepassword andrea.mendoza
.\.venv\Scripts\python.exe manage.py changepassword miguel.santos
```

Use your private `SEED_ACCOUNT_PASSWORD` value for each if you want both accounts to match the seed configuration. These commands keep accounts, Profiles, and transaction history. Editing `.env.local` alone does not change stored password hashes; reseeding is unnecessary for a password change.

#### Delete only the two authentication seed accounts

For your disposable local test identities, this deletes `auth_demo_admin`, `auth_demo_user`, and their cascading Profiles. Check that `.env.local` points to your own development database before running it:

```powershell
.\.venv\Scripts\python.exe manage.py shell --command "from accounts.models import User; print(User.objects.filter(username__in=['auth_demo_admin', 'auth_demo_user']).delete())"
.\.venv\Scripts\python.exe manage.py seed_auth_accounts
```

Run the seed command only after deletion succeeds. It recreates both identities using the current private `SEED_ACCOUNT_PASSWORD`; sign in again afterward. This does not reset equipment, settings, or other accounts. If either identity has protected workflow, audit, or settings references, Django raises `ProtectedError` and prevents deletion. Keep that history and use password changes instead; do not bypass the protections.

#### Delete all local records and seed again

**This deletes the entire selected database, including every account, Profile, session, equipment record, transaction, audit entry, setting, and migration record.** Use it only for your own disposable development database. [Back up the database and media first](#back-up-the-populated-demonstration-before-cleanup) if any records must be kept. Your code, migration files, `.env.local`, generated frontend assets and uploaded image files remain on disk. Catalog/photo database references are deleted, so retained image files will no longer appear in the app unless their catalog records are restored. No file deletion is included in this procedure.

1. Verify `DB_HOST`, `DB_PORT`, `DB_NAME`, and `DB_USER` in your private `.env.local`. The SQL below targets the standard local `campus_equipment` database; use your exact disposable database name if different. Stop Django with Ctrl+C and disconnect other clients from that database, including pgAdmin Query Tool tabs and any MCP/database tools.
2. In pgAdmin, connect to that same PostgreSQL server as the account named by `DB_USER`, then open Query Tool on the maintenance database **postgres**, not `campus_equipment`. Keep autocommit enabled. Execute each statement separately; database drop/create cannot run inside a transaction:

    ```sql
    DROP DATABASE campus_equipment;
    ```

    ```sql
    CREATE DATABASE campus_equipment;
    ```

    If PostgreSQL reports active connections, disconnect the clients it identifies before retrying. If it reports insufficient privileges, use the database owner/administrator to recreate the database with `DB_USER` as its owner, following [local database setup](#create-your-local-database). Stop on an error; do not continue to migrations until recreation succeeds.

3. From the project root, run these commands one at a time. Continue only after each succeeds:

    ```powershell
    .\.venv\Scripts\python.exe manage.py migrate --noinput
    .\.venv\Scripts\python.exe manage.py check --database default
    .\.venv\Scripts\python.exe manage.py showmigrations
    ```

    Migrations rebuild the schema, initialize the required settings singleton (7 days / 3 units per item) and its SYSTEM audit, and recreate Django metadata. All migrations should show `[X]`. Stop here if your professor wants an empty application database: there are no user accounts or equipment/transaction records, only required framework/system rows.

    If login accounts are needed afterward, choose **one** account setup:

    ```powershell
    .\.venv\Scripts\python.exe manage.py seed_demo_data
    ```

    This supplies the documented one-admin/eight-user roster with the current private password. For only the two authentication test accounts, use `seed_auth_accounts` instead. For only an administrator and no borrowers, use [create_admin](#create-an-administrator-account). Equipment and transaction seeds require catalog preparation as described in the [runbook](#demo-command-runbook); migrations and account seeds do not restore deleted catalog/photos.

4. Restart Django using [everyday startup](#everyday-startup) when you are ready. If you created accounts, verify the roles using the matching seed table. Existing login sessions were deleted, so sign in again.

Do not use `manage.py flush` as this project's fresh-start procedure. It deletes data created by migrations, including `SystemSetting` row 1, but retains migration history; running ordinary `migrate` afterward will not rerun the already-applied initialization migration. Use database recreation above even if you have already flushed the disposable database. Keep the migration files in Git; deleting them or using `--fake` is not a data-reset procedure.

## Everyday startup

Start PostgreSQL and open the project root. In terminal 1, keep both asset watchers running:

```powershell
npm.cmd run dev
```

In terminal 2, run Django:

```powershell
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Keep both terminals open; refresh the browser after edits (no automatic browser reload is installed). Stop the watchers and Django with Ctrl+C. For a one-off run, `npm.cmd run build` can replace terminal 1.

Stop asset watchers before syncing a branch update that moves source directories, then restart them using the updated package scripts. The shared source directory is `static/`; generated bundles stay in `static/build/` and collection output in `staticfiles/`.

After team updates, [sync your branch](#bring-main-into-your-work-before-starting) first. If requirements changed, run `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` before migrating. If `package-lock.json` changed, stop the watchers, run `npm.cmd ci`, then restart them. Keep your own `.env.local`; add any new required keys from the template.

<a id="frontend-assets-tailwind-and-axios"></a>

## Frontend assets: Tailwind and page scripts

The library rationale and course-pattern requirements are in [architecture.md](docs/architecture.md#required-patterns-and-selected-libraries). This setup adds a shared template shell and asset build; feature owners still implement the role layouts and pages.

| Path                     | Purpose                                                                                                                                   |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `static/css/app.css`     | Tailwind entry point, local fonts, shared M3 components and explicit source locations                                                        |
| `static/css/fonts.css`   | Existing local font declarations; imported into Tailwind's base layer                                                                     |
| `static/js/*.js`         | Browser page modules; the JavaScript build compiles every top-level module                                                                |
| `static/build/`          | Generated CSS, browser ES modules/chunks, and any generated dependency license notices                                                    |
| `templates/base.html`    | Shared document shell loading `build/app.css`, favicon links, and metadata; blocks: title, meta_description, extra_head, content, scripts |
| `static/images/favicon/` | Supplied browser/touch icons and web manifest; manifest icon paths are relative to this directory                                         |

`npm.cmd run build` compiles minified CSS/browser modules. The fixed palette lives in `static/css/app.css`; no color-generation dependency or separate `theme.css` is required. `build:css` invokes `check:theme` (`scripts/check-theme.mjs`) before compiling, including at CSS watcher startup. Run `npm.cmd run check:theme` after editing semantic role colors; the dependency-free check rejects nine text-role pairs below 4.5:1. See the [canonical component rules](docs/coding-standards.md#shared-m3-roles-and-components-ui-09) for the desktop sidebar and compact navigation. Frontend agents also load the shared [campus-ui skill](.agents/skills/campus-ui/SKILL.md); it guides component reuse and browser verification without acting as an enforcement service.

 `npm.cmd run dev` runs CSS and JavaScript watchers together and stops the sibling if either exits. Build before running `collectstatic` or assembling a submission; include the complete generated build, including chunks/license files, in a runnable artifact. Source control keeps the npm lockfile and source assets; the submission process must build assets explicitly because ignored files are not supplied by Git.

When updating a workstation from the earlier Axios setup, remove its obsolete generated `static/build/http.js` and `static/build/axios-LICENSE.txt` if present before rebuilding or collecting static files. Current builds do not create those files. Keep the source assets and font license files.

### Frontend preview

The shared shell and page modules use the `compiled_asset` template tag to append a content fingerprint to built CSS/JavaScript URLs. Rebuilding changes that URL when bundle bytes change, avoiding stale browser styles or scripts. Missing compiled files raise an explicit build instruction. T23 adds `operations.E001` through Django's staticfiles checks, so ordinary `runserver` refuses to serve until all required entry bundles exist. Run `npm.cmd ci`, then `npm.cmd run build`; verify with `.\.venv\Scripts\python.exe manage.py check --tag staticfiles`. Hosts that skip startup checks, including separate WSGI/ASGI deployments, must run this preflight explicitly. The check detects absent entries, not stale contents or every generated chunk; run the asset build before starting the app or tests. Keep these generated bundles with a runnable submission and rebuild before static collection.

After building assets and starting Django, go directly to **<http://127.0.0.1:8000/test>** (no trailing slash) with `DJANGO_DEBUG=True` in your private `.env.local`. The preview links back to the application home. Expect a pale background, rounded typography cards, green/slate/amber swatches, and the message **DM Sans and Poppins loaded successfully from local assets.** The message checks real font loading in the browser; it reports a failure if font declarations/files cannot load. If it stays at “Checking local fonts…”, check that `build/frontend-test.js` loads and rebuild assets.

The page uses the shared base template and compiled assets. Typography cards sit side by side on wider screens; color swatches stack on small screens. It accepts GET/HEAD without sign-in, reads no application data, and returns 404 when debug is disabled. [config/views.py](config/views.py) owns the preview handler, [templates/dev/frontend-test.html](templates/dev/frontend-test.html) its markup, and [static/js/frontend-test.js](static/js/frontend-test.js) the font check. This is a development preview, not a role layout or product page.

### Styling templates

Feature pages extend the existing `operations/manage/base.html` or `accounts/portal/base.html` role layout and fill `workspace_content`; both inherit the shared document shell. Use literal Tailwind class names in templates, app Python files (including form-widget attributes), or `static/js/`; these locations are scanned explicitly. Write complete alternative class names rather than concatenating fragments such as `bg-{{ color }}-500`. Use `font-sans` for DM Sans and `font-heading` for Poppins. The current font CSS also applies Poppins to headings.

The common shell loads the compiled stylesheet, including local fonts; do not load fonts.css again when extending it. Tailwind styling does not enforce roles, active accounts, ownership, or workflow rules. Django views/forms/services remain authoritative.

### Browser interactions

Use ordinary Django forms and links for the current server-rendered pages. Login and logout use native form submission with CSRF tokens; no JavaScript HTTP library is installed or needed.

Load an actual page module through its template's scripts block, preserving `{{ block.super }}`, with `<script type="module" src="{% compiled_asset 'build/your-page.js' %}"></script>` and `{% load assets %}`. The build compiles/minifies `frontend-test.js`, `workspace-navigation.js`, the local `equipment-photo.js` preview, `borrowing-slip.js`, `request-list.js` for whole-row request navigation and T18's `dashboard-charts.js`. The workspace uses a native top-bar profile link and a red sidebar POST logout form; no account dropdown script is needed. Use the [coding guide](docs/coding-standards.md#browser-interactions) for future explicitly authorized enhancements and the [HTTP contract](docs/api_spec.md#common-protocol) for existing HTML/form/CSV response semantics.

## Working with migrations

### Apply existing migrations

Use the migration files supplied by the team. On shared Neon, only the coordinator applies approved migrations; other members use read-only `showmigrations`, `migrate --plan` and `migrate --check`:

```powershell
.\.venv\Scripts\python.exe manage.py showmigrations
.\.venv\Scripts\python.exe manage.py migrate --plan
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py migrate --check
```

`[X]` means applied in `showmigrations`. `migrate --plan` previews work; `migrate` applies it. An updated database reports no migrations to apply. `migrate --check` fails if any are pending.

### Change models in your assigned task

Coordinate shared model changes with their owners. For an authorized inventory change, for example:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations inventory --name describe_your_schema_change --noinput
.\.venv\Scripts\python.exe manage.py migrate --plan
.\.venv\Scripts\python.exe manage.py migrate --noinput
```

Review and include models and migrations together. Preserve applied/shared migrations; use new migrations for corrections. Reconcile conflicting migration leaves with affected owners. Do not delete another member's migration or use `--fake` to hide a mismatch. The custom user is already `accounts.User`; the settings initialization data migration is deliberately irreversible.

## Formatting and code consistency

Formatting is split by language so Django tags and Python keep their correct parsers:

| Files                              | Write formatting                                  | Check without rewriting                        |
| ---------------------------------- | ------------------------------------------------- | ---------------------------------------------- |
| Source JS/MJS/CSS and project JSON | `npm.cmd run format`                              | `npm.cmd run format:check`                     |
| Django templates                   | `.\.venv\Scripts\djlint.exe templates --reformat` | `.\.venv\Scripts\djlint.exe templates --check` |
| Python                             | `.\.venv\Scripts\ruff.exe format .`               | `.\.venv\Scripts\ruff.exe format --check .`    |

Install both dependency sets first: `npm.cmd ci` and `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt`. Prettier is pinned in package.json; djLint/Ruff are pinned in requirements-dev.txt. `.prettierrc.json` and pyproject.toml hold shared options; `.prettierignore` excludes Django HTML, Python, private files, dependencies, fonts, and generated output. The npm scripts target source/config files and `scripts/**/*.mjs`, without rewriting historical Markdown. To format a changed Markdown file deliberately, run `.\node_modules\.bin\prettier.cmd path/to/changed-file.md --write` with its actual path; prose wrapping is preserved.

For a small feature, use the local formatter executable on the actual owned paths, then run the full non-writing checks. Do not use Prettier's generic HTML parser on Django templates or enable two formatters for the same language in your editor. Editor extensions are optional; the CLI is the team reference. djLint is configured as a Django template formatter; its separate optional linter rules are not a new acceptance gate. Ruff remains the Python linter. No pre-commit hook, automatic Tailwind class sorter, or CI job is installed.

The [coding standards](docs/coding-standards.md#http-endpoint-design) own endpoint/calling/styling/naming rules, and [README](README.md#third-party-packages-and-assets) owns dependency justifications. Formatting does not validate those design rules.

### Tailwind CSS in VS Code

Install the workspace-recommended **Tailwind CSS IntelliSense** extension (`bradlc.vscode-tailwindcss`). The shared [.vscode/settings.json](.vscode/settings.json) associates only `static/css/app.css` with its **Tailwind CSS** language mode; ordinary CSS keeps its normal parser. Open the repository root as your workspace so these settings apply.

If `app.css` shows `{ expected` near `source(none)` or warnings on `@source` / `@theme`, check the bottom-right language mode: it should say **Tailwind CSS**, not **CSS**. After installing/enabling the extension, run **Developer: Reload Window** from the Command Palette and reopen the file. These are valid Tailwind v4 directives; verify compilation with `npm.cmd run build:css`. Keep CSS validation enabled. See the [official editor setup](https://tailwindcss.com/docs/editor-setup) for the supported language mode. CLI formatting remains the team reference above.

## T22 automated system acceptance

**With Neon active, use [the isolated local test command](#isolated-tests-while-using-neon).** The direct test commands below assume an isolated local configuration (`IS_LOCAL_DB_CONNECTION=True`, `MEDIA_STORAGE=local`, and local `DB_*`). Do not run them against the shared connection.

Run the complete automated T22 acceptance checks from the project root:

```powershell
.\.venv\Scripts\python.exe manage.py test --noinput
```

This is the native Django test runner. It runs the complete project suite, including all eleven [SRS minimum acceptance scenarios](docs/SRS.md#minimum-acceptance-scenarios), the integrated T22 HTTP checks, real PostgreSQL races, rollback, access control, return/maintenance/report checks and seed checks. Success ends with `Ran ... tests` and `OK`, with process exit code **0**; failures/errors produce a nonzero exit code. The test count can grow as features are added. T22 results and the exact tested revision belong in the [T22 manual/acceptance section](docs/manual-test-guide.md#module-21--automated-system-acceptance-t22).

Prerequisites: PostgreSQL running; your project virtual environment and dependencies installed; configured private `.env.local`; and built frontend assets (`npm.cmd run build`). The database account needs permission to create/drop the separate `test_<DB_NAME>` database. Run one test command at a time: parallel test processes using that same database can interfere. `--noinput` permits replacing an existing database with that test name, so keep valuable data out of it. Tests build their own fictional fixtures; you do **not** need to run any seed or cleanup command against the populated development database first. Photo fixtures use temporary storage and leave existing uploads intact.

For a quick rerun of only the **three additional T22 integration tests**:

```powershell
.\.venv\Scripts\python.exe manage.py test operations.tests.test_system_acceptance --noinput --verbosity 2
```

These exercise a three-item request through real CSRF-protected HTTP approval/date revision/issue/partial return/damaged final return/repair and matching HTML/CSV results; access denial across all current management routes; foreign-owner isolation; and rejection of administrator POSTs without CSRF. This focused command supplements the full suite; it does not rerun the existing concurrency/rollback scenarios by itself.

To rerun the **eight PostgreSQL concurrency checks** alone:

```powershell
.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_approval_concurrency borrowing.tests.test_release_concurrency borrowing.tests.test_return_concurrency inventory.tests.test_maintenance_integrity.MaintenanceConcurrencyTests --noinput --verbosity 2
```

To save a full run's output privately in PowerShell and preserve failure visibility:

```powershell
New-Item -ItemType Directory -Path output/t22 -Force
.\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2 2>&1 | Tee-Object -FilePath output/t22/acceptance-tests.txt
$t22ExitCode = $LASTEXITCODE
if ($t22ExitCode -ne 0) { throw "T22 acceptance tests failed with exit code $t22ExitCode. See output/t22/acceptance-tests.txt." }
```

The ignored log is overwritten on each run; save dated copies if needed for evidence. Do not treat a started command as a pass: review the final summary and fix failures before recording acceptance. These commands automate database and Django HTTP behavior. They do not run a real browser, conduct the T23 user sessions, benchmark T24 performance or demonstrate backup/restore. Those remain separately recorded work.

## T24 readiness and consumer handoff

**T24 Done and integrated through PR #58 at `478eab3`, source `49d5538`.** [Operational results](docs/operational-verification.md) record the full 1,000-unit/5,000-request/10-session measurements, SQL plans and current Neon database/media recovery. The [dated handoff](handoffs/t24-performance-and-recovery-verification-10-22-2026.md) owns final checks/integration evidence. T23 is Done/integrated on its retained limited acceptance evidence. T25/T29 prerequisite integration gates are satisfied; T25 reference preparation is In progress, with editable conversion/review pending.

### T24 replay prerequisites

Use a dedicated local PostgreSQL **18** server and matching native tools for recovery. This workstation used [official EDB portable 18.6 tools](https://www.enterprisedb.com/download-postgresql-binaries) under ignored `output/t24/tools/pgsql/bin`, a separate cluster at `127.0.0.1:55424`, and no new application packages/global installation. Keep both sets of ordinary `.env.local` credentials intact; the replay launchers explicitly select their target without overwriting that file. Private `.env.t24.local` supplies only `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` for the isolated server; `DB_HOST` must be `127.0.0.1`. This workstation's private profile already exists; teammates supply their own local values.

The retained portable cluster is stopped. To inspect its retained databases on this workstation:

```powershell
& .\output\t24\tools\pgsql\bin\pg_ctl.exe -D .\output\t24\pgdata -l .\output\t24\postgres.log -o "-p 55424 -h 127.0.0.1" -w start
```

A fresh fixture/restore replay requires a fresh isolated local cluster or separately coordinated archival of the old dedicated databases. Scripts refuse rerunning fixtures, overwriting earlier output directories or restoring into populated targets. Do not clear a database to bypass a refusal. The original PostgreSQL service, `campus_equipment` database and `media/` remain separate. Build assets first with `npm.cmd ci`, `npm.cmd run build`.

### T24 performance replay

In a project Python session, the following setup derives an explicit child-process environment from the private local profile and creates only the guarded benchmark database. Use the same setup statements for the launchers below; no secrets are printed or persisted into shared files:

```python
import os
import subprocess
import sys
from pathlib import Path
import psycopg
from config.environment import read_environment_values, required_value

values = read_environment_values(Path(".env.t24.local"), {})
local = {
    key: required_value(values, key) for key in ("DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD")
}
if local["DB_HOST"] != "127.0.0.1":
    raise ValueError("T24 writes require loopback PostgreSQL.")
with psycopg.connect(
    host=local["DB_HOST"],
    port=int(local["DB_PORT"]),
    user=local["DB_USER"],
    password=local["DB_PASSWORD"],
    dbname="postgres",
    sslmode="disable",
    autocommit=True,
) as database:
    database.execute("CREATE DATABASE campus_t24_benchmark TEMPLATE template0")
env = {
    **os.environ,
    **local,
    "IS_LOCAL_DB_CONNECTION": "True",
    "DATABASE_URL": "",
    "MEDIA_STORAGE": "local",
    "DB_NAME": "campus_t24_benchmark",
    "DJANGO_DEBUG": "False",
}
subprocess.run(
    [
        sys.executable,
        "manage.py",
        "shell",
        "-c",
        "from django.db import connection; connection.ensure_connection(); print('Database:', connection.settings_dict['NAME'])",
    ],
    env=env,
    check=True,
)
subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], env=env, check=True)
```

Start the local HTTP server from that prepared session (foreground; use another terminal for the load). It uses the benchmark child environment rather than ordinary Neon configuration:

```python
subprocess.run(
    [sys.executable, "manage.py", "runserver", "127.0.0.1:8024", "--noreload"], env=env, check=True
)
```

In the second project Python session, repeat only the imports, private-profile validation and `env` assignment above, **not database creation or migration**, then run:

```python
subprocess.run(
    [
        sys.executable,
        "manage.py",
        "shell",
        "-c",
        "from pathlib import Path; from scripts.t24_fixture import seed_benchmark; from scripts.t24_load import run_load; run_load(seed_benchmark(), 'http://127.0.0.1:8024', Path('output/t24-replay/measurement'))",
    ],
    env=env,
    check=True,
)
```

For non-interactive use from the project root, wrap each Python block in a PowerShell here-string and pipe it into `.\.venv\Scripts\python.exe -`. The measured run used a temporary server process with a readiness check and guaranteed termination; stop the server after replay.

`latency.json` retains individual timings/statuses and concrete-route p95/targets. `sql-profiles.json` retains query counts and actual EXPLAIN plans for the three slowest captured SELECTs per representative route. The load uses ten distinct real CSRF/password sessions and 260 synchronized request waves. A non-200 response or target miss produces a nonzero result after saving measurements. Login/warm-up/barrier waiting are excluded from individual response times. Keep load traffic separate from backup, regression tests and other benchmark work.

### T24 current database/media recovery replay

For this coordinator-only backup, explicitly select `IS_LOCAL_DB_CONNECTION=False` and `MEDIA_STORAGE=neon` in the private file before starting the command; verify `neondb` as documented above. It takes a **read-only** exported database snapshot and all current referenced photo bytes. Use fresh output paths; coordinate against planned photo replacement/deletion because the two services have no atomic joint snapshot:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from pathlib import Path; from scripts.t24_recovery import backup_neon; backup_neon(Path('output/t24-recovery-replay/backup'), Path('output/t24/tools/pgsql/bin'))"
```

The source must be `neondb`. Native credentials are passed privately through the process environment; an optional direct database URL is used for pg_dump when supplied. Keep the dump, photos and manifest together. Nothing is migrated, seeded or changed on Neon. Matching/newer compatible tools are required; restoring a PostgreSQL 18 dump into the original PostgreSQL 17 service is not this verified procedure.

For restore, reuse the validated private local profile/imports above in a separate project Python session. Create only a **fresh empty local** target, then pass its environment explicitly:

```python
with psycopg.connect(
    host=local["DB_HOST"],
    port=int(local["DB_PORT"]),
    user=local["DB_USER"],
    password=local["DB_PASSWORD"],
    dbname="postgres",
    sslmode="disable",
    autocommit=True,
) as database:
    database.execute("CREATE DATABASE campus_t24_restore TEMPLATE template0")
env = {
    **os.environ,
    **local,
    "IS_LOCAL_DB_CONNECTION": "True",
    "DATABASE_URL": "",
    "MEDIA_STORAGE": "local",
    "DB_NAME": "campus_t24_restore",
    "DJANGO_DEBUG": "False",
}
subprocess.run(
    [
        sys.executable,
        "manage.py",
        "shell",
        "-c",
        "from django.db import connection; connection.ensure_connection(); print('Database:', connection.settings_dict['NAME'])",
    ],
    env=env,
    check=True,
)
subprocess.run(
    [
        sys.executable,
        "manage.py",
        "shell",
        "-c",
        "from pathlib import Path; from scripts.t24_recovery import restore_local; restore_local(Path('output/t24-recovery-replay/backup'), Path('output/t24/tools/pgsql/bin'), Path('output/t24-recovery-replay/restored-media'), Path('output/t24-recovery-replay/result.json'))",
    ],
    env=env,
    check=True,
)
```

The schema-inclusive dump creates `public`, so the helper verifies an empty target and drops only that local empty schema without CASCADE before a single-transaction, fail-fast restore. It verifies complete table hashes **before** login/session updates, restores separate media and checks protected routes. The private `SEED_ACCOUNT_PASSWORD` must match the stored demonstration account password; it verifies real sign-in and never resets passwords. No migrations or seeds follow a full restore. Keep partial failed evidence and diagnose the root cause; do not bypass failures.

Stop the dedicated portable cluster after inspection using the same verified data directory with `pg_ctl -m fast -w stop`; leave the original service running. [Maintenance and limitations](docs/operational-verification.md#maintenance-and-limitations) define the backup scope, sensitive artifacts, retention gaps and unmeasured cases. No restore into shared Neon is authorized by this local runbook.

## T25 readiness and consumer handoff

**Owner: Jerome coordinates; Kenneth/Ellyssa convert diagrams, Margareth supports validation/documentation; everyone reviews. Status: In progress, reference documentation audited locally.** Jerome authorized reconciling the documentation diagrams as the basis for Ellyssa and Kenneth's editable-tool work. The references match implemented main `e2c3f61` (PR #59, preserving documentation source `0e65b8b` exactly). T22/T23/T24 are accepted and integrated; their results and limits are unchanged. This audit and its publication receipt are integrated through PR #60 at `692e89a`, with source ancestry and exact merge-tree equality verified. Jerome reports Ellyssa/Kenneth conversion is ongoing; editable delivery, exports, final traceability and team review remain pending. See the [course requirements audit](handoffs/course-requirements-audit-before-t26-10-22-2026.md). See [publication receipt](handoffs/t25-diagram-reference-publication-10-22-2026.md). See [task evidence](docs/tasks.md#verified-task-evidence).

1. Use the canonical references below and their drawing notes. Read both database views together and both workflow state views; do not copy an earlier handoff's draft. Preserve existing contributor credit.
2. Kenneth and Ellyssa recreate the diagrams in an editable tool such as Lucidchart under Jerome's coordination. Keep role/MTV boundaries, actual field names, crow's-foot ends, actor labels and transaction/derived-state notes. Split large diagrams into linked pages at readable scale. Margareth can review flow/validation coverage. This documentation audit does not claim that conversion or teammate delivery has occurred.
3. Review the editable diagrams against those references and actual source. Add real editable document links and readable exports beside the matching canonical diagram; record the tool, revision/date and reviewers. Do not add placeholder URLs or duplicate design manuals. Keep external documents free of credentials, real borrower records and private backups.

| T25 evidence                       | Canonical source                                                                                                                                                                   | Remaining delivery check                                                                                                                                                                                      |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Requirements to source/tests       | [SRS](docs/SRS.md), [T22 acceptance mapping](docs/manual-test-guide.md#module-21--automated-system-acceptance-t22), [acceptance tests](operations/tests/test_system_acceptance.py) | Final team-reviewed A1-A8/U1-U4 source/test traceability, access/ownership and failure behavior; distinguish old executed checks from new review                                                              |
| MTV                                | [Reference and drawing guide](docs/architecture.md#model-template-view-structure)                                                                                                  | Editable page preserves views orchestrating forms/services/queries, protected reads, templates, ORM/database and separate media storage                                                                       |
| Database                           | [Core/actor ERDs and drawing guide](docs/db_design.md#relationships)                                                                                                               | All 14 domain entities and 23 FK/one-to-one relations; PK/FK/unique/nullability notes; schema cardinalities separate from service minimum counts; source-return maintenance link and LoanUnit bridge retained |
| Workflow                           | [Request and unit/maintenance views](docs/architecture.md#workflow-view)                                                                                                           | Both state pages preserve date revision, exact reservation, cancellation, repeated partial/final returns, damaged-return maintenance, repair/retirement and terminal states; overdue stays derived            |
| Resolved issue/enhancement         | [T23 R01/R02/F02/E01](docs/usability-acceptance.md)                                                                                                                                | Retain real self-report/source attribution, verified startup improvement and Not-run human recheck; no invented campus sample                                                                                 |
| Performance/recovery/limits        | [T24 record](docs/operational-verification.md), [Module 23](docs/manual-test-guide.md#module-23--performance-and-recovery-t24)                                                     | Retain hardware/workload/results, current database/photo recovery and local/cloud/atomicity limits; private artifacts remain excluded                                                                         |
| Dependencies/professional evidence | [Dependencies](docs/third-party-dependencies.md), [coding standards](docs/coding-standards.md), [T26 guide](docs/user-needs-evidence-guide.md), backlog T26-T28                    | Reference real licenses/tooling/decisions and available team/professional evidence; T25 does not invent or finish those separate tasks                                                                        |

T25 is Done only after reviewed diagrams/traceability match implementation, real editable sources/exports are linked, evidence/constraints/limitations are covered and the dated handoff is finalized. Mermaid reference review alone does not complete T25. T29 prerequisites are satisfied but it is not started by this request; T30 retains all original evidence/submission prerequisites.

## T27 readiness and consumer handoff

**Owner: everyone; Alex coordinates security/privacy, with Jerome coordinating delivery. T27 is In progress.** The [canonical professional-judgment record](docs/professional-judgment-and-ethics.md) now consolidates the current source register, stakeholders/duties, personal-data lifecycle, risk decisions, intellectual-property boundaries, accessibility/bias/public-welfare findings, and AI/reuse disclosure. Coursework disclosure/member review and conditional approval before real-data use are separate; there is no T26-main-integration prerequisite. The record is evidence and an interim safety boundary; it is not BulSU/DPO/instructor approval or permission to use real data.

Read the [Part 6 requirement](docs/Project-Requirements.txt), [T27 acceptance](docs/tasks.md#course-evidence-and-delivery), [contribution/licensing rules](CONTRIBUTING.md), the [canonical T27 record](docs/professional-judgment-and-ethics.md), and the existing evidence before changing the decisions. Ralph's integrated [technical contribution](handoffs/ralph-t17-per-unit-returns-and-overdue-10-20-2026.md#ralphs-t27-technical-contribution) remains separately attributed and linked rather than copied.

| T27 input / remaining work | Current source and next action |
| --- | --- |
| Applicable codes/laws/campus and AI rules | Existing sources and applicability limits are recorded. Jerome reports no separate disclosure format/instruction beyond the supplied course brief; the disclosure now explains actual assistance. University AI policy text remains unverified: clarify it at final review and incorporate actual instructions obtained without inventing approval. |
| Stakeholders, duties and accountability | Stakeholders, harms, duties and project owners are mapped. Institutional process/DPO/records ownership remains a conditional real-data adoption action, rather than an approval required to document the fictional prototype. |
| Privacy, access, retention and safe data use | Actual fields, safeguards and retention gaps are documented. Keep operational data fictional. Institutional lawful-basis/notice/PIA/access/hosting/retention/incident decisions remain unresolved before real-data use; they are not claimed as completed coursework approvals. |
| Intellectual property and asset provenance | Jerome confirmed Gemini origin for the logo, default avatars/equipment image and equipment images on October 23; the asset inventory records that evidence and its limits. Retain font/Chart.js notices and check final T30 package content; internet downloads require their actual source/permitted-use record, never a false AI label. |
| Accessibility, bias, conflicts and public welfare | Ralph's recorded responsive, keyboard/focus/error and contrast results are consolidated with untested screen-reader/zoom/user limits in the canonical record. This satisfies the evidence/disposition scope without claiming full WCAG conformance; further adoption checks remain recommendations. |
| AI/reuse disclosure and service controls | Codex/Kiro source evidence, the three supplied GitHub screenshots and reported Gemini image generation are explained in the existing T27 document. Screenshots support attribution, not instructor permission or account/service control guarantees. |
| Defensible final decisions | Final member review remains pending. Jerome reports a meeting on October 23, 8:00 PM onwards Asia/Manila; the canonical record has an agenda and pending fields, with no invented attendance, feedback or approvals. |

T25 diagrams and other delivery tasks continue separately. T27 is complete only when the [completion gate](docs/professional-judgment-and-ethics.md#completion-gate-and-member-review) has actual evidence and team review. Follow the [project handoff convention](.agents/skills/project-handoff/SKILL.md); this record does not authorize an application change, external message, policy certification, or data operation.

## Before handing over work

Run the configured checks and any meaningful tests for your feature. The direct test command below assumes an isolated local configuration; with Neon active, substitute [the local child-process command](#isolated-tests-while-using-neon). Shared migrations are coordinator-owned.

```powershell
npm.cmd run format:check
.\.venv\Scripts\djlint.exe templates --check
npm.cmd run build
npm.cmd audit
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --noinput
.\.venv\Scripts\python.exe manage.py migrate --check
.\.venv\Scripts\python.exe manage.py test --noinput
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\python.exe -m pip check
git --no-pager diff --check
```

Tests create and remove a separate `test_<DB_NAME>` PostgreSQL database. Your local account needs permission to create test databases; keep personal data out of them. The T14 module below verifies competing approvals; the foundation suite alone does not establish that result or acceptance for unimplemented workflows. To format edited Python files, run `.\.venv\Scripts\ruff.exe format .`.

For each new feature or changed documented flow, update the relevant [manual testing section](docs/manual-test-guide.md) using the [manual-guide requirements](docs/coding-standards.md#manual-testing-guide-for-feature-delivery). Then write the required [dated handoff](.agents/skills/project-handoff/SKILL.md), link that section, update affected task evidence/current readiness, and leave AI changes uncommitted unless the user requests a commit.

## Continuing with T08

**T08 is Done and integrated** through PR #22 at `6c91d48`. Physical-unit management is available under `/manage/units/`. **T16 including its integrity/conflict corrections is integrated** through PR #33 at `aa36c86`, preserving `d68d7f7` and Kenneth's PR #31 baseline. Follow [the member-branch workflow](#assigned-branches-and-main-integration) before continuing. Prepare or refresh the workstation with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm.cmd ci
npm.cmd run build
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py test --noinput
```

The T07 continuation adds `inventory.0002_category_name_case_insensitive`, `inventory.0003_catalog_item_photo`, and `operations.0003_catalog_restore_audit_actions`. T08-T13 and T16 add no migration or dependency. Do not rewrite existing migrations. Use the existing catalog forms, distinct services, read-only queries, active-admin boundary and documented lock order; see the [HTTP contract](docs/api_spec.md#custom-administration-accounts-and-inventory), [coding standards](docs/coding-standards.md) and [T16 review](handoffs/t16-main-integration-and-documentation-review-10-19-2026.md). `/manage/maintenance/` now implements list/detail/open/close. Registering an initially damaged unit opens maintenance atomically; T16 adds repair/retirement closure. The manual opener accepts no return identifier; integrated T17 creates damaged-return maintenance in its complete atomic return workflow. T15 is integrated through PR #42 with accepted T13/T14 integrated; the T16 corrections are integrated. Integration does not supply the full demonstration dataset.

### Borrower account verification after T09 integration

Anonymous users can register at `/accounts/register/`, then sign in through the shared login page. Registration fixes the role to BASIC_USER; an active borrower edits only their own name, email and optional contact number at `/portal/profile/`. The administrator profile remains read-only. Registration/profile changes use transactional audit services; see the [HTTP contract](docs/api_spec.md#shared-account-routes) for fields and access rules.

Run `.\.venv\Scripts\python.exe manage.py test accounts.tests.test_borrower_portal operations.tests.test_navigation --noinput` for the focused integration suites. The T10 integration review passed 174 tests; the combined source integrated through PR #27 passed 181 tests. The [username-validation follow-up](handoffs/registration-username-validation-and-t09-status-10-18-2026.md) uses Django normalization and the model validator to return bound field errors before writes; it is integrated through PR #24 at `f29bd91`. T09 remains Done.

### Borrower equipment verification after T10 integration

Active BASIC_USER accounts browse `/portal/equipment/` with name/description search, active-category filtering and 10-item pagination. Detail pages show descriptions, protected photos or the shared default, and database-derived serviceable/available counts. Archived items and items under archived categories are excluded from browsing, detail and photo access. Admins and inactive accounts are denied; internal unit notes and asset codes stay outside these catalog pages. See the [portal contract](docs/api_spec.md#basic-user-portal).

Run `.\.venv\Scripts\python.exe manage.py test inventory.tests.test_portal_equipment --noinput` for the 25 T10 integration tests. The [integration review](handoffs/t10-main-integration-and-documentation-review-10-18-2026.md) records earlier checks and the open test-photo-storage follow-up. Integrated T11 now supplies submission and a create link from the request section, resolving the earlier premature-request-guidance gap; T12 adds integrated history/cancellation. The user subsequently reported successful manual T10 testing; detailed mobile/keyboard scenarios were not supplied. See [publication evidence](handoffs/t10-documentation-publication-10-18-2026.md).

### Borrower request submission (T11)

An active BASIC_USER can submit `/portal/requests/new/` with a purpose, desired return date and one to three distinct active catalog items. The service locks/rechecks the borrower, current settings and eligible catalog records, snapshots both limits and writes the Pending request/items atomically without allocating units. `/portal/requests/` displays submission confirmation, a create link and the integrated T12 owner-scoped history.

Run `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_request_submission --noinput` for focused checks. See the [Ralph implementation snapshot](handoffs/ralph-t11-request-submission-10-18-2026.md), [resolution review](handoffs/pr27-t11-conflict-resolution-review-10-18-2026.md) and [main integration receipt](handoffs/pr27-t11-main-integration-10-18-2026.md) for actual verification/integration evidence. No new migration or dependency is required by T11. After pulling, run the existing asset build to include the request templates. T12 history/cancellation is integrated through PR #29; PR #34 supplies administrative approval; the subsequent T13 query fixes are integrated through PR #35 at `cf50d0c`.

### Borrower request and loan tracking (T12)

The request list at `/portal/requests/` shows only the signed-in borrower's requests, with status filtering and 6-row pagination. Request details show requested items, decision, due dates and any issued/returned units. `/portal/loans/` and `/portal/loans/<id>/` show only that borrower's loans, due dates, asset codes and individual return progress. Pending and Approved requests can be cancelled through a GET confirmation followed by a CSRF-protected POST; approved reservations are released in the same audited transaction. Foreign IDs return 404; ineligible or changed request states return 409 without partial writes.

Run `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_request_submission borrowing.tests.test_request_tracking --noinput` for focused checks. PR #29 integrates source `eb04470` at main `170cc38`; the [integration review](handoffs/t12-main-integration-and-documentation-review-10-19-2026.md) records 191 passing PostgreSQL tests on that tree. No migration or dependency was added. Rebuild assets after pulling. [Module 10 of the manual test guide](docs/manual-test-guide.md#module-10--borrower-request-and-loan-tracking-t12) provides current Pending-request cases and read-only audit verification. Approved cancellation can now be prepared through T13; PR #35 integrates detail queries that hide ended reservations while preserving allocation history; T15 is integrated through PR #42; T17's isolated borrower returned-unit checks are recorded in Module 16; its source is integrated through PR #43. An empty loan history is expected until loans exist; manual results remain pending.

### Administrator request review and decisions (T13)

PR #34 integrates Margareth's `marga` head `c5cfe37` at main `23c1ad9`. Active ADMIN users can search `/manage/requests/` by request ID or borrower username, filter status and inclusive submission dates, and traverse 25-row pages. Request detail shows purpose, quantities, dates, availability and decision history. Approval/rejection confirmation GETs do not write; POST requires a reason (maximum 500 characters), derives the actor from the session, and calls the atomic workflow service. Approval reserves exact unit quantities or returns 409 with no partial allocation.

Run `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_requests --noinput` for the 28 T13 tests. Both query regressions failed on the baseline and pass with the corrections integrated through PR #35 at `cf50d0c`; the current full-suite result is in the T14 section below. The query uses decimal-only ID recognition while retaining Unicode username search, and lists only allocations that have neither ended nor been released under Reserved units. See [fix evidence](handoffs/t13-query-fixes-and-publication-10-19-2026.md) and [Module 12](docs/manual-test-guide.md#module-12--administrator-request-review-and-decisions-t13). Rebuild assets after pulling; no migration or dependency was added. Main includes both query corrections in `1d7a3c7`. Smaller defaults/typing/helper standards items remain non-blocking follow-ups. T14 is integrated through PR #37; T15 is integrated through PR #42 at `744bc39`.

### PostgreSQL competing approvals (T14)

Run `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_approval_concurrency --noinput --verbosity 2`. Two `TransactionTestCase` scenarios use committed fictional fixtures, distinct borrowers/admins and separate PostgreSQL connections to call the real `approve_request` service. The tests observe the lock-wait chain before releasing a held category lock, require exactly one approval and one `WorkflowConflict`, and verify allocation, decision, inventory and audit state. The multi-item case also verifies the loser's uncontested unit stays Available. Unexpected database errors fail the test; they do not count as the expected conflict. Existing T13 HTTP tests cover the service conflict's 409 response.

Verification on October 20, 2026: the implementation run passed **2 focused tests in 0.894s**; the fresh publication run passed **254 full-suite tests in 39.994s** on PostgreSQL 17.5. No application service, schema, dependency or live data changed. T14 source `058357c` is Done and integrated through PR #37 at `5381c83975753426208ffde6370c4e8da09fe5d9`; ancestry and exact tested-tree equality are verified. See [Module 13](docs/manual-test-guide.md#module-13--postgresql-competing-approvals-t14) for fixture values and reproduction, and the [integration receipt](handoffs/t14-publication-main-integration-and-t15-readiness-10-20-2026.md) for publication evidence. This proves the tested approval races; cancellation/issue concurrency remains outside T14.

### Release and borrowing slip (T15)

T15 source `74924dd` is integrated through PR #42 at `744bc3995f310fe365d7e00d8b187d765df326a8`; fetched ancestry and the merge/published-tree equality were verified in Ralph's T17 session. `borrowing/release_services.py` exposes `revise_due_date(actor_id, request_id, agreed_due_date, reason)` and `release_request(actor_id, request_id)`; `borrowing/reservations.py` shares complete reservation locking with cancellation. Release preserves active allocation exclusivity until return; date revision preserves the original desired date and submission limits. Rebuild assets to supply `build/borrowing-slip.js`. No migration or dependency was added. Run `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_release borrowing.tests.test_release_concurrency --noinput`; [Module 15](docs/manual-test-guide.md#module-15--release-due-date-revision-and-borrowing-slip-t15) retains exact dated examples and actual checks. Both T17 prerequisites are now integrated.

### T17 readiness and consumer handoff

Ralph owns T17 on `ralph`. Source `bd62ed7b93db965ed5b4442af84e8186ccf45065` is integrated through PR #43 at main `55899d0f18e5f0ec76dc3374db1765f32b49893e`. Fetched ancestry verifies T15 source `74924dd` and T16 corrections `d68d7f7`; the T17 source and merge trees match exactly. T16's existing maintenance services and Kenneth's implementation credit are preserved. [Task evidence](docs/tasks.md#verified-task-evidence) and [the current handoff](HANDOFF.md) record the merged-source review and next consumer.

T17 exposes `borrowing.return_services.return_units(actor_id, loan_id, rows)` with immutable `ReturnInput(loan_unit_id, returned_condition, notes, maintenance_problem)` values. `borrowing/return_forms.py` validates the `returns` formset and `return_views.py` handles `borrowing_manage:return-create`. GOOD/FAIR ends the allocation and makes its unit Available; DAMAGED creates matching open maintenance in the same return transaction. The loan closes only after the final outstanding unit returns. `borrowing.queries.with_loan_progress(loans, today)` derives issued/returned/outstanding counts, active/overdue flags and calendar overdue days for management and borrower pages; it performs no writes. Alex / T18 is integrated through PR #45; T19 has accepted, integrated T17/T18 prerequisites. T19 is now accepted and integrated through PR #49; see [T20 consumer guidance](#t20-readiness-and-consumer-handoff).

| Existing interface | T17 boundary |
| --- | --- |
| `borrowing.release_services.release_request(actor_id, request_id)` | Creates one Loan and LoanUnits with active, released allocations; use this stored issue state as the starting point for returns |
| `operations.locking.lock_request(owner_id, request_id)` and `lock_units(unit_ids)` | Reuse the [canonical transaction/lock order](docs/architecture.md#transaction-boundaries-and-lock-order); derive the actor from the signed-in ADMIN and recheck authoritative membership/state |
| `borrowing.reservations.lock_reserved_units(request_id)` | Pre-release cancellation/issue helper only: it requires Reserved units and rejects released allocations; it is not a return helper |
| `inventory.services.open_maintenance(actor_id, unit_id, problem)` | Manual Available-unit opener only; accepts no return identifier. T17 creates damaged-return maintenance inside its complete atomic return transaction |
| Existing LoanUnit, ReturnRecord and MaintenanceRecord models/constraints | Follow [the database contract](docs/db_design.md#issue-and-return), including unique per-unit return and matching damaged-return linkage; the T17 return service now implements these transitions |
| `borrowing_manage:return-create` | Mounted GET/POST `/manage/loans/<loan_id>/returns/new/`; active ADMIN only. See the [return formset/HTTP contract](docs/api_spec.md#custom-administration-requests-loans-and-maintenance) |

Run `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_returns borrowing.tests.test_return_concurrency --noinput` for 21 focused tests, including separate-connection duplicate/disjoint-return races and real return/maintenance audit-constraint rollback. The full 294-test PostgreSQL suite passes. [Module 16](docs/manual-test-guide.md#module-16--per-unit-returns-and-overdue-t17) records inputs, read-only live-data availability and actual browser results. No migration, dependency or live business-data write was needed. Historical manual/browser follow-ups and the diagram standby gate remain open.

`.idea/` is ignored and removed from tracked files through main commit `f08fb04`. Each developer may keep local IDE settings; do not force-add them. Generated builds, uploads, dependencies and private environment files also stay outside Git.

### T18 readiness and consumer handoff

**Alex / T18 is Done and integrated through PR #45 at `26b1ee555ae5b98e9d744bd7a11b3bfb74153b60`, source `54380fd912b6cb684c11a8c2e79fa4cac00f856a`.** At that integration review, local `jerome` HEAD equalled fetched `origin/main`; source ancestry and exact source/merge tree equality were verified. The implementation replaces the protected `/manage/` placeholder with four live cards, a monthly issued-loan chart and a category issued-unit chart. It preserves the active-ADMIN boundary and shared role shell. The integrated baseline changed no schema or repository dependency. UI-11/UI-12 are integrated through PR #48 at `9d67fab`; UI-11 bundles Chart.js 4.5.1; Django still safely embeds the real query data with `json_script`. Rebuild assets after pulling to generate `build/dashboard-charts.js`.

`operations.queries.dashboard_snapshot(today)` owns the read-only calculations. It reuses `borrowing.queries.with_loan_progress` for active/overdue totals, counts each `Loan` once by issue month and separately counts every issued `LoanUnit` by category, including returned units. The view passes `timezone.localdate()` explicitly and only prepares JSON-safe presentation data. See [SRS A7/A7-CHART](docs/SRS.md#functional-requirements), [BR-11/BR-12](docs/SRS.md#business-rules-and-calculations), the [HTTP contract](docs/api_spec.md#custom-administration-reports-audit-settings) and [Module 17](docs/manual-test-guide.md#module-17--live-administration-dashboard-t18).

**Earlier T18 baseline review:** 298 PostgreSQL tests passed in 56.385s, with no blocking runtime defect; the [review receipt](handoffs/t18-main-integration-review-and-t19-readiness-10-20-2026.md) retains the actual checks and dated data snapshot. UI-11/UI-12 subsequently integrated through PR #48 at `9d67fab`; Alex's T19 integrated through PR #49 at `e8f2a19`. The combined application passed 315 PostgreSQL tests in 57.317s during the [T19 review](handoffs/t19-main-review-and-local-merge-conflict-resolution-10-21-2026.md). Ralph / T20 is now integrated through PR #51; current consumer guidance follows below.

UI-11 uses monthly columns from the first release through the current month (including zero-issue months), plus category bars ordered by usage with alphabetical ties. No data window or reporting endpoint is added. Card links reuse the Available/Pending filters and existing loan list; that list has no active/overdue filter. The chart module registers only the bar components/scales and tooltip, reads existing CSS color roles/fonts, and keeps exact tables usable without JavaScript. `npm.cmd ci` and the normal build include Chart.js locally without a CDN. Retain `static/licenses/chartjs-MIT.txt` with collected/submission assets. See the [Chart.js handoff](handoffs/admin-dashboard-chartjs-improvement-10-20-2026.md) and updated [Module 17](docs/manual-test-guide.md#module-17--live-administration-dashboard-t18).

UI-12 adds `operations.context_processors.nav_badges` to the template context and reuses `operations.queries.pending_request_count()` for the administrator navigation badge. The [canonical navigation styling contract](docs/coding-standards.md#shared-m3-roles-and-components-ui-09) and [manual cases](docs/manual-test-guide.md#t18-05---workspace-shortcuts-pending-badge-and-filters-ui-12) cover its display/access rules. Dashboard shortcuts use `ui-tool-link` rows; request filters retain the existing field/action layout with Clear before Search. The combined UI-11/UI-12 delivery passes 301 PostgreSQL tests and is integrated through user-merged PR #48 at `9d67fab`, preserving source `f3d42ba` and publication receipt `5fb8236`. See [publication review](handoffs/dashboard-and-workspace-publication-review-10-20-2026.md).

### T20 readiness and consumer handoff

**Ralph / T20 is Done and integrated through PR #51 at `6f18116da83859aa6b4e2d2c982104cfae4e62b6`, source `b43fb999ee571bbb90a1d5be32245c2d7f638b1c`.** Local `jerome` equals fetched main, and the source/merge trees match exactly. Its implementation baseline `f8b1c5b` contains all five prerequisite merges below. [The backlog](docs/tasks.md#administrator-operations) owns acceptance and status; [HANDOFF.md](HANDOFF.md) owns current readiness.

| Prerequisite | Verified main integration | Existing input for T20 |
| --- | --- | --- |
| T10 | PR #25, `016a78b` | Borrower equipment list/detail and protected photos |
| T12 | PR #29, `170cc38` | Owner-scoped request/loan history, detail and cancellation |
| T17 | PR #43, `55899d0` | Partial/damaged/final returns and derived overdue state |
| T18 | PR #45, `26b1ee5`; UI-11/UI-12 through PR #48, `9d67fab` | Live dashboard, two Chart.js charts, shared navigation badge and workspace styling |
| T19 | PR #49, `e8f2a19`, source `16e1d4c` | Loan/overdue report pages and matching spreadsheet-safe CSV exports |

Use the [member-branch workflow](#assigned-branches-and-main-integration), preserving local work. Load the [Django MTV skill](.agents/skills/django-mtv/SKILL.md), [Campus UI skill](.agents/skills/campus-ui/SKILL.md) and [coding standards](docs/coding-standards.md). T20 retains the management/portal bases and `templates/components/workspace.html`, direct profile link, POST/CSRF logout, existing widgets and `ui-*` components. `accounts.views.portal_home` now renders `accounts/portal/home.html`; `borrowing.queries.borrower_workspace(owner_id, today)` supplies its immutable owner-scoped counts and bounded previews using the existing return-aware loan calculation. The view supplies the current campus date explicitly. The [HTTP contract](docs/api_spec.md#basic-user-portal) defines card/preview ordering and behavior.

Shared `components/form_field.html`, `request_status.html`, `loan_status.html`, `pagination.html` and `empty_state.html` serve the affected portal/management pages. The older `operations/manage/form_field.html` delegates to the shared field renderer for existing callers. Request and loan statuses stay distinct: a Closed loan has no outstanding units, while its request is Returned. `components/messages.html` exposes error messages as alerts and other messages as status regions. Pagination keeps submitted filters through Django's `querystring` tag. Rebuild assets after pulling templates or shared CSS; no new migration or dependency is required.

Preserve the active-role/ownership helpers in [accounts/access.py](accounts/access.py), workflow entry points in [borrowing services](borrowing/services.py), [release services](borrowing/release_services.py) and [return services](borrowing/return_services.py), and existing named routes in the [HTTP contract](docs/api_spec.md). T19 presentation is in [workspace_views.py](operations/workspace_views.py) and [report.html](templates/operations/manage/report.html); `loan_report_rows`, `overdue_report_rows` and `report_totals` in [queries.py](operations/queries.py) own its read-only calculations. Keep both report pages and both exports active-ADMIN/GET-only, with inclusive issue-date filters and matching all-row CSV totals. Reports use `report_navigation_active` to keep their shared parent active. The [folder guide](docs/project-folder-architecture.md#where-views-and-page-html-go) maps the other implemented pages.

The historical [T19 review](handoffs/t19-main-review-and-local-merge-conflict-resolution-10-21-2026.md) passed 315 PostgreSQL tests. Fresh merged-source review passes **322 PostgreSQL tests in 127.102s**, including seven workspace integration checks, with no blocking runtime defect. See the [integration review](handoffs/t20-main-integration-review-and-documentation-10-21-2026.md). Ralph's earlier implementation run passed 322 tests in 87.253s. His isolated Edge/Chromium browser run covers 17 portal/management routes at 1440/1024/768/390/320px, keyboard navigation, invalid/valid requests, approval/release back-out, partial/final damaged returns, cancellation, access errors, both CSV downloads, native logout and JavaScript-disabled empty-state navigation. See [Module 19](docs/manual-test-guide.md#module-19--integrated-role-workspaces-t20) for procedures and limitations. This review did not rerun browsers. That review recorded three formatting findings; T22 resolves the owned photo test's line endings, leaving the template and archived handoff findings. Spreadsheet-opening and screen-reader checks remain pending. T21 is integrated through PR #53 at `b828945` with the historical transactions; see [seed setup](#seed-the-t21-demonstration-dataset). T22 automated acceptance is Done locally; T23 is Done on its retained limited acceptance evidence; T25's prerequisite integration gate is satisfied; its reference audit is In progress, with editable conversion/review pending.

## Equipment photos and local media

The **New equipment item** form uses metadata on the left and an optional image/preview panel on the right at desktop widths; leaving the photo empty uses the default image. Selecting a file previews it locally without an upload. **Remove selected image** clears that pending selection, allowing another file to be chosen. The existing photo is changed only when a form is saved; confirmed removal of a saved photo remains a separate action. Creation with a photo saves the item, file reference and audit together, rolling everything back if the operation fails. For an existing item, open its detail page and choose **Manage photo**. Upload one JPEG, PNG or WebP, up to 5 MiB and 20 million pixels. The server rejects animated/invalid files, removes metadata, and saves a WebP fitting within 1600×1600 without cropping. Replace and confirmed removal are audited administrator actions.

With `MEDIA_STORAGE=local` (the template default), uploads are created in `media/equipment/` under Django's `MEDIA_ROOT`. With `MEDIA_STORAGE=neon`, they use the private shared `assets` bucket; see [setup and import](#shared-neon-database-and-photos). PostgreSQL stores a relative path such as `equipment/<generated-id>.webp`; it does not store image bytes. The default `static/images/default-photo-equipment-270x360.webp` is a shared static asset and is used when no photo is assigned. A missing assigned upload is an error, rather than a silently replaced photo.

`media/` is ignored by Git. Isolated developers have separate local uploads; Neon-configured members share stored photos. Pulling source does not copy equipment photos. Back up the selected storage backend together with the database, preserving relative paths; local `media/` backups do not include new Neon uploads. Review any files left unreferenced after an interrupted process before removing them; there is no automatic purge command.

Photos are delivered through the active-ADMIN-protected `inventory_manage:item-photo` route and the active-BASIC_USER-protected `portal:equipment-photo` route. The portal route additionally requires an active item and category. Both stream stored WebP with private/no-store caching. Do not use `item.photo.url` in templates or add a public `static(settings.MEDIA_URL, ...)` mapping: the media directory intentionally has no direct HTTP route. Protected delivery also works with `DEBUG=False`.

To obtain the image dependency and schema after syncing this change:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe manage.py migrate
```

Restart Django after applying the migration. The bundled Pillow wheel includes its license and native-library notices; keep them if redistributing the installed runtime.

## Fonts and static assets

The root `static/` directory contains shared source files. [Django's static-files finder](https://docs.djangoproject.com/en/5.2/howto/static-files/) searches it through `STATICFILES_DIRS` in [config/settings.py](config/settings.py). `STATIC_URL` defines the browser prefix `/static/`, so `static/fonts/...` is served at `/static/fonts/...`. Keep `STATIC_ROOT` (`staticfiles/`) separate for generated collection output.

[static/css/fonts.css](static/css/fonts.css) defines the local DM Sans variable fonts and all Poppins weights/styles. [app.css](static/css/app.css) imports it into Tailwind's base layer alongside the fixed color roles, and [base.html](templates/base.html) loads the compiled stylesheet once:

```django
{% load assets %}
<link rel="stylesheet" href="{% compiled_asset 'build/app.css' %}">
```

Keep the existing font files and their `OFL.txt` notices. Use CSS-relative URLs inside the stylesheet, `{% compiled_asset %}` for built CSS/JS and Django's `{% static %}` tag for other template assets. No fonts are downloaded from a CDN. The DM Sans variable pair covers weights 100–1000, so the included DM Sans static variants need no additional declarations.

For discovery checks:

```powershell
.\.venv\Scripts\python.exe manage.py findstatic build/app.css build/frontend-test.js fonts/Poppins/Poppins-Regular.ttf --verbosity 2
```

Runserver serves static files during local debugging. `STATIC_ROOT` (`staticfiles/`) is generated collection output, not where source assets belong. `collectstatic` is not needed for the local setup above.

## Assigned branches and main integration

Assignments come from [Project-Members.txt](docs/Project-Members.txt). Keep permanent member branches after PR merges.

| Member    | GitHub        | Branch    |
| --------- | ------------- | --------- |
| Jerome    | `javecilla`   | `jerome`  |
| Alex      | `AlexCayanan` | `alex`    |
| Kenneth   | `corkenneth`  | `kenneth` |
| Ellyssa   | `ellieebeann` | `elly`    |
| Margareth | `raifun`      | `marga`   |
| Ralph     | `dreygigz`    | `ralph`   |

Work and push on your own branch. Only Jerome integrates `main`; do not push another member's branch, force-push, or rewrite shared history. The [main-owner-only ruleset](https://github.com/javecilla/Campus-Equipment-Borrowing-System/rules/25213591) controls main updates; branch assignments are a team convention, not exclusive authorship.

The ruleset's **Restrict updates** rule allows only its bypass actor, `@javecilla`, to update main. GitHub therefore shows **Merging is blocked / Cannot update this protected ref** even on Jerome's PRs. For a reviewed, ready PR, Jerome selects **Merge without waiting for requirements to be met (bypass rules)** and merges it. Other members submit PRs for Jerome to integrate. This banner is expected for the owner-only rule; it does not identify a failed test. See [GitHub's Restrict updates documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets#restrict-updates).

### First checkout of your member branch

From a fresh clone, choose your branch; this example uses Alex:

```powershell
$memberBranch = 'alex'
git fetch origin --prune
git switch --create $memberBranch --track "origin/$memberBranch"
```

If the branch already exists locally, use `git switch $memberBranch` instead. If the remote branch is missing, ask Jerome to verify setup. Preserve local changes before switching.

### Bring main into your work before starting

With a clean working tree, set `$memberBranch` to your assignment, then run:

```powershell
git status --short
git fetch origin --prune
git switch $memberBranch
git merge --ff-only "origin/$memberBranch"
git merge --no-edit origin/main
```

This brings fetched main into your member branch without updating remote main. If a fast-forward fails, inspect the divergence. Resolve conflicts with affected owners and preserve their work. Follow [PLAN.md](PLAN.md)'s gates before starting dependent tasks. The local-batch exception applies only to T01–T03.

### Commit, push your branch, and open a PR

After checks and handoff, review/stage the intended paths only. For an AI agent, commit/push/PR actions still require the user's explicit instruction.

```powershell
git status --short
git --no-pager diff
git add -- path/to/changed-file path/to/dated-handoff.md
git --no-pager diff --cached
git diff --cached --check
git commit -m "feat: implement the assigned task"
git push --set-upstream origin $memberBranch
```

On GitHub, open a PR with **base: main**, **compare: your branch**, the task, actual checks, and handoff link. Keep unrelated unfinished tasks out of the PR. After integration, keep the member branch and sync main before the next task.

### Resolve merge conflicts without losing another member's work

Use `git status` and `git diff --name-only --diff-filter=U` to locate conflicts. Read both changes, coordinate with affected owners, and edit the correct combined result. Stage resolved paths, run checks, and finish the existing merge with `git commit --no-edit` when authorized. Use `git merge --abort` to cancel the merge. Never blindly choose one side or use a hard reset to hide conflicts.

### Jerome's integration responsibility

Jerome reviews scope, contracts, checks, and handoff before using **Create a merge commit**. Preserve contributor credit and permanent member branches. [CODEOWNERS](CODEOWNERS) routes reviews to `@javecilla`; GitHub cannot accept an author's approval of their own PR. [CONTRIBUTING.md](CONTRIBUTING.md#verification-and-review) explains review restrictions and attribution. Local Django/Ruff checks exist; no repository test CI workflow is configured (the platform Copilot cloud-agent entry is separate).

## Updating dependencies

Change runtime ranges in [requirements.in](requirements.in), or development tooling in [requirements-dev.in](requirements-dev.in). With uv already installed, regenerate both locks:

```powershell
uv pip compile requirements.in --output-file requirements.txt
uv pip compile requirements-dev.in --output-file requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Run checks before sharing updated locks. Ordinary setup installs the pins without re-resolving them. Psycopg binary avoids a C build; python-dotenv parses configuration; tzdata supplies Windows time-zone data; Ruff is development-only.

JavaScript dependencies belong in package.json/package-lock.json. Use `npm.cmd install --save-exact package@version` for a runtime dependency, adding `--save-dev` for build tools; use real reviewed package/version values. Reinstall with `npm.cmd ci`, then format/check, build, and audit before sharing the lockfile. Tailwind CLI 4.3.0 currently permits the locked watcher 2.6.0, avoiding the [vulnerable braces chain](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) pinned by CLI 4.3.3. Recheck that dependency path during updates; do not run a forced audit fix without reviewing the actual change. Update [README purposes/tradeoffs](README.md#third-party-packages-and-assets) and the [full inventory](docs/third-party-dependencies.md) from lockfile/distribution metadata, including indirect/optional packages and their parent/license declarations. UI-11 bundles Chart.js/color in the dashboard module. Keep their full MIT notices in `static/licenses/chartjs-MIT.txt` with collected/submission assets. If npm prunes existing bundled optional dependency records, inspect the lock diff and preserve the original valid records; a plain `npm.cmd ci` must pass before handoff.

## Configure your MCP client

MCP is optional AI database inspection, separate from running Django. Node.js 24 LTS/npm are needed for pinned DBHub 1.5.0 (Node >=22.5); use [Node's installer](https://nodejs.org/en/download) for this tooling. The connection remains read-only.

<details>
<summary>Expand optional MCP connection and client setup</summary>

Set `MCP_DATABASE_URL` privately in `.env.local` using this shape:

```text
postgresql://YOUR_USER:YOUR_URL_ENCODED_PASSWORD@127.0.0.1:5432/campus_equipment?sslmode=disable
```

Include the database name and percent-encode special characters in URI credentials; `DB_PASSWORD` stays raw. This URI may use a separate inspection account. `sslmode=disable` is for the local loopback connection. Node explicitly loads `.env.local` through `--env-file`, with existing process values taking precedence. The file is not automatically loaded into your terminal or pgAdmin.

### Shared JSON template

[.agents/mcp.json](.agents/mcp.json) contains the `mcpServers` entry named `campus_equipment`. It is a shared template; `.agents/mcp.json` is not a universal auto-discovery location. Import/copy the entry into your client's supported local configuration, preserving other existing servers. Some clients use a different top-level key or do not support `cwd`; follow that client's schema rather than renaming fields by guesswork.

In your **local client copy**, change these machine-specific values:

| Value               | Required adjustment                                                                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cwd`               | Replace `REPLACE_WITH_ABSOLUTE_PROJECT_PATH` with your project's absolute root, such as `C:/School/PythonProject`; this makes `.env.local` and `.agents/dbhub.toml` resolve correctly |
| `command`           | `node` must resolve in the AI client's PATH; use the absolute `node.exe` path if necessary                                                                                            |
| Second `args` entry | Default Windows npm entry point is `C:/Program Files/nodejs/node_modules/npm/bin/npx-cli.js`; replace it if Node/npm is installed elsewhere                                           |

Keep `--env-file=.env.local` before the npm entry point. Keep the pinned package version, stdio transport, and `.agents/dbhub.toml` path. Do not add passwords to `args`, `env`, or the shared JSON. For a client without a working-directory option, replace the env-file and DBHub config paths with absolute paths in its private configuration.

For the standard Windows installer, verify/locate the npm entry point:

```powershell
$npxEntryPath = Join-Path (Split-Path (Get-Command npx.cmd).Source) 'node_modules/npm/bin/npx-cli.js'
Test-Path -LiteralPath $npxEntryPath
$npxEntryPath
```

The check must return True. A custom installation may put npm elsewhere; locate its actual `npm/bin/npx-cli.js` and update the local client copy. On macOS/Linux use your platform's Node executable and npm entry-point path. Those platforms have not been tested in this workspace.

The JSON intentionally has no client-specific `disabled` flag. Enable the server in your client's UI/configuration using that client's supported settings.

### Codex

Codex reads TOML, so it does not load the JSON template directly. In Settings → MCP servers, register a local stdio server using the same command/arguments, or add this table to your private `~/.codex/config.toml`. Replace the project path and any nonstandard Node/npm paths, and preserve unrelated settings:

```toml
[mcp_servers.campus_equipment]
command = "node"
args = [
  "--env-file=.env.local",
  "C:/Program Files/nodejs/node_modules/npm/bin/npx-cli.js",
  "--yes",
  "@bytebase/dbhub@1.5.0",
  "--transport",
  "stdio",
  "--config",
  ".agents/dbhub.toml",
]
cwd = "C:/School/PythonProject"
enabled = true
startup_timeout_sec = 120
tool_timeout_sec = 60
```

You can instead use a local `.codex/config.toml` in a trusted project; it is ignored by this project's Git rules. Configure the server once, avoiding duplicate user/project registrations. The current workstation's existing user-level registration has been updated to use this project's `.env.local` and shared policy. Refer to the [official Codex configuration guide](https://learn.chatgpt.com/docs/extend/mcp#connect-codex-to-an-mcp-server).

Restart/reload the MCP server or client after saving changes. The first launch needs internet access to obtain pinned DBHub 1.5.0 through npm's cache. No global DBHub install is required. Native Node invokes npm's entry point directly to avoid Windows batch-shell quoting problems.

### Shared DBHub policy and verification

[.agents/dbhub.toml](.agents/dbhub.toml) resolves `${MCP_DATABASE_URL}` from the environment and exposes `execute_sql` and `search_objects`. SQL runs with `readonly = true`, a 1,000-row result limit, and connection/query timeouts. These are MCP tool restrictions; they do not remove privileges from the underlying PostgreSQL account. Keep writes disabled during requirements preparation. Configuration fields are documented in the [DBHub TOML reference](https://dbhub.ai/config/toml).

Ask the connected agent to execute:

```sql
SELECT current_database() AS database,
       current_user AS username,
       current_setting('server_version') AS server_version,
       current_setting('transaction_read_only') AS read_only;
```

Expected: database `campus_equipment`, your own account, PostgreSQL 17.x, and `read_only` = `on`. Confirm both tools appear in your client. A successful pgAdmin login alone does not verify the MCP registration. Do not use schema changes to test this read-only connection.

</details>

## Troubleshooting

| Symptom                              | Fix                                                                                                           |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Missing or invalid configuration     | Fill every required `DB_*`/`DJANGO_*` key in `.env.local`; check quotes, duplicates, and stale process values |
| Database connection refused          | Start PostgreSQL and check `DB_HOST`/`DB_PORT`                                                                |
| Database login fails                 | Verify the local account, raw `DB_PASSWORD`, and database ownership                                           |
| Tables missing or migrations pending | Check `DB_NAME`, then inspect/apply [existing migrations](#apply-existing-migrations)                         |
| Root redirects to login              | Expected after T04; use `/test` with `DJANGO_DEBUG=True` for the frontend/font preview                        |
| Font or CSS returns 404              | Use `DJANGO_DEBUG=True` with runserver; run `findstatic` and use paths relative to `static/`                  |
| Port 8000 is busy                    | Stop your previous server or choose another port and update CSRF origins if needed                            |
| pip missing                          | Run `.\.venv\Scripts\python.exe -m ensurepip --upgrade`                                                       |
| Tests cannot create a database       | Use a local account permitted to create `test_<DB_NAME>`                                                      |
| MCP cannot find files or tools       | Check client working directory, Node/npm paths, enable/reload the server, and keep credentials private        |
| MCP read_only is off                 | Check the shared DBHub policy; do not enable writes to test the connection                                    |

For a ZIP, exclude private files, environments, caches, and generated output explicitly; `.gitignore` does not filter ZIP contents.
