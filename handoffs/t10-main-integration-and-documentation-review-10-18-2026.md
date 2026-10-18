# T10 main integration and documentation review

- Date: October 18, 2026, Asia/Manila (+08:00).
- Work: Jerome with Codex review; T10 implementation and original Antigravity assistance remain credited to Ellyssa.
- Scope: review the merged T10 source, verify preservation of T09, and reconcile current documentation. No application changes, new commit, push, PR or merge performed.
- Outcome: T10 remains **Done and integrated**. Two follow-ups are recorded below; fresh browser mobile/keyboard verification remains unrun.

## Integration and interfaces

[PR #25](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/25) merges Ellyssa source `45b38c77ff49b62410c80f7adb27a2df791fdfd0` at main `016a78bbf9e0e98c05ea4c62d24060591460f6d8`. Local `jerome`, `origin/main` and the remote main ref resolve to that merge. Application paths under accounts, inventory and templates match Ellyssa's source exactly. Remote `jerome` remains at `e60aa5f`; the local branch is four commits ahead before these uncommitted documentation edits.

The registration username correction `e60aa5f` is integrated through [PR #24](https://github.com/javecilla/Campus-Equipment-Borrowing-System/pull/24) at `f29bd91`. Its account form and regression test are unchanged by T10. Both that correction and T08 source `083a9da` are ancestors of current main. Earlier completed snapshots describing pending integration remain historical records.

Actual T10 interfaces are GET/HEAD `/portal/equipment/`, `/portal/equipment/<id>/` and `/portal/equipment/<id>/photo/`, mounted in [portal URLs](../accounts/portal_urls.py). [Inventory portal views](../inventory/portal_views.py) use the existing active BASIC_USER boundary, [search form](../inventory/forms.py), and [read-only queries](../inventory/queries.py). See the [HTTP contract](../docs/api_spec.md#basic-user-portal) for inputs, counts, archive exclusion and protected photo behavior. No new migration or dependency is introduced.

## Review findings

1. **P2: isolate the photo fixture from developer uploads.** [PortalEquipmentPhotoTests.setUpTestData](../inventory/tests/test_portal_equipment.py:396) saves an uploaded file through the default storage without an override or cleanup. With the configured MEDIA_ROOT this writes to local `media/equipment/`; database rollback does not delete the file. The fresh suite left a 66-byte `test.webp` there, and repeated runs can accumulate renamed files. Ellyssa should use Django's isolated test storage or a temporary media directory with cleanup. Existing local uploads were not deleted during review.
2. **P3: align request guidance with delivered behavior.** The [equipment detail footer](../templates/inventory/portal/equipment_detail.html:71) tells borrowers to submit through `portal:request-list`. That destination still renders the [T11 placeholder](../accounts/portal_views.py), with no submission form. Ellyssa should adjust the guidance until T11 supplies its create route; Ralph then connects the real request flow. This is a presentation follow-up, not a reopening of completed catalog browsing.

No core catalog authorization, archival, count or confidentiality failure was found in the inspected source and passing integration coverage. These checks do not establish full application acceptance or untested browser behavior.

## Fresh verification

All commands ran against the integrated source in this workspace; subsequent changes affect documentation only.

| Check | Actual result |
| --- | --- |
| `.venv/Scripts/python.exe manage.py test --noinput` | **174 PostgreSQL tests passed in 28.548s**, including 25 T10 tests and the T09 username regression; test database removed |
| Ruff check and format check | Passed; 177 files already formatted |
| djLint check of `templates/inventory/portal/` and `templates/accounts/portal/base.html` | Passed; 3 files checked, zero updates |
| Django `check --database default` | Zero issues |
| `makemigrations --check --dry-run --noinput` / `migrate --check` | No model drift or unapplied migrations |
| `npm.cmd run format:check` / `npm.cmd run build` | Passed; generated outputs remain ignored |
| `npm.cmd audit` / Python `pip check` | Zero vulnerabilities / no broken requirements |
| Git source/ref checks | Main merge and remote refs verified; source equality and prerequisite ancestry checks passed |
| Documentation and whitespace | 506 local links across 10 Markdown files resolve, including heading anchors; code fences balanced, encoding checks and `git diff --check` pass |

The affected-template result does not cover the previously recorded T08 unit-detail formatting issue. No fresh browser mobile/keyboard check, CI, T14 competing approval proof, performance measurement or backup/restore was run. Ellyssa's [original handoff](t10-borrower-equipment-catalog-10-18-2026.md) remains preserved with its own earlier checks.

## Documentation and next action

Updated [README](../README.md), [DEV](../DEV.md), [AGENTS](../AGENTS.md), [current handoff](../HANDOFF.md), [task evidence](../docs/tasks.md#verified-task-evidence), [SRS](../docs/SRS.md), [architecture](../docs/architecture.md), [HTTP contract](../docs/api_spec.md) and [folder guide](../docs/project-folder-architecture.md). The updates replace stale pending-integration claims, identify implemented borrower routes/photos, and preserve T09 Done. PLAN sequencing, source briefs, original snapshots and feature code are unchanged.

Ralph / T11 has integrated T03/T08/T09 prerequisites and can consume the T10 browsing interface. Kenneth / T16 has integrated T03/T08 prerequisites. Both remain Not started; this review does not authorize starting them. T20 still waits on T12/T17/T18/T19. Ellyssa owns the recorded T10 follow-ups and remaining browser verification. Documentation changes stay uncommitted on `jerome` for user review.
