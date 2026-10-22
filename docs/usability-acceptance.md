# Usability acceptance sessions (T23)

## Current outcome and ownership

T23's preparation, R01 report and startup asset enhancement E01 are integrated through user-merged PR #56 at main `17873b6` (source `cc00a93`), October 22, 2026, 13:26:59 Asia/Manila. Fresh review verifies exact source/merge-tree equality and preservation of T20/T21/T22 and HOST-01. Ralph owns the delivery with Codex assistance; Ralph/Ellyssa remain usability coordinators. See [integration review](../handoffs/t23-main-integration-review-and-t24-readiness-10-22-2026.md).

**Implementation integrated; acceptance evidence follow-up In progress.** R01 is a limited user report that both roles work. Ralph's [delivery snapshot](../handoffs/t23-acceptance-and-startup-asset-feedback-enhancement-10-22-2026.md) also reports a real missing-build symptom (R02/F02) and E01 implementation, but the merged canonical record omitted that evidence and its referenced tests. This review supplies the missing technical checks and attributed record below. It does not reconstruct an unavailable original traceback or invent participant metadata. Ralph's reported local Done outcome remains in the historical snapshot; full participant-session acceptance and the human recheck cannot be independently substantiated from this checkout.

T20 source `b43fb99`, T21 source `e3402bf`, and T22 source `a7ce0a2`/publication `7d0043d` are main ancestors. T23's entry gate and T24's independent T22 gate are satisfied. T24 measurements/restore remain Not started and can proceed alongside participant-evidence follow-up.

## Local setup checked before sessions

