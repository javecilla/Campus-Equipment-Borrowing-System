# Team Development Guide

[First-time setup](#first-time-setup) | [Everyday startup](#everyday-startup) | [Frontend assets](#frontend-assets-tailwind-and-axios) | [Formatting](#formatting-and-code-consistency) | [Migrations](#working-with-migrations) | [Checks](#before-handing-over-work) | [Fonts](#fonts-and-static-assets) | [Team Git](#assigned-branches-and-main-integration) | [Optional MCP](#configure-your-mcp-client) | [Troubleshooting](#troubleshooting)

Run commands in **PowerShell from the project root**, where `manage.py` lives. Every member uses their own `.venv`, `.env.local`, and local PostgreSQL database. Git shares source and migrations, not credentials or database contents.

The T01–T03 foundation is integrated into `main` through [PR #3](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/3). Sync your member branch with main before starting dependent work; see [HANDOFF.md](HANDOFF.md) for readiness. Login and feature pages remain pending.

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

Commit `package.json` and `package-lock.json` when dependencies change. `node_modules/` and `static/build/` are local generated files and remain ignored. Rebuild them on each workstation; do not copy them from another member. Python dependencies remain in the requirements files. See [frontend usage](#frontend-assets-tailwind-and-axios) for watch mode and template integration.

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
| `DJANGO_DEBUG` | `True` for local development to see the success screen and serve assets through runserver |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | Keep the template's localhost entries when using port 8000 |
| `MCP_DATABASE_URL` | Leave blank unless using optional MCP tooling |

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

Open **<http://127.0.0.1:8000/>** with `DJANGO_DEBUG=True` for the development index, then follow **Tailwind & font preview** to `/test`. The terminal should report no system-check errors or unapplied migrations. Keep that terminal open while working; stop with Ctrl+C, or Ctrl+Break on Windows.

### Expected startup screen

The screenshot below records Django's initial startup before custom routes were added:

![Django initial installation success page with DEBUG=True, before custom routes are added](static/images/inital-setup-running-success-screen.png)

After setup and server startup, the current development index should look like this:

![Current development index at / with a Tailwind and font preview link to /test](static/images/new-inital-setup-running-success-screen.png)

The current startup screen is the development index at `/`, with a navigation card for `/test`, described below. These debug-only pages replace Django's automatic welcome screen. Both return 404 when debug is disabled. The planned account home behavior, login, `/manage/`, and `/portal/` pages arrive in their assigned tasks.

Migrations initialize the settings row (7 days and 3 units per item) and its system audit. They create no accounts or equipment. Admin-account provisioning is part of T04; demonstration seeding is T21.

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

## Frontend assets: Tailwind and Axios

The library rationale and course-pattern requirements are in [architecture.md](docs/architecture.md#required-patterns-and-selected-libraries). This setup adds a shared template shell and asset build; feature owners still implement the role layouts and pages.

| Path | Purpose |
| --- | --- |
| `static/css/app.css` | Tailwind entry point, local font import, font theme, and explicit source locations |
| `static/css/fonts.css` | Existing local font declarations; imported into Tailwind's base layer |
| `static/js/http.js` | Shared Axios instance with Django CSRF names and a 10-second timeout |
| `static/js/*.js` | Browser page modules; the JavaScript build compiles every top-level module |
| `static/build/` | Generated CSS, browser ES modules/chunks, and any generated dependency license notices |
| `templates/base.html` | Shared document shell loading `build/app.css`, favicon links, and metadata; blocks: title, meta_description, extra_head, content, scripts |
| `static/images/favicon/` | Supplied browser/touch icons and web manifest; manifest icon paths are relative to this directory |

`npm.cmd run build` creates a minified build. `npm.cmd run dev` runs CSS and JavaScript watchers together and stops the sibling if either exits. Build before running `collectstatic` or assembling a submission; include the complete generated build, including chunks/license files, in a runnable artifact. Source control keeps the npm lockfile and source assets; the submission process must build assets explicitly because ignored files are not supplied by Git.

### Frontend preview

After building assets and starting Django, visit **<http://127.0.0.1:8000/>** and select **Tailwind & font preview**, or go directly to **<http://127.0.0.1:8000/test>** (no trailing slash). Set `DJANGO_DEBUG=True` in your private `.env.local`. The preview links back to the development index. Expect a pale background, rounded typography cards, green/slate/amber swatches, and the message **DM Sans and Poppins loaded successfully from local assets.** The message checks real font loading in the browser; it reports a failure if font declarations/files cannot load. If it stays at “Checking local fonts…”, check that `build/frontend-test.js` loads and rebuild assets.

The page uses the shared base template and compiled assets. Typography cards sit side by side on wider screens; color swatches stack on small screens. It accepts GET/HEAD without sign-in, reads no application data, and returns 404 when debug is disabled. [config/views.py](config/views.py) owns the preview handler, [templates/dev/frontend-test.html](templates/dev/frontend-test.html) its markup, and [static/js/frontend-test.js](static/js/frontend-test.js) the font check. This is a development preview, not a role layout or product page.

### Styling templates

Feature owners make `manage/base.html` and `portal/base.html` extend `base.html`, then have feature pages extend the appropriate role layout. Role layouts are not created by this setup. Use literal Tailwind class names in templates, app Python files (including form-widget attributes), or `static/js/`; these locations are scanned explicitly. Write complete alternative class names rather than concatenating fragments such as `bg-{{ color }}-500`. Use `font-sans` for DM Sans and `font-heading` for Poppins. The current font CSS also applies Poppins to headings.

The common shell loads the compiled stylesheet, including local fonts; do not load fonts.css again when extending it. Tailwind styling does not enforce roles, active accounts, ownership, or workflow rules. Django views/forms/services remain authoritative.

### Calling Django with Axios

Page modules in `static/js/` import the shared client:

```javascript
import { http } from "./http.js";
```

Load a page's compiled module in its template's `scripts` block with `<script type="module" src="{% static 'build/your-page.js' %}"></script>` and `{% load static %}` in that template. The build bundles bare npm imports and shares dependency chunks; do not serve `static/js/http.js` directly as browser-ready JavaScript. No Axios request is made until a feature calls the client.

Use named Django URLs rendered into the page and same-origin requests. Current form endpoints use the URL-encoded encoding in [api_spec.md](docs/api_spec.md#common-protocol): send string fields through URLSearchParams, rather than JSON. Use FormData/multipart only when the affected contract explicitly allows it. Render `{% csrf_token %}` in state-changing forms; that also causes Django to issue the CSRF cookie. A future page without such a form that makes POST requests must explicitly arrange for Django to set that cookie, following [Django's CSRF guidance](https://docs.djangoproject.com/en/5.2/howto/csrf/).

Axios reads `csrftoken` and sends `X-CSRFToken` for same-origin browser requests. Session cookies use the browser's normal same-origin behavior; cross-origin credentials and CSRF exemptions are not enabled. Handle rejected responses/timeouts in the calling feature with visible, actionable feedback. Do not retry state-changing requests automatically. Validate any response data a feature consumes; Axios is a transport, not runtime schema validation. The [HTTP contract](docs/api_spec.md) still describes server-rendered HTML/forms/CSV, with no separate JSON API or chart endpoint added by this setup.

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

Write the required [dated handoff](.agents/skills/project-handoff/SKILL.md), update affected task evidence/current readiness, and leave AI changes uncommitted unless the user requests a commit.

## Fonts and static assets

The root `static/` directory contains shared source files. [Django's static-files finder](https://docs.djangoproject.com/en/5.2/howto/static-files/) searches it through `STATICFILES_DIRS` in [config/settings.py](config/settings.py). `STATIC_URL` defines the browser prefix `/static/`, so `static/fonts/...` is served at `/static/fonts/...`. Keep `STATIC_ROOT` (`staticfiles/`) separate for generated collection output.

[static/css/fonts.css](static/css/fonts.css) defines the local DM Sans variable fonts and all Poppins weights/styles. [app.css](static/css/app.css) imports it into Tailwind's base layer, and [base.html](templates/base.html) loads the compiled stylesheet once:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'build/app.css' %}">
```

Keep the existing font files and their `OFL.txt` notices. Use CSS-relative URLs inside the stylesheet and Django's `{% static %}` tag in templates. No fonts are downloaded from a CDN. The DM Sans variable pair covers weights 100–1000, so the included DM Sans static variants need no additional declarations.

For discovery checks:

```powershell
.\.venv\Scripts\python.exe manage.py findstatic build/app.css build/http.js fonts/Poppins/Poppins-Regular.ttf --verbosity 2
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

JavaScript dependencies belong in package.json/package-lock.json. Use `npm.cmd install --save-exact package@version` for a runtime dependency, adding `--save-dev` for build tools; use real reviewed package/version values. Reinstall with `npm.cmd ci`, then format/check, build, and audit before sharing the lockfile. Tailwind CLI 4.3.0 currently permits the locked watcher 2.6.0, avoiding the [vulnerable braces chain](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) pinned by CLI 4.3.3. Recheck that dependency path during updates; do not run a forced audit fix without reviewing the actual change. Update [README purposes/tradeoffs](README.md#third-party-packages-and-assets) and the [full inventory](docs/third-party-dependencies.md) from lockfile/distribution metadata, including indirect/optional packages and their parent/license declarations. The JS build copies Axios's complete MIT notice beside its bundle through `scripts/copy-licenses.mjs`; extend that step if another package enters the browser bundle.

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
| Welcome screen or 404 | Expected until custom routes exist; use `DJANGO_DEBUG=True` locally to see the supplied success screen |
| Font or CSS returns 404 | Use `DJANGO_DEBUG=True` with runserver; run `findstatic` and use paths relative to `static/` |
| Port 8000 is busy | Stop your previous server or choose another port and update CSRF origins if needed |
| pip missing | Run `.\.venv\Scripts\python.exe -m ensurepip --upgrade` |
| Tests cannot create a database | Use a local account permitted to create `test_<DB_NAME>` |
| MCP cannot find files or tools | Check client working directory, Node/npm paths, enable/reload the server, and keep credentials private |
| MCP read_only is off | Check the shared DBHub policy; do not enable writes to test the connection |

For a ZIP, exclude private files, environments, caches, and generated output explicitly; `.gitignore` does not filter ZIP contents.
