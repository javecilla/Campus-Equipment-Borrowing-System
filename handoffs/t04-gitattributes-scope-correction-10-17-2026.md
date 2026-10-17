# T04 `.gitattributes` scope correction

- Owner: Alex Enrico Cayanan (`@AlexCayanan`), with Codex assistance.
- Date/time: October 17, 2026, Asia/Manila (UTC+08:00).
- Task: T04 publication follow-up only—compare PR #9's committed line-ending rule with the isolated candidate and prepare the smallest correction.
- Delivery: PR #9 is merged into main at `cb96319991cd42a0dbd3ab88243fdda2e85f2d66`. This correction is committed separately on `alex` but is not pushed; publishing it requires a new PR. The correction is **Not integrated into main**.

## Outcome

The isolated T04 candidate tested this extension-specific policy:

```gitattributes
# Prettier owns these text formats and is configured to require LF output.
*.css text eol=lf
*.js text eol=lf
*.json text eol=lf
*.mjs text eol=lf
```

Commit `7ae5e87` instead contains `* text=auto eol=lf`, which applies the LF rule to every detected text file. During later commit preparation, Codex recreated `.gitattributes` from memory as the global rule and validated that substituted file instead of comparing its exact content with the isolated candidate. This was a commit-preparation error, not a result of the isolated verification.

[`.gitattributes`](../.gitattributes) now matches the isolated candidate exactly. PR #9 and its merge commit retain the broader rule; this separate correction must be published through a new PR rather than amending history.

## Verification performed for this correction

- Exact five-line candidate content comparison: passed.
- Line-ending inspection: zero CRLF sequences and five LF line endings in the working file.
- `git check-attr text eol`: `text: set`, `eol: lf` for the configured CSS, JavaScript, JSON, and MJS paths; Markdown, Python, HTML, and `.gitattributes` itself are unspecified.
- `npm run format:check`: passed for all configured Prettier-owned files; npm repeated the existing non-fatal `min-release-age` warning.
- `git diff --check`: passed for the complete working tree.
- Git synchronization: fetched `origin`; verified `7ae5e87` is an ancestor of PR #9 merge `cb96319` with no tree delta; fast-forwarded `alex` while preserving the complete dirty status, tracked diff, and empty index.
- Staged scope: exactly `.gitattributes`, this handoff, and correction-only hunks from `HANDOFF.md` and `docs/tasks.md`; excluded MCP/setup, preview, lockfile, dependency, generated, private, and IDE paths.
- `git diff --cached --check`: passed before commit.
- No amend, push, force-push, new PR, merge, dependency change, or generated-file change was made for this correction.

The Django/authentication suite was not rerun because this correction changes only Git checkout line-ending attributes and exactly restores the already isolated-and-tested policy. The existing T04 authentication results remain in the [implementation handoff](alex-t04-authentication-and-access-10-17-2026.md).

## Preserved work and next action

Existing MCP/setup, preview, lockfile, IDE, and other working-tree changes were not edited or staged. The next action is a separately authorized push of this correction commit and a new PR into `main`; do not amend `7ae5e87`, force-push, or start T05 as part of this follow-up.
