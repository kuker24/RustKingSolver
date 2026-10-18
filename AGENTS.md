# omp Unified Technical Router

Technical router for `omp` (`oh-my-pi`). Integrates `cli-pentestv1` offensive engine (`hypeking`), `OpenCodeHighEnd` engineering catalog (51 automatic + 15 manual slash commands + full browser stack), and 5 functional gap packs (`geo-sleuth`, `rea`, `universal-modder`, `deepteam`, `supply-chain`).

```text
pikir dulu → bukti di repo → satu spesialis → cek hasil
```

---

## 1. Closed Intent Classification (33 Intents)

Every user task is classified into exactly one of the 33 closed intents below at intake:

```text
repo_understand | bug | security | perf | ui_direction | ui_implement | generative_ui |
motion | scroll_2d | scroll_3d | launch_film | gateway_llm | docs | ingest_md | prose |
academic | longdoc_nav | web_research | browser_qa | architecture | warehouse | ops_data |
video_html | demo_id | slides_pptx | penulis_ilmiah |
recon | exploit | c2_ops | reverse | ctf | osint | llm_redteam
```

---

## 2. Intent Routing Table

| Intent | Primary Route | Handoff Boundary / Rule |
|---|---|---|
| `repo_understand` | Codebase Memory MCP → `skills/code-tour` | Codebase Memory first; guided tour anchors `.tours/` |
| `architecture` | `commands/why.md` (manual); blast risk → `commands/blast-radius.md` | Rationale and blast radius; no auto-architect |
| `bug` | `skills/diagnosing-bugs` | Reproduce red-green; known typos stay `/tdd` or in-session |
| `security` | `skills/full-audit-keamanan` | Defensive code/auth/secrets audit (max 1 risk specialist) |
| `perf` | `skills/full-performance-audit` | Measured LCP/INP/CLS/latency/bundle bottlenecks |
| `ui_direction` | `skills/found-this-design` | Stop after writing `.impeccable/found-this-design.json` |
| `ui_implement` | `skills/impeccable` | Requires pinned world or project `DESIGN.md` |
| `generative_ui` | `skills/json-render` | Typed catalog + JSON spec → components; never bypass Design Bank for marketing |
| `motion` | `skills/emil-design-eng` | Micro-interactions, spring physics, touch feel |
| `scroll_2d` | `skills/scroll-craft` | Scrollytelling, pinned 2D timelines, scroll triggers |
| `scroll_3d` | `skills/scroll-world` | Continuous 3D fly-through, camera-scrub worlds |
| `launch_film` | `skills/business-motion-film` | Commercials, launch films, business explainers; render via hyperframes |
| `gateway_llm` | `skills/ninerouter` | 9Router gateway (chat, image, video, TTS, STT, embeddings, web) via NINEROUTER_URL |
| `docs` | `skills/smartdoc` | Technical docs, OCR/PDF/DOCX extraction & contracts |
| `slides_pptx` | `skills/deck-design` | Consulting PPTX / 16:9 HTML decks; smartdoc keeps PDF/DOCX |
| `ingest_md` | `skills/markitdown` | Structure-preserving Markdown ingest from Office/PDF |
| `prose` | `skills/humanizer` / `commands/unslop.md` | Prose AI-tell removal; technical docs stay technical-writing |
| `academic` | `skills/academic` | Literature surveys, IMRaD manuscripts, peer critique |
| `longdoc_nav` | `skills/pageindex` | Tree/reasoning nav of long structured docs; not Graphiti/Cognee |
| `web_research` | `skills/research` | Web/social data gathering (`references/web-data.md`); read-only, not QA |
| `browser_qa` | `skills/playwright-qa` → `skills/browser-act` → `skills/chrome-devtools-axi` → `skills/click-path-audit` | 4-door hierarchy; isolated verification sessions |
| `video_html` | `skills/hyperframes` | Programmatic HTML-to-MP4 via headless Chrome + FFmpeg |
| `demo_id` | `skills/id-demo-video` (`commands/demo-video.md`) | Indonesian narrated app tour; cards via hyperframes |
| `penulis_ilmiah` | `skills/penulis-ilmiah` | Indonesian academic drafting, EYD V, KBBI standard words, fail-closed citation verification |
| `warehouse` | Only when user names the job | `agent-architecture-audit`, `cost-aware-llm-pipeline`, etc. |
| `ops_data` | `skills/supabase-ops` / `skills/mongodb-ops` / `skills/vercel-ops` | Operational data/hosting config; never generates UI |
| `recon` | `skill://hypeking/pwn-recon/SKILL.md` / `pwn-api-recon/` | Network, subdomain, endpoint, asset and API surface discovery |
| `exploit` | `skill://hypeking/pwn-exploit/SKILL.md` / `HackinMode/` | Vulnerability exploitation, payload delivery, web pwn pipeline |
| `c2_ops` | `skill://hypeking/pwn-red-team/SKILL.md` / `operating-sliver-c2/` | Command & control management (Sliver, Havoc, Caldera, Adaptix) |
| `reverse` | `skill://hypeking/pwn-reverse/SKILL.md` / `reverse-skill/` | Binary decompilation, APK/IPA analysis, protocol & firmware reverse, game modding |
| `ctf` | `skill://hypeking/ctf/SKILL.md` | CTF competition solving (crypto, reverse, forensics, osint, ics, web-ctf, infra) |
| `osint` | `skill://hypeking/ctf/osint/SKILL.md` | Geolocation (`photo-geolocation`), open-source intelligence, telemetry feeds (`gods-eye-view-sources.md`) |
| `llm_redteam` | `skill://hypeking/pwn-ai-llm/SKILL.md` | AI & LLM red teaming (`red-teaming-llms-with-deepteam`, `garak`, `pyrit`, `promptfoo`) |

