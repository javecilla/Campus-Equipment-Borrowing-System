# Auth and interface publication

- Owner: Jerome Avecilla; source commit co-authored by Alex Enrico Cayanan and Codex, as explicitly requested.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00), around 12:43.
- Scope: authorized member-branch publication of AUTH-01/AUTH-02/UI-04/UI-05 and related development guidance/assets; current-state publication receipt.
- Delivery: source commit `aa6d8e89fc0988c202277af4e7f9b53857c4272d` pushed to `origin/jerome`. **Not integrated into main**. No new PR, main merge/push, force push, seed deletion, or database reset performed.

## Published result

The 39-file source commit contains the private-environment [authentication seed](../accounts/management/commands/seed_auth_accounts.py), [username/email login](../accounts/forms.py), [minimal login/wave](../templates/accounts/login.html), [admin](../templates/operations/manage/dashboard.html) and [basic-user](../templates/accounts/portal/home.html) destinations, and shared [403](../templates/403.html)/[404](../templates/404.html) pages with safe recovery and logout controls. Contracts, current task evidence, and previous completed handoffs are preserved in the batch.

[DEV.md](../DEV.md) includes the supplied [login screenshot](../static/images/login-screen.png), both fictional test identities, private-password setup, narrowly scoped disposable-account deletion/reseed guidance, and local DEBUG=False/static-serving error preview steps. The [guide snapshot](login-screen-and-auth-dev-guide-10-17-2026.md) records the documentation scope; it contains no real password. No documented deletion/reseed command was executed during publication.

## Attribution and Git evidence

The source commit retains Jerome's configured submitting identity and ends with:

```text
Co-authored-by: Alex Enrico Cayanan <AlexCayanan@users.noreply.github.com>
Co-authored-by: Codex <codex@openai.com>
```

Alex's integrated T04 `7ae5e87` and LF correction `5f42ac0` remain original ancestors, with authors unchanged. They were not squashed or reattributed. `git push origin jerome` succeeded, and read-only remote verification returned `aa6d8e89fc0988c202277af4e7f9b53857c4272d` for `refs/heads/jerome` and `847a8c03b24aa03f0a2841f859121c372ab2fe85` for `refs/heads/main`. No main integration is implied by member-branch publication.

The source push left a clean working tree synchronized with origin/jerome. This follow-up receipt updates only [HANDOFF.md](../HANDOFF.md), [task evidence](../docs/tasks.md#verified-task-evidence), and this snapshot, and is included in a separate documentation commit under the same authorized publication request.

## Verification and limits

- Fresh PostgreSQL suite before the source commit: 44 passed in 16.006 seconds; separate test database created/destroyed.
- Django database and migration checks passed; no schema drift. Ruff lint/format, djLint (11 templates), npm source formatting/build, pip check, and npm audit passed; zero npm vulnerabilities.
- 490 relative links/anchors across the 20 pre-publication documents passed; screenshot visually inspected; all 39 staged files scanned for actual private seed/database passwords and Django secret, with none found. The staged screenshot matched its original bytes.
- Source requirements/member files, LF scope, and all 18 original T04–T21 task rows were unchanged. Earlier browser results remain in their actual [login](minimal-branded-login-10-17-2026.md), [wave](login-bottom-wave-10-17-2026.md), and [role/error](minimal-role-and-error-pages-10-17-2026.md) snapshots. CI and a new browser run were not performed for this documentation receipt.
- Private `.env.local` remains ignored and byte-for-byte preserved; generated assets/dependencies were excluded. Stash `781af4165b93d2a4b4327997eef7334c096b6dd6` remains a backup. All 214 receipt links/anchors across three documents, Markdown fences, whitespace, scope, both source co-author trailers, secret exclusion, and all 18 feature task rows passed verification. Final commit/remote state is verified before handover.

## Next action

Jerome reviews the published branch before separately requesting a PR/main integration. No feature ownership or prerequisite gate changed. T05/T06/T07/T09 retain their existing readiness; later workflows, live dashboards/reports, full T20 layouts, and T21 dataset remain pending under their canonical backlog dependencies. Keep the stash until satisfied with the restored work.
