# Single-row header and account dropdown

- Date: October 17, 2026, Asia/Manila.
- Owner: Jerome, explicit header/profile UI request; Codex assistance. Alex's T04/T05 logic remains credited and preserved.
- Scope: UI-08, following the local UI-07 work on `jerome` at base `7a80257`. Uncommitted and **Not integrated**; no commit, push, PR, or merge performed.

## Current outcome

The shared header places brand, primary navigation, and the account disclosure in one desktop row at 1280px and above. Smaller widths keep brand/account together and wrap primary links beneath them. Sticky navigation, light branding, active section, shared messages, and existing account-management functionality remain.

The dropdown trigger renders uppercase surname and first initial, followed by the stored role. Opening it reveals My profile with the supplied role avatar, then the existing CSRF-protected POST logout. Native details/summary supplies keyboard activation without requiring JavaScript; the small account-menu module adds Escape dismissal with focus restoration and outside-click dismissal. Profile moved from the borrower's primary navigation into this shared dropdown.

My profile displays only the signed-in account's identity, email, role, and contact details. GET/HEAD are supported; POST returns 405. No account ID is taken from the URL/query for this lookup. Administrator route: `operations:profile`, `/manage/profile/`; borrower route: `portal:profile`, `/portal/profile/`. Profile editing/uploads/password changes are not implemented. T09 and full T20 acceptance retain their assigned owners and prerequisites. Eleven module destinations remain placeholders after replacing the portal profile placeholder.

## Relevant files and interfaces

- [Workspace](../templates/components/workspace.html), [admin base](../templates/operations/manage/base.html), [portal base](../templates/accounts/portal/base.html): shared row and role-specific account-menu profile destination.
- [Account menu](../templates/components/account_menu.html), [display name](../templates/components/account_name.html), [avatar](../templates/components/profile_avatar.html), [profile presentation](../templates/components/profile.html): reused presentation components.
- [Account-menu module](../static/js/account-menu.js): DOM-only enhancement, compiled by the existing wildcard build to `build/account-menu.js` (504 bytes). No new dependencies or browser HTTP library.
- [Admin views](../operations/views.py)/[routes](../operations/urls.py) and [portal views](../accounts/portal_views.py): role-protected read-only own-profile handlers. The current account's related Profile is resolved explicitly in the view.
- [Admin profile template](../templates/operations/manage/profile.html), [portal profile template](../templates/accounts/portal/profile.html): extend existing role layouts; T09 editing remains pending.
- User-provided [admin avatar](../static/images/default-profile-admin.png) and [basic-user avatar](../static/images/default-profile-user.png) are used unchanged. The [asset inventory](../docs/third-party-dependencies.md#supplied-assets-and-optional-inspection-tooling) records their supplied provenance and unknown original license; no team-authorship/MIT claim is made for third-party artwork.
- [HTTP contract](../docs/api_spec.md#status-and-interface-choice), [coding guidance](../docs/coding-standards.md#tailwind-styling-pattern), and [DEV](../DEV.md#browser-interactions) describe the current behavior. [Navigation tests](../operations/tests/test_navigation.py) include profile isolation and POST rejection.

## Verification

- Full PostgreSQL suite: **61 tests passed**, 18.226 seconds, including the existing T05 tests, navigation/access checks, and the new own-profile check with supplied account IDs and attempted updates. Separate test database created and destroyed.
- Django database check: no issues. Migration drift: no changes. Applied migrations check: passed. No schema or seed changes.
- npm build/format check passed; account-menu.js and existing font-preview output both compile. Ruff lint/format passed (126 Python files); djLint passed (28 templates); pip check and whitespace check passed.
- No dependency declarations/locks changed. This task did not repeat npm installation/audit; the preceding UI-07 verification recorded zero audit vulnerabilities.
- Chrome fresh preview on `127.0.0.1:8013`: single-row desktop layout at 1704px/1280px, 375px mobile layout, no page-level horizontal overflow, dropdown bounds within viewport, formatted names/roles, both default images loaded, My profile for each role, Enter/Escape/outside-click dismissal and focus restoration, and both roles' dropdown logout verified. The native dropdown was opened before clicking its normally hidden logout control.
- Viewport override reset, temporary preview tab closed, preview server stopped; user's existing development server left alone.
- All 482 relative links/anchors and Markdown fences across 11 affected documents passed validation. Alex's forms/account views/queries/services and existing account/authentication tests have no source diff; dependency manifests/locks are unchanged and Git's index is empty. No CI, editing/upload workflow, or full T20 acceptance claimed.

## Next action

Jerome reviews the uncommitted UI-07/UI-08 diff before separately authorizing publication. Feature owners preserve the shared header and account menu. Ellyssa extends the existing own-profile presentation with validated T09 editing once authorized; no role or account-activation fields become self-editable.
