# Practical Accessibility (WCAG AA) Checklist

Core accessibility principles merged from `fixing-accessibility`. A practical, verifiable guide for creating accessible interfaces without confusing or conflicting standards.

## 1. Accessible Names & Interactive Elements

- [ ] **Every Interactive Element Must Have a Name**: Every `<button>`, `<a>`, `<input>`, `<select>`, and custom control must compute to a non-empty accessible name.
  - Icon-only buttons must include `aria-label="Action name"` or an visually-hidden text span (`<span class="sr-only">Action name</span>`).
  - Never render naked icon SVGs inside buttons without accessible text:
    ```html
    <!-- Bad -->
    <button><svg ...></svg></button>

    <!-- Good -->
    <button aria-label="Close settings"><svg aria-hidden="true" ...></svg></button>
    ```
- [ ] **Native HTML Controls Over ARIA Divs**: Always prefer native `<button>` and `<a>` tags. If a custom element must act as a button, it requires `role="button"`, `tabindex="0"`, and keyboard handlers for both `Enter` and `Space`.

## 2. Keyboard Navigation & Focus Management

- [ ] **Never Remove Focus Indicators Unconditionally**: Never use `outline: none` or `outline: 0` without providing an explicit, high-contrast `:focus-visible` replacement:
  ```css
  :focus-visible {
    outline: 2px solid var(--ring-color, #2563eb);
    outline-offset: 2px;
  }
  ```
- [ ] **Logical DOM Tab Order**: Visual tab order must follow reading order. Avoid using positive `tabindex` (`tabindex="1"`). Use `tabindex="0"` to include interactive elements or `tabindex="-1"` for programmatically focusable containers.
- [ ] **Modal Dialog Focus Trapping**: When a modal opens:
  - Move focus to the first interactive element or dialog container.
  - Trap tab cycling within the dialog (`Shift+Tab` on first element wraps to last; `Tab` on last wraps to first).
  - Pressing `Escape` closes the dialog.
  - Restoring focus to the trigger element when the dialog closes.

## 3. Dialogs, Drawers & Overlays

- [ ] **Modal Semantics**: Every overlay dialog requires:
  - `role="dialog"` or `role="alertdialog"`.
  - `aria-modal="true"`.
  - `aria-labelledby="<title-id>"` referencing the heading.
  - `aria-describedby="<desc-id>"` referencing supporting text if present.
- [ ] **Inert Background Content**: When a modal or mobile navigation drawer is active, apply the `inert` attribute to background content containers (`<main inert>`) to prevent screen readers and tab navigation from escaping.

## 4. Forms & Error Handling

- [ ] **Explicit Input Labels**: Every form field must have an associated `<label for="id">` or `aria-label`. Placeholder text is NOT a replacement for a label (placeholders disappear upon typing and usually fail contrast).
- [ ] **Inline Error Announcement**:
  - When an input has a validation error, set `aria-invalid="true"`.
  - Associate the error text via `aria-describedby="<input-id>-error"`.
  - Use `aria-live="polite"` or `role="alert"` for dynamically rendered error messages so screen readers announce them.

## 5. Color Contrast & Visual Legibility

- [ ] **Text Contrast Ratios**:
  - Normal text (< 18pt or < 14pt bold): minimum **4.5:1** contrast against computed background.
  - Large text (>= 18pt or >= 14pt bold): minimum **3:1** contrast.
- [ ] **Non-Text UI Contrast (3:1)**:
  - Input field borders and checkboxes in unselected states must maintain at least **3:1** contrast against adjacent backgrounds.
  - Active selection indicators, tab underlines, and focus rings must maintain at least **3:1** contrast.
- [ ] **Never Rely on Color Alone**: Convey critical state (errors, active states, status badges) with icons or text labels in addition to color.

## 6. Semantic Structure & Landmarks

- [ ] **Single H1 & Logical Heading Levels**: Exactly one `<h1>` per page. Sub-sections follow `<h2>` -> `<h3>` without skipping levels (e.g. `<h2>` directly to `<h4>`).
- [ ] **Landmarks**: Ensure the page has standard landmark regions: `<header>`, `<nav>`, `<main>`, `<footer>`.

## 7. Keyboard Path & Motion Controls (addyosmani/accessibility MERGE)

- [ ] **Complete Keyboard Path**: Every user flow must be executable end-to-end via keyboard alone (`Tab`, `Shift+Tab`, `Enter`, `Space`, `Escape`, arrow keys). Never leave dead ends where focus gets dropped or trapped.
- [ ] **Skip Links**: Long navigation trees or complex headers must provide a visible-on-focus skip link: `<a href="#main" class="sr-only focus:not-sr-only">Skip to main content</a>`.
- [ ] **Reduced-Motion Fallback**: When `prefers-reduced-motion: reduce` is active, collapse all spatial translations, layout scaling, and parallax sweeps into clean opacity fades or instant transitions, preserving functional state clarity.
