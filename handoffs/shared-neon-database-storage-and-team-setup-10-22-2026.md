# Shared Neon database, private storage and teammate setup

Date: October 22, 2026, Asia/Manila. Owner: Jerome, assisted by Codex. Task: HOST-01, explicitly authorized shared data services and teammate documentation. Branch: `jerome`, based on `7d0043d`; changes uncommitted, Not integrated into main. No commit, push, PR, main merge or email sent.

## Outcome and interfaces

The existing Django app uses Neon PostgreSQL through its existing Psycopg driver, and private S3-compatible Object Storage through Django's storage API. The active ignored `.env.local` selects the shared database and media; original local PostgreSQL and `media/` files remain intact. Django still owns users, sessions, ORM, workflows and custom role pages. Other Neon services and Django application hosting are outside this delivery.

[DEV.md](../DEV.md#shared-neon-database-and-photos) owns the step-by-step teammate setup, credential-free environment example, private-email delivery, test isolation and coordinator import guidance. [README.md](../README.md#run-locally) discloses Neon and links that setup; its dependency disclosure and [complete inventory](../docs/third-party-dependencies.md) cover the new Python storage packages. Live credentials remain only in ignored private configuration/backups.

Relevant implementation: [URL validation](../config/database_url.py), [environment selection](../config/environment.py), [database/storage settings](../config/settings.py), [private S3 configuration](../config/media_storage.py), [configuration checks](../config/tests.py), [photo import command](../inventory/management/commands/upload_catalog_photos.py), [.env.example](../.env.example), and the pinned Python requirements. Existing photo views/services/models/routes required no changes.

## Migration evidence

- Verified an empty remote public schema before import. Neon PostgreSQL 18.6 uses required client TLS; source/test PostgreSQL is 17.5.
- Saved a custom-format local dump privately as `output/private-backups/before-neon-database-20261022-103407.dump` (98,617 bytes). Preserved the prior environment file privately and all local media.
- Restored using native `pg_restore --no-owner --no-acl --single-transaction --exit-on-error`; no reseeding or deletion of source records. Compared all 14 domain-model datasets field for field immediately after restore: exact match.
- Copied 9 users, 12 categories, 29 catalog items, 46 units, 10 maintenance records, 30 requests, 20 loans and 28 returns, including existing settings/audit/history references.
- Created the private `assets` bucket through supported S3 operations. `upload_catalog_photos` copied only the 23 referenced images, preserving keys/bytes. Repetition reported zero uploaded and 23 matching; every image was also verified through the protected HTTP route. Unreferenced local files were retained locally.
- Enabled the pooled URL and Neon storage only after database/media verification. Login verification subsequently updated normal cloud login/session metadata; the restore equality check predates those logins.

## Checks actually run

| Check                                                                                                 | Result                                                                                                                                                                                                         |
| ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Full suite using DEV's child-process local overrides while `.env.local` selects Neon                  | **342 tests passed in 93.997s**, separate local `test_campus_equipment` created/destroyed                                                                                                                      |
| Earlier focused configuration and existing photo suites                                               | 20 passed in 2.020s                                                                                                                                                                                            |
| Live Django server at `127.0.0.1:8011`, real HTTP/cookies/CSRF and actual cloud services              | Both roles signed in/out; admin dashboard/catalog/stock/reports/CSV 200; all 23 administrator photos hash-matched originals; borrower catalog/photo 200; management 403; anonymous protected routes redirected |
| Django S3 storage save/read/delete and unsigned object access                                         | Passed; scratch object removed; unsigned request HTTP 403                                                                                                                                                      |
| Cloud `check --database default`, applied-migration check and migration drift check                   | Passed; no pending migrations or model changes                                                                                                                                                                 |
| Ruff lint / owned Python formatting / pip dependency check                                            | Passed                                                                                                                                                                                                         |
| Frontend build, contrast and source formatting                                                        | Passed; all nine contrast pairs pass; CSS/JS compiled                                                                                                                                                          |
| Full Ruff formatting / full djLint formatting                                                         | Same two pre-existing findings: archived borrower-portal handoff example and portal equipment grid attribute wrapping; left unchanged                                                                          |
| Prettier on changed Markdown files (`docs/third-party-dependencies.md`, `docs/tasks.md`, new handoff) | Passed after formatting; new S3 package rows and task table now use consistent Prettier column alignment. Kiro applied this step; pre-existing long-line findings in other docs left unchanged                 | A first helper-script invocation lacked the project import path; running it through `runpy` from the project root resolved that harness issue, and the complete live check passed. Neon CLI bootstrap installation stalled and was cancelled; the cached CLI had no authenticated profile. The supplied service credentials were sufficient for native database/S3 setup, so no CLI platform login, `neon.ts`, global installation or extra service deployment was needed. |

## Remaining work and next owner

[Module 22](../docs/manual-test-guide.md#module-22---shared-neon-database-and-photos-host-01) separates executed HTTP checks from pending browser/second-workstation onboarding. Full workflow/concurrency tests ran on local PostgreSQL 17.5; the full suite was deliberately not pointed at the shared Neon database. T24 performance measurement and complete operational database/media recovery rehearsal remain pending; this initial import is not T24 acceptance. Existing T22 publication/integration evidence is unchanged.

Jerome reviews the local diff, then publishes/integrates when explicitly authorized before teammates pull the setup. Jerome supplies real connection/storage values and the seeded application password privately by email. Teammates follow DEV setup without reseeding or clearing the central dataset; use their own local PostgreSQL and local media for tests and destructive reset rehearsals.
