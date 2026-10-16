# Team AI implementation prompts

Open this repository in your coding agent, then copy your entire member prompt below. Sending it authorizes implementation of your assigned work under [PLAN.md](../PLAN.md); the agent should begin ready work after inspecting the checkout. Task ownership and acceptance remain in [tasks.md](tasks.md), with branches defined in [Project-Members.txt](Project-Members.txt).

Use the same prompt again after prerequisites merge or to resume unfinished work. The agent reads current evidence each time, so you do not need to maintain a task list inside the prompt. Creating this guide does not start another member's features.

## Copy your prompt

### Alex

```text
I am Alex Enrico Cayanan (@AlexCayanan), assigned branch alex.

Implement my unfinished assigned work from docs/tasks.md in PLAN.md dependency order. Read AGENTS.md, PLAN.md, HANDOFF.md, and docs/team-agent-prompts.md, then follow its Implementation workflow.

Start implementing ready work now and continue with other ready tasks assigned to me. Verify each change and complete the required handoff. Leave changes uncommitted for my review; do not push, open a PR, or merge into main.
```

### Kenneth

```text
I am Kenneth T. Cortez (@corkenneth), assigned branch kenneth.

Implement my unfinished assigned work from docs/tasks.md in PLAN.md dependency order. Read AGENTS.md, PLAN.md, HANDOFF.md, and docs/team-agent-prompts.md, then follow its Implementation workflow.

Start implementing ready work now and continue with other ready tasks assigned to me. Verify each change and complete the required handoff. Leave changes uncommitted for my review; do not push, open a PR, or merge into main.
```

### Ellyssa

```text
I am Ma. Ellyssa Bianca Regodon (@ellieebeann), assigned branch elly.

Implement my unfinished assigned work from docs/tasks.md in PLAN.md dependency order. Read AGENTS.md, PLAN.md, HANDOFF.md, and docs/team-agent-prompts.md, then follow its Implementation workflow.

Start implementing ready work now and continue with other ready tasks assigned to me. Verify each change and complete the required handoff. Leave changes uncommitted for my review; do not push, open a PR, or merge into main.
```

### Ralph

```text
I am Ralph Andre F. Giga (@dreygigz), assigned branch ralph.

Implement my unfinished assigned work from docs/tasks.md in PLAN.md dependency order. Read AGENTS.md, PLAN.md, HANDOFF.md, and docs/team-agent-prompts.md, then follow its Implementation workflow.

Start implementing ready work now and continue with other ready tasks assigned to me. Verify each change and complete the required handoff. Leave changes uncommitted for my review; do not push, open a PR, or merge into main.
```

### Margareth

```text
I am Margareth Raine H. Ignacio (@raifun), assigned branch marga.

Implement my unfinished assigned work from docs/tasks.md in PLAN.md dependency order. Read AGENTS.md, PLAN.md, HANDOFF.md, and docs/team-agent-prompts.md, then follow its Implementation workflow.

Start implementing ready work now and continue with other ready tasks assigned to me. Verify each change and complete the required handoff. Leave changes uncommitted for my review; do not push, open a PR, or merge into main.
```

### Jerome

```text
I am Jerome S. Avecilla (@javecilla), assigned branch jerome.

Implement my unfinished assigned work from docs/tasks.md in PLAN.md dependency order. Read AGENTS.md, PLAN.md, HANDOFF.md, and docs/team-agent-prompts.md, then follow its Implementation workflow.

Start implementing ready work now and continue with other ready tasks assigned to me. Verify each change and complete the required handoff. Leave changes uncommitted for my review; do not push, open a PR, or merge into main.
```

## Implementation workflow

These instructions apply when a member sends an implementation prompt. Follow the linked canonical rules rather than treating examples or planned files as delivered features.

1. **Establish the member and checkout.** Confirm the prompt's identity/branch against the source assignments, inspect Git status, and preserve existing work. Follow [DEV.md's synchronization workflow](../DEV.md#assigned-branches-and-main-integration), fetching origin and switching to the assigned branch before edits. This prompt permits a safe fast-forward update; if synchronization needs a merge commit or unresolved conflicts, report the required integration action before dependent implementation. Do not discard/stash someone else's changes or create commits under this prompt.
2. **Select actual assigned work.** Read [PLAN.md's selection rules](../PLAN.md#select-the-next-task-in-a-new-session), the member's unfinished backlog entries, current handoff, and linked work evidence. Resume assigned In progress work first, then select ready assigned tasks in dependency order. For shared tasks, work only the member's contribution and available evidence; do not claim another owner's portion or invent interviews, feedback, measurements, or presentation participation.
3. **Verify prerequisites on main.** Inspect fetched main history, the recorded merge/commit evidence, and actual prerequisite interfaces. Apply the [integration gate](../PLAN.md#complete-work-and-hand-it-to-the-next-member) to every selected task, including dependencies implemented earlier in this session. Local Done work or an open PR does not satisfy it. Keep blocked tasks Not started, identify the missing task/owner/integration, and continue any independent ready assigned work. Jerome's earlier T01–T03 exception does not grant a new local batch exception.
4. **Read the feature contracts and skills.** Inspect existing code, relevant PRD/SRS, architecture, database, HTTP contracts, [folder guide](project-folder-architecture.md), and [coding standards](coding-standards.md). Read and follow the [Django MTV skill](../.agents/skills/django-mtv/SKILL.md) and [project-handoff skill](../.agents/skills/project-handoff/SKILL.md) directly even if the agent does not discover them automatically.
5. **Implement and verify.** State the selected task and acceptance scope briefly, mark it In progress, then implement the required behavior. Use [DEV.md](../DEV.md) for the local environment, migrations, and [configured checks](../DEV.md#before-handing-over-work). Run relevant real feature checks and required project checks; fix failures within the authorized scope. Continue through routine implementation choices without repeatedly asking whether to proceed. Missing credentials, tools, or prerequisite services require a specific blocker report; never invent successful checks or bypass a missing feature with placeholders.
6. **Complete the handoff.** For file-changing work, follow the handoff skill after verification, preserving other members' entries and historical snapshots. Record only accepted work as Done, identify local changes as uncommitted and Not integrated, and update affected backlog evidence and HANDOFF.md. Keep partially completed work In progress with its remaining acceptance gaps. Continue only if another assigned task passes the same prerequisite gate.
7. **Return a reviewable result.** Summarize completed/partial task IDs, changed paths, actual check results and unrun checks, the dated handoff, branch/uncommitted state, and each remaining blocker with its next owner/action. Stop when no further assigned task is ready or a blocker prevents progress. Leave commit, push, PR, main integration, and teammate notifications to separately authorized actions.

For example, Alex can implement T04 after verifying integrated T02. T05 still waits for T04 to be accepted and integrated into main, even if T04 passes locally. After Jerome merges it, Alex sends the same prompt again to continue. Read current readiness from [HANDOFF.md](../HANDOFF.md), rather than assuming this example describes every member's present state.
