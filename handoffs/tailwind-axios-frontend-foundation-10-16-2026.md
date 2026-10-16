# Tailwind and Axios frontend foundation

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Task/scope: UI-01, explicitly requested shared Tailwind styling and Axios HTTP setup; explain course pattern requirements and library justification.
- Branch/integration: `jerome`, uncommitted over `8668ff8`; **Not integrated**. No commit, push, PR, merge, database migration, or another member's feature implementation performed in this task.

## Current outcome and interfaces

- [package.json](../package.json) and [lockfile](../package-lock.json) declare Axios 1.20.0, Tailwind/CLI 4.3.0, esbuild 0.28.2, and concurrently 10.0.6. Tested Node 24.5.0/npm 11.6.2; minimum declared Node 22/npm 10. All five direct packages identify MIT licensing.
- [app.css](../assets/css/app.css) imports Tailwind and existing fonts in the base layer, defines font-sans/font-heading, and scans root templates, feature apps, and browser scripts. Source assets remain in assets/; node_modules/ and assets/build/ are ignored generated files.
- [http.js](../assets/js/http.js) exports a shared Axios instance with csrftoken/X-CSRFToken and a 10-second timeout. Default same-origin browser behavior is retained; no cross-origin credentials, global retry/interceptor behavior, or new API contract was added. Top-level assets/js/*.js entries bundle into browser ES modules with shared chunks when needed.
- [base.html](../templates/base.html) loads compiled build/app.css and supplies title, extra_head, content, and scripts blocks. It is a common shell; manage/base.html, portal/base.html, navigation/components, login, and workflow pages remain feature-owner work. Root URL configuration stays empty.
- [License-copy script](../scripts/copy-licenses.mjs) retains the complete Axios MIT notice beside generated JavaScript. Metafile inspection confirms Axios is the only npm package included in the current browser bundle. Existing font OFL notices are preserved.
- [DEV.md](../DEV.md#frontend-assets-tailwind-and-axios) owns install/build/watch/template/HTTP instructions; README and the folder guide reflect the new files. [Architecture](../docs/architecture.md#required-patterns-and-selected-libraries) distinguishes required MTV/inheritance/reusable logic from the selected service-layer approach and documents library tradeoffs. Source course/member files are preserved.

## Verification and decisions

- Locked npm ci installation, npm run build, and npm audit pass; final audit reports zero vulnerabilities. CLI 4.3.3 pinned watcher 2.5.1 and pulled the vulnerable braces chain; CLI 4.3.0 permits watcher 2.6.0. The lockfile selects that compatible chain without overrides or a forced audit fix.
- npm run dev starts both watchers. Temporary template/JS edits trigger CSS and JS rebuilds; the real browser sees the changed JS result. Compiled CSS contains the added utility. Both watchers were stopped after the smoke run.
- A temporary loopback WSGI harness used the actual shared template, compiled assets, Axios, Django CSRF middleware, and real browser requests. Valid POST returned 200 with the CSRF header and form value; a missing-token POST returned 403; an intentional HTTP 503 rejected into the caller. Local DM Sans/Poppins fonts loaded, and Tailwind desktop spacing computed to 40px. No production route or permanent test-only page was added; harness files and generated test bundles were removed.
- A clean final build renders through Django's template loader. Django static serving returns exact bytes for compiled CSS/JS and all 20 referenced font URLs; the font URLs resolve from the output directory. The license copy matches the installed Axios LICENSE.
- All 23 real PostgreSQL foundation tests pass (1.959 seconds). Django database check, migration drift check, applied-migration check, Ruff lint/format, and pip check pass. These checks do not establish acceptance of unimplemented role/workflow pages.
- Final verification passes: all 444 relative links/anchors across 31 Markdown files resolve; code fences/details are balanced; private-value scan passes across 187 shareable files; original TXT sources and all 31 application task/three integration-evidence rows are unchanged. Git excludes private/generated assets and git diff --check passes. The smoke listener and asset watchers are stopped and temporary sources are absent.
- No clean-machine install, CI, full role UI, chart library, separate JSON API, or T14 competing-approval test is claimed.

## Next action

Jerome reviews the shared frontend setup for separately authorized publication/integration. Teammates then run npm ci and either npm run build or npm run dev using DEV.md, extend the shared shell in their role layouts, and import the shared client where a contracted enhancement needs HTTP. Alex's T04 readiness still depends on the already integrated foundation; other task dependencies and ownership are unchanged.
