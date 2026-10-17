# Local database reset guide

- Owner: Jerome Avecilla, with Codex documentation assistance.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00), around 11:29.
- Scope: AUTH-01 documentation follow-up requested after the seed reported existing usernames. No application change, password change, deletion, or database reset performed.
- Delivery: local, uncommitted on `jerome`, based on `cb96319`; **Not integrated**. Earlier uncommitted work and dated handoffs preserved; no commit, push, PR, or merge performed.

## Outcome

[DEV.md](../DEV.md#reset-local-development-data) now explains existing-seed errors, password-only changes that preserve records, and a full reset for a disposable local PostgreSQL database. The full reset verifies the target, disconnects clients, recreates the database through pgAdmin's maintenance database, then runs migrations, seed, and verification commands. It states the destructive scope and preserves source/migration/private configuration files.

The guide distinguishes recreating the database from Django `flush`: the installed flush command removes migration-created data without resetting applied migration history. The project initializes `SystemSetting` row 1 and its SYSTEM audit through [operations migration 0002](../operations/migrations/0002_initial_settings.py), so ordinary migration after a flush would not restore them. No reset helper or automatic recovery was added.

[HANDOFF.md](../HANDOFF.md) indexes this snapshot; [AUTH-01 evidence](../docs/tasks.md#verified-task-evidence) links the guide. Feature readiness and T21's full-dataset dependency are unchanged.

## Verification and limits

- Reviewed the actual seed behavior, settings initializer, required-singleton query/service errors, and installed Django flush/introspection/migration code. `manage.py help changepassword` confirms the documented username argument.
- Checked 218 relative links/heading anchors, code fences, dated naming, unchanged application task statuses, preserved Alex snapshot, private seed-value exclusion from shareable files, and diff whitespace after edits; all passed.
- Documentation only: application tests/lint were not rerun. The earlier 39-test result belongs to the environment-password handoff. No destructive SQL, flush, password change, or reset/reseed sequence was executed; this procedure has not been validated by an actual database recreation in this task.

## Next action

Jerome can sign in with the existing seed accounts immediately. Use DEV.md's password-only steps to retain records, or follow the full reset only when all data in that disposable local database may be deleted. Review the uncommitted documentation before separately requesting publication.