Read-only PostgreSQL inspection on October 22, 2026, 10:38 Asia/Manila found the following. These are Ralph's historical local records from preparation, not current shared Neon facts or this review workstation's records. Ordinary startup now selects shared Neon; follow [DEV setup](../DEV.md#shared-neon-database-and-photos) and recheck the chosen session dataset read-only.

| Input / prerequisite | Verified local state |
| --- | --- |
| Fictional accounts | Active ADMIN `auth_demo_admin` and BASIC_USER `auth_demo_user`; obtain passwords privately |
| Dataset | 5 requests, 2 loans, 4 units |
| Current limits | 7 maximum loan days; 3 units per item |
| Active catalog under active category Camera | Item 2, Nokia: 1 available; Sony and DJI: 0 available |
| Borrower history | Loan 1: due October 21, no outstanding units, not overdue; loan 2: due October 21, 2 outstanding units, overdue on October 22 |
| Cancellation exercise | No Pending/Approved request owned by `auth_demo_user`; a new participant request is needed in the writable session dataset |
| T21 roster/history | `andrea.mendoza`, `miguel.santos` and `sofia.reyes` are absent locally; do not use Module 20's IDs/accounts as local facts |
| Runtime checks | Django database check and discovery of app CSS, dashboard JS and navigation JS passed; server startup/HTTP results are in the dated preparation handoff |

Recheck ownership, stock, dates and limits before each session. Nokia's single available unit supports a one-unit request/release exercise, not a two-unit partial-return exercise. Existing loan 2 can be inspected read-only; changing it would alter existing history. Use a disposable session copy for write exercises, following [DEV's database/backup runbook](../DEV.md#demo-command-runbook), and label the chosen database in private session notes. Do not run cleanup, seed commands or reset passwords merely to author this guide. No database rows or media were changed during preparation.

## Facilitation

Cover both BASIC_USER and ADMIN perspectives. State whether a participant is an intended user or a classmate acting as a proxy; report the limits of proxy feedback. The course/backlog specifies no participant count or satisfaction threshold, so record the actual sample without inventing either.

1. Explain the school-project purpose and intended use of anonymized notes using the existing collection guidance. Let participants decline. Record permission before retaining notes or recordings; avoid passwords, real campus identities and private histories in Git.
2. Record the actual tested revision, session date/time zone, device, browser, role and facilitator. Use anonymous participant codes; do not enter a row before a real session exists.
3. Give the participant a task goal from Module 22 and let them try before supplying navigation instructions. Record assistance explicitly. Do not lead with a proposed improvement or assume hesitation is a defect.
4. Ask what was clear/confusing, what they expected, and what they would change. Separate their statement, the observed behavior and the facilitator's interpretation. Optional timing is evidence only if actually measured.
5. Confirm the anonymized summary with the participant when practical, then link each actionable finding to an SRS requirement and an existing flow. Actual task failure can be useful feedback; report it honestly.

## Session register

### R01: User-reported functional confirmation

The current user reported the following after the borrower/admin walkthrough was provided. This record preserves the scope actually supplied; it does not turn the brief report into a detailed observed session.

| Field | Actual record |
| --- | --- |
| Report ID / receipt date and time zone | R01; October 22, 2026, 11:12 Asia/Manila. Actual test date/time not supplied |
| Participant code / role / intended user or proxy | P01, current user reporting both BASIC_USER and ADMIN flows; intended-user/proxy classification not supplied |
| Facilitator / observer / device / browser | Walkthrough supplied by Codex; independent observation, device/browser and assistance level not supplied |
| Tested branch and exact revision / dataset | Repository was on `ralph` at `f9811ea` when feedback was received; actual tested revision/dataset not specified |
| Permission / retained material | User supplied this nonidentifying outcome while requesting T23 completion; no recording or identifying participant material retained |
| Tasks attempted and result | Borrower flow: reported working. Administrator flow: reported working. Individual B1-B5/A1-A5 outcomes and independence/assistance not specified |
| Participant feedback, verbatim | "BOTH OF THEM ARE WORKING" |
| Satisfaction/ease response | No rating or ease assessment supplied |
| Source | User's T23 task conversation; only the short anonymized outcome retained here |
| Remaining uncertainty | R01 supplies no specific issue or improvement. R02/E01 below comes from the separate delivery record; individual task results and human recheck remain unavailable |

### R02: Reported missing-build failure

Ralph's October 22 [delivery snapshot](../handoffs/t23-acceptance-and-startup-asset-feedback-enhancement-10-22-2026.md#actual-feedback-and-scope) attributes an earlier `/manage/` template traceback to a real user report: the compiled dashboard charts bundle was missing. This is an attributed delivery record, not a new participant observation or a retained original traceback. The original report time, tested revision, device/browser and exact exception text are unavailable in the merged files. No additional participant identity, quotation or rating is inferred.

Fresh technical verification reproduces that failure condition using a temporary copy of the real build with `dashboard-charts.js` removed. Ordinary CLI startup refuses to serve and reports `operations.E001`, the missing path and the build command. The integrated system check and restoration checks pass without changing project assets or shared records. Post-enhancement human recheck: Not run by this review; none is retained in the delivery.

## Findings and resolution register

| Finding ID | Session/task source | Observation and participant feedback | Requirement / severity / rationale | Owner / disposition | Change and verification | Participant recheck |
| --- | --- | --- | --- | --- | --- | --- |
| F01 | R01 / both role flows, individual tasks unspecified | User reports both roles working; no difficulty or requested change stated | Positive functional feedback; no defect severity assigned | Ralph/Ellyssa: retain limited result | No change attributed to this positive report | Task-level recheck unavailable |
| F02 | R02 / Ralph's delivery record | Missing dashboard charts bundle reportedly failed at `/manage/` rendering | A7, NFR-07/NFR-08; startup configuration failure, no numerical severity invented | Ralph: E01 implemented and integrated; coordinators retain source/session evidence when available | Fresh real-file checks verify missing-build errors, recovery and CLI startup rejection | Not run; no human recheck supplied |

Use [SRS U1-U4 and NFR-04](SRS.md#functional-requirements) and the affected administrator requirements. Explain priorities with the observed impact, without manufacturing numerical scores. For deferred requests, record the reason and whether they conflict with scope; do not silently discard feedback.

## Feedback-driven enhancement

**E01 implemented and integrated:** Django's registered staticfiles check reports absent required CSS/JavaScript bundles before ordinary `runserver` serves requests. The repair remains an explicit `npm ci`, then `npm run build`; Django does not automatically build assets. See [DEV's preflight](../DEV.md#frontend-preview).

| Required evidence | Actual record |
| --- | --- |
| Source motivating the change | R02/F02, attributed to Ralph's delivery; original traceback unavailable here |
| Before / after | Missing dashboard bundle failed at template rendering; ordinary startup now fails with a named missing-file/build instruction |
| Requirement / owner | A7, NFR-07/NFR-08; Ralph with Codex assistance; no role, route, schema or workflow change |
| Source / revision | `operations/apps.py`, `operations/checks.py`; source `cc00a93`, PR #56 merge `17873b6` |
| Fresh verification | `operations/tests/test_assets.py` now covers registered checks using real build copies, missing build and recovery. Ordinary CLI missing-chart startup independently rejects with `operations.E001`. Full results are in the integration review |
| Earlier browser verification | Ralph reports Edge/Chromium borrower/admin flows at four widths in disposable databases; see his delivery snapshot. Not independently rerun here |
| Participant recheck / limits | Not run. One brief both-role functional report; original missing-build report and session metadata unavailable |
| Integration | Fresh fetched main equals local `jerome` at `17873b6`; exact source/merge tree verified before review edits |

The check detects absent entry files, not stale contents or every generated chunk. WSGI/ASGI hosts that skip checks must run `manage.py check --tag staticfiles` separately. Automated checks establish the enhancement's technical behavior, not a representative usability sample.

## Completion gate and next action

T23 remains In progress for acceptance-evidence follow-up: Ralph/Ellyssa should reconcile the reported completion with the retained session/source record and seek a participant recheck where practical. Keep unspecified task outcomes, environment and assistance explicit; no extra participants or satisfaction scores are invented. E01 is integrated and technically verified, so the outstanding work is evidence/participant follow-up rather than another enhancement.

**Next action:** Jerome may start T24 because its sole prerequisite is integrated T22. Ralph/Ellyssa continue the T23 evidence follow-up in parallel. T26 research and T25 diagrams remain separate; diagrams still need T23/T24 completion and Jerome's go signal.
