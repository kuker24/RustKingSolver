# Fluid Interfaces & Apple Design Principles

Synthesized from Apple's design engineering foundations and WWDC *Designing Fluid Interfaces* (WWDC 2018), translated for modern web and native application engineering.

---

## 1. The Core Law of Fluidity

> An interface feels alive when motion begins from the current on-screen position, inherits the user's velocity, projects momentum forward, and remains interruptible at any sub-millisecond instant.

When software treats animations as fire-and-forget fixed-duration movies, it feels stiff and mechanical. When software treats motion as physical objects governed by mass, stiffness, and damping, it feels like an extension of the user's body.

---

## 2. The Nine Fluid Interaction Principles

### Principle 1: Zero Latency Response
Immediate visual confirmation on pointerdown. When a user touches or clicks a surface, visual acknowledgment must occur within 16ms (the very first frame).
- Never wait for a click or pointerup event before providing visual feedback.
- Buttons scale to `0.97` or illuminate immediately on pointerdown.

### Principle 2: 1:1 Direct Manipulation
While a pointer or finger is moving across the screen, the dragged element must track 1:1 with pointer coordinates.
- No lagging behind or rubber-banding while within active bounds.
- The anchor point under the user's cursor remains locked.

### Principle 3: Absolute Interruptibility
**This is the single most critical principle in modern interaction design.**
- If an element is animating in and the user taps close, it must immediately reverse from its current position and velocity.
- Never block gestures with boolean flags like `isAnimating = true`.
- Never queue transitions sequentially when the user rapidly toggles state; blend them dynamically.

### Principle 4: Springs Over Bezier Timers
Fixed-duration bezier curves (`transition: transform 300ms ease`) cannot handle interruptibility smoothly because resetting time `t = 0` causes velocity jumps or hitching.
Springs do not have fixed durations—they calculate instantaneous acceleration based on distance and velocity:

$$\text{Force} = -k \cdot x - c \cdot v$$

Recommended spring configurations:
- **Snappy UI (Buttons, toggles, menus)**: Stiffness: 400, Damping: 30, Mass: 1 (rapid settle, zero overshoot).
- **Smooth Sheets / Drawers**: Stiffness: 300, Damping: 32, Mass: 1 (clean glide, gentle settle).
- **Bouncy Accents (Badges, likes, celebrations)**: Stiffness: 350, Damping: 18, Mass: 1 (controlled 1-2 oscillation overshoot).

### Principle 5: Velocity Handoff
When the user releases a drag or swipe gesture, the physics simulation must inherit the pointer's release velocity vector ($v_x, v_y$):
- If the user flicks a sheet downward fast, the closing spring must start with that downward speed.
- If the user slowly drags and lets go, initial velocity is ~0.
- A fast flick must never abruptly decelerate to a preset slow transition speed.

### Principle 6: Momentum Projection
Project the user's trajectory to decide target state:
$$\text{Projected Position} = \text{Current Position} + \frac{\text{Velocity}}{\text{Deceleration Rate}}$$
If the projected position crosses 50% of the threshold or velocity exceeds flick threshold (e.g. 500px/s), commit to the open/close state even if the release point was only 20% along the path.

### Principle 7: Spatial Symmetry & Anchor Points
- Elements must exit along the path they entered. A drawer that slides in from the bottom must slide out to the bottom.
- Popovers, context menus, and tooltips must anchor their `transform-origin` to the exact bounding box of the trigger control, not screen center.

### Principle 8: Rubber-Banding at Soft Boundaries
When dragging beyond valid scroll or drag limits, apply logarithmic resistance rather than a hard stop:
$$dx_{\text{clamped}} = dx_{\text{boundary}} + (dx - dx_{\text{boundary}}) \times \left(1 - \frac{1}{\frac{|dx - dx_{\text{boundary}}|}{\text{dimension}} \times c + 1}\right)$$
This communicates boundary elasticity and hints that the action has reached its extent.

### Principle 9: Reduced Motion & Accessibility
When `prefers-reduced-motion: reduce` is active:
- Disable spatial translations (`translateX`, `translateY`, `scale`).
- Preserve instantaneous or subtle cross-fade opacity transitions (`150ms ease-out`).
- Never strip functional state changes; ensure focus outlines and selection badges remain visible.

---

## 3. Materials, Depth & Translucency

In Apple design, depth is functional hierarchy, not decoration:
1. **Translucent Frosted Materials**:
   - Navigation bars, toolbars, and sheets use backdrop blur with semi-transparent backgrounds to maintain environmental context:
     ```css
     backdrop-filter: blur(20px) saturate(180%);
     background-color: rgba(255, 255, 255, 0.75); /* Light */
     /* Dark mode */
     background-color: rgba(18, 18, 18, 0.75);
     ```
2. **Specular Hairlines & Bevels**:
   - Glass surfaces feature an inner 1px white highlight at top (`inset 0 1px 0 rgba(255, 255, 255, 0.15)`) to ground illumination.
3. **Concentric Radii**:
   - Outer and inner rounded rectangles must share a center:
     $$\text{Radius}_{\text{inner}} = \max(0, \text{Radius}_{\text{outer}} - \text{Padding})$$

---

## 4. Typography Discipline (Optical Sizing & SF Pro Harmony)

- **Tracking (Letter Spacing)**:
  - Large display type (≥32px): tight negative tracking (`-0.02em` to `-0.03em`).
  - Standard body text (14–17px): default tracking (`0em`).
  - Small captions / badges (10–12px): slightly positive tracking (`+0.01em` to `+0.03em`).
- **Tabular Figures**:
  - Always enforce `tabular-nums` on timers, counters, stock tickers, and tabular data to avoid vibrating characters.
- **Dynamic Type Balance**:
  - Use `text-wrap: balance` for titles up to 3 lines.
