# PR #27 T11 conflict resolution and review

- Date: October 18, 2026, Asia/Manila (+08:00).
- Work/owner: Jerome with Codex review; Ralph's T11 source and Ellyssa's T10 source/credit preserved.
- Scope: review [PR #27](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/27), resolve its conflicts against current main, and verify the combined candidate. No commit, push, PR comment or main merge performed.
- Outcome: seven conflicts resolved locally; **181 PostgreSQL tests pass**. T11 remains Done on its member branch and **not integrated into main**.

## Source and integration state

Authenticated GitHub metadata identifies open PR #27, head `ralph` at `7477b2babee66e0101b0e05ff52eb8237175ad37`, base `main` at `3817e7e7aaa0cdbbeab955c7fbad2bb9766d538f`; GitHub reports conflicts before publication. The isolated worktree is `D:/SchoolThings/PythonProject-pr27-review`, detached at Ralph's source with a pending non-fast-forward merge of current main. The primary `jerome` checkout remains unchanged at `a736760`.

Resolved [DEV](../DEV.md), [HANDOFF](../HANDOFF.md), [portal URLs](../accounts/portal_urls.py), [HTTP contract](../docs/api_spec.md), [architecture](../docs/architecture.md), [folder guide](../docs/project-folder-architecture.md) and [backlog](../docs/tasks.md). Both T10's list/detail/photo routes and T11's request-create route remain registered. Shared documents retain main's T09/T10 integration evidence, historical handoffs and Ralph's request form/service/contracts. README/current authorization are aligned with this candidate's actual state.

Ten inspected source files match current main exactly, including the T09 form/regression, T10 views/forms/queries/tests/templates/layout and existing inventory service. Six T11 files match Ralph's source exactly: forms, service, views, submission tests and both new templates. The auto-merged account portal module retains T09 profile editing and Ralph's confirmation section while removing T10's superseded placeholder. No migration, dependency or workflow-service change is introduced by resolution. Original [Ralph handoff](ralph-t11-request-submission-10-18-2026.md) and T10 snapshots are preserved.

## Review result and follow-ups

T11 enforces active BASIC_USER access, bounded/distinct item forms, server-controlled ownership/status/timestamps, campus-date limits and complete validation before persistence. Its service locks/rechecks the borrower, singleton settings and eligible catalog records, then stores both limit snapshots and Pending request/items in one transaction. Submission creates no reservation. The existing tests exercise invalid-third-row rejection, field tampering, duplicate/incomplete/over-limit rows, invalid dates/purpose/counts, archived records, role/method checks and CSRF.

Two non-blocking review follow-ups remain in Ralph's source:

- The request-create page does not highlight the My requests tab: [request view](../borrowing/views.py:27) renders with resolver name `request-create`, while the [portal navigation](../templates/accounts/portal/base.html:16) checks `request-list`. Use an explicit section indicator when completing navigation polish; functional submission is unaffected.
- [RequestForm](../borrowing/forms.py:54) and the [test payload helper](../borrowing/tests/test_request_submission.py:55) introduce default parameters despite the project's explicit-parameter convention. The view already supplies the submission date. This is a style follow-up; no service behavior was changed during resolution.

No acceptance-blocking submission failure was found in this source review and passing coverage. Browser visual/keyboard/mobile behavior was not verified. Request history, detail and cancellation remain T12 scope. T10's existing photo-test storage isolation follow-up is unchanged; its request guidance now reaches a section containing a create link in this candidate.

## Actual verification

| Check | Result |
| --- | --- |
| `python manage.py test --noinput` on the combined candidate | **181 PostgreSQL tests passed in 28.472s**; test database removed |
| Ruff lint / format check | Passed; 184 Python files already formatted |
| djLint on the two T11 templates, two T10 templates and portal base | Five files checked; zero updates |
| Django `check --database default` | Zero issues |
| `makemigrations --check --dry-run --noinput` / `migrate --check` | No changes detected / no unapplied migrations |
| `npm.cmd run build` / `npm.cmd run format:check` | Passed in the isolated worktree |
| `npm.cmd audit` / Python `pip check` | Zero vulnerabilities / no broken requirements |
| Source preservation, module parsing and Git conflicts | Main/T11 source comparisons pass; portal modules parse; zero unmerged index entries |
| Documentation and whitespace | 562 local links across 13 changed Markdown files resolve, including heading anchors; fences and encoding checks pass; staged and unstaged whitespace checks pass |

The primary environment supplied the existing Python tools and a local ignored node_modules junction. Private environment values were copied only to ignored local configuration for checks and removed afterward. Generated review assets/uploads remain ignored. The previously recorded unit-detail formatting issue is outside the targeted template check. No new browser, CI, T14 competing-approval, performance or backup/restore evidence is claimed.

## Next action

The owner must authorize committing and pushing this resolution to `ralph` before GitHub PR #27 can become conflict-free. Follow the ordinary merge workflow; do not force-push or merge main automatically. After the PR is actually merged, record the real main revision and recheck integration before marking Ralph / T12 or Margareth / T13 ready. Kenneth / T16 remains independently ready; T20 retains its other prerequisites.
