# Seed account access table and missing physical units

- Date: October 22, 2026, Asia/Manila.
- Owner: Jerome Avecilla with Codex assistance.
- Scope: user-requested DEV.md login roster and local physical-unit registration. The user explicitly approved restoring Audio Cassette Duplicator before registering its unit. No new application code, dependency, migration, borrowing transaction, commit, push, PR/main integration, teammate message or diagram work.

## Outcome

The [DEV account table](../DEV.md#seed-the-t21-demonstration-dataset) now lists all nine fictional full names, usernames, emails, roles and default password sources. Each password cell refers to private `.env.local` / `SEED_ACCOUNT_PASSWORD`; no secret value was copied into documentation. Instructions cover the login URL, username or email sign-in, role destinations, per-developer configuration, environment overrides and existing-account password changes. The current private value was verified through the actual application's LoginForm for all nine usernames and all nine emails.

One Good/Available physical unit was registered for each of the eleven items that had no units. Ten were active already; Audio Cassette Duplicator was restored using the existing audited service with the user's explicit approval, then received `CEL-ANR-DUP-001`. The [added-unit table](../DEV.md#physical-units-for-the-current-local-catalog) lists every item/asset code. Acquisition dates use October 22, 2026, as the registration date for these fictional demonstration units; notes give equipment-specific handling checks without claiming completed technician work.

All **29 catalog items now have at least one physical unit**. Current counts: **46 units = 39 Available + 5 Maintenance + 2 Retired**. All 35 prior units, 12 categories, 9 maintenance records, 9 accounts and 23 catalog photos remain. Requests, allocations, loans and returns remain empty. These are local database additions; the account-only `seed_demo_data` command does not generate equipment or distribute uploaded photos to another developer's machine.

## Verification

- New units were inserted through `inventory.services.create_equipment_unit` inside transactions, with model validation, unique asset codes, active-admin/catalog checks and one real `UNIT_CREATED` audit each. Eleven creation audits and one `ITEM_RESTORED` audit are present. Re-read queries show zero catalog items without units and zero borrowing records.
- Serialized comparisons verified unchanged pre-existing records across all 14 domain models. The restoration transaction excluded only the expressly changed item's archive flag/update timestamp; its other fields were compared. All 23 photo paths and SHA-256 file hashes were checked before/after both registration batches. No photo files were modified or deleted.
- The account table was checked against all nine live full names/usernames/emails/roles; every password cell references private configuration. All 18 username/email identifiers pass `accounts.forms.LoginForm` with the private environment password. No authentication code changed.
- Django `check --database default` passed. Documentation verification passed: 819 relative targets, 205 heading anchors and paired fences across seven documents, account table completeness and diff whitespace.
- No application source changed in this follow-up. The complete **327-test / 82.767s** PostgreSQL run belongs to the [previous cleanup task](clean-demonstration-accounts-and-equipment-preservation-10-22-2026.md) and was not rerun for this documentation/data operation. No new browser, mobile, keyboard, spreadsheet or user acceptance result is claimed.

## State and next action

Current records are linked from [Module 20](../docs/manual-test-guide.md#module-20--fictional-demonstration-dataset-t21), [HANDOFF](../HANDOFF.md) and [task evidence](../docs/tasks.md#verified-task-evidence). Source remains uncommitted on `jerome` over main `4f285cb`; these changes are **Not integrated into main**. Original requirement/member files and earlier completed handoffs remain intact.

**T21 remains In progress** because the user deferred its required borrowing scenarios. T22/T23 still await full T21 completion, authorized main integration and actual execution. The user can now inspect equipment stock and sign in using any documented account. No extra units were added to items that already had stock; existing Maintenance/Retired states remain intact.
