# T27 Professional Judgment, Ethics, Privacy, and Reuse Evidence

## Work and owner

- **Task:** T27 professional-judgment evidence continuation
- **Owner:** Everyone; Alex Enrico Cayanan coordinates security/privacy, with Jerome coordinating delivery
- **Assistance:** Codex research and documentation; Ralph Andre F. Giga's earlier technical contribution remains separately attributed
- **Branch/base:** `alex` at `1ab0f07cd79fc79b792c8520e5dc6113fcbf7d1d`, aligned with the latest fetched `main` before this work
- **Publication state at handoff time:** Prepared locally for one-commit publication from `alex`; no push, pull request,
  or merge had yet been performed

## Date and time zone

- October 23, 2026, 02:29 Asia/Manila (UTC+08:00)

## Current outcome

- Added the canonical [T27 professional-judgment record](../docs/professional-judgment-and-ethics.md).
- Recorded reviewed primary sources for Philippine/BulSU privacy governance, security, privacy impact assessment,
  cybercrime, intellectual property, disability/accessibility, public records, professional ethics, AI/privacy, and
  Codex/OpenAI service controls. Applicability and non-certification boundaries are explicit.
- Mapped stakeholders, duties, accountable decisions, actual personal-data/record categories, existing technical
  safeguards, residual risks, and required institutional actions.
- Set the interim safety decision to fictional operational data only. No lawful basis, BulSU/DPO approval, privacy
  notice, PIA approval, data-sharing approval, or retention/deletion schedule is inferred.
- Recorded WCAG 2.2 Level AA as an evaluation target rather than a conformance claim and separated demonstrated UI
  evidence from missing screen-reader/disability-user coverage.
- Recorded the unresolved provenance of the default avatars/equipment artwork and the required rights/content review for
  uploaded/submission photos.
- Recorded that the product has no AI feature, preserved existing Codex/reuse disclosures, prohibited secrets/real
  personal data in AI use, and left the actual BulSU AI Policy/instructor instructions as a completion blocker.
- Updated README, DEV, SUBMISSION, the T27 backlog evidence row, and the current HANDOFF so every delivery surface points
  to the canonical record and keeps T27 **In progress**.

## Relevant files

- [Canonical T27 record](../docs/professional-judgment-and-ethics.md)
- [T27 consumer handoff](../DEV.md#t27-readiness-and-consumer-handoff)
- [Submission evidence map and package checklist](../SUBMISSION.md#part-5-and-part-6-evidence-readiness)
- [README Part 6 readiness](../README.md#part-6-professional-evidence-and-delivery)
- [T27 backlog evidence](../docs/tasks.md#verified-task-evidence)
- [Current project handoff](../HANDOFF.md)
- [Ralph's preserved technical contribution](ralph-t17-per-unit-returns-and-overdue-10-20-2026.md#ralphs-t27-technical-contribution)

## Checks and actual results

- `git diff --check` passed for the tracked Markdown changes; only existing Git LF-to-CRLF notices were printed.
- A read-only PowerShell link scan verified **1,024 relative Markdown link targets** across all seven changed Markdown
  files, including this dated handoff and the current HANDOFF index.
- Six explicitly referenced heading anchors were verified: the T27 AI/reuse and completion-gate sections, DEV's T27
  handoff, the supplied-asset inventory, the course-evidence backlog section, and README Part 6.
- The canonical record contains **17 HTTPS source links** and the required privacy, campus, accessibility, professional
  code, IP, conflict/public-welfare, retention, and AI/reuse coverage terms.
- Explicit T27 `In progress` assertions were found in the canonical record and current delivery documents; no completion
  status was assigned.
- The canonical record has no trailing whitespace.
- An informational `npm.cmd exec -- prettier --check` probe reported formatting differences in all six Markdown files
  passed to it. The repository's configured `npm run format:check` excludes Markdown, so no broad Markdown reflow was
  applied and this was not treated as a configured project gate.
- Application tests, builds, database checks, migrations, and browser checks were not run because this change is
  documentation-only and does not alter runtime behavior. No local or shared database/media operation was performed.

## Unresolved issues and decisions

1. Obtain the actual current BulSU AI Policy and instructor permitted-use/disclosure instructions; record title,
   version/date, source, required disclosure, and prohibited uses. The reviewed official public pages did not supply the
   required policy text, and absence from that review is not evidence that no policy exists.
2. Identify the accountable BulSU process/system owner, DPO/privacy contact, and records owner for any proposed real-data
   use.
3. Obtain an approved purpose/lawful basis, privacy notice, PIA outcome, access review, processor/hosting/data-sharing
   decision, incident path, and data-subject request process.
4. Approve a record-by-record retention, archive, deletion/anonymization, backup/export, and secure-disposal schedule;
   the current deactivation/history design is not an approved retention rule.
5. Replace or document source/license/permission for the default avatars and equipment artwork, then verify every
   uploaded/submitted photograph's rights and absence of unnecessary personal/confidential content.
6. Complete the final accessibility review and record the limits without an unsupported WCAG conformance claim.
7. Have all six members review the final record, add any missing reuse/AI assistance, and prepare to defend their own
   decisions, risks, safeguards, evidence, and limitations.

## Next action

Alex coordinates collection of the missing policy and institutional privacy/records inputs. Jerome coordinates delivery
and final package decisions. Each member reviews the [completion gate](../docs/professional-judgment-and-ethics.md#completion-gate-and-member-review), supplies their asset/reuse/AI and module-specific evidence, and records only reviews
that actually occur. Keep operational data fictional until the real-data gate is approved; do not mark T27 Done on the
current draft alone.
