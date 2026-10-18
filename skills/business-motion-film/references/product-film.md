# Product-Film Mode Reference (Real App UI)

Distilled motion doctrine adapted from `kaventro/motion-designer@0cf0ba9` (MIT).
Used when the user requests a launch film, teaser, or product promo of a real application interface (iOS, macOS/Windows/Linux desktop, Electron/Tauri, web app) rather than an abstract business commercial.

## 1. Real App Interface & Device Boundaries

- **Real Code or Screenshots Only**: Rebuild screens directly from repository components, styling tokens, icons, and layout, or use verified repository screenshots (e.g. 3× iOS simulator captures or desktop snapshots). Generic mockups, stock UI, and ungrounded templates are rejected.
- **Mobile in Device Chrome**:
  - Screen dimensions: 402 × 874 pt (iPhone 16 Pro / 17 Pro standard), corner radius `R: 55`, bezel: 5 pt, titanium frame: 3 pt.
  - Overlay chrome: Status bar (time 9:41, cellular, wifi, battery), Dynamic Island (125 × 37 pt at `y: 11`), Home indicator (134 × 5 pt at `y: 861`). Set `--sb` to `#fff` over dark scenes.
  - Framing: Both side edges must remain visible in frame (`s ≤ 3.3` on 1440 stage); crop only vertically for close-ups. Never display app UI full-bleed without device context.
  - Legibility: 13 pt app text requires camera scale `s ≥ 1.55` (~20 px on stage).
