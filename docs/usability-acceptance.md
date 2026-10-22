# Usability acceptance sessions (T23)

## Current outcome and ownership

Preparation is committed and pushed on `origin/ralph` as `5d5ca49`, with Codex co-author credit; see [publication receipt](../handoffs/ralph-t23-preparation-publication-10-22-2026.md). It is not integrated into main, and publication does not complete the participant acceptance work below.

**In progress: session preparation only. No participant sessions or findings are recorded, and no feedback-driven enhancement has been selected or implemented.** Ralph and Ellyssa coordinate; all members can help facilitate, observe and verify. This is the canonical T23 session/results and improvement record. Use [Module 22](manual-test-guide.md#module-22--participant-usability-sessions-t23) for the executable walkthrough and [the T26 collection guide](user-needs-evidence-guide.md#collecting-feedback) for interview/consent guidance; link findings between topics rather than copying source notes.

Baseline checked October 22, 2026: `ralph` was fast-forwarded to fetched main `6e6f594`. T20 source `b43fb99` and T21 source `e3402bf` are main ancestors, satisfying T23's entry gate. T22 source `a7ce0a2` and publication `7d0043d` are also included through PR #54; its merge tree exactly equals the publication tree. The earlier 339-test result belongs to that delivery; no acceptance suite or participant session was rerun for this preparation.

## Local setup checked before sessions

Read-only PostgreSQL inspection on October 22, 2026, 10:38 Asia/Manila found the following. These are this workstation's records, not Jerome's separate demonstration database.

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

**No sessions recorded.** Copy this blank record for each actual session. Pending fields are not attendance, consent or execution evidence.

| Field | Actual record |
| --- | --- |
| Session ID / date and Asia/Manila time | Pending |
| Participant code / role / intended user or proxy | Pending |
| Facilitator / observer / device / browser | Pending |
| Tested branch and exact revision / dataset or private environment reference | Pending |
| Consent to anonymized notes / permitted use and recording limits | Pending |
| Tasks attempted and result per task: independent, assisted, unsuccessful or not attempted | Pending |
| What actually happened; assistance given | Pending |
| Participant feedback in their words or an explicitly labeled paraphrase | Pending |
| Satisfaction/ease response, if asked; no invented rating | Pending |
| Anonymized evidence reference and access restrictions | Pending |
| Participant confirmation or remaining uncertainty | Pending |

## Findings and resolution register

**No findings recorded.** Add entries only from an actual session, with enough context to reproduce the observation. Keep bugs separate from preferences and setup limitations; absence of data is not automatically a UI failure.

| Finding ID | Session/task source | Observation and participant feedback | Requirement / severity / rationale | Owner / disposition | Change and verification | Participant recheck |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | No actual source yet | Pending | Pending | Pending | Not run | Not run |

Use [SRS U1-U4 and NFR-04](SRS.md#functional-requirements) and the affected administrator requirements. Explain priorities with the observed impact, without manufacturing numerical scores. For deferred requests, record the reason and whether they conflict with scope; do not silently discard feedback.

## Feedback-driven enhancement

**Not selected.** T23 requires at least one improvement based on actual feedback, followed by implementation and verification. Automated tests, an agent's UI review and the existence of this packet cannot substitute for that source feedback.

| Required evidence | Actual record |
| --- | --- |
| Real session and finding ID motivating the change | Pending |
| Before behavior / participant goal / smallest proposed change | Pending |
| Requirement and scope check / responsible owner | Pending |
| Source/template/query/service paths and local revision | Pending |
| Relevant regression checks with actual commands/results | Not run |
| Browser/keyboard/compact checks relevant to the change | Not run |
| Participant recheck and outstanding concern | Not run |
| Review/publication/main integration references, when they exist | Not published or integrated |

Implement only after recording the source observation and agreeing the smallest change within the existing two-role, native-form workflow contracts. Follow the Django MTV/Campus UI skills, update the affected manual case, and retain any unresolved issue. A preference for payments, extra roles or external integrations does not expand project scope.

## Completion gate and next action

T23 stays In progress until actual sessions cover both role perspectives, their findings/dispositions are recorded, at least one feedback-driven enhancement is implemented and verified, and the recorded feedback is rechecked with a participant where practical. Link the final evidence and handoff from the backlog; distinguish member-branch delivery from main integration. T26 technology/persona evidence, T24 performance/restore and T25 diagram work remain separate.

**Next action:** Ralph/Ellyssa facilitate the Module 22 sessions and fill the session register. If feedback already exists, supply its anonymized role/task/observation/results so it can be recorded accurately. Participant records, enhancement results and user satisfaction must remain pending until supplied or actually observed.
