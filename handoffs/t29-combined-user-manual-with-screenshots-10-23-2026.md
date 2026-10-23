# T29 combined user manual with screenshots

Date: October 23, 2026, Asia/Manila. Owner: Jerome's explicit request; Codex authoring and source/screenshot review.
Original T29 responsibilities remain: Ellyssa/Ralph for borrower guidance, Margareth/Kenneth for administrator guidance
and Jerome/Alex for technical guidance. The requested combined manual is documentation scope; application behavior,
technical maintenance implementation and clean-machine packaging are separate.

## Baseline and outcome

Fresh fetch verified user-merged PR #69 at `0396bca049474b861a05609b67e45f0573efe82f`. Source/receipt
`38d9e4136a92f9f0c253c5cbea8c6690982c34f6` is an ancestor and has exactly the merge tree
`b0f2eee21a21a098c76cc4ef82bb91439242d8a6`. Local `jerome` was fast-forwarded before editing. T22 source
`a7ce0a25c598b929852f4498ab40dd5b2d5e6f6c` and T24 source `49d55382a665f4295f11acab2092fd9170398708` are verified
main ancestors, satisfying T29's integrated prerequisites.

Created one [basic-user/admin manual](../docs/user-manual-guides.md) with 19 representative, existing screenshots:

- Shared sign-in/navigation/logout, borrower registration, Home, equipment search, request submission, tracking/returns,
  pre-issue cancellation and profile changes.
- Administrator dashboard and chart meanings, basic-user activation, categories/catalog/photos/archive/restore,
  physical units, request decisions, due-date revision, release/slip, per-unit/damaged returns, equipment maintenance,
  reports/CSV, settings and audit history.
- Request/loan/unit status reference, common problems and support routes. Screenshot records/dates are explicitly
  illustrative, drawn from separate October 22 captures rather than one purported sequential walkthrough.

Steps use actual implemented labels, forms and eligibility restrictions. The manual is written for users; the existing
[manual testing guide](../docs/manual-test-guide.md) remains the test-case/execution record. The
[full gallery](../docs/system-screenshots.md) supplies extra screens without duplicating every image in this manual.
Screenshot bytes are unchanged and no new screenshot capture was performed.

Updated README/DEV/SUBMISSION, the T29 backlog/current phase and current handoff/index to link the manual and mark T29
**In progress**. Reconciled the already-published T27 source/receipt integration through PR #69 in the affected current
records; its task remains In progress pending the previously recorded actual member review. Historical snapshots remain
unchanged. All new work is **uncommitted and Not integrated**.

## Source and screenshot review

Reviewed the course/backlog acceptance, SRS workflow/rules and HTTP contracts against actual account/inventory/borrowing/
operations forms, URL modules, templates and workflow services. In particular, checked registration's sign-in redirect,
profile allowlists, fixed one-to-three distinct item rows, snapshotted due/quantity limits, mandatory decision reasons,
complete reservation/release, return condition selection and damaged-maintenance linkage, archive/restore behavior,
locked unit identity, report issue-date bounds, CSV filtering, settings scope and read-only audit history.

Visually inspected all 19 images embedded in the manual: `01`, `65`, `37`, `38`, `40`, `43c`, `67`, `45`, `02`, `35`,
`53`, `57`, `14`, `19`, `21`, `60`, `29`, `33` and `32` under `screenshots/`. Compared the key field/button labels with
the current templates/forms. Screenshots are prior capture evidence, not proof that this edition's complete user journey
was freshly executed. No passwords or current-record examples were invented; dates/limits are described relative to
the current form rather than requiring the old capture values.

Checked changed Markdown relative targets and heading anchors, image presence/integrity, table structure, fenced blocks,
conflict markers and changed-line whitespace. No application source, dependency or test files changed; runtime tests,
builds, browser reruns and management commands were not run. No local/shared database/media operation was performed,
so no database target was opened or mutated for authoring.

All **1,126 relative targets and 266 heading anchors across seven Markdown files passed**. All 19 embedded PNGs passed
integrity checks and byte-for-byte comparison with the baseline; their descriptive alternative text and both new
documents' table structures passed. The canonical T29 row is In progress and the diff contains documentation only.

## Review record and remaining T29 work

| Scope | Reviewer/owner | Current result | Next evidence |
| --- | --- | --- | --- |
| Source and embedded-image consistency | Codex authoring/review | Reviewed against implemented source and existing screenshots | Document/link checks recorded above; resolve any reader-reported mismatch |
| Basic-user manual walkthrough | Ellyssa/Ralph | Not run for this edition | Follow registration/sign-in, browse, submit, track/cancel, profile and logout; record actual date/environment, result and corrections |
| Administrator manual walkthrough | Margareth/Kenneth | Not run for this edition | Follow account/catalog/unit operations and the full approval-release-partial/damaged-return-maintenance-report journey on an appropriately isolated demonstration setup; record actual outcomes |
| Technical setup/application maintenance | Jerome/Alex | Existing README/DEV/T24 evidence retained; complete T29 delivery pending | Finish verified configuration/maintenance guidance and fresh local setup, including complete fictional catalog/maintenance data replay |

**The requested manual is authored; full T29 remains In progress.** The remaining reader checks are not a claim of a
new course-mandated participant count or sign-off rule: T29 already requires verified guides. Use the repository's
database-safety rules for any later walkthrough; this authoring request did not run workflows or authorize shared seeds,
resets or migrations. T30 still needs its own prerequisite acceptance and clean-machine ZIP verification.

Next: Jerome reviews this local documentation. Assigned role-guide owners verify the relevant sections and report
actual corrections/results; Jerome/Alex continue the remaining technical scope when authorized. No commit, push, PR,
main merge, external message, new participant result or workflow execution was performed by this task.
