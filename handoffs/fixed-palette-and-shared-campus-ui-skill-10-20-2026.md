# Fixed Palette and Shared Campus UI Skill

- **Owner:** Jerome Avecilla with Codex assistance.
- **Date/time zone:** October 20, 2026, Asia/Manila.
- **Scope:** UI-09 fixed-palette dependency cleanup and DOC-09 shared frontend skill.
- **Outcome:** Done locally on `jerome`, uncommitted and **not integrated into main**. No commit, push, PR, application workflow or business-data change.

## Result

Material Color Utilities was still imported by the old palette generator, so deleting the dependency alone would have broken the build. The exact **31 existing semantic colors** now live in [app.css](../static/css/app.css), and [base.html](../templates/base.html) loads the single compiled stylesheet. Existing `--md-sys-color-*` names remain CSS contracts and require no Material package. The generator and unused generated theme bundle were removed. [Package scripts](../package.json) use a dependency-free [contrast checker](../scripts/check-theme.mjs) before compiling; nine existing text-role pairs must meet 4.5:1.

[campus-ui](../.agents/skills/campus-ui/SKILL.md) is a repository-shared skill for frontend implementation/review. It routes agents to the canonical styling/component table and actual role shells, grids, fields, buttons, tables, profile link, logout form and source examples. It requires relevant browser/accessibility checks and the existing manual-guide/handoff workflow without authorizing new features or publication. It avoids a duplicate palette/specification or copied page scaffolds.

[AGENTS.md](../AGENTS.md), the [Django skill](../.agents/skills/django-mtv/SKILL.md), [team agent prompts](../docs/team-agent-prompts.md), README and DEV guidance link the skill. Agents can invoke `$campus-ui` after obtaining this work; tools without skill discovery need its SKILL.md loaded explicitly. This is instruction-based guidance, not an enforcement service or a guarantee of agent compliance. Automatic invocation was not disabled. UI metadata supplies a default prompt and display label.

## Verification

- Exact comparison against the pre-removal palette confirms **all 31 colors unchanged**. The lock graph matches the saved graph except for the removed Material package/root entry: **113 non-root package entries remain**, with all other metadata/versions preserved.
- An initial `npm uninstall` pruned unrelated optional lock entries; `npm ci` correctly rejected the incomplete graph. Restoring the saved optional metadata while removing only Material fixed the cause. The final **fresh npm ci, build, formatting and audit pass; zero vulnerabilities**.
- The dependency-free contrast check passes all nine pairs. Temporary low-contrast and missing-role CSS fixtures fail with specific RangeError/SyntaxError messages; application CSS was not changed for these probes.
- New campus-ui and updated django-mtv pass the bundled `quick_validate.py`. UI metadata parses with the existing PyYAML installation; display/default-prompt constraints and relative references were checked. No extra skill tooling dependency was installed, and no subagent evaluation was required for this small routing skill.
- **254 PostgreSQL tests passed in 42.919s** using the temporary test settings' distinct `test_campus_equipment_ui_skill_20261020` database, created and destroyed by Django. The first standard `test_campus_equipment` attempt encountered an existing database, duplicate fixtures and teardown reporting that the database no longer existed. It failed and is not counted as a pass; no service/schema change or application fallback was made to suppress it.
- Chrome **155.0.8059.84** passed **12 home/profile page checks** across ADMIN/BASIC_USER at 320/1024/1440px: expected colors/font, profile visibility, one compiled stylesheet and no page overflow. **4 direct-profile/logout actions passed**. Existing fictional active accounts were reused; temporary sessions were logged out. Screenshots remain ignored under `output/playwright/`.
- Django database/schema/migration checks, Ruff lint/format, djLint (70 templates), pip check and diff whitespace checks pass. Current document/skill links and fences were checked. Historical handoffs were preserved and can reference retired source files.

## Concurrent work and limits

Unowned edits to `operations/views.py` and the shared workspace header appeared during verification; the administrator destination rendered the T18 placeholder in the current worktree. Those edits were preserved, not introduced or reverted by this task. Browser checks establish the fixed-palette/loading behavior for that observed checkout, not immutable-tree acceptance of other agents' dashboard changes. Prior navigation/layout evidence remains in the [navigation handoff](sidebar-logout-and-topbar-profile-link-10-20-2026.md).

No full screen-reader, Firefox/Safari or complete lifecycle acceptance was run. The new skill's metadata/references were validated; that is not proof that every external AI client will automatically load or obey it. Templates should be reviewed against the canonical guide during each feature delivery.

Jerome/user reviews the uncommitted dependency and skill changes before publication. Teammates must obtain this local skill before using it. Margareth / T15 readiness and T20 gates remain as recorded in [HANDOFF.md](../HANDOFF.md) and [tasks.md](../docs/tasks.md).
