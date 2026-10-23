# T25 PDF diagram delivery and documentation closure

Date: October 23, 2026 (Asia/Manila). Jerome supplied five diagram PDFs and explicitly requested marking diagram delivery Done. Codex inspected the PDFs and reconciled current documentation on `jerome`, starting at `114c160e9f9c1c89c137babd806898d6cf36f6b0`. Kenneth/Ellyssa retain diagram responsibility; Margareth retains validation/documentation support; original source contributors remain credited. Changes are uncommitted and Not integrated.

## Accepted deliverables

| Diagram | Supplied export | Editable source |
| --- | --- | --- |
| MTV | [Model-template-view structure](../docs/Model-template-view%20structure.pdf) | [Architecture MTV block](../docs/architecture.md#model-template-view-structure) |
| Request/loan states | [Workflow view](../docs/Workflow%20view.pdf) | [Architecture workflow block](../docs/architecture.md#workflow-view) |
| Unit and maintenance states | [Physical-unit and maintenance workflow](../docs/Physical-unit%20and%20maintenance%20workflow.pdf) | [Architecture unit workflow block](../docs/architecture.md#physical-unit-and-maintenance-workflow) |
| Core entities/relations | [Relationships](../docs/Relationships.pdf) | [Database relationships block](../docs/db_design.md#relationships) |
| Actor relations | [Actor relationships](../docs/Actor%20relationships.pdf) | [Database actor block](../docs/db_design.md#actor-relationships) |

T25 is Done locally under Jerome's acceptance of the supplied exports paired with the existing editable Mermaid definitions. The earlier Lucidchart-style conversion checklist is superseded by this accepted delivery format. Metadata identifies Mermaid Diagram Designer / MermaidEditor.io, created October 23, 2026. No separate editor-project file, specific PDF author identity or all-member review approval is inferred. Existing T22/T23/T24 main integration remains the prerequisite evidence; no new integration of these PDFs is claimed.

## Evidence and checks

- All five PDFs open, each with one page and no encryption; all five pages were rendered and visually inspected using PyMuPDF in an isolated ignored tooling project under `output/t25-review/`.
- The MTV page follows the editable reference's browser/middleware/routes/views/forms/services/queries/templates/ORM/database/storage flow. Workflow pages retain approval/reservation, cancellation, revised due date, one-time issue, partial/final return, damage, maintenance, repair and retirement. The two ERD views correspond to 14 domain entities and 23 relationships (16 core, 7 actor edges) in the editable sources.
- Both ERD PDFs render relationship-label bars without text. The labeled editable Mermaid definitions and field dictionary remain available; no PDF regeneration or claim of defect-free export typography is made. PDF diagram content is rasterized, so text extraction returns only the MermaidEditor.io footer; visual inspection was necessary.
- [Architecture source mapping](../docs/architecture.md#mtv-drawing-guide), [database models/constraints](../docs/db_design.md), [SRS A1-A8/U1-U4 mapping](../docs/SRS.md), [T22 executed acceptance mapping](../docs/manual-test-guide.md#module-21--automated-system-acceptance-t22), [T23 issue/enhancement](../docs/usability-acceptance.md) and [T24 results/limitations](../docs/operational-verification.md) supply existing traceability. Their links/paths were checked; prior executed tests are retained as prior evidence, not a new run.
- Current status references across README, SUBMISSION, backlog, HANDOFF, DEV, PLAN, agent guidance and related design/acceptance records are reconciled; historical dated handoffs are preserved. All 285 checked local links/anchors across added/changed text, this handoff and the two canonical design guides pass, as do unchanged PDF SHA-256 hashes and `git diff --check`.

No application code, database, uploaded media or supplied PDF was changed. No application tests or management commands ran; the database was not used. No commit/push, PR, main merge, external message or participant review session was performed.

## Next action

Jerome can review/publish this delivery and handle main integration. T30 remains Not started under its remaining prerequisites, including T28 and integration of dependent deliveries; final-ZIP inclusion and clean-machine replay remain separate. The PDF label display limitation remains explicit; the editable sources provide the labels for current review and future re-export.