- **Desktop in Window Chrome**:
  - Screen dimensions: 1512 × 982 pt (14" laptop standard) or floating application window (`WIN` e.g. 1200 pt).
  - Window chrome: Title bar, native window controls (traffic lights red `#FF5F56`, yellow `#FFBD2E`, green `#27C93F` on macOS; platform caption controls on Windows/Linux).
  - Pointer choreography: Arrive one beat early, click squarely on the beat, pause for UI reaction before moving. Typing pace: 60–90 ms per keystroke; hide cursor while typing. The cursor moves only when demonstrating intentional interaction—never wander or idle-wiggle.
  - Legibility: 13–14 pt desktop labels need zoom `1.15–1.9` on the active pane. Never cut text labels at frame edges.
- **No Style Kits**: Do not adopt foreign upstream style kits (Meadow, Midnight, Warm Ink, Field Guide, Paper and Ink, Color Block). Derive visual tokens directly from the app itself or from `emil-design-eng` motion principles.

## 2. Deterministic Frame Contract: `seek(t)`

- **Pure Function of Time**: Every scene property, layout transform, spinner, caret, and kinetic element must be a pure deterministic function of elapsed time `seek(t)`.
- **Prohibited Primitives**: Zero timers (`setTimeout`, `setInterval`), zero `Date.now()`, zero `Math.random()`, and zero asynchronous state carryover between frames. Zero CSS transitions or CSS `@keyframes` animations.
- **Seam & Path Consistency**: The timeline loop must close cleanly (the frame immediately following the end must match the initial frame). Seeking to time `t` from any order or direction must yield bit-identical pixels.

## 3. Beat-Map & Sound Direction

- **Beat-Driven Choreography**: Map the story across tempo (BPM), bars, and musical drops.
  - Calculate beat timestamps: `t_beat = (60 / BPM) * beat_index`.
  - Align scene cuts to bar boundaries (e.g. every 4 or 8 beats).
- **Drop Synchronization**: Core product actions, key reveals, and major value transitions must land squarely on musical drops.
- **Micro-Drift on Holds**: During a hold scene, apply a subtle camera ease-in (2–3% zoom drift over the hold) so the screen never looks like a frozen video frame.
- **Soundtrack Priority**: Prioritize the user-provided audio track.
- **Optional Heavy Models**: Heavy audio generation models (ACE-Step ~11 GB) and speech synthesizers (Chatterbox, Kokoro) are `OPTIONAL_POINTER`. Never execute upstream `install.sh` and never auto-download models. When absent, report `NOT_CONFIGURED`.

## 4. Rights, Claims & Data Honesty

- **Real Features Only**: Feature claims must reflect real code paths in the repository. Opt-in features (notifications, AI, permissions) appear as user-enabled actions, not default states.
- **Fictional Plausible Data**: All names, merchants, amounts, balances, dates, and account numbers must be fictional and plausible. Never use real personal or customer data.
- **Audio Rights & Licensing**:
  - Record audio title, artist, source URL, and license terms in the evidence ledger.
  - Prioritize user-provided tracks, CC0, or verified MIT-licensed stems. Never use unlicensed copyrighted music.
  - Generated sound effects for UI clicks and transitions should be synthetic or licensed.
- **Marketing Film vs App Store Preview**:
  - Marketing films (built via HTML/hyperframes) are tailored for product launches, landing pages, Twitter/X, and social media.
  - If the user specifically requests an Apple App Store App Preview (Guideline 2.3.4), note that it requires raw simulator video captures without external device frames, exactly 30 fps, and portrait 886 × 1920 px.

## 5. The Four-Still Approval Gate

Before writing implementation code or starting a build, you must define the story beats and present four distinct still frames for explicit user review:
1. **Opening Still**: Hook and initial device entrance.
2. **Key Product Moment Still**: The primary feature or workflow shown in action.
3. **The Drop Still**: The pivotal climax or key result landing on the musical drop.
4. **Final Frame Still**: The concluding lock-up, product mark, and call to action.

*Halt Gate:* Without explicit approval of the four stills from the user, stop and do not proceed to build.

## 6. QA Loop & Mechanical Ledger

- **Contact Sheets & Verification**:
  - Timeline overview every 0.5 s, cuts/transitions every 0.05 s, full-scale text review (`--scale 2`), and phone-width overview at 360 px (`--phone`) to verify legibility in mobile feeds (note: `--scale` and `--phone` are flags of upstream helper scripts `sheet.py` / `render.mjs`, which are not vendored into the overlay).
  - Motion blur for fast camera moves or whips: average subframes across a 180° shutter (`--blur 8`, also a flag of upstream helper scripts `sheet.py` / `render.mjs`, which are not vendored into the overlay). Preview without blur; render finals with it.
- **Scored Review Gate**:
  - Evaluate stretches across 7 criteria scored from 1 to 10: `hook`, `readability`, `motion`, `variety`, `composition`, `sync`, and `accuracy`.
  - Quality gate requires every stretch to report `clean` with every dimension scoring ≥ 8 before final release.
- **Failure Catalogue**: Audit against common flaws:
  - Text cut off, unreadable on mobile, or truncated (`"Savi"`, `"Uncategori…"`).
  - UI displayed full-bleed without device framing.
  - Arbitrary crossfades between unrelated scenes instead of physical UI transitions.
  - Cursor moving without purpose or clicking empty space.
  - Invented features or claims not present in the codebase.
- **Evidence Ledger (`FACT:`)**:
  - `FACT:` Verified local MP4 output file path and byte size.
  - `FACT:` Presence or absence of `ffmpeg` and `ffprobe`.
  - `FACT:` Presence or absence of headless Chrome / Chromium.
  - `FACT:` Integrated audio loudness (LUFS) and true peak (dBFS) if audio is rendered.
- **Tooling Gate**: If `ffmpeg` or `chromium` is missing from the local environment, report `NOT_CONFIGURED`. Never emit a false `PASS`.

## 7. Rendering Engine Hierarchy

- **Default Engine**: Rendering is executed through `hyperframes` (deterministic HTML/CSS/canvas to seekable frames). 18-second brag cards remain strictly in `skills/hyperframes/references/brag.md`.
- **Alternative Upstream Pipeline**: Direct DevTools-driven Chrome frame capture into ffmpeg is used only when explicitly requested by the user and Chrome is verified available on the machine.

## 8. Neighbor Boundaries

- Spoken Indonesian app walkthroughs and demo contests: strictly `id-demo-video`.
- 2D timeline scrollytelling websites: `scroll-craft`.
- Continuous camera fly-through 3D worlds: `scroll-world`.
- UI motion physics and micro-interactions: `emil-design-eng`.
- Product UI atom design and implementation: `impeccable` and `found-this-design`.
- Gateway multi-model routing: `ninerouter`.
