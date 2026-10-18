# Slide rules (condensed)

Adapted from `carnot-tech/consulting-pptx-skill` slide-rules (MIT). Full upstream
list is ~80 items; this sheet is the overlay fence. Do not vendor the 62-type
catalog.

## Story

- Title states the conclusion. Default one line; break at a meaning boundary, never shrink-to-fit.
- No です/ます (or English equivalent filler). Titles concatenated must form one story.
- One slide = one message. Left = fact/figure, right = implication. No bottom “POINT” band.
- Title counts must match body numbering. Do not put the page’s item count in the title.

## Tables and figures

- Tables have axes (rows = items, columns = lenses). Header is larger/bolder than body, no fill, no thin-grey header color.
- Header vs body: at least +2pt (aim +3–4pt). Last row has no bottom rule.
- Trends, mix, and distributions are charts, not tables.
- Equal-width columns when cells are the same kind (dates, options, orgs).

## Decoration

- No rounded rectangles as a chrome system. Filled boxes have no extra outline.
- If color encodes meaning, the same slide carries a legend.
- No decorative kicker in all-caps English. Two-column headings must not start with a conjunction (“So”, “Therefore”, “だから”).
- One term per deck. Expand abbreviations on first use. Bullet endings match within a level.

## Checks before ship

- [ ] Title storyline reads as one argument
- [ ] FAIL-level rule breaches = 0
- [ ] Cover/back-cover empty-title WARN only if those pages are intentionally untitled
- [ ] Print or Chromium PDF pass: no overlap, no clip, no empty lower half
- [ ] PPTX requested but no exporter → `NOT_CONFIGURED`
