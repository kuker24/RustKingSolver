# Design Bank Architecture (12 Universal Banks)

Design Bank root resolution priority:
1. Explicit path (`--bank-root <path>` or `--bank <path>`)
2. `$OPENCODE_DESIGN_BANK` environment variable
3. HighEnd config pointer (`~/.omp/agent/config/design-bank.json`)
4. User home default (`~/Design`)
5. Owned shared cache (`~/.local/share/opencode-highend/design-bank`)

Catalog requirements:
- Search engine & skill indexing (`found-this-design`): dynamically discovers and indexes all available banks across the 12 universal catalogs (minimum: `Refero` + `motionsites` or any 2 valid catalogs).
- Design V2 Engine (`lib/design_v2/bootstrap.py` `REQUIRED_CATALOGS`): bootstrap and validation require four canonical catalogs (`21st`, `aura`, `refero`, `motionsites`). Full 12-bank suites expand the search footprint beyond bootstrap requirements.

---

## 🧭 12-Bank Catalog Registry & File Schemas

| Bank ID | Tier / Lane | Name | Catalog Path | Primary Asset Files | Role & Focus |
|---|---|---|---|---|---|
| **refero** | `identity` | Refero.design | `Refero/bank/catalog.json` | `DESIGN.md`, `tokens.css`, `tailwind.css`, `thumb.jpg` | Design system, tokens, typography, aesthetic rules |
| **aura** | `identity` | Aura.build | `aura/library/catalog.json` | `source.html`, `meta.json`, `prompt.md`, `preview.png` | End-to-end landing templates, complete SaaS dashboards |
| **motionsites** | `motion` | Motionsites.ai | `motionsites/library/catalog.json` | `prompt.md`, `preview.mp4`, `preview.webp`, `meta.json` | UI motion direction, hero animations, WebGL interactions |
| **scrolltide** | `motion` | Scrolltide.co | `scrolltide/library/catalog.json` | `prompt.md`, `preview.mp4`, `preview.png`, `meta.json` | Scrollytelling, timeline pinning, scroll-driven UI |
| **bencho** | `motion` | Bencho.dev | `bencho/library/catalog.json` | `prompt.md`, `meta.json`, `preview.png` | Micro-interactions, gooey physics, interactive widgets |
| **layers** | `motion` | Getlayers.ai | `layers/library/catalog.json` | `prompt.md`, `meta.json`, `preview.png` | 3D Three.js scenes, WebGL shaders, animated gradients |
| **supahero** | `section` | Supahero.io | `supahero/library/catalog.json` | `prompt.md`, `source.html`, `meta.json`, `preview.png` | High-converting SaaS hero headers, split layouts |
| **navbargallery** | `section` | Navbar.gallery | `navbargallery/library/catalog.json` | `prompt.md`, `source.html`, `meta.json`, `preview.png` | Sticky headers, mega-menus, floating docks, navs |
| **footerdesign** | `section` | Footer.design | `footerdesign/library/catalog.json` | `prompt.md`, `source.html`, `meta.json`, `preview.png` | Multi-column sitemaps, trust badges, legal footers |
| **ctagallery** | `section` | Cta.gallery | `ctagallery/library/catalog.json` | `prompt.md`, `source.html`, `meta.json`, `preview.png` | High-impact CTA sections, conversion banners |
| **404sdesign** | `section` | 404s.design | `404sdesign/library/catalog.json` | `prompt.md`, `meta.json`, `preview.png` | Playful 404 error pages, empty states, recovery flows |
| **21st** | `atomic` | 21st.dev | `21st/library/catalog.json` | `prompt.md`, `meta.json`, `preview.png` | Atomic UI components, inputs, buttons (handoff to Impeccable) |
| **oversightsupply** | `identity` | Oversight Supply | `oversightsupply/library/catalog.json` | `prompt.md`, `meta.json`, `preview.webp` | Webflow & Framer website templates (192). Operator bank, not one of the 12 universal catalogs. |
| **oversightsections** | `section` | Oversight Supply Sections | `oversightsupply/library/catalog-sections.json` | `prompt.md`, `meta.json`, `preview.webp` | 32 free interactive sections (10 studio originals + 22 Evergrid). Same folder as templates. |

---

## ⚡ Field Matching Details

### 1. Refero (`styles[]`)
`name`, `slug`, `northStar`, `theme` (`dark`/`light`), `kind`, `tags[]`, `industry`, `fonts[]`, `colors[].hex`, `thumb`, `popularRank`, `files`.
- **Kinds on disk**: `dark-mode`, `editorial`, `playful`, `monochrome`, `high-contrast`, `soft-gradients`, `brutalist`, `minimal`, `lainnya`.

### 2. Aura (`items[]`)
`id`, `title`, `author`, `category` (or `jenis`), `tags[]`, `description`, `popular_rank`, `popular_score`, `preview`, `files`.
- Complete screens and templates with live HTML sources.

### 3. Motion Banks (Motionsites, Scrolltide, Bencho, Layers)
`id`, `title`, `jenis`, `category`, `tags[]`, `description`, `preview`, `files.prompt`, `files.meta`.
- Animation prompts, seekable preview clips, and canvas shader setups.

### 4. Section Banks (Supahero, Navbar, Footer, CTA, 404s)
`id`, `title`, `category`, `tags[]`, `description`, `popular_rank`, `files.prompt`, `files.source`.
- Structural component blueprints targeted to specific viewport zones.
