# RustKingSolver — omp Unified Bundle (v1)

Unified capability bundle for `omp` (`oh-my-pi` v18.12.1). Combines the full offensive security suite `hypeking` (`cli-pentestv1`), the complete software engineering catalog from `OpenCodeHighEnd` (51 automatic skills + 15 manual slash commands + full browser CDP stack), 5 functional gap integrations (`geo-sleuth`, `rea`, `universal-modder`, `deepteam`, `supply-chain`), 17 configured MCP servers, and a single technical router in `AGENTS.md`.

## Repository Structure

| Path | Purpose |
|---|---|
| `skills/` | 52 discovered skills: 1 umbrella offensive router (`hypeking`) + 51 engineering skills. |
| `manual-skills/` | 15 manual specialists isolated from automatic scanner discovery. |
| `commands/` | 15 slash command stubs routing to `~/.omp/agent/manual-skills/<name>/SKILL.md`. |
| `bin/` | Executables: `opencode-chromium-cdp` (with symlink `omp-chromium-cdp`) and `codebase-memory-mcp`. |
| `mcp/` | First-party MCP packages: `penulis-ilmiah` (Indonesian academic paper assistant). |
| `rules/` | Operational governance: `00-routing.md`, `01-verification.md`, `02-engineering-principles.md`, `03-prose-discipline.md`, `decision-log-protocol.md`. |
| `mcp.json` | Unified MCP configuration: 4 enabled (codebase-memory, context7, shadcn, penulis-ilmiah) + 13 disabled. |
| `AGENTS.md` | Pure technical router with 33 closed intents, lazy knowledge chain, and 6 Done-Gate profiles. |
| `config.yml` | Harness settings for omp (model roles, thinking budget). |
| `models.yml` | Model provider endpoint definitions. |
| `vendor/` | Component provenance records (`provenance.json`, `sources.json`), licenses (`vendor/licenses/`). |
| `restore.sh` | Automated deployment script to sync bundle to `~/.omp/agent/` and provision binaries. |
| `LICENSE` | MIT License. |
| `NOTICE` | Third-party software attribution and copyright notices. |

## Quick Start & Installation

> **Important**: A raw git clone of this repository does not include the pre-built `bin/codebase-memory-mcp` binary (>280 MB, excluded via `.gitignore` to comply with GitHub object limits). Running `./restore.sh` is **required** to download and verify the binary with SHA256 integrity (`ce11c141431aeadd788506c3a7e6942db8fd438dec369d0707a39ec9fd8c6510`) before running `omp`.

Run the automated restore script to synchronize this bundle to `~/.omp/agent/`:

```bash
chmod +x restore.sh
./restore.sh
```
To verify skill discovery with `omp`:

```bash
omp skill list --json
```

Target discovery: exactly **52 skills** (1 `hypeking` + 51 OpenCodeHighEnd skills).

## MCP Profiles & Presets

The bundle ships with two pre-configured MCP operational profiles under `profiles/`:

1. **Default Engineering Profile** (`profiles/mcp.default.json`):
   - Active: `codebase-memory-mcp`, `context7`, `shadcn`, `penulis-ilmiah`.
   - Designed for standard software engineering, UI design, refactoring, and academic writing.

2. **Pentest-Mode Profile** (`profiles/mcp.pentest.json`):
   - Active: `sliver` (C2 ops), `jshook` (JS runtime hooking), `ghidra` (binary reverse), `rea` (RE agent), `scrapling` (stealth OSINT/scraping), `context7` (docs), `codebase-memory-mcp` (codebase graph).
   - Dormant: `shadcn`, `ui-skills`, `stitch`, `markitdown`, `penulis-ilmiah`, `reticle`, `exa`, `crawl4ai`, `idapro`, `serena` to conserve CPU/RAM.

**Profile Commands**:
```bash
# Deploy with pentest profile at restore time
./restore.sh --profile pentest

# Or switch profiles on a deployed environment at any time
bin/omp-profile pentest
bin/omp-profile default
bin/omp-profile status
```

## Environment Variables

Credentials are never stored in the repository. Set the required variables in your shell environment:

| Variable | Target Component | Purpose |
|---|---|---|
| `NINEROUTER_API_KEY` | `models.yml` | Gateway API key for 9router. |
| `SLIVER_MULTIPLAYER_CFG` | `mcp.json` (`sliver`) | Path to Sliver C2 client multiplayer configuration (optional). |
| `OPENALEX_API_KEY` | `mcp.json` (`penulis-ilmiah`) | Optional API key to increase OpenAlex query rate limits. |
| `CROSSREF_MAILTO` | `mcp.json` (`penulis-ilmiah`) | Contact email address for Crossref polite pool. |
| `STITCH_API_KEY` | `mcp.json` (`stitch`) | Optional Google Stitch API key. |
| `EXA_API_KEY` | `mcp.json` (`exa`) | Optional Exa API key for neural search. |

## Verification & Testing

1. **Verify Path Sanitization**:
   ```bash
   grep -rn "~/.config/"'opencode' .
   ```
   (Must return 0 matches)

2. **Verify MCP Configuration**:
   ```bash
   python3 -c "import json; d=json.load(open('mcp.json')); assert len(d['mcpServers']) == 17; assert len(d['disabledServers']) == 13; assert d['mcpServers']['codebase-memory-mcp']['enabled'] is True; print('VALID')"
   ```

3. **Verify Hypeking Auto-Router**:
   ```bash
   python3 skills/hypeking/scripts/route.py --ask "photo geolocation exif where was this taken"
   python3 skills/hypeking/scripts/route.py --ask "game modding unity memory recon"
   python3 skills/hypeking/scripts/route.py --ask "deepteam red teaming llms"
   python3 skills/hypeking/scripts/route.py --ask "supply chain sbom sca methodology"
   python3 skills/hypeking/scripts/route.py --ask "godmode bypass"
   ```

4. **Verify Chromium CDP Runner**:
   ```bash
   bin/opencode-chromium-cdp start
   bin/opencode-chromium-cdp status
   bin/opencode-chromium-cdp stop
   ```
