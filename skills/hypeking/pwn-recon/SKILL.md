---
name: pwn-recon
description: "Web reconnaissance: HTTP probing, crawling, fuzzing, parameter mining, tech fingerprinting + ARTEX api-recon (SPA/MPA frontend API harvest). Skills: automated-web-fuzzing, httpx-smart-recon, katana-crawler-auto, param-miner-advanced, recon-methodology, api-recon. Trigger: httpx, katana, param miner, web fuzz, recon methodology, api recon."
---

# pwn-recon — 01-recon

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/01-recon/`

## Routing table (6 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `automated-web-fuzzing` | `01-recon/automated-web-fuzzing/scripts/agent.py` | run | Automated Web Fuzzer — Parameter Discovery & Recursive Path Enumeration |
| `httpx-smart-recon` | `01-recon/httpx-smart-recon/scripts/agent.py` | run | Smart reconnaissance tool probing URLs with httpx for tech detection and probing. |
| `katana-crawler-auto` | `01-recon/katana-crawler-auto/scripts/agent.py` | run | Automates katana headless crawler with JS parsing and smart crawling logic. |
| `param-miner-advanced` | `01-recon/param-miner-advanced/scripts/agent.py` | run | Advanced parameter mining tool replicating Burp Param Miner logic for hidden parameter discovery. |
| `recon-methodology` | `01-recon/recon-methodology/SKILL.md` | read | Bug bounty and pentest reconnaissance methodology |
| `api-recon` | `01-recon/api-recon/SKILL.md` (+ scripts/) | read | ARTEX SPA/MPA frontend API harvest (static + auth-stub runtime). Prefer `pwn-api-recon` route. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
