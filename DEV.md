# Developer Preparation and Local Database/MCP Setup

## What is available now

This guide prepares a developer's workstation, local PostgreSQL database, private environment file, and AI database connection. The repository currently contains documentation and MCP configuration, with no Django application, `manage.py`, migrations, or `requirements.txt`. Application installation/start/test commands will be documented when the team implements and verifies them. Keep the README focused on the project overview.

Each member runs their own local PostgreSQL database. `localhost` refers to the machine running the MCP process; it does not connect to another member's computer or synchronize team data. The MCP runs locally over stdio and provides read-only inspection. It is separate from Django's future database connection.

## Tools to download

These steps target Windows, matching the tested workstation. Other operating systems need their equivalent paths/installers.

| Tool | Version / purpose | Official download |
| --- | --- | --- |
| Git | Source sharing and version control | [Git for Windows](https://git-scm.com/install/windows) |
| Python | Latest patched Python 3.13 release for the proposed Django application | [Python Windows releases](https://www.python.org/downloads/windows/) |
| PostgreSQL | Latest patched PostgreSQL 17 release; include server and command-line tools | [PostgreSQL Windows installer](https://www.postgresql.org/download/windows/) |
| pgAdmin | Optional GUI bundled with the PostgreSQL installer; convenient for database creation and SQL checks | [PostgreSQL installer components](https://www.postgresql.org/download/windows/) |
| Node.js and npm | Node.js 24 LTS with bundled npm; DBHub 1.5.0 requires Node >= 22.5 | [Node.js downloads](https://nodejs.org/en/download) |
| Editor and AI client | Your editor plus an MCP-capable desktop/CLI client; Codex configuration is described below | [Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp) |

Use current security patches within the agreed series. Django 5.2 LTS and Psycopg 3 remain proposed application dependencies; do not install them globally. The MCP package is pinned in the shared configuration and runs through npm's per-user execution cache, so there is no global DBHub installation or Node application dependency manifest.

After installing tools, reopen your terminal/client so PATH changes are visible. In PowerShell, check:

```powershell
git --version
py -3.13 --version
node --version
npm --version
```

For PostgreSQL installed in its standard location:

```powershell
& 'C:/Program Files/PostgreSQL/17/bin/psql.exe' --version
```

If a command is missing, fix its installation/PATH before continuing. Select Python 3.13 explicitly rather than assuming `python` points to the correct interpreter.

## Open your copy of the project

The shared private repository is [javecilla/Campus-Equipment-Borrowing-System](https://github.com/javecilla/Campus-Equipment-Borrowing-System). Jerome (`@javecilla`) manages repository access and integration into `main`; this responsibility does not make the team's project his individual work. Accept the collaborator invitation using your own GitHub account before cloning. Collaborator invitations are managed separately from these setup files.

For a new working copy:

```powershell
git clone https://github.com/javecilla/Campus-Equipment-Borrowing-System.git
Set-Location Campus-Equipment-Borrowing-System
git remote -v
```

For an existing working copy, open its project root and verify that `origin` points to that URL; do not initialize Git or add another origin blindly. Never put a GitHub token in the remote URL. Git for Windows can authenticate through Git Credential Manager. Open the folder containing `README.md`, `DEV.md`, `.env.example`, and `.agents/`. Run the remaining commands from that root.

Read [AGENTS.md](AGENTS.md), [PLAN.md](PLAN.md), [CONTRIBUTING.md](CONTRIBUTING.md), [coding standards](docs/coding-standards.md), [HANDOFF.md](HANDOFF.md), and your assigned task in [docs/tasks.md](docs/tasks.md) before changes. Use PLAN.md's readiness gates and the backlog's integration evidence before consuming another member's work. The handoff describes observed state on the current workstation; it does not prove another machine is configured.

## Assigned branches and main integration

Branch assignments come from `MEMBERS GITHUB REPO BRANCH` in [Project-Members.txt](docs/Project-Members.txt). These are persistent member branches; keep them after PR merges.

| Member | GitHub account | Working branch |
| --- | --- | --- |
| Jerome | `javecilla` | `jerome` |
| Alex | `AlexCayanan` | `alex` |
| Kenneth | `corkenneth` | `kenneth` |
| Ellyssa | `ellieebeann` | `elly` |
| Margareth | `raifun` | `marga` |
| Ralph | `dreygigz` | `ralph` |

`main` is the shared integration branch. All members may fetch/pull it, but only Jerome integrates changes into it. Develop and push on your own assigned branch; do not push to `main` or another member's branch. Do not delete permanent member branches, force-push, squash, or rewrite shared history as part of ordinary work.

An active GitHub [main-owner-only ruleset](https://github.com/javecilla/Campus-Equipment-Borrowing-System/rules/25213591) targets `refs/heads/main`. It restricts creation, updates, deletion, and non-fast-forward updates, with only `javecilla` as the bypass user. This restricts collaborator pushes and PR merges into main; it does not grant extra permissions on other branches. Member-branch ownership is a team convention, not a separate GitHub access restriction. See [GitHub's ruleset behavior](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).

### First checkout of your member branch

The repository owner initializes the assigned remote branches from the shared baseline. Use your branch from the table; the examples below use Alex's branch. Change the variable once to your assignment:

```powershell
$memberBranch = 'alex'
git status --short
git fetch origin --prune
git switch --create $memberBranch --track "origin/$memberBranch"
```

Start with a clean working tree. Run the create command only when the local branch does not already exist. On later visits, use `git switch $memberBranch`. If the assigned remote branch is missing, ask Jerome to confirm its setup; do not create another naming scheme or push a replacement main branch.

### Bring main into your work before starting

First finish or safely preserve any local work on your own branch; do not switch branches with unrelated uncommitted changes. Then run:

```powershell
git fetch origin --prune
git switch main
git pull --ff-only origin main
git switch $memberBranch
git merge --ff-only "origin/$memberBranch"
git merge --no-edit main
```

Pulling `main` updates your **local copy**; it does not push changes or give you main-write permission. The final merge brings the shared work into your member branch, preserving history. If the fast-forward-only update fails, stop and inspect the divergence rather than resetting or force-pushing. If the main-to-member merge conflicts, resolve it as described below before continuing.

### Commit, push your branch, and open a PR

Complete the task, relevant checks, and dated handoff first. Inspect/stage only its intended files. Replace the example paths and message below with your actual work; never stage `.env.local` or private user configuration:

```powershell
git status --short
git --no-pager diff
git add -- path/to/changed-file path/to/dated-handoff.md
git --no-pager diff --cached
git diff --cached --check
git commit -m "feat: implement the assigned task"
git push --set-upstream origin $memberBranch
```

On GitHub, open **Pull requests → New pull request**, choose **base: main** and **compare: your assigned branch**, and describe the task, resulting behavior, files, actual verification, and remaining limitations. Jerome reviews and integrates it. You may address review comments by committing and pushing more changes to the same member branch. Do not include unrelated unfinished tasks in a PR from a persistent member branch. GitHub documents the [PR creation flow](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request).

After Jerome merges a PR, keep your member branch and run the main-sync steps before the next task. Prefer an ordinary merge to squash/rebase so individual work and contribution history remain available. A change to this history policy must be explicitly agreed/requested.

### Resolve merge conflicts without losing another member's work

```powershell
git status
git diff --name-only --diff-filter=U
```

Read each conflict and coordinate with the affected feature owner when a shared rule/schema is involved. Edit the file to preserve the correct combined behavior and remove conflict markers. Stage the resolved files explicitly, run the relevant checks, then complete the existing merge with `git commit --no-edit` and push **your member branch**. To cancel a merge instead, use `git merge --abort` before starting another change. Do not blindly choose one side for every file, use `reset --hard`, or force-push to hide a conflict.

### Jerome's integration responsibility

Jerome checks the PR's scope, source contracts, tests/evidence, and dated handoff, then uses GitHub's **Create a merge commit** option for normal PR integration. Only the designated repository maintainer performs the main update. Keep persistent member branches; do not select their deletion after merge. Reviewers and contributors retain accurate credit, and repository access must remain separate from claims of individual authorship.

Review requests follow [CODEOWNERS and its access requirements](CONTRIBUTING.md#verification-and-review): `@javecilla` is the designated default reviewer. GitHub uses the base branch's file, so a local/jerome change takes effect for main-targeting PRs only after integration into main. A PR authored by `javecilla` cannot receive his own approving review. Collaborator invitations and acceptance still control private repository access; teammate membership does not require listing every member in CODEOWNERS. Current verified access is recorded in HANDOFF.md. This setup does not send invitations.

The empty repository's initial snapshot is created on `jerome` and published as the main baseline; there is no earlier main history to review against for that first publication. Subsequent task changes use the member-branch → PR → Jerome/main workflow above. No application CI/test checks are claimed to exist yet; use the checks actually configured for the task.

## Prepare the Python environment

An isolated Python environment can be prepared when starting Python work:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe --version
```

Activation is unnecessary when calling that interpreter directly. Application dependencies must eventually be declared with tested versions in the project's requirements file. Do not invent a `pip install -r requirements.txt`, migration, or server-start step while those files do not exist.

## Create your local database

1. Install/start the PostgreSQL 17 Windows service. Remember your own database account and password. The sample account `postgres` is a local administrative account; no dedicated application account is created by these documents.
2. Open pgAdmin and connect to your local server at `127.0.0.1`, port `5432` unless you selected another port during installation.
3. Under Databases, create a database named `campus_equipment`, owned by the local account you will use. If that database already exists, use it; do not recreate/drop it.
4. Open the Query Tool for **campus_equipment** and run:

```sql
SELECT current_database(), current_user, current_setting('server_version');
```

The database name must be `campus_equipment` and the server version must be in the 17 series. On the current workstation, PostgreSQL 17.5 was verified. New workstations should use a current patched PostgreSQL 17 release.

No tables are expected before migrations are implemented. Do not execute the design document as SQL or create competing hand-written application tables. Django migrations will own the executable schema.

## Create and edit .env.local

[.env.example](.env.example) is the canonical key inventory. Copy it only if you do not already have a private file:

```powershell
New-Item -Path .env.local -ItemType File -Value (Get-Content -LiteralPath .env.example -Raw) -ErrorAction Stop
```

This command fails if the file already exists. Keep an existing file and edit it rather than replacing it. Edit `.env.local` locally, never the shared template, to set:

| Key or group | What each developer changes |
| --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` | Your future application's local database address, name, and account |
| `DB_PASSWORD` | That account's raw password, without URL encoding |
| `MCP_DATABASE_URL` | Full connection URI for AI inspection; include the database name and URL-encode username/password |
| `DJANGO_SECRET_KEY` | A unique generated local secret for the future application |
| Other `DJANGO_*` values | Local host/origin settings; set DEBUG True only for private local development |

The connection URI shape is:

```text
postgresql://YOUR_USER:YOUR_URL_ENCODED_PASSWORD@127.0.0.1:5432/campus_equipment?sslmode=disable
```

`sslmode=disable` here is only for the local loopback connection. Remote database connections need their own validated TLS configuration. Characters such as `/`, `@`, `:`, `#`, `%`, and parentheses in credentials must be percent-encoded in the URI; avoid double encoding. `DB_PASSWORD` remains raw. Keep values containing `#` or whitespace quoted in the environment file.

Generate a local Django secret without installing Django:

```powershell
py -3.13 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Paste it into `.env.local`, not chat or documentation. `MCP_DATABASE_URL` is an independent connection setting, allowing an inspection account separate from the application account. If you use the same account for both and change its password/host/port, update both the URL and matching DB_* values. An existing password was configured only in the current developer's private file; other members must supply their own values.

The shared MCP command explicitly loads `.env.local` using Node's [required `--env-file` option](https://nodejs.org/docs/latest-v24.x/api/cli.html#--env-filefile). A missing file fails startup. Existing process environment values take precedence; clear stale matching variables in the launching client if changes to the file seem ignored. The file is not automatically loaded into your terminal, pgAdmin, or Django. Django's loader/settings have not been implemented yet.

`.gitignore` excludes `.env.local`, other private local env files, virtual environments, and local Codex configuration. Keep `.env.example`, [the MCP JSON](.agents/mcp.json), and [DBHub policy](.agents/dbhub.toml) shareable and free of credentials. When using a ZIP instead of Git, explicitly omit `.env.local` and other private files: `.gitignore` does not filter ZIP contents.

## Configure your MCP client

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

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Cannot find .env.local or DBHub config | Correct the client's `cwd`; use the project root, not `.agents/` |
| Node/npm entry point missing | Reopen the client after installation, verify PATH and the actual entry-point file |
| Connection refused | PostgreSQL service is running on the configured host/port |
| Authentication failed | Own account/password, raw DB_PASSWORD, correct percent encoding in MCP_DATABASE_URL |
| Database does not exist / wrong database | Create/select campus_equipment and include `/campus_equipment` in the URI |
| Tools do not appear | Correct client schema, enable the server, and restart/reload; inspect its error log without sharing credentials |
| Query says read_only = off | Confirm this server uses the shared policy and its execute_sql tool; do not continue with writes |
| No application tables | Expected before Django migrations exist; follow the backlog when implementation is authorized |

After completing a file-changing task or transferring unfinished work, follow the [project-handoff skill](.agents/skills/project-handoff/SKILL.md): create `handoffs/{title-of-work}-{MM-DD-YYYY}.md` using the current Asia/Manila date, then update HANDOFF.md's current state/index and the affected tasks with actual verification results.
