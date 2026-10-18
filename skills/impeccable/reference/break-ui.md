# Adversarial UI Stress Testing (Break-UI)

Adversarial stress testing doctrine for UI components and screens under realistic worst-case conditions.
Adapted from [emilkowalski/skills](https://github.com/emilkowalski/skills) (`e8a175de22ae1e49370fc144c1f3bb9aeedf988d`, MIT, Emil Kowalski) into OpenCodeHighEnd craft standards.

This reference guides the `harden` and `audit` passes inside `impeccable`. It evaluates whether a component designed against comfortable demo data survives authentic, messy production realities.

---

## 1. Operating Posture

Demo data is inherently benevolent: short single-line names, numbers that never need thousands separators, avatars that always resolve, and lists with convenient item counts. Production data is not benevolent.

Act as the most demanding authentic user:
- Realistic edge cases: compound hyphenated names, diacritics, plus-addressed corporate email addresses, single-letter initials, and large workspace counts.
- **Never test absurd garbage**: strings of `"aaaaaaa"` or 10,000-character gibberish are easily dismissed. Test values that a real user could input or that schema/database boundaries permit.
- **Data-boundary changes only**: introduce stress values through props, fixture files, API stubs, or URL parameters. Never manually alter CSS or HTML structure to manufacture an artificial break.

---

## 2. Six-Phase Workflow

### Phase 1: Map the Rendered Surface
Catalog every value rendered on screen before testing:
- **Field & Source**: where does the value originate (e.g. `user.name`, `org.members.length`)?
- **Schema & Storage Bounds**: what is the explicit boundary in Zod/database migrations (e.g. `varchar(255)`) or is it unbounded?
- **Optionality & Fallbacks**: what renders if the field is null, undefined, or empty?
- **Implicit Values**: headers, relative dates, badges, count labels, and avatar image URLs.

### Phase 2: Assemble the Worst-Case Fixture
Construct a realistic worst-case dataset mirroring the shape of the existing demo fixture:
- **Names & Text**: long compound names (`Aleksandra Wiśniewska-Kowalczyk`), two-letter names (`Jo`), single-letter names (`J`), non-Latin scripts (`王秀英`, `نور الهدى`), and emoji prefixes (`🦊 Fox`).
- **Identifiers & URLs**: unbreakable long emails (`bartholomew.fitzgerald@northwind-industries-holdings.example.com`), lengthy parameterized URLs, and long file names.
- **Numbers & Currencies**: count of `0` (empty states), count of `1` (pluralization), `1284` (thousands separators), negative amounts, and live-updating figures needing `tabular-nums`.
- **Collections & Bounds**: `0` items (empty state), `1` item (grid layout balance), and `1,000+` unpaginated items (virtualization / scrolling budget).
- **Media**: missing avatar images (fallback to initials or neutral glyph), panoramic or extreme aspect ratio images.

### Phase 3: Wire a Dev-Only Toggle
Mount a lightweight, neutral toggle control (`Demo data` / `Worst case` / `Empty` / `1,000 rows`) in the development environment or prototype harness:
- Persist selection via URL query parameter (e.g. `?data=worst`).
- Position fixed at the bottom center, styled strictly as plain developer chrome (system fonts, neutral pills).
- Ensure the toggle never leaks into production builds.

### Phase 4: Identify Break Signatures & Root Causes

| Visual Signature | Underlying Cause | Prescribed Remediation |
|---|---|---|
| Avatar squished into an oval | Flex child shrinking | Apply `flex-shrink: 0` to avatar / icon container |
| Text column overflows parent container | Flex/grid child defaulting to `min-width: auto` | Apply `min-width: 0` to flex child (`minmax(0, 1fr)` in CSS grid) |
| Email / URL runs beyond box boundary | Unbreakable string with no whitespace | Add `overflow-wrap: anywhere` or `break-words` |
| Trailing actions (buttons, dropdowns) clipped | Mid-row content consumes available track | Set `min-width: 0` on content, `flex-shrink: 0` on actions |
| Multi-line badge wrapping | Badge container shrinking | Apply `white-space: nowrap; flex-shrink: 0` |
| Avatar vertically misaligned on wrapped names | `align-items: center` across variable rows | Switch to `align-items: flex-start` once text wraps |
| Naive initials (`"J"` for "Jo", `""` for emoji) | Naive char slicing (`str[0]`) | Use `Intl.Segmenter` for grapheme clusters and safe fallbacks |
| "1 members", "0 member" | Hardcoded string concatenation | Use `Intl.PluralRules` or localized plural variants |
| Number jitter during counters | Proportional font figures | Apply `font-variant-numeric: tabular-nums` |
| Broken image glyph on avatar error | Missing load failure handler | Fall back gracefully to initials with styled placeholder |

#### Truncation vs. Wrapping Principles
- **Wrap** identifiers essential for comprehension (e.g. user names, titles in detail views).
- **Truncate at the end** for secondary metadata with immediate full-view access (e.g. descriptions, subtitles).
- **Truncate in the middle** when disambiguation happens at the end (e.g. file extensions, commit SHAs, email domains).
- **Clamp** (`line-clamp: 2`) for card grids where uniform height maintains layout rhythm.
- **Never truncate** financial totals, balances, dates, or comparative metrics.

### Phase 5: Structured Adversarial Report
Before modifying production code, report findings categorized by severity:
1. **Broken**: content unreadable, action unreachable, data corrupted or clipped off-screen.
2. **Ugly**: legible but visibly flawed (squished icons, broken alignment, orphaned separators).
3. **Fragile**: works under current test values but lacks validation limits or graceful error fallbacks.

Include file:line pointers for every proposed fix, list architectural trade-offs requiring user direction, and record what held up cleanly.

### Phase 6: Targeted Remediation
Upon explicit user direction, apply targeted fixes to components without degrading standard demo data views. Retain the worst-case fixture in the test suite or dev sandbox as a durable regression shield.
