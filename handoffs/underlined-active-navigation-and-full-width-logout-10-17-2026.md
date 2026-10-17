# Underlined active navigation and full-width logout

- Date: October 17, 2026, Asia/Manila.
- Owner: Jerome, explicit navbar styling request; Codex assistance.
- Scope: UI-08 styling follow-up on `jerome`, on top of the uncommitted UI-07/UI-08 work. Uncommitted and **Not integrated**; no commit, push, PR, or merge performed.

## Current outcome

Primary navigation links no longer look like buttons: the background fill and rounded corners are removed. The active link (`aria-current="page"`) uses the accent color, bold weight, and a 2px underline offset beneath the text. Inactive links stay slate/medium and show a light slate underline on hover. Routes, test IDs, and active-section resolution are unchanged.

The account dropdown's Log out button now spans the panel width like My profile, with the same padding, hover background, and left alignment. Its icon leads and occupies the avatar's 40px width so both labels align. POST/CSRF behavior is unchanged. `account_name.html` needed no change.

## Relevant files

- [Navigation link](../templates/components/navigation_link.html): active/inactive text styling.
- [Logout](../templates/components/logout.html): full-width button; currently included only by the [account menu](../templates/components/account_menu.html).

## Verification

- `npm run build:css` passed; compiled `static/build/app.css` contains the new underline/decoration utilities.
- `djlint templates/components --check`: 10 files, no changes needed.
- `manage.py test --noinput`: **61 tests passed** on PostgreSQL.
- Not run: browser visual check, full-repo djLint/Ruff (no Python changed), npm format check (no JS/CSS source changed).

## Next action

Jerome reviews the appearance in the browser together with the rest of the uncommitted UI-07/UI-08 diff before authorizing publication.
