# T23 acceptance and startup asset feedback enhancement

- Date: October 22, 2026, Asia/Manila.
- Owner: Ralph; Codex implementation/verification assistance. Ellyssa remains co-coordinator; no additional participant contribution claimed.
- Outcome: **T23 Done locally on `ralph`, uncommitted over `6c97f0d`, Not integrated.** No commit, push, PR or merge performed. The user-requested rollback remains respected: the request-card feature and unfinished main merge were not restored.

## Actual feedback and scope

[R01](../docs/usability-acceptance.md#r01-user-reported-functional-confirmation) retains the user's reported borrower/admin acceptance. Their earlier real `/manage/` traceback supplies R02/F02: missing compiled dashboard charts failed at template rendering. E01 adds a native Django staticfiles system check naming missing bundles and the repair commands before ordinary `runserver` accepts requests. No invented difficulty, satisfaction score, extra participant or independent human observation is claimed. The optional request-guidance/filter preference question was unanswered; its suggestions are not findings and did not supply the enhancement source.

SRS A7/NFR-07/NFR-08 remain within the existing Django/Node build scope. No models, routes, dependencies, roles or workflow services changed. No automatic npm installation/build occurs inside Django.

## Relevant files and interfaces

- [operations/apps.py](../operations/apps.py): lifecycle registration of the staticfiles check.
- [operations/checks.py](../operations/checks.py): `check_compiled_assets(app_configs, **kwargs)` returns `operations.E001` for missing CSS/six current JavaScript entries via the real staticfiles finders.
- [operations/tests/test_assets.py](../operations/tests/test_assets.py): real build copy, missing-chart startup/recovery, complete missing build and existing fingerprints.
- [Module 22 / T23-05](../docs/manual-test-guide.md#t23-05-missing-build-feedback-enhancement-e01), [canonical session/result](../docs/usability-acceptance.md), [DEV](../DEV.md#frontend-preview), [backlog](../docs/tasks.md#verified-task-evidence), [README](../README.md), [SRS](../docs/SRS.md) and [T26 pointer](../docs/user-needs-evidence-guide.md): current status, repair path, verification and evidence limits. Existing dated handoffs were preserved.

## Verification

- Local target verified as `campus_equipment` on loopback, not shared `neondb`. Tests explicitly used `DATABASE_URL=''` / `MEDIA_STORAGE=local`; data lived in `test_campus_equipment`. Read-only live snapshot at 11:48: 6 requests / 3 loans / 4 units, no available Camera units, limits 7 days / 3 per item. No seeds, reset, schema application, shared Neon writes or media modifications.
- Before E01: 339 PostgreSQL tests passed in 159.434s. Final E01 suite: **341 PostgreSQL tests passed in 134.726s**. Three targeted asset tests passed in 0.072s.
- Initial full E01 run caught a test-harness mistake: programmatic `call_command('runserver')` skips checks by default. The test now explicitly uses `skip_checks=False`, matching ordinary CLI startup; targeted and final full suite pass. No unresolved runtime failure remains from that run.
- Build, nine theme contrast pairs, npm format check, npm audit (0 vulnerabilities), Ruff lint/changed Python formatting, Django database check, migration drift/state checks and pip dependency check passed. No migrations generated or applied.
- Existing unrelated formatting findings were preserved: Ruff's Python code fence in `handoffs/borrower-portal-ui-improvements-10-20-2026.md`; djLint's long grid tag in `templates/inventory/portal/equipment_list.html`.
- Edge/Chromium 155.0.4283.62 before and after E01: real borrower/admin login plus four routes each at 1440/768/390/320px (32 route/width checks each run), one heading and no page overflow/JS errors. Borrower foreign-ID 404, keyboard Clear filters and visible focus pass. Browser fixtures ran in dedicated local `test_campus_t23_browser_1022` / `test_campus_t23_postcheck_1022`, both destroyed afterward. Ignored screenshots/results are in `output/t23/`.
- Documentation verification passed: 79 added relative links and 28 heading anchors; affected T23 current-state records agree on Done locally / Not integrated. Git diff whitespace checks pass.

## Limits and next action

Human acceptance is the limited self-reported R01, not a representative campus sample or an independently observed session. Device/assistance/task timings were not supplied; post-enhancement human recheck Not run. Only nonidentifying user-supplied outcome/symptom retained. The check detects absent entries; it does not assess stale build contents, every generated chunk, or automatically run in hosts that skip system checks. Run `manage.py check --tag staticfiles` before a separate WSGI/ASGI deployment.

T20 source `b43fb99` and T21 source `e3402bf` remain ancestors of `origin/main` `29003cf`, satisfying prerequisites. HOST-01/newer main source was not merged back after the rollback; T23 uses the accepted foundation already in Ralph's branch. Ralph reviews and requests publication when ready; Jerome handles main integration. T24 operational evidence, T25 diagrams and T26 wider research are separate.