---

## 3. Lazy Knowledge Retrieval Chain

Query knowledge sources in strict hierarchical sequence:

```text
1. Codebase Memory (local AST & symbol graph)
   ↓ (if not found in codebase)
2. Serena (symbol navigation & project outline, if registered)
   ↓ (if external library documentation required)
3. Context7 (curated library & framework documentation)
   ↓ (if web information or external references needed)
4. WebSearch / WebFetch (standard search engines)
   ↓ (if specialized deep web extraction required)
5. exa (semantic neural web index, if configured)
```

Never jump directly to external web retrieval when local repository evidence answers the query.

---

## 4. Browser QA 4-Door Hierarchy

Browser automation and QA adheres to the 4-door hierarchy:

1. **Door 1 (Default)**: `playwright-qa` — Standard isolated verification sessions, assertions, visual diffs, and headful/headless testing.
2. **Door 2 (Specialized)**: `browser-act` — Used only on explicit user request or for persistent multi-session workflows.
3. **Door 3 (Diagnostics)**: `chrome-devtools-axi` — Direct Chrome DevTools Protocol debugging, network request inspection, DOM performance profiling.
4. **Door 4 (Deterministic)**: `click-path-audit` — End-to-end user journeys, journey maps, and deterministic click path verification.

---

## 5. Tool Usage Reporting Contract

Every response involving tools must report invocation accounting:

```text
USED: <list of actually invoked tools/specialists>
CONSIDERED_NOT_USED: <list of candidates considered but rejected with reason>
MANUAL_NOT_INVOKED: <manual slash commands not called>
```

---

## 6. Done-Gate Verification Profiles

Every significant code modification or deliverable must pass one of the 6 Done-Gate profiles before completion:

- **FAST**: Clean lint, syntax check, typecheck passing.
- **STANDARD**: Unit test suite green, zero regression, exit 0.
- **UI**: Visual rendering verified via headless browser / screenshot, layout responsive, no console errors.
- **SECURITY**: Zero plain-text secrets, auth boundary verified, no unsanitized inputs, SAST pass.
- **PERFORMANCE**: Bundle size within budget, query execution plan verified, LCP/INP within acceptable bounds.
- **RELEASE**: End-to-end integration tests green, changelog updated, migration tested, provenance intact.

Reporting ledger format:
```text
FACT: <objective mechanical result, command run, exit code, diff>
JUDGMENT: <qualitative engineering evaluation and risk assessment>
```

---

## 7. Operational Rules

Core behavioral rules reside under `rules/`:
- `rules/00-routing.md`: Complete routing logic and boundary rules.
- `rules/01-verification.md`: Granular verification checks and failure contracts.
- `rules/02-engineering-principles.md`: Code quality, simplicity, and maintainability gates.
- `rules/03-prose-discipline.md`: Concise, factual communication discipline.
- `rules/decision-log-protocol.md`: Decision record ledger format.

---

## 8. MCP Operational Profiles

Toggle MCP servers per mission focus using `omp-profile [default|pentest]` or `./restore.sh --profile <name>`:

- **Standard Engineering Profile** (`default`): Active: `codebase-memory-mcp`, `context7`, `shadcn`, `penulis-ilmiah`.
- **Pentest / CTF / Reverse Profile** (`pentest`): Active: `sliver` (C2 ops), `jshook` (JS hook/runtime), `ghidra` (binary reverse), `rea` (RE agent), `scrapling` (stealth OSINT/scraping), `context7` (API/tool docs), `codebase-memory-mcp` (codebase memory). Dormant: UI, office, and academic servers to minimize resource overhead.
