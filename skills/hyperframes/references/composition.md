# HyperFrames Composition Architecture

HTML, CSS, and SVG/Canvas structure for seekable deterministic video compositions.

## The Declarative Timeline Contract

HyperFrames binds the composition lifecycle directly to semantic HTML data attributes. Rather than invoking ad-hoc runtime stepping functions, the engine compiles declarative timing markers and steps through each frame deterministically.

### 1. Root Composition Definition

The root element declares the composition boundary, resolution, and default frame rate:

```html
<main
  id="main-comp"
  data-composition-id="main-comp"
  data-width="1920"
  data-height="1080"
  data-fps="30"
>
  <!-- Timed clips and tracks -->
</main>
```

### 2. Timed Clips (`class="clip"`)

Individual scenes or layers use `class="clip"` along with duration attributes:

```html
<!-- Absolute timing -->
<section
  id="scene-intro"
  class="clip"
  data-start="0"
  data-duration="4"
  data-track-index="0"
>
  <h1>Product Launch</h1>
</section>

<!-- Relative timing: start relative to another clip ID -->
<section
  id="scene-demo"
  class="clip"
  data-start="scene-intro"
  data-duration="8"
  data-track-index="1"
>
  <h2>Key Features</h2>
</section>
```

- `data-start`: Absolute second (e.g. `"0"`, `"4.5"`) or relative clip reference (e.g. `"scene-intro"`, `"scene-intro - 0.5"` for crossfades).
- `data-duration`: Duration of the clip in seconds.
- `data-track-index`: Studio timeline row lane (optional; rendering order is governed by CSS `z-index`).

### 3. Nested Compositions

Reusable sub-scenes or modules can be nested using `data-composition-src`:

```html
<div
  id="lower-third"
  class="clip"
  data-composition-src="./components/lower-third.html"
  data-start="1.5"
  data-duration="5"
  data-track-index="2"
></div>
```

## Determinism & Seekable Animation

Frame capture steps through `t = frame / fps` without real-time wall-clock playback:

1. **Paused & Seeked GSAP:** All GSAP timelines must be paused on creation and scrubbed via `.seek(t, false)`. Never call `.play()`.
2. **Zero Wall-Clock Clocks:** No `Date.now()`, `performance.now()`, `requestAnimationFrame`, or `setInterval`.
3. **No Unseeded Randomness:** `Math.random()` produces divergent frames across runs. Use a seeded pseudo-random number generator (e.g. Mulberry32) if procedural noise is required.
4. **No Mid-Render Fetch:** Preload all fonts, images, and JSON data before frame 0. Dynamic network fetches during capture cause dropped frames or non-deterministic blank flashes.

## Viewport & Resolution Presets

- **16:9 Landscape (YouTube / Presentation):** `data-width="1920"` `data-height="1080"`
- **9:16 Vertical (Reels / TikTok / Shorts):** `data-width="1080"` `data-height="1920"`
- **1:1 Square (Feed):** `data-width="1080"` `data-height="1080"`

Standard reset styles:
```css
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: #000;
  -webkit-font-smoothing: antialiased;
}
[data-composition-id] {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
.clip {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
```
