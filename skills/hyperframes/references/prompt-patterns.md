# Code-Video Prompt Patterns & Gallery Adaptation

Reference guide for translating viral code-driven video prompts into deterministic HyperFrames compositions.

## Status: POINTER_ONLY

Upstream index: [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) (snapshot `3d54892e2ae5b0e8d337171e6508bba4cec01ab8`, dated 2026-09-29).
Distribution notice: Upstream curation indexes third-party social video posts whose respective authors retain rights. No upstream prompts, datasets, or video media are vendored into this distribution.

### Snapshot Facts (2026-09-29)
The upstream gallery catalogues 475 community creations across multiple domains:
- Categories: motion (288), interactive (70), explainer (62), 3D (55).
- Tech tags: canvas (336), svg (193), threejs (141), shader (100), gsap (81).
- Coverage: 196 partial or conceptual prompt fragments recorded.

## Translating One-Line Viral Prompts to HyperFrames Briefs

Viral prompts frequently say "generate an animation of X" without technical specs. Before writing HTML/CSS/JS, expand the brief into explicit deterministic parameters:

1. **Duration & Frame Budget:** Fix exact runtime (typically 15s to 25s) and frame rate (`data-fps="30"` or `"60"`).
2. **Aspect Ratio & Resolution:** Lock viewport dimensions on the root `[data-composition-id]` (`1920x1080` for 16:9, `1080x1920` for 9:16).
3. **Beat Sheet & Camera Positions:** Break timeline into timestamped scenes using `<section class="clip" data-start="..." data-duration="...">`.
4. **Style & Visual Identity:** Extract palette, fonts, and radii from project `DESIGN.md` rather than generic AI gradients.
5. **Tech Tag to Implementation Mapping:**
   - `canvas` / `svg`: Procedural 2D vector elements parameterized by seek time `t`.
   - `gsap`: Timeline instances created paused, scrubbed via `.seek(t)`.
   - `threejs` / `shader`: WebGL scenes rendered synchronously on `seek(t)` using fixed random seeds.
6. **Audio Alignment:** Plan cue markers for voiceover or soundtrack stems.

## Safety & Determinism Constraints

- **Seek-Driven Render over Screen Recording:** Never tell users to "screen record the browser window". Always compile to declarative HyperFrames composition and run `npx hyperframes render`.
- **Intellectual Property:** When prompt recipes mention external assets, use only user-provided or clearly licensed local media. Never incorporate third-party trademarks or proprietary logos without license.
- **Model-Agnostic Execution:** Do not condition prompt execution on specific proprietary LLM brand names. Model identifiers in this runtime remain opaque.

## Quality Gates & Verification

1. **Contact Sheet Audit:** Capture and inspect raster frames at 0%, 25%, 50%, 75%, and 100% of duration to verify progression.
2. **Determinism Check:** Perform two sequential test renders and compare SHA-256 hashes of sample frames; identical inputs must yield identical pixel bytes.

## Routing Handoffs

- Commercial SaaS ad, product film, or sample reel: `/business-motion-film` (renders via HyperFrames).
- Fast 18-second milestone launch card: [references/brag.md](brag.md).
- Indonesian spoken app walkthrough: `/id-demo-video`.
- Photoreal VFX or studio imagery: `/visual-studio`.
- Interactive or playable widgets: Not video compositions (`video_html`). Route to `/impeccable` for product UI or `/prototype` for experiments.
