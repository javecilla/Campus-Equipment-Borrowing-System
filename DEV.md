# Team Development Guide

[First-time setup](#first-time-setup) | [Everyday startup](#everyday-startup) | [Error pages](#preview-custom-error-pages) | [Reset local data](#reset-local-development-data) | [Frontend assets](#frontend-assets-tailwind-and-page-scripts) | [Formatting](#formatting-and-code-consistency) | [Migrations](#working-with-migrations) | [Checks](#before-handing-over-work) | [Manual browser tests](docs/manual-test-guide.md) | [Fonts](#fonts-and-static-assets) | [Team Git](#assigned-branches-and-main-integration) | [Optional MCP](#configure-your-mcp-client) | [Troubleshooting](#troubleshooting)

Run commands in **PowerShell from the project root**, where `manage.py` lives. Every member uses their own `.venv`, `.env.local`, and local PostgreSQL database. Git shares source and migrations, not credentials or database contents.

**Current phase: T01-T11 are Done and integrated into main** through PR #27 at `6c5ea8f`. The verified combined source passed 181 PostgreSQL tests and preserves T10 browsing plus the T09 username correction. Ralph / T12, Margareth / T13 and Kenneth / T16 have satisfied prerequisites and remain Not started. Request history/cancellation, approval, maintenance lifecycle and live reporting remain pending; see [HANDOFF.md](HANDOFF.md).

For where to add views, models, forms, URLs, and page templates, use [Project Folder Architecture](docs/project-folder-architecture.md).

To have your coding agent implement your assigned backlog work, copy your member prompt from [Team AI implementation prompts](docs/team-agent-prompts.md). It includes implementation authorization, prerequisite checks, verification, and handoff; feature changes stay uncommitted for review.

## First-time setup

Follow these steps once, in order. Keep an existing environment, database, or private configuration.

### Tools to download

| Required tool | Version | Download |
| --- | --- | --- |
| Git | Git for Windows | [Install Git](https://git-scm.com/install/windows) |
| Python | Python 3.13 | [Windows downloads](https://www.python.org/downloads/windows/) |
| PostgreSQL | PostgreSQL 17, including pgAdmin | [Windows installer](https://www.postgresql.org/download/windows/) |
| Node.js with npm | Node 22+ and npm 10+; tested with Node 24.5.0/npm 11.6.2 | [Node.js downloads](https://nodejs.org/en/download) |

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

| Setting | What to enter |
| --- | --- |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Your database name, account, raw password, host, and port. Usual local values are `campus_equipment`, your account, `127.0.0.1`, and `5432` |
| `DJANGO_SECRET_KEY` | A unique secret generated with the command below |
| `DJANGO_DEBUG` | `True` for normal local debugging and static serving; use the [error-page preview steps](#preview-custom-error-pages) to inspect the custom 404 |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | Keep the template's localhost entries when using port 8000 |
| `MCP_DATABASE_URL` | Leave blank unless using optional MCP tooling |
| `SEED_ACCOUNT_PASSWORD` | Your shared private password for both authentication test accounts; required only when running `seed_auth_accounts` |

Generate a secret locally, then paste the result into `.env.local`:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```

[.env.example](.env.example) is the full key inventory. All `DB_*` and `DJANGO_*` values are required. `DJANGO_DEBUG` accepts exactly `True` or `False`; quote passwords containing `#` or whitespace. Django reads literal values without variable expansion, and explicit process environment values override the file. Missing, blank, malformed, or duplicate configuration fails clearly. Keep `.env.local` private and out of Git.

## Application migrations, checks, and local server

After first-time setup, check configuration and apply the shared migrations:

```powershell
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py migrate --noinput
```

Then start the server:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open **<http://127.0.0.1:8000/>** for the custom sign-in route. With `DJANGO_DEBUG=True`, the Tailwind/font preview remains available directly at **<http://127.0.0.1:8000/test>**. The terminal should report no system-check errors or unapplied migrations. Keep that terminal open while working; stop with Ctrl+C, or Ctrl+Break on Windows.

### Expected startup screen

Anonymous visitors now see the custom sign-in page, with the existing green branding and bottom wave:

![Campus Equipment sign-in page with username or email, password, and the green bottom wave](static/images/login-screen.png)

The current root is `accounts:home`: anonymous visitors go to the custom login page and active users go to `/portal/` or `/manage/` from their stored role. `/test` remains a separate debug-only preview and returns 404 when debug is disabled. The role destinations intentionally contain no demonstration workflow/dashboard data.

<details>
<summary>Earlier setup screens (historical)</summary>

The screenshot below records Django's initial startup before custom routes were added:

![Django initial installation success page with DEBUG=True, before custom routes are added](static/images/inital-setup-running-success-screen.png)

The screenshot below records the temporary development index that preceded T04:

![Earlier development index at / with a Tailwind and font preview link to /test](static/images/new-inital-setup-running-success-screen.png)

</details>

Migrations initialize the settings row (7 days and 3 units per item) and its system audit. They create no accounts or equipment. Use the commands below for local account setup; the full demonstration dataset remains T21.

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

Set `SEED_ACCOUNT_PASSWORD` in your ignored `.env.local` first. The command uses that same private password for both accounts without prompting or printing it; explicit process environment values override the file. The setting is required only for this command, so other Django commands do not require a seed password. Keep its value out of shared files and Git.

It creates the fictional `auth_demo_admin` (`ADMIN`) and `auth_demo_user` (`BASIC_USER`), both active with Profiles and Django staff/superuser flags false. Django validates and hashes the configured password. Both accounts are created in one transaction; a missing/blank/invalid password or either username already existing causes a clear error without changing accounts. Reuse existing accounts or run `manage.py changepassword USERNAME` if needed. Changing the environment value does not reset existing accounts.

Open `/accounts/login/` and sign in with each account separately using the "Username or email" field:

| Role | Username | Email |
| --- | --- | --- |
| Admin | `auth_demo_admin` | `auth-admin@example.invalid` |
| Basic user | `auth_demo_user` | `auth-user@example.invalid` |

Both accounts use your private `SEED_ACCOUNT_PASSWORD`; there is no password shipped in the repository. Choose your own value in `.env.local`. To replace the password on existing accounts, follow [password changes](#change-seed-passwords-while-keeping-records); changing the environment value alone does not update them. Email matching ignores letter case; shared or otherwise ambiguous email addresses require an unambiguous username instead.

The admin should reach `/manage/` and receive 403 at `/portal/`; the basic user should reach `/portal/` and receive 403 at `/manage/`. Sign out using the page's logout button, then reopen the protected destination and confirm it redirects to login. These are authentication landing pages; later workflow features remain pending. This two-account development seed does not satisfy T21's full fictional demonstration dataset.

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

An existing-username error from `seed_auth_accounts` means the accounts have already been created. Sign in with them; the seed deliberately refuses to overwrite existing users. Choose password changes to keep accounts/history, deletion of the two disposable accounts to reseed only those identities, or the full reset for an empty local database.

#### Change seed passwords while keeping records

Run these commands and follow their hidden password/confirmation prompts:

```powershell
.\.venv\Scripts\python.exe manage.py changepassword auth_demo_admin
.\.venv\Scripts\python.exe manage.py changepassword auth_demo_user
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

**This deletes the entire selected database, including every account, Profile, session, equipment record, transaction, audit entry, setting, and migration record.** Use it only for your own disposable development database. Export a backup first if any records must be kept. Your code, migration files, `.env.local`, and generated frontend assets remain on disk.

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
    .\.venv\Scripts\python.exe manage.py seed_auth_accounts
    .\.venv\Scripts\python.exe manage.py check --database default
    .\.venv\Scripts\python.exe manage.py showmigrations
    ```

    Migrations rebuild the schema, initialize the required settings singleton (7 days / 3 units per item) and its SYSTEM audit, and recreate Django metadata. The seed recreates both authentication accounts and Profiles using the current private password. All migrations should show `[X]`; no equipment or borrowing demonstration records are supplied by this two-account seed.
4. Restart Django using [everyday startup](#everyday-startup) and verify both roles using the [authentication test steps](#seed-authentication-test-accounts). Existing login sessions were deleted, so sign in again.

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

| Path | Purpose |
| --- | --- |
| `static/css/app.css` | Tailwind entry point, local font import, font theme, and explicit source locations |
| `static/css/fonts.css` | Existing local font declarations; imported into Tailwind's base layer |
| `static/js/*.js` | Browser page modules; the JavaScript build compiles every top-level module |
| `static/build/` | Generated CSS, browser ES modules/chunks, and any generated dependency license notices |
| `templates/base.html` | Shared document shell loading `build/app.css`, favicon links, and metadata; blocks: title, meta_description, extra_head, content, scripts |
| `static/images/favicon/` | Supplied browser/touch icons and web manifest; manifest icon paths are relative to this directory |

`npm.cmd run build` creates a minified build. `npm.cmd run dev` runs CSS and JavaScript watchers together and stops the sibling if either exits. Build before running `collectstatic` or assembling a submission; include the complete generated build, including chunks/license files, in a runnable artifact. Source control keeps the npm lockfile and source assets; the submission process must build assets explicitly because ignored files are not supplied by Git.

When updating a workstation from the earlier Axios setup, remove its obsolete generated `static/build/http.js` and `static/build/axios-LICENSE.txt` if present before rebuilding or collecting static files. Current builds do not create those files. Keep the source assets and font license files.

### Frontend preview

The shared shell and page modules use the `compiled_asset` template tag to append a content fingerprint to built CSS/JavaScript URLs. Rebuilding changes that URL when bundle bytes change, avoiding stale browser styles or scripts. Missing compiled files raise an explicit build instruction; run the asset build before starting the app or tests. Keep these generated bundles with a runnable submission and rebuild before static collection.

After building assets and starting Django, go directly to **<http://127.0.0.1:8000/test>** (no trailing slash) with `DJANGO_DEBUG=True` in your private `.env.local`. The preview links back to the application home. Expect a pale background, rounded typography cards, green/slate/amber swatches, and the message **DM Sans and Poppins loaded successfully from local assets.** The message checks real font loading in the browser; it reports a failure if font declarations/files cannot load. If it stays at “Checking local fonts…”, check that `build/frontend-test.js` loads and rebuild assets.

The page uses the shared base template and compiled assets. Typography cards sit side by side on wider screens; color swatches stack on small screens. It accepts GET/HEAD without sign-in, reads no application data, and returns 404 when debug is disabled. [config/views.py](config/views.py) owns the preview handler, [templates/dev/frontend-test.html](templates/dev/frontend-test.html) its markup, and [static/js/frontend-test.js](static/js/frontend-test.js) the font check. This is a development preview, not a role layout or product page.

### Styling templates

Feature pages extend the existing `operations/manage/base.html` or `accounts/portal/base.html` role layout and fill `workspace_content`; both inherit the shared document shell. Use literal Tailwind class names in templates, app Python files (including form-widget attributes), or `static/js/`; these locations are scanned explicitly. Write complete alternative class names rather than concatenating fragments such as `bg-{{ color }}-500`. Use `font-sans` for DM Sans and `font-heading` for Poppins. The current font CSS also applies Poppins to headings.

The common shell loads the compiled stylesheet, including local fonts; do not load fonts.css again when extending it. Tailwind styling does not enforce roles, active accounts, ownership, or workflow rules. Django views/forms/services remain authoritative.

### Browser interactions

Use ordinary Django forms and links for the current server-rendered pages. Login and logout use native form submission with CSRF tokens; no JavaScript HTTP library is installed or needed.

Load an actual page module through its template's scripts block, preserving `{{ block.super }}`, with `<script type="module" src="{% compiled_asset 'build/your-page.js' %}"></script>` and `{% load assets %}`. The build compiles/minifies `frontend-test.js`, `account-menu.js` and the local `equipment-photo.js` preview. The shared workspace loads the account disclosure for outside-click/Escape dismissal; native links/forms still handle profile navigation and logout. Use the [coding guide](docs/coding-standards.md#browser-interactions) for future explicitly authorized enhancements and the [HTTP contract](docs/api_spec.md#common-protocol) for existing HTML/form/CSV response semantics.

## Working with migrations

### Apply existing migrations

Use the migration files supplied by the team:

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

| Files | Write formatting | Check without rewriting |
| --- | --- | --- |
| Source JS/MJS/CSS and project JSON | `npm.cmd run format` | `npm.cmd run format:check` |
| Django templates | `.\.venv\Scripts\djlint.exe templates --reformat` | `.\.venv\Scripts\djlint.exe templates --check` |
| Python | `.\.venv\Scripts\ruff.exe format .` | `.\.venv\Scripts\ruff.exe format --check .` |

Install both dependency sets first: `npm.cmd ci` and `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt`. Prettier is pinned in package.json; djLint/Ruff are pinned in requirements-dev.txt. `.prettierrc.json` and pyproject.toml hold shared options; `.prettierignore` excludes Django HTML, Python, private files, dependencies, fonts, and generated output. The npm scripts target source/config files, without rewriting historical Markdown. To format a changed Markdown file deliberately, run `.\node_modules\.bin\prettier.cmd path/to/changed-file.md --write` with its actual path; prose wrapping is preserved.

For a small feature, use the local formatter executable on the actual owned paths, then run the full non-writing checks. Do not use Prettier's generic HTML parser on Django templates or enable two formatters for the same language in your editor. Editor extensions are optional; the CLI is the team reference. djLint is configured as a Django template formatter; its separate optional linter rules are not a new acceptance gate. Ruff remains the Python linter. No pre-commit hook, automatic Tailwind class sorter, or CI job is installed.

The [coding standards](docs/coding-standards.md#http-endpoint-design) own endpoint/calling/styling/naming rules, and [README](README.md#third-party-packages-and-assets) owns dependency justifications. Formatting does not validate those design rules.

### Tailwind CSS in VS Code

Install the workspace-recommended **Tailwind CSS IntelliSense** extension (`bradlc.vscode-tailwindcss`). The shared [.vscode/settings.json](.vscode/settings.json) associates only `static/css/app.css` with its **Tailwind CSS** language mode; ordinary CSS keeps its normal parser. Open the repository root as your workspace so these settings apply.

If `app.css` shows `{ expected` near `source(none)` or warnings on `@source` / `@theme`, check the bottom-right language mode: it should say **Tailwind CSS**, not **CSS**. After installing/enabling the extension, run **Developer: Reload Window** from the Command Palette and reopen the file. These are valid Tailwind v4 directives; verify compilation with `npm.cmd run build:css`. Keep CSS validation enabled. See the [official editor setup](https://tailwindcss.com/docs/editor-setup) for the supported language mode. CLI formatting remains the team reference above.

## Before handing over work

Run the configured checks and any meaningful tests for your feature:

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

Tests create and remove a separate `test_<DB_NAME>` PostgreSQL database. Your local account needs permission to create test databases; keep personal data out of them. The foundation suite does not establish acceptance for unimplemented workflows or T14 competing approvals. To format edited Python files, run `.\.venv\Scripts\ruff.exe format .`.

For each new feature or changed documented flow, update the relevant [manual testing section](docs/manual-test-guide.md) using the [manual-guide requirements](docs/coding-standards.md#manual-testing-guide-for-feature-delivery). Then write the required [dated handoff](.agents/skills/project-handoff/SKILL.md), link that section, update affected task evidence/current readiness, and leave AI changes uncommitted unless the user requests a commit.

## Continuing with T08

**T08 is Done and integrated** through PR #22 at `6c91d48`. Its physical-unit list, registration, detail/history and metadata editing are available under `/manage/units/`. Kenneth's next inventory task is **T16**, currently Not started; its T03/T08 prerequisites are integrated. Follow [the member-branch workflow](#assigned-branches-and-main-integration) to sync `kenneth` with main, then prepare the workstation with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm.cmd ci
npm.cmd run build
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py test --noinput
```

The T07 continuation adds `inventory.0002_category_name_case_insensitive`, `inventory.0003_catalog_item_photo`, and `operations.0003_catalog_restore_audit_actions`. T08, T09 and T10 add no migration or dependency. Do not rewrite existing migrations. Use the existing catalog forms, distinct services, read-only queries, active-admin boundary and parent-before-child lock order; see the [HTTP contract](docs/api_spec.md#custom-administration-accounts-and-inventory), [coding standards](docs/coding-standards.md) and [T08 acceptance](docs/tasks.md#inventory-and-borrower-portal). `/manage/units/` now implements those T08 operations; `/manage/maintenance/` remains a protected placeholder until T16. Registering an initially damaged unit opens maintenance atomically, while subsequent maintenance closure/status transitions remain T16 work. Integration does not start T16 or supply the full demonstration dataset.

### Borrower account verification after T09 integration

Anonymous users can register at `/accounts/register/`, then sign in through the shared login page. Registration fixes the role to BASIC_USER; an active borrower edits only their own name, email and optional contact number at `/portal/profile/`. The administrator profile remains read-only. Registration/profile changes use transactional audit services; see the [HTTP contract](docs/api_spec.md#shared-account-routes) for fields and access rules.

Run `.\.venv\Scripts\python.exe manage.py test accounts.tests.test_borrower_portal operations.tests.test_navigation --noinput` for the focused integration suites. The T10 integration review passed 174 tests; the combined source integrated through PR #27 passed 181 tests. The [username-validation follow-up](handoffs/registration-username-validation-and-t09-status-10-18-2026.md) uses Django normalization and the model validator to return bound field errors before writes; it is integrated through PR #24 at `f29bd91`. T09 remains Done.

### Borrower equipment verification after T10 integration

Active BASIC_USER accounts browse `/portal/equipment/` with name/description search, active-category filtering and 25-item pagination. Detail pages show descriptions, protected photos or the shared default, and database-derived serviceable/available counts. Archived items and items under archived categories are excluded from browsing, detail and photo access. Admins and inactive accounts are denied; internal unit notes and asset codes stay outside these catalog pages. See the [portal contract](docs/api_spec.md#basic-user-portal).

Run `.\.venv\Scripts\python.exe manage.py test inventory.tests.test_portal_equipment --noinput` for the 25 T10 integration tests. The [integration review](handoffs/t10-main-integration-and-documentation-review-10-18-2026.md) records earlier checks and the open test-photo-storage follow-up. Integrated T11 now supplies submission and a create link from the request section, resolving the earlier premature-request-guidance gap; request/loan history and cancellation remain T12 work. The user subsequently reported successful manual T10 testing; detailed mobile/keyboard scenarios were not supplied. See [publication evidence](handoffs/t10-documentation-publication-10-18-2026.md).

### Borrower request submission (T11)

An active BASIC_USER can submit `/portal/requests/new/` with a purpose, desired return date and one to three distinct active catalog items. The service locks/rechecks the borrower, current settings and eligible catalog records, snapshots both limits and writes the Pending request/items atomically without allocating units. `/portal/requests/` displays submission confirmation and a create link; history, details and cancellation remain T12 work.

Run `.\.venv\Scripts\python.exe manage.py test borrowing.tests.test_request_submission --noinput` for focused checks. See the [Ralph implementation snapshot](handoffs/ralph-t11-request-submission-10-18-2026.md), [resolution review](handoffs/pr27-t11-conflict-resolution-review-10-18-2026.md) and [main integration receipt](handoffs/pr27-t11-main-integration-10-18-2026.md) for actual verification/integration evidence. No new migration or dependency is required by T11. After pulling, run the existing asset build to include the request templates; request history/cancellation and administrative approval are still pending.

`.idea/` is ignored and removed from tracked files through main commit `f08fb04`. Each developer may keep local IDE settings; do not force-add them. Generated builds, uploads, dependencies and private environment files also stay outside Git.

## Equipment photos and local media

The **New equipment item** form uses metadata on the left and an optional image/preview panel on the right at desktop widths; leaving the photo empty uses the default image. Selecting a file previews it locally without an upload. **Remove selected image** clears that pending selection, allowing another file to be chosen. The existing photo is changed only when a form is saved; confirmed removal of a saved photo remains a separate action. Creation with a photo saves the item, file reference and audit together, rolling everything back if the operation fails. For an existing item, open its detail page and choose **Manage photo**. Upload one JPEG, PNG or WebP, up to 5 MiB and 20 million pixels. The server rejects animated/invalid files, removes metadata, and saves a WebP fitting within 1600×1600 without cropping. Replace and confirmed removal are audited administrator actions.

Uploads are created automatically in `media/equipment/` under the project root (Django's `MEDIA_ROOT`). PostgreSQL stores a relative path such as `equipment/<generated-id>.webp`; it does not store image bytes. The default `static/images/default-photo-equipment-270x360.webp` is a shared static asset and is used when no photo is assigned. A missing assigned upload is an error, rather than a silently replaced photo.

`media/` is ignored by Git. Every teammate has separate local uploads; pulling source does not copy equipment photos. Back up and restore this folder together with the database, preserving its relative paths. Review any files left unreferenced after an interrupted process before removing them; there is no automatic purge command.

Photos are delivered through the active-ADMIN-protected `inventory_manage:item-photo` route and the active-BASIC_USER-protected `portal:equipment-photo` route. The portal route additionally requires an active item and category. Both stream stored WebP with private/no-store caching. Do not use `item.photo.url` in templates or add a public `static(settings.MEDIA_URL, ...)` mapping: the media directory intentionally has no direct HTTP route. Protected delivery also works with `DEBUG=False`.

To obtain the image dependency and schema after syncing this change:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe manage.py migrate
```

Restart Django after applying the migration. The bundled Pillow wheel includes its license and native-library notices; keep them if redistributing the installed runtime.

## Fonts and static assets

The root `static/` directory contains shared source files. [Django's static-files finder](https://docs.djangoproject.com/en/5.2/howto/static-files/) searches it through `STATICFILES_DIRS` in [config/settings.py](config/settings.py). `STATIC_URL` defines the browser prefix `/static/`, so `static/fonts/...` is served at `/static/fonts/...`. Keep `STATIC_ROOT` (`staticfiles/`) separate for generated collection output.

[static/css/fonts.css](static/css/fonts.css) defines the local DM Sans variable fonts and all Poppins weights/styles. [app.css](static/css/app.css) imports it into Tailwind's base layer, and [base.html](templates/base.html) loads the compiled stylesheet once:

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

| Member | GitHub | Branch |
| --- | --- | --- |
| Jerome | `javecilla` | `jerome` |
| Alex | `AlexCayanan` | `alex` |
| Kenneth | `corkenneth` | `kenneth` |
| Ellyssa | `ellieebeann` | `elly` |
| Margareth | `raifun` | `marga` |
| Ralph | `dreygigz` | `ralph` |

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

Jerome reviews scope, contracts, checks, and handoff before using **Create a merge commit**. Preserve contributor credit and permanent member branches. [CODEOWNERS](CODEOWNERS) routes reviews to `@javecilla`; GitHub cannot accept an author's approval of their own PR. [CONTRIBUTING.md](CONTRIBUTING.md#verification-and-review) explains review restrictions and attribution. Local Django/Ruff checks exist; no GitHub Actions workflow is configured.

## Updating dependencies

Change runtime ranges in [requirements.in](requirements.in), or development tooling in [requirements-dev.in](requirements-dev.in). With uv already installed, regenerate both locks:

```powershell
uv pip compile requirements.in --output-file requirements.txt
uv pip compile requirements-dev.in --output-file requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Run checks before sharing updated locks. Ordinary setup installs the pins without re-resolving them. Psycopg binary avoids a C build; python-dotenv parses configuration; tzdata supplies Windows time-zone data; Ruff is development-only.

JavaScript dependencies belong in package.json/package-lock.json. Use `npm.cmd install --save-exact package@version` for a runtime dependency, adding `--save-dev` for build tools; use real reviewed package/version values. Reinstall with `npm.cmd ci`, then format/check, build, and audit before sharing the lockfile. Tailwind CLI 4.3.0 currently permits the locked watcher 2.6.0, avoiding the [vulnerable braces chain](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) pinned by CLI 4.3.3. Recheck that dependency path during updates; do not run a forced audit fix without reviewing the actual change. Update [README purposes/tradeoffs](README.md#third-party-packages-and-assets) and the [full inventory](docs/third-party-dependencies.md) from lockfile/distribution metadata, including indirect/optional packages and their parent/license declarations. Current page JavaScript contains no bundled third-party runtime package. If a future authorized dependency enters the browser bundle, include its required upstream notices in the generated artifact.

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

| Value | Required adjustment |
| --- | --- |
| `cwd` | Replace `REPLACE_WITH_ABSOLUTE_PROJECT_PATH` with your project's absolute root, such as `C:/School/PythonProject`; this makes `.env.local` and `.agents/dbhub.toml` resolve correctly |
| `command` | `node` must resolve in the AI client's PATH; use the absolute `node.exe` path if necessary |
| Second `args` entry | Default Windows npm entry point is `C:/Program Files/nodejs/node_modules/npm/bin/npx-cli.js`; replace it if Node/npm is installed elsewhere |

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

| Symptom | Fix |
| --- | --- |
| Missing or invalid configuration | Fill every required `DB_*`/`DJANGO_*` key in `.env.local`; check quotes, duplicates, and stale process values |
| Database connection refused | Start PostgreSQL and check `DB_HOST`/`DB_PORT` |
| Database login fails | Verify the local account, raw `DB_PASSWORD`, and database ownership |
| Tables missing or migrations pending | Check `DB_NAME`, then inspect/apply [existing migrations](#apply-existing-migrations) |
| Root redirects to login | Expected after T04; use `/test` with `DJANGO_DEBUG=True` for the frontend/font preview |
| Font or CSS returns 404 | Use `DJANGO_DEBUG=True` with runserver; run `findstatic` and use paths relative to `static/` |
| Port 8000 is busy | Stop your previous server or choose another port and update CSRF origins if needed |
| pip missing | Run `.\.venv\Scripts\python.exe -m ensurepip --upgrade` |
| Tests cannot create a database | Use a local account permitted to create `test_<DB_NAME>` |
| MCP cannot find files or tools | Check client working directory, Node/npm paths, enable/reload the server, and keep credentials private |
| MCP read_only is off | Check the shared DBHub policy; do not enable writes to test the connection |

For a ZIP, exclude private files, environments, caches, and generated output explicitly; `.gitignore` does not filter ZIP contents.
