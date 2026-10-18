# Required manual testing guide in feature skills

- Date: October 18, 2026, Asia/Manila (+08:00).
- Work/owner: Jerome with Codex skill-creator assistance.
- Request: require a manual testing guide whenever a new feature is implemented, aligned with actual flow and database records.
- Outcome: the existing Django implementation and handoff skills now require a manual-guide section before feature handoff completion. This is a project instruction workflow, not a background generator or installed enforcement hook.

## Canonical requirement and routing

The [coding standards](../docs/coding-standards.md#manual-testing-guide-for-feature-delivery) own the detailed rule: maintain the shared [manual guide](../docs/manual-test-guide.md), create it if absent, and refresh affected cases when documented behavior changes. New cases describe actual routes/roles/preconditions, concrete Field / Value tables, relevant success/error/boundary/authorization/rollback behavior, and a verification path that already exists. Local test data/settings are inspected read-only; examples identify the revision and Asia/Manila snapshot date, with recalculation instructions for changing dates/limits. Unavailable data and unrun checks are explicit; no invented records, private identities or fabricated manual passes are permitted.

The [Django skill](../.agents/skills/django-mtv/SKILL.md) routes feature verification through that requirement. The [handoff skill](../.agents/skills/project-handoff/SKILL.md) checks it at completion and requires a guide link plus actual execution status/data-check evidence or remaining prerequisites. [AGENTS](../AGENTS.md) and [DEV](../DEV.md#before-handing-over-work) point contributors to the same canonical rule. The [DOC-02 evidence](../docs/tasks.md#documentation-baseline) and [current handoff](../HANDOFF.md) record this local workflow extension.

Existing skill names and implicit discovery remain unchanged; no new skill directories, scripts, packages or hooks were installed. Documentation-only work and read-only questions do not require unrelated manual cases. The requirement does not authorize application implementation, creating test records, executing mutating browser scenarios or publication beyond the user's existing scope.

## Verification and remaining work

The bundled skill-creator `quick_validate.py` passes for both modified skills using the existing project Python with UTF-8 mode. Fresh documentation checks pass: **613 local links across 17 changed Markdown files**, including heading anchors, balanced fences and encoding; metadata consistency and `git diff --check` also pass. The existing T11 examples remain the concrete guide format; no guide cases or database records were changed by this skill task. No application test/build run or independent-agent behavioral evaluation is claimed for this focused instruction update.

Earlier documentation work and the concurrent request-template spacing edit remain preserved. Changes are uncommitted on `jerome`; T01-T11 integration and T12/T13/T16 readiness are unchanged. Future feature owners must load the project instructions/skills and include the guide update in their authorized implementation handoff. Other agents that do not discover repository skills must be given these instructions explicitly.
