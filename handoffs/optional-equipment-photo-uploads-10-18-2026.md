# Optional equipment photo uploads

- Date/time zone: October 18, 2026, Asia/Manila (UTC+08:00).
- Owner: Kenneth Cortez's T07 catalog; user-authorized enhancement by Jerome Avecilla with Codex assistance.
- Branch/base: `jerome`, HEAD `20c4452`, matching the locally available `origin/main`. Kenneth's T07 baseline `e107dcb` is integrated through PR #19; T03/T04 ancestry was verified in the [completion review](t07-catalog-completion-and-integration-review-10-18-2026.md).
- Delivery: **Done locally / uncommitted / Not integrated**. Earlier T07 completion changes and both supplied placeholder assets are preserved. No commit, push, PR, merge or remote refresh performed.

## Result and interfaces

One optional image is stored per [CatalogItem](../inventory/models.py), shared by its physical units. Creation and existing metadata forms remain usable without a photo. Item details expose **Manage photo**; catalog rows display thumbnails. The supplied `default-photo-equipment-270x360.webp` is displayed when no photo is assigned; both supplied PNG/WebP originals are preserved.

- [Photo routes](../inventory/manage_urls.py) and [views](../inventory/photo_views.py): active ADMIN only; GET/POST upload at `inventory_manage:item-photo-upload`, protected GET/HEAD image delivery at `inventory_manage:item-photo`, and GET confirmation/POST removal at `inventory_manage:item-photo-remove`. Raw `/media/` requests are not routed. Photo responses use WebP, `nosniff`, and private/no-store caching. Removal restores the default image; repeat removal is 409.
- [Form](../inventory/photo_forms.py) and [normalization](../inventory/photos.py): real JPEG/PNG/WebP decoding, 5 MiB / 20 MP limits, animation rejection, EXIF orientation correction, metadata removal, and resizing to fit 1600×1600 without cropping. The client filename and MIME declaration do not determine the saved file.
- [Services](../inventory/photo_services.py): generated UUID WebP names, actor/category/item locks, ITEM_UPDATED audit, durable transactions, deletion of a new file if its database write fails, and deletion of superseded uploads after commit. The cleanup handler rethrows failures. Callers must not wrap these services in another business transaction.
- Storage: local `media/equipment/<generated-id>.webp`; PostgreSQL stores the relative path only. `media/` is ignored by Git and created on first upload. See [DEV storage guidance](../DEV.md#equipment-photos-and-local-media) for per-workstation uploads, backups, protected serving and setup. A process crash can leave an unreferenced file because filesystem writes and PostgreSQL cannot share one transaction; no silent recovery or automatic purge is installed.
- [Migration 0003](../inventory/migrations/0003_catalog_item_photo.py) adds the optional ImageField without rewriting previous migrations; it is applied to the local development database.
- Pillow 13.0.0 is declared/locked in the Python requirements and installed in `.venv`; existing package versions were preserved using constraints during resolution. README rationale and the complete [dependency inventory](../docs/third-party-dependencies.md) include MIT-CMU and bundled-library notice retention. WebP support was verified from the installed wheel. Supplied placeholder provenance is recorded without inventing an upstream license.
- [SRS](../docs/SRS.md), [HTTP](../docs/api_spec.md), [database](../docs/db_design.md), and [architecture](../docs/architecture.md) describe the enhancement and filesystem boundary. T08, T10, and T16 remain their owners' pending work; no portal endpoint was added.

## Verification

| Check | Actual result |
| --- | --- |
| Full real PostgreSQL suite | All 101 tests passed, including five new [photo integration tests](../inventory/tests/test_equipment_photos.py) and the earlier 96-test baseline |
| Photo lifecycle | PNG/JPEG/WebP upload, replacement, generated filename, resizing, protected streamed bytes, physical file cleanup, confirmed removal/default restoration and repeated removal verified |
| Validation/privacy/access | Invalid/truncated/oversized/disallowed/animated images rejected without file/audit writes; EXIF orientation corrected and metadata removed; role/inactive/service checks, CSRF, methods, and raw-media 404 verified |
| Atomicity | Real PostgreSQL audit constraint rejects replacement/removal; old reference/bytes survive and newly written file is removed. Tests use temporary filesystem storage, with no mocked writer |
| Django/database | Migration 0003 applied; database system check, migration drift and unapplied-migration checks passed |
| Formatting/build/dependencies | Ruff lint/format, djLint, npm format/build/audit, and pip check passed; zero npm vulnerabilities |
| Documentation/Git hygiene | 478 local Markdown links resolved across 11 current/changed documents; fences, handoff date/name, ignored media path and Git whitespace checked |
| Chrome | Temporary isolated test database/media on localhost:8011; own test login, default and uploaded image display, protected image 200, desktop/375px screenshots, keyboard order, and actual confirmation/removal/default restoration passed. Viewport restored, tab/server closed, temporary media and database removed |

The browser extension blocked local file selection because its file-URL permission is disabled. Browser upload/replacement via the file chooser remains unrun; real multipart Django requests verify those actions. An uploaded-photo fixture was prepared through the actual service in the isolated database for the display/removal browser checks. No extension permission was changed, and no catalog records were added to the development database. Its schema migration is the intended persistent local database change.

During test development, the fixture needed PostgreSQL deferred constraints flushed before adding a rejecting audit constraint; the streaming-response test also needed Django's own response cleanup rather than a second manual close. These test issues were corrected before the final 101-test passing run.

## Next action and limits

Review the complete uncommitted T07 batch on `jerome`; publish/integrate only when explicitly requested. Other workstations install the updated requirements, apply migrations 0002/0003 and restart Django. The current workstation already has the dependency and migrations; its existing application server needs a restart to load the new model/routes/templates.

Kenneth / T08 should consume the corrected, integrated T07 batch before starting unit work. Ellyssa / T10 will add its own authorized portal photo interface after T08/T09; the admin image route must not be reused as public media serving. Full borrower workflows, T14 competing approvals, clean-machine setup, performance, backup/restore and CI were not executed or claimed.
