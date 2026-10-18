# feat(bundle): assemble unified omp bundle v1

## Summary

Assembled the unified production bundle for harness `omp` (`oh-my-pi` v18.12.1) combining:
1. **Offensive Engine `hypeking`**: Cleaned dead `g0dm0d3` and `scopesentry` paths; routed `godmode` to `HackinMode/SKILL.md`; preserved 8-field router output contract (`ROUTE`, `SUITE`, `MODE`, `NEXT`, `MATCHED`, `SCORE`, `PATH`, `ALTS`).
2. **Software Engineering Catalog (`OpenCodeHighEnd` v0.1.18)**: Ported 51 automatic skills into `skills/`, 15 manual specialists into `manual-skills/`, 15 slash command stubs into `commands/`, and full browser CDP automation into `bin/`.
3. **5 Functional Gap Repositories & OSINT Telemetry**:
   - `geo-sleuth`: Integrated candidate board and regional packs into `skills/hypeking/ctf/osint/photo-geolocation/` (weight 98).
   - `rea`: Configured stdio MCP server in `mcp.json` (`rea-agents@6.6.0`), disabled by default.
   - `universal-modder`: Integrated modular game modding into `skills/hypeking/reverse-skill/game-modding/` with engine playbooks (`unity`, `unreal`, `bethesda`, `godot`, `native`, `retro-decomp`) and optional generative asset markers.
   - `deepteam`: Added Confident AI LLM red teaming skill pack to `skills/hypeking/всегда побеждать/09-ai-llm-web/red-teaming-llms-with-deepteam/` (weight 95).
   - `supply-chain`: Integrated SCA/SBOM methodology into `skills/hypeking/reverse-skill/supply-chain-security/` and competition CTF sandbox.
   - `gods-eye-view`: Extracted curated public telemetry feeds (ADS-B, AIS, TLE, USGS, FIRMS) to `skills/hypeking/ctf/osint/references/gods-eye-view-sources.md`.
4. **Unified `mcp.json`**: Conformed to official `omp` MCP schema with 17 total servers (4 active: `codebase-memory-mcp`, `context7`, `shadcn`, `penulis-ilmiah`; 13 disabled).
5. **Technical Router `AGENTS.md`**: Removed VANTA charter entirely; implemented pure 33 closed intent technical router, lazy knowledge retrieval chain, 4-door browser QA hierarchy, tool invocation accounting, and 6 Done-Gate verification profiles.
6. **Path Sanitization**: Converted all occurrences of `~/.config/opencode` to `~/.omp/agent`.
7. **Deployment & Provenance**: Added `restore.sh` for one-command deployment to `~/.omp/agent/` and populated `vendor/provenance.json` and `vendor/sources.json`.

---

## Component Provenance & 40-Hex SHAs

| Component | Upstream Repository | Version / Tag | Commit SHA (40-hex) |
|---|---|---|---|
| `cli-pentestv1` | `https://github.com/kuker24/cli-pentestv1.git` | `main` | `fda8e627f43897884c6c9802619fe839fa149391` |
| `OpenCodeHighEnd` | `https://github.com/kuker24/OpenCodeHighEnd.git` | `v0.1.18` | `30d394fb37bbe1ca64abe1a660aefd91ac7d99fc` |
| `geo-sleuth` | `https://github.com/Oldcircle/geo-sleuth.git` | `main` | `da0813705c8beb0d9b82fbbf9ec5480ed11468c4` |
| `rea` | `https://github.com/morluto/rea.git` | `v6.6.0` | `7c458f04b9155707c8ba406f8b455b10016f1b99` |
| `universal-modder` | `https://github.com/rehan-remade/universal-modder.git` | `main` | `6a8865ae171b406f50892c7f46fc5f45655269eb` |
| `deepteam` | `https://github.com/confident-ai/deepteam.git` | `main` | `bc80bfa1daffa240f53fdbafa7740bbc690aa23f` |
| `supply-chain` | `https://github.com/zhaoxuya520/reverse-skill.git` | `main` | `cab634bd855fc287f6e420c1f36fd1a6b9245960` |
| `gods-eye-view` | `https://github.com/bilawalsidhu/gods-eye-view.git` | `main` | `93ea088f4556a5a65b3292a2d15142d5a6c562bc` |
| `codebase-memory-mcp` | `https://github.com/DeusData/codebase-memory-mcp` | `v0.11.0` | SHA256: `ce11c141431aeadd788506c3a7e6942db8fd438dec369d0707a39ec9fd8c6510` |

---

## Done-Gate Verification Ledger

### FACT
- **Path Sanitization**: `grep -rn "~/.config/opencode" .` returned 0 matches (exit code 1).
- **Schema Validation**: `mcp.json` parsed with exactly 17 servers, 4 active (`enabled: true`), 13 disabled (`enabled: false`), matching `disabledServers` array.
- **Gap Repository Integrity**: All 5 gap asset paths verified present on disk:
  - `skills/hypeking/ctf/osint/photo-geolocation/SKILL.md`
  - `skills/hypeking/reverse-skill/game-modding/SKILL.md`
  - `skills/hypeking/reverse-skill/supply-chain-security/SKILL.md`
  - `skills/hypeking/всегда побеждать/09-ai-llm-web/red-teaming-llms-with-deepteam/SKILL.md`
  - `skills/hypeking/ctf/osint/references/gods-eye-view-sources.md`
- **Dispatcher Routing**:
  - `photo geolocation exif where was this taken` → `ctf/osint/photo-geolocation/SKILL.md` (SCORE: 196)
  - `game modding unity memory recon` → `reverse-skill/game-modding/SKILL.md` (SCORE: 95)
  - `deepteam red teaming llms` → `09-ai-llm-web/red-teaming-llms-with-deepteam/SKILL.md` (SCORE: 95)
  - `supply chain sbom sca methodology` → `reverse-skill/supply-chain-security/SKILL.md` (SCORE: 285)
  - `godmode bypass` → `HackinMode/SKILL.md` (SCORE: 90)
- **Skill Discovery**: `./restore.sh` deployed bundle to `~/.omp/agent/`. `omp skill list --json` discovered exactly **52 skills** (1 `hypeking` umbrella + 51 OpenCodeHighEnd skills) with zero configuration errors.
- **Chromium CDP**: Headless runner started on `127.0.0.1:9223`, reported `state=ready`, and cleanly stopped.

### JUDGMENT
- Isolating 15 manual specialists under `manual-skills/` prevents catalog pollution in `omp`'s automatic tool selection, while slash command stubs preserve human-in-the-loop manual entry points.
- Pruning VANTA charter in favor of an explicit 33 closed intent classification technical router aligns with omp's architectural discipline.
- Large binary `codebase-memory-mcp` (286MB) is provisioned via `restore.sh` with exact SHA256 verification and excluded from git, strictly observing GitHub's 100MB commit limit.
