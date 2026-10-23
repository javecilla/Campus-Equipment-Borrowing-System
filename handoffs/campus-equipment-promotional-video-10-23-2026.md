# Campus Equipment promotional video

Date: October 23, 2026 (Asia/Manila). Jerome requested the artifact; Codex authored the composition and original score and generated the English voiceover. Local branch: `jerome`, starting at `6c0d3426b2472533fd18b312af4fe21d7656adcb`. Changes are uncommitted; no publication or main integration is requested or claimed.

## Scope and artifact

The authorized deliverable is a 30-second promotional film using existing system screenshots and the [screenshot gallery](../docs/system-screenshots.md)/[role manual](../docs/user-manual-guides.md), with background music and narration. The user's [HyperFrames reference examples](https://hyperframes.heygen.com/examples) inform the beat-led editing and product-film direction; no reference footage, avatar or soundtrack is copied.

The completed [MP4](../output/campus-promo/campus-equipment-promo.mp4) and [portable editable source ZIP](../output/campus-promo/campus-equipment-promo-project.zip) are available locally. The editable project is [output/campus-promo](../output/campus-promo/README.md), an ignored artifact folder. Its `DESIGN.md`, `index.html`, `film.css`, `film.js`, pinned package/lock and launcher define a 1920 × 1080, 30 fps, eight-scene film. Original screenshot files remain unchanged; nine used screenshot copies match their sources by SHA-256. Sources, voice/music provenance and evidence are retained with the project. The screenshot scenes use fictional demonstration records and do not represent a single continuous transaction.

The soundtrack combines a project-original 120 BPM D-major instrumental with synthesized Kokoro-82M `af_heart` English narration. Phrase-level SRT captions and separate audio stems are available. This is a supplementary promotional artifact: T30 packaging and T31's 12-minute live team demonstration/3-minute Q&A and rehearsal remain Not started under their existing gates.

## Verification

- HyperFrames 0.8.186 `check`: no lint/runtime/layout/contrast errors or warnings; 62 contrast checks pass. The newer CLI's separate craft advisory flags the intentional first-frame entrance build and small metadata/browser-label text. Main headings and narration-supporting body copy are substantially larger. These are reviewed design choices within the user-supplied skill's timing/type guidance.
- Explicit `validate`: `ok=true`, no errors/warnings, 60 contrast checks and zero contrast failures. Explicit `inspect` at all eight hero times: zero errors, warnings or issues. Evidence is in the project's `qa/` folder.
- Eight scene hero frames were visually reviewed, including a second independent review. Awkward title wrapping, a report-column crop and the approval-page top crop were corrected. The final scene uses a push transition to avoid cross-scene text overlap.
- Audio master: exact 30.000 seconds, stereo 48 kHz/24-bit; −17.9 LUFS integrated, −1.3 dB true peak, 4.6 LU loudness range. All eight narration segments finish within their scene windows. No clipping is reported.
- The supplied older animation-map helper was attempted with adapters for the newer CLI's bundled producer exports, raw page initialization and duration access. It could not discover the raw timeline registry and produced no report; no successful map is claimed. The newer static `keyframes` command also reports no external-script tweens. Choreography was instead checked directly in eight exported hero frames and 21 exported transition frames, with no blank transition or unintended collision observed.
- HyperFrames high-quality, single-worker render completed successfully in 2m 18.9s. The final file is 12,106,904 bytes: H.264, 1920 × 1080, 30/1 fps, 900 frames, exactly 30.000000 seconds; stereo AAC, 48 kHz, exactly 30.000000 seconds. Full FFmpeg decode succeeds. Encoded audio remains −17.9 LUFS with −1.2 dB true peak and 4.6 LU loudness range.
- The portable source ZIP has 46 files and is 30,241,258 bytes. Every archived file matches its source SHA-256 manifest and ZIP CRC verification passes. Dependency folders, virtual environments, caches and private environment files are excluded. This is the video source archive, not the T30 course submission ZIP.
- Background [HyperFrames Studio](http://localhost:3017/#project/campus-promo) is running locally, with its status and HTTP 200 verified in the same unrestricted user environment used to launch it. The app-panel open request is queued. `node run.mjs preview --stop` from the project folder stops it. Delivery links, final stream specifications and `git diff --check` pass.

No Django commands, application tests, database connection, schema/data operation, media-store write or original screenshot edit was performed. The database was not used. Application regression results in prior handoffs are not presented as new checks for this artifact.

## Next action and ownership

Jerome can review the completed MP4, edit the source in HyperFrames Studio and optionally load the provided SRT captions. No participant feedback or approval is inferred. Existing T25/T28/T30/T31 owners, prerequisites and completion evidence remain in the [backlog](../docs/tasks.md). No application work, commit, push, external message or hosting is authorized by this video request. The ignored local artifacts require the supplied source ZIP when sharing; they are not available from Git or main.
