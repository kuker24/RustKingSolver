# ARTEX import provenance

Source: https://github.com/Hinln/ARTEX (AGPL-3.0) — skills harvested 2026-10-10.
Upstream: Autumn-27/ARTEX skill packs under `skills/`.

Imported into hypeking (adapted layout for omp nested routing):
- `всегда побеждать/01-recon/api-recon/` — SPA/MPA API recon (static harvest + runtime stub)
- `scopesentry/` — ScopeSentry MCP operator playbook
- `playwright-cli/` — playwright-cli automation skill + references
- `pwn-api-recon/` — category index pack

MCP stubs (disabled by default) live in `~/.omp/agent/mcp.json`:
- `scopesentry` (http) — fill URL + X-API-Key
- `playwright` (stdio `@playwright/mcp`) — optional; omp already has built-in browser

Do not vendor the ARTEX Go/Next.js platform binary into omp; skills/MCP configs only.
