# ARTEX import provenance

Source: https://github.com/Hinln/ARTEX (AGPL-3.0) — skills harvested 2026-10-10.
Upstream: Autumn-27/ARTEX skill packs under `skills/`.

Imported into hypeking (adapted layout for omp nested routing):
- `всегда побеждать/01-recon/api-recon/` — SPA/MPA API recon (static harvest + runtime stub)
- `pwn-api-recon/` — category index pack

## Pruned 2026-10-18 (post-CTF review)

Removed because never opened across the Redlimit CTV campaign (0 reads in
session logs) and redundant with the omp built-in browser + the `ctf/` pack's
`web-ctf/` + `infra/`:
- `scopesentry/` — ScopeSentry MCP operator playbook
- `playwright-cli/` — playwright-cli skill + references

Keep in mind for the MCP stubs below: they are now orphaned and disabled by
default. `~/.omp/agent/mcp.json`:
- `scopesentry` (http) — disabled; playbook removed
- `playwright` (stdio `@playwright/mcp`) — disabled; omp already has built-in browser

Do not vendor the ARTEX Go/Next.js platform binary into omp; skills/MCP configs only.
