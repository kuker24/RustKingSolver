# Matching Specification (12-Bank Universal Design Engine)

Implemented by `scripts/search.mjs` and `scripts/fingerprint.mjs`.

## Brief Structure (from `fingerprint.mjs`)

- `intent`: `new` | `redesign` | `section`
- `mode`: `Persuade` | `Operate` | `Read` | `Experience`
- `surface`: `landing-page` | `hero` | `navigation` | `footer` | `cta` | `404` | `scrollytelling` | `micro-interaction` | `3d-website` | `dashboard` | `component` | etc.
- `industry`: `saas` | `wellness` | `portfolio` | `agency` | `finance` | `commerce`
- `theme`: `dark` | `light` | `unknown`
- `kinds[]`: `dark-mode` | `minimal` | `editorial` | `playful` | `monochrome` | `high-contrast` | `soft-gradients` | `brutalist` | `lainnya`
- `query`: Compact token string (not bloated context)
- `hexes[]`: Extracted brand color accents
- `preferredBanks[]`: Specialist banks auto-mapped from surface/intent
- `count`: 3 (default) or 5
- `laneHint`: `identity` | `section` | `motion` | `atomic` | `both`

---

## 🎯 Scoring Engine Breakdown

### 1. Specialist Bank Matching (+20 to +30 pts)
When a query targets a specific surface zone, dedicated banks receive specialist priority:
- `hero` → `supahero`, `motionsites`
- `navigation` → `navbargallery`
- `footer` → `footerdesign`
- `cta` → `ctagallery`
- `404` → `404sdesign`
- `scrollytelling` → `scrolltide`
- `micro-interaction` → `bencho`
- `3d-website` / `shader` → `layers`, `motionsites`
- `dashboard` → `refero`, `aura`
- `landing-page` → `aura`, `oversightsupply`

### 2. Token Overlap (0 to +24 pts)
Calculated against normalized stemmed words across item title, tags, description, category, and author.

### 3. Theme & Kind Alignment (0 to +24 pts)
- Exact kind match (`dark-mode`, `minimal`, etc.): +24 pts
- Tag-level kind match: +12 pts
- Theme alignment (`dark` vs `light`): +20 pts (opposite theme: −8 pts)

### 4. Industry Match (+12 to +20 pts)
Matched against industry categorization in metadata.

### 5. Color Accent Hue Match (0 to +10 pts)
Computed using perceptual HSL closeness for accent hues within Δ ≤ 30°.

### 6. Authority & Community Rank Bonus (+1 to +5 pts)
Rank-based boost for top community-ranked designs (`popular_rank` #1 through #50).

---

## 🧭 Lanes & Diversity

- `identity`: Focuses on complete brand worlds, design systems, tokens, and templates (`refero`, `aura`, `oversightsupply`).
- `section`: Focuses on structural UI parts (`supahero`, `navbargallery`, `footerdesign`, `ctagallery`, `404sdesign`, `oversightsections`).
- `motion`: Focuses on animation, scrollytelling, physics, and WebGL (`motionsites`, `scrolltide`, `bencho`, `layers`).
- `atomic`: Individual UI components and buttons (`21st` — handed off to Impeccable).
- `both` / `all`: Balanced synthesis ensuring at least 1 identity world and 1 dynamic surface/motion candidate, filled out by top overall scores.

Diversity rule: One item per slug family (`familyOf` normalizes IDs by stripping hash suffixes and `-hero` tags). Re-roll drops previous candidates via `--exclude <id1,id2>`.
