# Shared favicon and page metadata

- Owner: Jerome Avecilla (`@javecilla`), with Codex assistance.
- Date/time zone: October 16, 2026, Asia/Manila (UTC+08:00).
- Scope: UI-01 follow-up; explicitly requested supplied browser icons and metadata in the shared template.
- Branch/integration: `jerome`, uncommitted over `8668ff8`; **Not integrated**. No commit, push, dependency, schema, or application-data changes. Existing local work preserved.

## Outcome

[base.html](../templates/base.html) links the supplied ICO, 16px/32px PNG icons, Apple touch icon, and manifest using Django static URLs. It supplies description, application name, and theme color metadata. Feature templates can override `meta_description` alongside the existing `title` block. [DEV.md](../DEV.md#frontend-assets-tailwind-and-axios) lists the shared blocks/assets.

The supplied [manifest](../assets/images/favicon/site.webmanifest) now identifies Campus Equipment and uses relative Android icon paths, avoiding requests to nonexistent site-root image URLs. Its theme color matches the template. All six supplied icon images remain unchanged. This integrates favicon/manifest assets; it does not add offline behavior or claim installable-PWA support.

## Actual verification

- Visually inspected the supplied 192px icon.
- All three Django templates pass djLint. Prettier source checks and an explicit JSON-parser check of the web manifest pass after formatting it. Django system checks pass.
- Real Django client renders `/` and `/test` with description metadata and all five icon/manifest links. All seven supplied files, including both manifest-referenced images, are found and served with exact source bytes. A real child-template render overrides the description correctly.
- Chrome reload confirms the expected metadata and static icon/manifest URLs in the running page. Native tab-strip icon rendering was not separately inspected.
- Python/runtime code and dependencies were unchanged by this task. Foundation tests were not rerun for this template/asset-only change; their previous results remain in earlier handoffs.
- Final integrity checks pass: 533 relative links/anchors across 38 Markdown files, balanced fences/details, private-value scan across 211 shareable files, preserved source requirements/member files and application task rows, dependency inventory/lock consistency, and Git whitespace checks.

## Next action

Jerome can refresh either development page to use the shared icon. Feature owners extend the common shell and override the description when needed. Review local changes before separately authorizing publication. Alex/T04 and Jerome/T06 readiness remains unchanged.
