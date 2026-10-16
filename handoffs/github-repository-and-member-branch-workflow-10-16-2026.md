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

Initial commit [04ecb37](https://github.com/javecilla/Campus-Equipment-Borrowing-System/commit/04ecb37e3319ee38897991ee0d6811d81fe1bba5) was created on `jerome` and pushed atomically to `jerome`, `main`, `alex`, `kenneth`, `elly`, `marga`, and `ralph`. Git and GitHub REST both verified all seven heads at that initial snapshot. GitHub confirms private visibility and `main` as the protected default branch; Git reported the expected owner bypass for initial main creation. Local jerome/main upstreams point to their corresponding origin branches. No older history was replaced, and no PR was needed for the empty repository bootstrap.

The commit preserves the configured human author and includes `Co-authored-by: Codex <codex@openai.com>`. All 27 intended shared files were staged and scanned, including the DOCX archive; supplied secrets were absent. Live database credentials remain in ignored .env.local, absent from the commit. Private user settings were not published. This closing handoff records verification after that initial push; its final documentation update also belongs on jerome before main integration.

GitHub's CODEOWNERS errors endpoint parsed the wildcard rule and returned exactly five `Unknown owner` errors, one for each teammate lacking write access. This is an unresolved access prerequisite, not a successful six-reviewer activation. Only `javecilla` is currently recognized. Do not claim invitations, teammate access, six mandatory approvals, or an unauthorized-push test occurred.

## Checks and next actions

- Completed: remote initially empty; user/account/admin access; origin URL; assigned branch names; active ruleset and effective main rules read-back; collaborator/invitation inspection; CODEOWNERS format; 179 relative links across 17 Markdown files; credential scan across 25 shareable text/configuration files; shared JSON/TOML parsing; dated filename checks; all 31 application tasks remain Not started.
- Completed publication checks: staged secret scan and authored-file whitespace checks; initial commit with co-author trailer; atomic push of all seven branch refs; Git/REST head verification; default main, private visibility, protected status, effective main rules; CODEOWNERS errors inspection. All application work remains Not started.
- Remaining access action: Jerome invites the five teammates with write access; they accept; recheck CODEOWNERS before relying on automatic team review requests. Invitations and teammate logins were not performed in this task.
- Not run: application tests, migrations, CI, or benchmarks; the repository still contains documentation/tooling, not an implemented Django application.

After setup publication, each member follows DEV.md using their own account and branch. Jerome manages collaborator invitations separately and handles main integration. Do not force-push, delete persistent member branches after merging, or commit private environment files. Future handoffs follow the [project-handoff skill](../.agents/skills/project-handoff/SKILL.md) and are indexed in [HANDOFF.md](../HANDOFF.md).
