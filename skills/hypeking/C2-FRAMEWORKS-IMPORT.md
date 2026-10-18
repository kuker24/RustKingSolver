# C2 frameworks harvest — AdaptixC2 / Caldera / Sliver

**Date:** 2026-10-10  
**Clones:** `/tmp/harvest/c2/{AdaptixC2,caldera,sliver}`

| Source | License | Imported into hypeking | Skipped |
|---|---|---|---|
| [Adaptix-Framework/AdaptixC2](https://github.com/Adaptix-Framework/AdaptixC2) | GPL-3.0 | `12-red-team-web/operating-adaptix-c2/` playbook + helper + refs (README, compose, pre_install) | Full Go/Qt tree |
| [apache/caldera](https://github.com/apache/caldera) | Apache-2.0 | `operating-caldera-adversary-emulation/` + REST agent + sample Stockpile adversaries/abilities | Full server; empty submodule stubs replaced by samples only |
| [BishopFox/sliver](https://github.com/BishopFox/sliver) | GPL-3.0 | Upgraded `operating-sliver-c2` with MCP docs (`references/sliver-mcp.md`); MCP stub in `mcp.json` | Full Go monorepo / vendor |

## Pruned (stale duplicates)

| Removed | Reason | Kept instead |
|---|---|---|
| `performing-phishing-simulation-with-gophish` | Truncated frontmatter; subset of GoPhish API | `performing-red-team-phishing-with-gophish` |
| `executing-phishing-simulation-campaign` | Thin metrics wrapper overlapping GoPhish packs | same + `conducting-spearphishing-simulation-campaign` |

## Prefer adapted layout

Platforms run from `~/tools/{AdaptixC2,caldera}` or upstream installers — skills are operator playbooks only.

## Tools equipped (2026-10-10)

See `C2-TOOLS.md`. Staged `~/tools/{AdaptixC2,caldera,sliver,c2-venv}`; `docker-compose` apt; `sliver-client` alias; agents shebang → c2-venv.

