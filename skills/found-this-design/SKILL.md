---
name: found-this-design
description: "Find 3 or 5 matching UI designs from the local design bank (12 universal banks plus Oversight Supply templates and sections) for the current web project or redesign brief, then generate a high-fidelity first-viewport photo of this product in each recommended world. Use when the user runs /found-this-design or /found_this_design, or asks to find a design, cari desain, rekomendasi desain, design yang cocok, preview desain, prototype visual, design bank, Refero, Motionsites, Oversight, or which visual direction fits this site. Not for implementing UI (use impeccable after a pick) or photoreal product/ad video (use visual-studio)."
compatibility: opencode
license: MIT
---

# Found This Design

Find a visual direction from the 12 universal local design banks plus Oversight Supply. Recommend 3 (default) or 5.
Generate a high-fidelity first-viewport photo of **this product** in each recommended world, then stop.
`/impeccable` builds after the user picks. Stop before component atoms; atoms are impeccable + Design V2.

`/found_this_design` is the same command.

## 🧭 Design Banks

| Level | Banks | Role | Output Assets |
|---|---|---|---|
| **Identity** (`identity`) | **Refero**, **Aura** | Full design system & layout world | `DESIGN.md`, `tokens.css`, `tailwind.css`, full templates |
| **Motion** (`motion`) | **Motionsites**, **Scrolltide**, **Bencho**, **Layers** | Dynamic movement, scrollytelling & 3D | `prompt.md`, `preview.mp4`, WebGL/Shader specs |
| **Section** (`section`) | **Supahero**, **Navbar**, **Footer**, **CTA**, **404s** | Dedicated viewport zone blueprints | `prompt.md`, `source.html`, responsive headers/menus/cards |
| **Atomic** (`atomic`) | **21st** | Buttons, inputs, bento blocks | Component atoms (handed off to Impeccable) |
| **Oversight** (`identity` / `section`) | **Oversight Supply**, **Oversight Sections** | Webflow/Framer website templates and 32 free interactive sections | `prompt.md`, `preview.webp` |

## Load

- Matching: [references/matching.md](references/matching.md)
- Bank paths and fields: [references/banks.md](references/banks.md)
- Before any `image_gen` / `image_edit`: OpenCode native image tools if the session exposes them; otherwise write prompt files and mark DEGRADED. Do not restate it.
- Do not load `impeccable`, `emil-design-eng`, `visual-studio`, or `adhd`.

## Hard rules

- Stop before component atoms; atoms are impeccable + Design V2.
- Schema/JSON generative UI (typed catalog → spec → components) routes to `json-render`. This skill remains visual direction from the Design Bank.
- **Search with the scripts only.** Never read any `catalog.json` into context.
- External brand pattern corpora (e.g. `awesome-design-md`) may be referenced by humans as styling ideas, but never fetched, cloned, or vendored into the project. Product UI direction flows strictly from the local Design Bank → `impeccable`.
- Do not implement UI, copy a Motion prompt into code, or overwrite the project's `DESIGN.md` unless the user asked to pin files.
- Do not crawl banks. Do not open `npm run bank` unless the user asked to browse.
- Generate comps only for the shortlist. One viewport per candidate. No full-page scroll, no contact sheet.
- Comp text may be approximate. Product facts on the cards must be true.
- Match the user's language. Lane names stay English.

## Run

`<skill-dir>` is this skill's directory.

1. **Fingerprint.** From user text, determine `count` (5 only if asked for 5 / "lebih banyak") and query context:

   ```bash
   node <skill-dir>/scripts/fingerprint.mjs --cwd <project> --query "<text>" --count 3 > brief.json
   ```

   If `PRODUCT.md` is missing and query does not specify a surface or product, ask one quick clarification round: which surface, and what mood is forbidden. Do not ask for hexes or canned aesthetic lanes.

2. **Search.** Fast multi-bank query:

   ```bash
   node <skill-dir>/scripts/search.mjs --brief brief.json --lane <identity|section|motion|both> --count <n>
   ```

   Or direct fast search:
   ```bash
   node <skill-dir>/scripts/search.mjs --query "<keywords>" [--bank <bank_id>] [--lane <lane>] --count 3
   ```

   Use `laneHint` from brief unless user named a lane. Override bank root with `OPENCODE_DESIGN_BANK` or `--bank-root`. Exit 2 = catalogs missing; report paths and stop.

3. **Read the shortlist packs only.** Inspect only the 3 (or 5) candidate items returned:
   - `preview`: image or video path
   - `files.meta`: author and tags
   - `files.design` / `files.tokens` (Refero), `files.source` (Aura/Sections), or `files.prompt` (Motion/Sections)
   - Extract real product name, offer, and visitor job from `PRODUCT.md` / the query. Never invent claims.

4. **Comps.** Generate after the shortlist, not before. Save:

   ```text
   .impeccable/found-this-design/<slug>-comp.png
   .impeccable/found-this-design/<slug>-comp.prompt.txt
   ```

   One first-viewport photo of **this product** wearing that bank world. High fidelity, not a wireframe, not the raw source thumb. Aspect `16:9` desktop; `9:16` when surface is `mobile-app` or requested mobile.

   | Condition | Tool | References |
   |---|---|---|
   | Current-site screenshot exists | `image_edit` | screenshot (product facts) + bank preview (world) |
   | Greenfield / no UI | `image_edit` | bank preview only; prompt carries product facts |
   | Tool blocked or failed | do not retry to evade | show the bank thumb; say the comp is missing |

   If there is no screenshot but a local page exists, capture one first viewport through `opencode-chromium-cdp` + `browser-act` only as an edit reference.

   Fire parallel calls, one prompt per candidate (2–5 sentences): surface regions in order → product content in those regions → bank northStar / hexes / typography → "high-fidelity designed website viewport, not a poster, not an interior photo".

5. **Cards.** Equal weight presentation:
   - Hero = generated comp (workspace-relative path)
   - Bank thumb = small source thumbnail
   - Details: Name, Bank, Category/Jenis, Theme, one sentence from `reasons` (why it fits this brief)
   - Mark score leader as "closest to the brief"
   - Prompt choices: pick one · show 5 (if 3) · re-roll with a steer

6. **Pin + Handoff.** After user picks:
   - Write `.impeccable/found-this-design.json` (`slug`, `bank`, pack paths, `lane`, one-line reason, `comp` path).
   - Read that pack's `DESIGN.md` + tokens or prompt.
   - The comp is a north-star preview; the bank pack owns design tokens, fonts, and styling.
   - Instruct user that next step is `/impeccable` with this pinned world. Stop. Do not write components.
