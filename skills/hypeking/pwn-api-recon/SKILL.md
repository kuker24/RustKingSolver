---
name: pwn-api-recon
description: "SPA/MPA API surface recon from ARTEX: static JS harvest, auth-stub runtime capture, param matrix, permission-tree restore. Trigger: api recon, frontend API, SPA harvest, webpack chunk, vite manifest, XHR harvest, fetch stub, param samples, shadow endpoint discovery, route map."
---

# pwn-api-recon — ARTEX api-recon

**Suite path:** `~/.omp/agent/skills/hypeking/всегда побеждать/01-recon/api-recon/`

Net-new vs classic `pwn-recon` (httpx/katana/param-miner): this pack reverse-engineers **frontend-declared APIs** (bundles + live XHR/fetch/WS) with client-side auth stubs — no credential hunting.

## Entry

```
read skill://hypeking/всегда побеждать/01-recon/api-recon/SKILL.md
```

Reference recipes:

```
read skill://hypeking/всегда побеждать/01-recon/api-recon/reference.md
```

## Scripts (copy → OUTDIR, never run in-place)

| Script | Role |
|---|---|
| `scripts/harvest_static.py` | webpack/Vite chunk harvest → `api_static.txt`, `routes.txt` |
| `scripts/spider_mpa.py` | MPA form/link spider |
| `scripts/runtime_harvest.js` | Puppeteer depth mode (`puppeteer-core`) |
| `scripts/preload.js` | document-start XHR/fetch stub + observe |
| `scripts/build_perm_tree.py` | Phase 4 permission-tree stubs |
| `scripts/extract_route_map.py` | route map extract |

```bash
# static (after copying scripts into OUTDIR=recon/)
python3 recon/harvest_static.py https://target.example recon/

# runtime (needs chromium + npm i in OUTDIR)
cd recon && npm install   # package.json ships with skill
node runtime_harvest.js config.json
```

## Phases (hard order)

0 classify SPA/MPA → 1 static harvest → 1b param reverse → 2 auth gates → 3 runtime depth/coverage → 4 perm tree (if blank modules) → 5 merge + report

## Complements

| Need | Pack |
|---|---|
| HTTP probe / crawl / fuzz | `pwn-recon` |
| API exploit (BOLA/BFLA/…) | `pwn-web-security` |
| Browser MCP / CLI | `playwright-cli` + omp `browser` tool |
| Asset platform sync | `scopesentry` |

## Provenance

Imported from [Hinln/ARTEX](https://github.com/Hinln/ARTEX) `skills/api-recon` (AGPL-3.0). See `skill://hypeking/ARTEX-IMPORT.md`.
