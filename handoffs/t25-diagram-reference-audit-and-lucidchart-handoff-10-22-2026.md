# T25 diagram reference audit and Lucidchart handoff

- **Owner/scope:** Jerome Avecilla requested the audit; Codex documentation assistance. Kenneth and Ellyssa consume the references for editable-tool conversion; Margareth retains validation/documentation support. Original implementation credit is preserved.
- **Date:** October 22, 2026, Asia/Manila; verification finalized at 15:03 Asia/Manila.
- **Outcome:** T25 In progress. Documentation reference reconciliation is complete locally; editable tool sources/exports, team review and final requirements/source/test traceability remain pending. Uncommitted on `jerome`, Not integrated. No commit/push, external message or tool document was created.
- **Baseline:** fetched main PR #59, `e2c3f61174ca555e7d8e57184fbad84bd22ccd4d`, October 22 at 14:40:56 Asia/Manila. Documentation source `0e65b8bbfe53d6fc35aa6ba8f5abbe222947dbe9` is its ancestor; source and merge share tree `ead037fe768b15c1dea07a0e5278cbeaa08e16e7`. Local `jerome` was fast-forwarded before editing. T22/T23/T24 remain accepted/integrated.

## References and corrections

- [Architecture](../docs/architecture.md#model-template-view-structure): views orchestrate forms, services, queries and rendering; templates/ORM have explicit MTV boundaries; protected photo storage is separate from PostgreSQL. Actual source paths and template inheritance guide the drawing. Audit annotations cover actual writer calls; submission has no audit event in current code.
- [Database](../docs/db_design.md#relationships): 14 domain entities, all 23 FK/one-to-one links, actual column names, key/nullability notes, source-return maintenance relationship and actor supplement. Schema zero-or-many differs from service-enforced request/loan minimum children. A User is not guaranteed a Profile by SQL alone. Settings are one singleton; audit targets are historical references; framework support tables are excluded from domain ERD.
- [Workflow](../docs/architecture.md#workflow-view): exact stored request states, date-revision and repeated-partial-return loops, separate unit/maintenance lifecycle, initial damage, linked damaged returns, repair/retirement and terminal states. Allocation remains active after release; final return closes the loan even with open maintenance. Overdue remains derived; returns remain possible for inactive borrowers/archived catalog.
- [Consumer instructions](../DEV.md#t25-readiness-and-consumer-handoff), [backlog](../docs/tasks.md#verified-task-evidence), [current handoff](../HANDOFF.md), README/SRS/AGENTS: reference preparation is authorized/In progress, with actual conversion/review still pending. No application/schema/workflow contract changed.

## Verification

- Git source ancestry/exact merge-tree equality and clean starting state verified. Earlier dated handoffs retained.
- Five Mermaid blocks parsed/rendered locally using Mermaid 11.12.0 with Playwright/Chrome; screenshots inspected. Reference labels shortened and layout adjusted after initial visual review. Only a harmless missing local favicon was logged; no diagram parser/render failure remains.
- Metadata verification passed: all 14 entity names, 23 relationship/column names and schema cardinalities; displayed key/nullability markers; all model/migration fields, constraints and indexes; all seven request and five unit status values. This check opened no database connection.
- Documentation verification passed: 1,006 local links, 264 anchors and four Python fences across nine changed Markdown files; no conflict markers; exactly one T25 task row marked In progress; documentation-only diff; earlier completed handoffs unchanged. Git whitespace checks pass. The new handoff and edited T25 consumer section pass targeted Prettier checks. Whole-file formatting still flags pre-existing table/spacing differences in design/DEV documents; unrelated formatting was preserved.
- No management command, database connection, test suite, seed, migration, workflow or storage write was required. Metadata inspection uses explicit local `DATABASE_URL=''`, `MEDIA_STORAGE=local` and `MigrationLoader(None)`. Shared Neon and local data/media remain unchanged. Prior T24's 344-test/measurement/recovery results are referenced, not rerun.
- Local render inputs/vendor bundle/screenshots are ignored under `output/playwright/t25-diagrams/`; they are validation artifacts, not completed editable-tool submissions. No application dependency/configuration was added.

## Remaining work and next owner

Jerome reviews the reference diff and coordinates Kenneth/Ellyssa conversion. They should use the source/drawing guides in the canonical design documents, split large views into readable pages, preserve all states/relationships/notes, and link the real editable sources and exports there. Everyone reviews final diagrams and requirements/source/test traceability before T25 is Done. No teammate conversion or human review is invented; T26-T29 statuses are not completed by this audit.
