# Interface Feel: Tactile Polish Checklist

Tactile polish and interface feel principles merged from `make-interfaces-feel-better`. Applied in tandem with Emil Kowalski's motion doctrines to elevate static UI into interfaces that feel physically responsive, stable, and crafted.

## 1. Typography & Number Stability

- [ ] **Tabular Figures for Dynamic Numbers**: Apply `font-variant-numeric: tabular-nums` (Tailwind: `tabular-nums`) to counters, timers, financial figures, metrics, and data tables. Prevents horizontal jitter and layout jitter when numbers increment.
- [ ] **Text Wrapping Balance**: Use `text-wrap: balance` on headlines and card titles (up to 2–3 lines) to avoid trailing orphan words. Use `text-wrap: pretty` on paragraph bodies to prevent single-word last lines.
- [ ] **Proportional Leading**: Tighten line-height on large display titles (`leading-tight`, ~1.1–1.2); open up body text line-height (`leading-relaxed`, ~1.5–1.6) for comfortable scanning.
- [ ] **Letter-Spacing (Tracking)**: Apply subtle negative tracking (`letter-spacing: -0.015em` / `-0.02em`) on large bold display headers (>=24px) to increase typographic cohesion; maintain neutral or slight positive tracking (`0.02em`) on small all-caps badges/subtitles.

## 2. Hit Targets & Touch Ergonomics

- [ ] **Minimum 44×44px Hit Target**: Even when an icon button is visually 20×20px or 24×24px, expand the interactive target to at least 44×44px using negative margins or an invisible pseudo-element:
  ```css
  .icon-button::after {
    content: "";
    position: absolute;
    inset: -10px;
  }
  ```
- [ ] **Cursor Discipline**:
  - Interactive clickable items (`<button>`, `<a>`, `<select>`, custom toggles): `cursor: pointer`.
  - Non-interactive cards and containers: `cursor: default`.
  - Disabled actions: `cursor: not-allowed` (with reduced opacity and disabled attributes).
- [ ] **Prevent Selection on Rapid Clicks**: Apply `user-select: none` on interactive badges, toggle switches, steppers, and buttons to prevent annoying text selection highlighting during fast repeated presses.

## 3. Surfaces, Corners & Layered Depth

- [ ] **Concentric / Nested Border Radius**: Outer and inner corners must share the same visual center. Use the nesting formula:
  $$\text{inner\_radius} = \max(0\text{px}, \text{outer\_radius} - \text{padding})$$
  ```css
  .card {
    border-radius: 16px;
    padding: 12px;
  }
  .card-inner {
    border-radius: max(0px, 16px - 12px); /* 4px */
  }
  ```
  Never let inner element corners appear sharper or bulge against outer borders.
- [ ] **Layered Subtle Borders**: Rather than harsh contrast outlines, use subtle semi-transparent borders:
  - Dark mode: `1px solid rgba(255, 255, 255, 0.08)` to `0.12`.
  - Light mode: `1px solid rgba(0, 0, 0, 0.06)` to `0.08`.
- [ ] **Multi-Layer Diffuse Shadows**: Avoid single dark muddy drop-shadows. Stack multiple low-opacity layers for natural ambient occlusion:
  ```css
  /* Crisp elevated card shadow */
  box-shadow: 
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 4px 12px rgba(0, 0, 0, 0.06);
  ```
- [ ] **Frosted Overlays**: When layering sticky navbars or floating action bars over content, combine `backdrop-filter: blur(8px-16px)` with an 85–90% alpha background to maintain legibility without creating opaque visual roadblocks.

## 4. Spacing, Rhythm & Optical Alignment

- [ ] **Optical Icon Alignment**: Icons paired with text inside buttons or menu items often sit mathematically centered but optically low. Nudge icon containers up by `0.5px` or `1px` relative to text baseline to align with font capital height.
- [ ] **Layout Shift-Free Skeletons**: Skeleton loaders and fallback placeholders must match the exact dimensions, line-height, and padding of the final content to guarantee 0 CLS (Cumulative Layout Shift) when asynchronous data settles.
- [ ] **Predictable Interactive States**: Every interactive surface must define explicit visual states for `:hover`, `:active`, `:focus-visible`, and `disabled`. Never leave a control in a dead static state.

## 5. Apple-Grade Motion & Tactile Physics (emilkowalski/apple-design + wshobson/interaction-design MERGE)

- [ ] **Interruptible Springs**: Gesture-driven and state animations must remain interruptible mid-flight without snapping or layout hitching.
- [ ] **Velocity Inheritance**: When releasing drag or swipe gestures, inherit user touch velocity directly into the resolving spring physics curve.
- [ ] **Press Feedback Discipline**: Interactive cards and buttons should respond with subtle downward scaling (`transform: scale(0.97)`) on pointerdown, resolving cleanly on pointerup within 100–150ms.
- [ ] **Reduced-Motion Fallback**: When `prefers-reduced-motion: reduce` is enabled, zero out spatial translations and physical bounces while preserving opacity fades for state clarity.
- [ ] **No Hairline-Only Affordances (better-interface MERGE)**: Interactive elements must not rely strictly on a 1px border to communicate clickable boundaries; use background contrast, elevation, or padded hit targets.
- [ ] **Contrast boundaries**: Adjacent surfaces that are only separated by a 1px line must also differ in fill, elevation, or padding so the edge survives 200% zoom and grayscale.
- [ ] **State is not hue-only**: hover / active / disabled / selected remain distinguishable without color (weight, icon, pattern, or copy).

## 6. Layered Shadows & Adaptive Flow (mengto/beautiful-shadows + pbakaus/adapt + superfuture/design-review MERGE)

- [ ] **Multi-Stop Ambient Shadows**: Simulate realistic ambient illumination by layering multiple subtle box-shadows (sharp contact shadow + mid ambient diffusion) rather than single harsh offsets.
- [ ] **Container-Adaptive Components**: Use CSS container queries (`@container`) on self-contained cards and modules so they adapt fluidly to local container width rather than global viewport size alone. Drop optional chrome before shrinking type below 14px inside a container.
- [ ] **Pre-Verification Design Review**: Audit visual hierarchy, contrast ratios, concentric radius geometry, and hit targets before handing off to browser verification.
