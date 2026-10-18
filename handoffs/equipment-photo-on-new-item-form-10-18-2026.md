# Equipment photo on the new-item form

- Date/time zone: October 18, 2026, Asia/Manila (UTC+08:00).
- Owner: Kenneth Cortez's T07 catalog; Jerome Avecilla with Codex assistance, following the user's request to expose uploads during item creation.
- Branch/base: `jerome`, HEAD `20c4452`; Kenneth's baseline is integrated through PR #19. The current completion/photo batch remains **uncommitted / Not integrated**. No publication or branch operation performed.

## Outcome and interfaces

`/manage/items/new/` now renders **Equipment photo (optional)** below the description. The native multipart form accepts a photo together with the new item; leaving it empty keeps the default image. Existing items retain their separate Manage photo actions.

- [Creation form](../inventory/forms.py) reuses the shared [photo form input/parser](../inventory/photo_forms.py), with explicit typed data/files/category inputs and optional file selection.
- [Creation view](../inventory/views.py) binds `request.FILES` and dispatches to either the existing metadata-only service or the distinct [create_catalog_item_with_photo service](../inventory/photo_services.py).
- The photo creation service validates before writing and commits the item, photo reference and both audit records in one durable transaction. Failure rolls back the new item/audits and removes its new file. Upload errors attach to the photo field. Shared photo recording is reused by replacement; no flag-based service mode was introduced.
- [Item form](../templates/inventory/manage/item_form.html) and [photo action form](../templates/inventory/manage/photo_form.html) reuse the new [photo field component](../templates/inventory/manage/photo_field.html).
- [HTTP contract](../docs/api_spec.md) and [DEV guidance](../DEV.md#equipment-photos-and-local-media) describe creation-time upload. No new dependency or migration is needed beyond the preceding [photo upload work](optional-equipment-photo-uploads-10-18-2026.md).

## Verification performed

| Check | Actual result |
| --- | --- |
| Full PostgreSQL suite | All 103 tests pass, including two new creation/photo integration checks; earlier photo lifecycle and metadata-only creation checks also pass |
| Creation/photo behavior | Actual multipart creation persists the new item and WebP; invalid image leaves no item/file/audit; a real PostgreSQL rejection of the photo audit rolls back the item, its creation audit and the stored file |
| Browser on user's port 8000 | New-item page shows the optional file input below description; native input is `type=file`, not required, and its form uses multipart encoding. Desktop screenshot inspected; 375px page width stays within the viewport, and Tab from description reaches the photo input. No form submitted or development data added |
| Required checks | Django database check, migration drift/applied checks, Ruff lint/format, djLint across 44 templates, npm format/build/audit, pip check and Git whitespace pass; zero npm vulnerabilities |
| Documentation | 492 local Markdown links resolve across current/changed documents; fences and dated handoff paths checked |

The previous browser extension file-selection limitation remains; chooser upload was not retried. Creation uploads and rollback were verified with real Django multipart requests against PostgreSQL and temporary media. The viewport was restored after inspection. The existing port-8000 server already serves the updated field; no server process or private configuration was changed during this follow-up.

## Transfer

Refresh an existing browser tab on `/manage/items/new/` to load the optional field. Review the complete uncommitted T07 batch before separately authorized publication/integration. Existing dependency/migration setup remains in DEV.md; no further schema operation was required here. Kenneth's T08 and Ellyssa's future T10 retain their established integration/prerequisite gates. No full browser creation, CI, performance or unrelated workflow acceptance is claimed.
