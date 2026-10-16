# GitHub Repository and Member Branch Workflow Handoff

## Scope and authorization

- Date: October 16, 2026, Asia/Manila.
- Responsible member: Jerome (`javecilla`), with Codex assistance.
- Task: GIT-01 in [the backlog](../docs/tasks.md).
- User authorization: connect the private repository, commit/push the prepared setup from `jerome`, publish/integrate main, add Codex co-authorship, and document member branches and owner-managed main updates.
- Application implementation and schema/data changes remain outside this task.

## Repository and workflow

The remote is [javecilla/Campus-Equipment-Borrowing-System](https://github.com/javecilla/Campus-Equipment-Borrowing-System), private, with `main` as the integration/default branch. Git Credential Manager access was verified as `javecilla` with repository administration permission. No credentials were written to the remote URL or shared files.

Assignments in [Project-Members.txt](../docs/Project-Members.txt) are `jerome`, `alex`, `kenneth`, `elly`, `marga`, and `ralph`. The source file's new assignments were supplied by the user and preserved. [DEV.md](../DEV.md#assigned-branches-and-main-integration) is the canonical workflow: own member branch, sync main, task/checks/handoff, push own branch, PR to main, and Jerome's merge. [CONTRIBUTING.md](../CONTRIBUTING.md) and [AGENTS.md](../AGENTS.md) route developers/agents to it. Repository maintenance does not imply sole ownership of the team's work.

The repository was empty when inspected. The initial setup snapshot is created on jerome and used to initialize main; the first baseline has no older main commit to compare against. Assigned member branches are initialized from the shared baseline for future work.

The user's `CODEOWNER` file was corrected to root [CODEOWNERS](../CODEOWNERS), plural and without an extension. Team ownership prose is preserved as comments, and one wildcard rule assigns all six members as reviewers. [CONTRIBUTING.md](../CONTRIBUTING.md#verification-and-review) explains review semantics and access requirements; the file does not give exclusive ownership or override main restrictions.

The collaborator/invitation API check currently lists only `javecilla` and no pending invitations. The other five accounts therefore need write-access invitations and acceptance before they can clone this private repository or function as code owners. No invitations were sent as part of this task.

## Main protection

The GitHub [main-owner-only ruleset](https://github.com/javecilla/Campus-Equipment-Borrowing-System/rules/25213591) was created and read back as active. It targets `refs/heads/main`, restricts creation/update/deletion/non-fast-forward changes, and has only `javecilla` as a User bypass actor. Main integration is reserved for Jerome. Ordinary member branches are assigned by team policy; they do not have individual GitHub write restrictions.

This was verified through the authenticated GitHub API, not by logging in as another teammate or attempting an unauthorized push. The separate connected GitHub app could not see the new private repository; the working Git Credential Manager account was used instead. GitHub CLI is not installed and was not required or installed for this task.

## Publication state

Origin is connected and the local branch is jerome. Initial commit/push and remote branch verification are pending closing checks. The commit will retain the configured human author and include `Co-authored-by: Codex <codex@openai.com>`. Live database credentials remain in ignored .env.local; private user settings are not part of the publication.

## Checks and next actions

- Completed: remote initially empty; user/account/admin access; origin URL; assigned branch names; active ruleset and effective main rules read-back; collaborator/invitation inspection; CODEOWNERS format; 179 relative links across 17 Markdown files; credential scan across 25 shareable text/configuration files; shared JSON/TOML parsing; dated filename checks; all 31 application tasks remain Not started.
- Pending: complete secret/link/staging checks, commit/push, create/synchronize main and assigned remote branches, verify remote heads/default/protection, and update this snapshot/current handoff with actual results.
- Not run: application tests, migrations, CI, or benchmarks; the repository still contains documentation/tooling, not an implemented Django application.

After setup publication, each member follows DEV.md using their own account and branch. Jerome manages collaborator invitations separately and handles main integration. Do not force-push, delete persistent member branches after merging, or commit private environment files. Future handoffs follow the [project-handoff skill](../.agents/skills/project-handoff/SKILL.md) and are indexed in [HANDOFF.md](../HANDOFF.md).
