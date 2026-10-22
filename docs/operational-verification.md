# Operational verification (T24)

## Outcome and tested scope

October 22, 2026, Asia/Manila. Jerome owns T24; Codex assisted execution, repeatable tooling and documentation. **Performance and recovery acceptance passed locally; final regression/check results are in the dated handoff.** Source baseline `a9fff7e45369e3ba6f42bf4839742ce7bf1d9af9` includes T22 through main PR #54 and Ralph's T23 implementation through PR #56. T24 scripts/documentation are local and uncommitted, **Not integrated**. T23 is Done/integrated on retained limited acceptance evidence; T25 execution awaits T24 main integration and the separate diagram go signal.

This is the canonical measured result and limitations record. [DEV replay instructions](../DEV.md#t24-readiness-and-consumer-handoff) own commands; [manual cases](manual-test-guide.md#module-23--performance-and-recovery-t24) own expected-versus-executed checks. [SRS NFR-05/NFR-09](SRS.md#non-functional-requirements) define the proposed performance targets and recovery requirement.

## Environment and workload

| Field | Actual configuration |
| --- | --- |
| Machine | AMD Ryzen 5 7430U, 6 cores / 12 logical processors; 16,515,997,696 physical RAM bytes (15.38 GiB) |
| OS / application | Windows 11 Home Single Language 10.0.26200; Python 3.13.12; Django 5.2.18 |
| Measured database | Dedicated `campus_t24_benchmark`, portable PostgreSQL 18.6, `127.0.0.1:55424`, UTF-8 / C locale; shared_buffers 128 MB, work_mem 4 MB, max_connections 100 |
| HTTP server | Threaded Django `runserver --noreload`, `DJANGO_DEBUG=False`, loopback port 8024; client/server/database on this machine |
| Fixture | 5 categories, 20 items, **1,000 units / 5,000 requests**, 5 ADMIN and 5 BASIC_USER accounts; one requested unit per request |
| Request states | 3,180 Pending; 260 Approved; 260 Rejected; 260 Cancelled; 260 Issued; 780 Returned |
| Loan/stock distribution | 1,040 loans; 780 complete, 260 active, 130 overdue; 480 Available, 260 Reserved and 260 Issued units |
| Construction | Existing account/catalog/unit/request/approval/cancellation/release/return services; no generic status setter. Half the newly generated active loans and their request/allocation/audit timestamps were dated five days earlier, after acquisition, to supply overdue workload |
| Sessions | Ten independent cookie jars, actual password + CSRF login; five admins and five borrowers; 260 synchronized request waves, **2,600 measured GETs** |
| Samples / timing | One warm-up per route/session; each admin route 100 measured samples, borrower route patterns 185 or 190; individual borrower detail IDs 37 each. Nearest-rank p95; barrier/login/warm-up excluded from individual response times; total run including login/warm-up 93.216 seconds |

The initial 2,000-request pilot also passed, but different role route counts let borrower workers finish earlier. The accepted second pass synchronized every wave, keeping all ten session workers participating until the final wave. SQL profiling/EXPLAIN ran afterward, outside timed traffic. Recovery work was complete before either load run.

## Response measurements

All **2,600 measured responses were HTTP 200**; no target misses. Seconds below include loopback request, response generation and body transfer. `<id>` combines the actual tested IDs within that route pattern; acceptance was also checked independently for each concrete route. Read-only lists/details target p95 <= 2 seconds; dashboard/home/report target <= 3 seconds. Each measured home also meets the stricter 2-second bound.

| Route | Samples | p95 seconds | Maximum seconds | Target seconds |
| --- | --- | --- | --- | --- |
| `/manage/` | 100 | 0.375 | 0.443 | 3 |
| `/manage/audit/` | 100 | 0.370 | 0.449 | 2 |
| `/manage/items/` | 100 | 0.363 | 0.413 | 2 |
| `/manage/items/<id>/` | 100 | 0.454 | 0.471 | 2 |
| `/manage/loans/` | 100 | 0.447 | 0.463 | 2 |
| `/manage/loans/<id>/` | 100 | 0.390 | 0.423 | 2 |
| `/manage/reports/loans/` | 100 | 0.431 | 0.593 | 3 |
| `/manage/reports/overdue/` | 100 | 0.422 | 0.463 | 3 |
| `/manage/requests/` | 100 | 0.443 | 0.481 | 2 |
| `/manage/requests/<id>/` | 100 | 0.383 | 0.544 | 2 |
| `/manage/requests/?status=PENDING` | 100 | 0.376 | 0.471 | 2 |
| `/manage/units/` | 100 | 0.420 | 0.552 | 2 |
| `/manage/units/<id>/` | 100 | 0.372 | 0.400 | 2 |
| `/portal/` | 190 | 0.444 | 0.471 | 3 |
| `/portal/equipment/` | 185 | 0.367 | 0.438 | 2 |
| `/portal/equipment/<id>/` | 185 | 0.292 | 0.349 | 2 |
| `/portal/loans/` | 185 | 0.483 | 0.591 | 2 |
| `/portal/loans/<id>/` | 185 | 0.346 | 0.380 | 2 |
| `/portal/requests/` | 185 | 0.335 | 0.445 | 2 |
| `/portal/requests/<id>/` | 185 | 0.357 | 0.433 | 2 |

The highest concrete-route p95 was **0.483 seconds** (`/portal/loans/`); the largest single response was **0.593 seconds** (loan report). These are lab observations for this configuration, not a production capacity promise.

## SQL inspection and decision

Captured real Django ORM queries for 20 representative routes and executed `EXPLAIN (ANALYZE, BUFFERS)` on the three slowest captured SELECTs per route. Counts were **3 to 9 queries per response**, with bounded page prefetches. The administrator request list had the largest sampled plan, **15.442 ms**; its five captured queries totalled approximately 22 ms. Dashboard: nine queries / approximately 13 ms captured SQL; loan report: seven / 14 ms; borrower loan list: six / 6 ms. Capture times have millisecond precision and include client overhead; EXPLAIN execution times are separate server observations.

Plans used the existing owner/foreign-key/due-date indexes for selective lookups, joins and aggregate scans for whole-table totals. Sequential scans over small catalogs and aggregate inputs were expected, not automatic evidence of a missing index. No latency target failed and no query refactor, new index, cache, schema or production dependency was justified by this run. Search/deep-pagination/large CSV performance and larger/longer workloads remain unmeasured.

## Backup and recovery demonstration

**Source:** current shared Neon `neondb`, PostgreSQL 18.6, plus its private Object Storage. Backup used an exported repeatable-read, read-only database snapshot and `pg_dump --snapshot`, custom format, public schema, no owner/ACL import. Every public table was fingerprinted by SHA-256 over all canonical ordered row values. Database dumps, row contents, credentials, cookies and photo bytes remain private under ignored `output/t24/`.

**Target:** a separate initially empty local `campus_t24_restore`, PostgreSQL 18.6 at loopback 55424, with a separate restored-media directory. `pg_restore --single-transaction --exit-on-error --no-owner --no-acl` completed; all **22 table row counts and full-content hashes** matched before HTTP verification changed only restored login/session records. The snapshot contains 14 domain models, 9 accounts, 12 categories, 29 items, 46 units, 30 requests, 20 loans, 34 loan units, 28 returns, 10 maintenance records and 101 audit records; these are snapshot counts, not permanent live totals.

All **23 referenced photos / 954,058 bytes** were downloaded from current Object Storage, read twice to detect an observed change, copied to a separate local media root and SHA-256 verified. A dump alone cannot recover photos. **58 real Django HTTP checks** passed: both roles' CSRF-protected password login and opposite-role 403, dashboard/portal/history/reports/CSV, and matching image bytes from all 23 protected admin and borrower photo routes. A further service-level submit -> approve -> release -> return cycle passed against recovered data, exercising new sequence-backed inserts; the surrounding transaction rolled back its verification rows.

| Measurement | Actual result |
| --- | --- |
| Custom database dump | 100,652 bytes; 5.431 seconds |
| Complete database/media backup and source verification | 19.989 seconds |
| Native database restore | 0.414 seconds |
| Restore, media copy/hash verification and 58 HTTP checks | 4.852 seconds |

The first restore attempt stopped because a fresh database already contained its empty `public` schema, while the schema-inclusive archive creates it. Its single transaction rolled back. The corrected procedure checks the target name/host and empty tables, verifies the dump hash, drops only that empty local schema **without CASCADE**, and restores. No existing dataset or shared schema was cleared.

Portable native tools were downloaded from [EDB's official binary distribution](https://www.enterprisedb.com/download-postgresql-binaries), under ignored `output/t24/tools/`; no app package was added or installed globally. Both dump and restore used PostgreSQL 18.6. PostgreSQL documents that an older pg_dump cannot dump a newer-major server and that restoring to an older-major server is not guaranteed; use matching/newer compatible tools and verify the target. See [official pg_dump guidance](https://www.postgresql.org/docs/18/app-pgdump.html).

## Maintenance and limitations

- Preserve a matched database dump, media directory and integrity manifest privately before coordinated schema/reset/import work. Choose fresh output directories: scripts refuse a populated restore target, benchmark fixture rerun or output overwrite. Keep the shared database URL untouched; local operations use explicit child-process overrides and verified names/loopback hosts. The benchmark/restore guards were also executed against configured Neon and rejected both operations before mutation.
- For the retained workstation rehearsal, the portable database cluster is stopped after verification. Its data, native tools, private local profile `.env.t24.local` and backup remain ignored. Restart it only when intentionally replaying T24; normal application startup continues to use Neon. The preserved original local `campus_equipment` database and `media/` were not used as restore targets.
- The database snapshot is transaction-consistent. Database and object storage have no cross-service atomic snapshot here; double reads detect observed content changes but cannot guarantee against every concurrent delete/replacement. A coordinated write pause or object versioning is needed for stronger recovery guarantees. Only referenced images were backed up; orphan objects, provider roles/ACLs, other provider schemas and infrastructure are outside this rehearsal.
- Recovery timings are one small-dataset local observation, not an RPO/RTO commitment, automated schedule, off-site redundancy, encrypted archival policy or a verified restore back into Neon. The dump contains sensitive stored password hashes/session data; keep access restricted and do not include ignored artifacts in the submission ZIP.
- Performance covers authenticated HTML GETs, warm caches, local media and a same-machine development server/database. It excludes cloud/network latency, image/static downloads, JavaScript rendering, cold starts, sustained traffic, concurrent writes, export throughput and production hosting. Each request has one item; only a small catalog and mostly same-day history were generated. No independent browser usability claim follows from these checks.

The current results satisfy T24's recorded lab-performance/recovery scope with these limits. T23 is Done with its evidence limits retained. T25 still requires T24 main integration and Jerome's explicit diagram go signal; T29 can consume T24 after its main integration is verified.
