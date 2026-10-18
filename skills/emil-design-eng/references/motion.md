# Motion Engineering & Animation Recipes

Knowledge synthesized from Emil Kowalski's animation engineering doctrines. Use this reference when building, refining, or reviewing interface animations.

---

## 1. The Animation Decision Framework

Before writing animation code, run these three gates in order:

### Gate 1: Should this animate at all?
Base the decision on usage frequency:

| Frequency | Action | Example |
| --- | --- | --- |
| **100+ times/day** | **Zero animation. Ever.** | Command palettes, keyboard shortcuts, tabs, editor hotkeys |
| **Tens of times/day** | **Minimal or instantaneous** | Hover states, list item selection, dropdown menus |
| **Occasional (a few times/session)** | **Standard polished motion** | Modals, drawers, toasts, accordions |
| **Rare / First-run** | **Can add expressive delight** | Onboarding milestones, celebrations, success states |

**Never animate keyboard-initiated actions.** Users type at 60–100 WPM; animation introduces perceived lag and breaks muscle memory.

### Gate 2: What is the purpose?
Valid purposes:
- **Spatial consistency**: Dialog originates from the button that triggered it; drawer slides back to the edge it came from.
- **State confirmation**: Button depresses on click to prove input was acknowledged.
- **Preventing jarring cuts**: Smoothly transitioning layout when items are added or removed.
- **Orientation**: Directing attention to what just changed (e.g. toast notification).

If the answer is merely "it looks fancy" on a high-frequency control, cut the animation.

### Gate 3: What easing curve?
- **Entering the screen**: Strong `ease-out` (starts instantly, decelerates smoothly).
- **Moving across screen**: Strong `ease-in-out` (smooth acceleration and deceleration).
- **Leaving the screen**: Fast `ease-in` or accelerated `ease-out` (exits must never linger).
- **Standard CSS curves (`ease`, `linear`) are too weak.** Use custom high-tension curves:

```css
:root {
  /* Strong ease-out for entering UI elements and popovers */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);

  /* Strong ease-in-out for morphing or cross-screen repositioning */
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);

  /* Deep iOS-style drawer curve */
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);

  /* Fast exit curve */
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);
}
```

---

## 2. Properties to Animate

Stick to compositor-only properties to guarantee steady 60/120fps without layout thrash:
- **Fast / GPU-accelerated**: `transform` (`translate`, `scale`, `rotate`), `opacity`, `filter` (`blur`), `clip-path`.
- **Forbidden in high-frequency animations**: `width`, `height`, `top`, `left`, `margin`, `padding`, `border-width`. These trigger costly layout reflows on the main thread.

For expanding accordion height, use CSS Grid 0fr → 1fr rather than animating max-height:
```css
.accordion-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 250ms var(--ease-out);
}
.accordion-content[data-expanded="true"] {
  grid-template-rows: 1fr;
}
.accordion-inner {
  overflow: hidden;
}
```

---

## 3. Production Animation Recipes

### Recipe A: Button Press
Immediate feedback that the interface received the user's action:

```css
.button {
  transition: transform 140ms var(--ease-out);
}

.button:active {
  transform: scale(0.97);
}
```

### Recipe B: Popover, Dropdown, Menu, Select
Originates from its trigger element using dynamic `transform-origin`:

```css
.popover {
  transform-origin: var(--transform-origin, center top);
  transition:
    opacity 180ms var(--ease-out),
    transform 180ms var(--ease-out);
}

.popover[data-state="closed"] {
  opacity: 0;
  transform: scale(0.95);
  pointer-events: none;
}

.popover[data-state="open"] {
  opacity: 1;
  transform: scale(1);
}
```

### Recipe C: Tooltip with Group Instant Warmup
Tooltips delay on first hover to prevent nuisance flashing, but open instantly once a toolbar session is active:

```css
.tooltip {
  transform-origin: var(--transform-origin, center bottom);
  transition:
    transform 120ms var(--ease-out),
    opacity 120ms var(--ease-out);
}

.tooltip[data-state="closed"] {
  opacity: 0;
  transform: scale(0.96);
}

/* When another tooltip in the group was recently open, skip delay & duration */
.tooltip-group[data-instant] .tooltip {
  transition-duration: 0ms !important;
}
```

### Recipe D: Centered Modal Dialog
Modals stay centered. Scale subtly from 0.95 → 1.0 (never 0 → 1.0; elements in reality do not emerge from a microscopic dot):

```css
.modal-overlay {
  transition: opacity 220ms var(--ease-out);
}
.modal-overlay[data-state="closed"] {
  opacity: 0;
}

.modal-content {
  transform-origin: center center;
  transition:
    opacity 220ms var(--ease-out),
    transform 220ms var(--ease-out);
}
.modal-content[data-state="closed"] {
  opacity: 0;
  transform: scale(0.95);
}
.modal-content[data-state="open"] {
  opacity: 1;
  transform: scale(1);
}
```

### Recipe E: Bottom Sheet / Drawer
Slides cleanly from viewport edge with iOS-like deceleration:

```css
.drawer {
  transition: transform 320ms var(--ease-drawer);
  transform: translateY(0);
}

.drawer[data-state="closed"] {
  transform: translateY(100%);
}
```

### Recipe F: List Item Exit / Deletion Choreography
Collapsing deleted items smoothly without jarring jumps:
1. Fade and slide out item horizontally (`opacity: 0; transform: translateX(20px);`).
2. Collapse item height and margin to 0 over 200ms using CSS grid or height animation on wrapper.
3. Cleanly remove node from DOM.

---

## 4. Exit Choreography Rules

1. **Exits must be faster than entries.** If entering takes 250ms, exiting should take 160–180ms. The user has already finished interacting and wants the obstacle out of the way.
2. **Never stagger exits.** Entering items can stagger by 20–30ms to reveal structure. Exiting items should vanish simultaneously or near-instantly.
3. **No exit spring oscillations.** Springs that overshoot on exit look sloppy; use clean critical damping or straight ease-out.

---

## 5. Review Format Checklist

When reviewing animation code, format output in a Markdown comparison table:

| Before | After | Why |
| --- | --- | --- |
| `transition: all 300ms ease;` | `transition: transform 180ms var(--ease-out);` | Never animate `all`; specify properties and use high-tension ease-out. |
| `transform: scale(0);` | `transform: scale(0.95); opacity: 0;` | Elements should scale from ~95%, not thin air. |
| `ease-in` on dropdown menu | `ease-out` | `ease-in` starts slowly and feels sluggish to human touch. |
| Missing active state | `transform: scale(0.97)` on `:active` | Touch/click lacks tactile confirmation without active scale. |
