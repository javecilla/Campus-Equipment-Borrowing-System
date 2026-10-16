# Jerome foundation publication

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time: October 16, 2026, Asia/Manila (UTC+08:00).
- Scope: publish accepted T01–T03, DOC-05, team setup guides, local font assets, and supplied setup screenshot from `jerome` through a PR into `main`.
- Authorization: commit all completed changes, push `jerome`, and open the PR, with `Co-authored-by: Codex <codex@openai.com>`. No merge is authorized.
- Publication state: preparation verified; commit/push/PR identity is finalized below after the operations succeed. **Not integrated**.

## Review and verification

- Reviewed schema, configuration, shared locks, audit/settings/validation functions, migrations, documentation diff, and asset scope. Earlier completed handoffs are preserved.
- Refetched origin before publication; HEAD, origin/jerome, and origin/main matched baseline `5b0d630`. Working changes are the authorized foundation/assets/documentation batch.
- `check --database default`, `makemigrations --check --dry-run --noinput`, and `migrate --check` pass.
- `manage.py test --noinput`: all **23** tests pass on real PostgreSQL for this publication run.
- `ruff check .`, `ruff format --check .`, and `python -m pip check` pass.
- Private environment, virtual environment, caches, and generated static output remain ignored. Shareable credential scan, local links/anchors, source preservation, and staged whitespace are checked before committing.
- All 383 local links/anchors across 28 Markdown files resolve; the credential scan passes across 178 shareable paths. The staged whitespace check found one upstream trailing space in each font OFL notice; only those two spaces were removed, preserving the complete license text and attribution.
- The authenticated Git account is `javecilla`; the private repository permits pushes. No existing open PR from `jerome` into `main` was found. The connected GitHub app could not access this private repository, so the authenticated Git credential helper and GitHub REST API are used without printing or storing credentials.
- Historical checks for the fresh migration, local HTTP bootstrap, and all font responses remain in the [foundation](jerome-django-foundation-10-16-2026.md) and [setup/assets](team-dev-guide-and-local-fonts-10-16-2026.md) handoffs. This publication does not claim a clean-machine demonstration, product UI, T14 competing approvals, performance results, backup/restore, or CI coverage.

## Next action

Open and verify the authorized PR, then update this handoff and canonical task/current-state records with its actual commit/link. Jerome reviews it for main integration. Alex's T04 remains blocked until T02 is integrated; this publication does not complete the merge gate.
