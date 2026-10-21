# Local dashboard asset build recovery

- Date: October 21, 2026, 15:25 Asia/Manila.
- Owner: AI agent; member not specified. Checkout: `ralph`.
- Scope: user-requested local asset build for the missing dashboard bundle; existing UI-11 tooling only. No feature task status changed.

The initial build failed because the installed dependencies lacked the Chart.js version already declared in [package.json](../package.json) and its lockfile. Reinstallation initially failed with Windows EPERM because the project's Tailwind watcher held the Lightning CSS native module open. Stopping that watcher allowed `npm ci` to finish. The frontend watch session is stopped; restart with `npm run dev` when needed.

Checks executed:

- `npm ci`: passed; 52 packages added, 53 audited, zero vulnerabilities reported.
- `npm run build`: passed, including all nine theme contrast checks and CSS/JavaScript compilation.
- `manage.py findstatic build/dashboard-charts.js --verbosity 1` using the local virtual environment: passed; resolves to `static/build/dashboard-charts.js` (154,905 bytes).
- Git status after the build: clean; dependencies and compiled output are ignored. Package manifests and application source were unchanged. This receipt and its index are uncommitted documentation.

Browser refresh and application tests: Not run. Next action: the local developer refreshes `/manage/` and optionally restarts watch mode. Setup remains documented in [DEV.md](../DEV.md#fonts-and-static-assets). No commit or push was performed.
