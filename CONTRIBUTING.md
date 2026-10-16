# Contributing

## A shared school project

The Campus Equipment Borrowing System is a team school project. The members and agreed feature responsibilities are listed in [README.md](README.md) and the original [member assignment file](docs/Project-Members.txt). The repository account holder, access administrator, task coordinator, or most frequent committer must not present the team's work as their individual project. Feature ownership means coordination and accountability, not exclusive ownership of the repository.

Give accurate credit for code, documentation, testing, design, and presentation work. Each member contributes across those areas and follows the course's leadership/individual-evidence requirements. Coordinate shared interfaces with affected members; do not erase attribution or another member's unreviewed work.

Participation follows [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Licensing is defined only by [LICENSE](LICENSE), using MIT and a project-contributors notice. Contributors retain the rights they hold and contribute original work under those terms; no transfer of rights to one member is required by this guide. Course/instructor-supplied requirements and external assets remain subject to their own terms; placing them in this repository does not relicense them. Preserve third-party notices and add only material the team is allowed to redistribute. Academic-integrity and institutional requirements still apply to course submissions; they do not add a noncommercial restriction to MIT.

## Before starting

1. Read [AGENTS.md](AGENTS.md), [PLAN.md](PLAN.md), [HANDOFF.md](HANDOFF.md), and the relevant entry in [docs/tasks.md](docs/tasks.md). Use the plan's handoff gates and verify prerequisite integration into main before dependent work. Claim/coordinate the task with its owner so two contributors do not independently change the same contract.
2. Read [docs/coding-standards.md](docs/coding-standards.md), including its MTV responsibility table, and the feature's requirements/design contracts. Follow [DEV.md](DEV.md) for workstation and private environment/MCP setup.
3. Define the requested outcome and minimum acceptance evidence. Keep the work within the authorized phase; a backlog entry or skill is not permission to begin application implementation.
4. Inspect existing files, working changes, and shared helpers before editing. If Git metadata is available, use non-interactive status/diff commands; otherwise do not claim a branch, commit, or PR exists.

## Making changes

Keep one focused change per task. Use the MTV guide as the canonical code standard; architecture/schema/SRS/HTTP contracts remain authoritative for their respective topics. Do not independently add roles, generated admin pages, integrations, or alternate architecture. Coordinate schema/workflow/URL changes with the affected feature owners and update their canonical contract.

Use your assigned persistent member branch from [Project-Members.txt](docs/Project-Members.txt) and the [Git workflow in DEV.md](DEV.md#assigned-branches-and-main-integration). The private shared remote is `javecilla/Campus-Equipment-Borrowing-System`; Jerome (`javecilla`) manages access and main integration. Members fetch/pull main, develop/push their own branch, and open a PR into main for Jerome to integrate. Do not push to main or another member's branch, delete assigned branches after merge, or rewrite shared history. Follow AGENTS.md for AI commit/push/merge authorization; an agent must not commit just because its change is ready. Prefer an ordinary merge when authorized, unless squash is explicitly requested.

Keep real credentials in ignored private files, not contributions, screenshots, logs, fixtures, review comments, or submission ZIPs. Share `.env.example` and credential-free templates. Report a private-data exposure through a private team/instructor channel rather than reproducing it publicly.

## AI-assisted work

The person submitting an AI-assisted contribution remains responsible for understanding, reviewing, testing, and explaining it. Follow the BulSU AI Policy and current instructor instructions for disclosure and permitted use. Do not fabricate test results, user interviews, meeting records, leadership evidence, or individual contributions.

Agents must read AGENTS.md. For Django design, implementation, or review, use [.agents/skills/django-mtv/SKILL.md](.agents/skills/django-mtv/SKILL.md); an explicit prompt can say `Use $django-mtv to implement T13 within the existing contracts.` This example does not authorize T13 now. Tools that do not discover repository instructions/skills need those files supplied explicitly. Human review checks adherence; skill availability alone cannot guarantee compliant code.

## Verification and review

Use the coding guide's verification table and actual configured commands. The current repository has no application test/lint configuration, so documentation changes need link/consistency/skill checks rather than invented application test runs. When implementation exists, use the appropriate real feature/integration checks and include access/concurrency evidence where required.

A review request or task handover should identify the task, resulting behavior, relevant files, actual verification commands/results, unresolved limitations, and any shared-contract change. Review against the requirements and MTV guide; avoid unrelated rewrites. Have an affected teammate review shared changes when practical. Jerome has been designated to integrate main and manage repository access; this role does not make him the sole author or owner of the team's work.

[CODEOWNERS](CODEOWNERS) assigns all six members as reviewers for every path. Its exact filename is `CODEOWNERS`, with no extension; prose is commented with `#`, and the `*` rule lists all reviewers on one line. These are review assignments, not exclusive ownership, access grants, or permission to merge main. GitHub requires listed accounts to have write access and the private repository to have a plan supporting code owners; collaborator invitations/acceptance are separate. This file does not require six approvals or enable mandatory approval by itself. See [GitHub's CODEOWNERS documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).

At the end of file-changing work or when transferring unfinished work, follow [.agents/skills/project-handoff/SKILL.md](.agents/skills/project-handoff/SKILL.md). Write a developer/AI snapshot in `handoffs/{title-of-work}-{MM-DD-YYYY}.md`, using a lowercase hyphenated title and the current Asia/Manila date. Preserve previous snapshots; use a distinct title if the same title/date is taken. Update the affected backlog status, current state, and dated index in HANDOFF.md after verification, preserving concurrent work. Mark a feature Done only when its acceptance behavior is actually verified. Keep durable technical rules in their canonical documents and link them from snapshots.

## Discussing disagreements

Explain disagreements using the requirement, observable behavior, and tradeoff. Consult affected members for changes to team conventions, attribution, or licensing. Follow the conduct/reporting process when a dispute concerns behavior, and ask the instructor to clarify course requirements or assessment questions. Do not invent an instructor decision or grant yourself authority over another member's grade.
