# T21 seeds and cleanup publication

- Date: October 22, 2026, Asia/Manila.
- Owner: Jerome Avecilla with Codex co-author credit; existing team contributions preserved.
- Scope: user-authorized commit and push of the completed T21 seed, cleanup, tests and documentation on `jerome`. No PR, main integration, new feature or live-data reset.

## Published result

Source **`e3402bf2c10baf7aa2618c8af418bd3f558d4e4c`**, `feat: add T21 demo seeds and scoped cleanup commands`, is committed and pushed to `origin/jerome`. Fetching after the push confirmed exact local HEAD/remote branch equality at that source. Its commit message includes `Co-authored-by: Codex <codex@openai.com>`.

The source contains the nine-account seed, physical-unit top-up, fixed August-October 2026 history, separate borrowing/stock purges, real PostgreSQL integration checks, [DEV command runbook](../DEV.md#demo-command-runbook) and the prior dated work snapshots. Private environment values, database dumps, uploaded media and generated assets are excluded. Source publication does not copy the workstation database or uploaded photos to Git.

This documentation follow-up records publication in [HANDOFF.md](../HANDOFF.md), [task evidence](../docs/tasks.md#verified-task-evidence), [README](../README.md), [Module 20](../docs/manual-test-guide.md#module-20--fictional-demonstration-dataset-t21) and AGENTS. Earlier completed snapshots retain their historical uncommitted state. The receipt commit also carries the requested Codex trailer.

## Verification and limits

- Earlier implementation verification, carried forward unchanged: **336 PostgreSQL tests passed in 101.342s**, with build, configuration/schema, dependency, lint and owned-file formatting checks. Three pre-existing unrelated formatting findings remain in the archived borrower-portal handoff example, portal-equipment test line endings and portal-equipment template attribute wrapping. See the [tooling verification receipt](demo-seed-and-cleanup-command-runbook-10-22-2026.md) for actual execution, rollback/preservation checks and unrun manual work.
- Publication checks: fetched branch was fast-forwardable; full Ruff lint, formatting of all 15 T21 Python files, staged whitespace and private-path exclusion checks passed. The source commit's co-author trailer and remote equality were verified. Final receipt edits receive documentation link/anchor/fence and whitespace checks; no implementation changed and the full suite was not rerun for prose/Git operations.
- `origin/main` remains **`4f285cb517bc41df937feb4e7f16ae7f8f351f26`** at publication verification. T21 is Done on the member branch and **Not integrated**. No PR was opened. T22/T23 still require actual T21 main integration and acceptance execution. T24 restore rehearsal, instructor credential delivery and packaging remain separate.

## Next action

Jerome can review the published source and request a PR/main integration when ready. The current local populated demonstration remains intact; no seed or cleanup command was rerun during publication. This receipt completes the commit/push handoff without changing application behavior.
