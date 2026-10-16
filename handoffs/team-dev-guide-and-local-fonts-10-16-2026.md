# Team dev guide and local fonts

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time: October 16, 2026, 15:44 Asia/Manila (UTC+08:00).
- Scope: T01 setup/assets follow-up requested by the user; clearer DEV instructions, supplied startup screenshot, README folder structure, and local font configuration.
- Delivery: `jerome`, uncommitted; **Not integrated**. No commit, push, PR, merge, schema change, or private environment modification. Earlier foundation work remains in the same working tree and is preserved.

## Current outcome and interfaces

- [DEV.md](../DEV.md) puts first-time setup, local database/environment preparation, migrations, startup, and the supplied success screenshot before advanced team tooling. Everyday startup has a short command block; optional MCP details are collapsed. Existing referenced setup/Git heading anchors are preserved.
- [README.md](../README.md#project-folder-structure) describes the actual project paths and links to the expected startup screen and everyday commands.
- [config/settings.py](../config/settings.py) registers the existing root `assets/` using `STATICFILES_DIRS`. Asset paths omit that root prefix: `assets/fonts/...` resolves under `/static/fonts/...`. `STATIC_ROOT` stays the ignored collection output `staticfiles/`.
- [assets/css/fonts.css](../assets/css/fonts.css) declares both DM Sans variable faces (weights 100–1000) and all 18 supplied Poppins weight/style files. It applies DM Sans to body text, Poppins to headings, and inherited families to form controls. Future custom base templates include it through `{% static 'css/fonts.css' %}`; no feature/base template or product route was invented.
- [The supplied screenshot](../assets/images/inital-setup-running-success-screen.png) is embedded unchanged. It shows Django's success page with DEBUG=True before custom routes exist. Django's built-in welcome page does not load the project's stylesheet.
- Existing fonts, static variants, and their OFL notices remain in their supplied locations. [Architecture](../docs/architecture.md) now names `assets/` as the shared source directory. The user did not request file moves or font conversion.

## Checks actually run

| Check | Result |
| --- | --- |
| Screenshot review | Viewed the supplied PNG; it contains Django's welcome page and no visible credentials |
| Font metadata | Read DM Sans's supplied README and both families' license notices. Inspected the variable fonts' fvar axes directly: weight 100–1000, optical size 9–40 |
| Static discovery | `manage.py findstatic css/fonts.css fonts/Poppins/Poppins-Regular.ttf --verbosity 2` finds both in the configured assets root |
| Static HTTP responses | Django's real static view with DEBUG=True served fonts.css and all 20 font URLs with status 200 and bytes equal to the files on disk; no mocks or server configuration changes |
| Application checks | `check --database default`, `makemigrations --check --dry-run --noinput`, and `migrate --check` pass; no model drift or pending migrations |
| Tests | `manage.py test --noinput`: all 23 existing tests pass on real PostgreSQL |
| Lint/environment | `ruff check .`, `ruff format --check .`, and `python -m pip check` pass |
| Documentation/scope | All 346 local links/anchors across 25 Markdown files resolve; fences and collapsible sections are balanced. Credential scan passes across 175 shareable paths; Git whitespace checks pass. Image/CSS references, private env, source TXT files, MCP configuration, and earlier handoffs are preserved |

No new test suite, dependency, browser feature page, or deployment setup was added. Browser rendering of a custom page using these fonts remains unrun because no such page exists yet. The earlier foundation handoff contains the actual runserver smoke; this follow-up verified static responses directly without starting another server. Clean-machine and non-Windows setup remain unverified.

## Next action and owner

Jerome reviews the uncommitted changes and separately authorizes publication/integration when ready. Existing T04/T06 and later-task prerequisites remain unchanged. When the assigned feature owners create custom role base templates, they load the shared font stylesheet using the example in DEV.md. No additional feature task is marked complete by this setup follow-up.
