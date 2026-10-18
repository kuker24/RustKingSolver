---
name: business-motion-film
description: Plan, storyboard, and quality-check premium short business commercials, product launch films (including real app UI product-film mode), sample reels, and explainers with code-built motion (HTML/GSAP/Three.js) and an independent critic Gauntlet. Render through hyperframes. Not for narrated Indonesian app tours (id-demo-video), 2D scrollytelling (scroll-craft), or continuous camera fly-through landings (scroll-world).
compatibility: opencode
license: MIT
---

# business-motion-film

Make short (15–40s) commercial launch films and product hero videos that sell a real business outcome. Claims must be true; visual execution is ambitious. Render executes through `hyperframes`.

Intent: `launch_film`. Product hero Three.js patterns live here (formerly `img2threejs`). Continuous 3D world scroll stays `scroll-world`. 18s brag cards stay `skills/hyperframes/references/brag.md`. Indonesian narrated app tours stay `id-demo-video`.

## Boundaries & Handoffs

| Request | Primary Route |
|---|---|
| Business commercial, launch film, pitch video, sample reel | **`business-motion-film`** |
| Deterministic frame rendering engine / MP4 pipeline | `hyperframes` |
| Indonesian voiceover application walkthrough / demo lomba | `id-demo-video` |
| Continuous camera 3D fly-through, diorama landing | `scroll-world` |
| 2D timeline scrollytelling website | `scroll-craft` |
| Photoreal stills, lifestyle ads, UGC raster packs | `visual-studio` |

## Pinned Upstream References

Read only the upstream reference needed for the current step:

- **Product-Film Mode (Real App UI)**: `references/product-film.md` (upstream `kaventro/motion-designer@0cf0ba9`)
- **Storyboarding & Motion Grammar**: `references/motion-grammar.md`, `references/launch-film-notes.md` (upstream `echris6/motion-video-kit@255562b`)
- **3D Components & Product Hero Realism**: `references/three-js-patterns.md`, `references/product-hero-realism.md`
- **Review & Gauntlet**: `references/gauntlet.md`, `references/critic-prompts.md`, `references/quality-bar.md`
- **Audio & Mix Rules**: `references/audio.md`
- **Offers & Business Logic**: `references/business-offers.md`

## Product-Film Mode (Real App UI)

Use this mode when the user requests a launch film, teaser, or product promo of a real application interface (iOS, desktop macOS/Windows/Linux, Electron/Tauri, web app) rather than an abstract business commercial.

1. **Grounded Interface in Device Frame**:
   - Reconstruct screens directly from repository source code, design tokens, or verified screenshots. Generic mockups and ungrounded templates are rejected.
   - Mobile apps remain contained inside an iPhone frame with dynamic island or status bar for the entire film; never display app UI full-bleed.
   - Desktop apps remain contained inside their application window; the cursor moves only when demonstrating an intentional user interaction.
   - Never adopt upstream foreign style kits (Meadow, Midnight, etc.); style from repository tokens or `emil-design-eng` motion principles.
2. **Deterministic Frame Contract (`seek(t)`)**:
   - Every layout property, camera move, and text element is a pure function of time `seek(t)`.
   - Zero timers (`setTimeout`, `setInterval`), zero `Date.now()`, zero `Math.random()`, and zero CSS transitions or `@keyframes` animations.
   - The timeline loop must close cleanly, and identical frames must render regardless of seek trajectory or order.
3. **Beat-Map & Audio Priority**:
   - Structure narrative along tempo (BPM), bars, and musical drops; pivotal feature reveals must land on the drop.
   - Prioritize the user-provided audio track.
   - Upstream heavy models (ACE-Step ~11 GB, Chatterbox, Kokoro) are `OPTIONAL_POINTER`. Never run upstream `install.sh` and never download models. Absent models report `NOT_CONFIGURED`.
4. **Four Stills Approval Gate**:
   - Before building, you must present four explicit still frames for user approval: (1) Opening / hook, (2) Key product moment in action, (3) The Drop climax, and (4) Final lock-up.
   - Without explicit user approval of these four stills, halt and do not proceed to build.
5. **QA Loop & Mechanical Evidence (`FACT:`)**:
   - Review contact sheets across transitions and verify against the failure catalogue (truncated labels, full-bleed UI, arbitrary crossfades, wandering pointer, unverified claims).
   - Done-gate requires `FACT:` citations: local MP4 file path, presence/absence of `ffmpeg` and Chrome, and measured loudness (LUFS) if audio is included.
   - If `ffmpeg` or Chrome is absent, report `NOT_CONFIGURED`; never emit a false `PASS`.
6. **Rendering Pipeline**:
   - Primary default rendering engine remains `hyperframes` (18s brag cards remain in `skills/hyperframes/references/brag.md`).
   - The upstream Chrome DevTools render pipeline is used only when explicitly requested and Chrome is present.

## The Gauntlet & Honesty Gates

1. **Truth on Business Claims**: Never invent testimonials, ratings, warranties, savings, or customer logos. Unverified concept ads must display a clear concept disclaimer.
2. **Builder ≠ Judge**: The builder never grades its own render. Full cuts and components go to an independent critic that inspects only the rendered frames, brief, and rubric.
3. **Item-by-Item Ledger**: Maintain a Gauntlet ledger: critic finding → change made → measured before/after.
4. **Mechanical Proof (FACT)**: Done-gate requires `FACT:` citations: frozen-time measurement (`<=0.2s`), integrated loudness (e.g. `-19` to `-30 LUFS`, true peak `<= -1 dBFS`), and verified artifact file paths.
5. **Tooling Requirement**: Requires local `ffmpeg` and `ffprobe` for render/audio measurement. If absent, report `NOT_CONFIGURED`; never fake a PASS.
