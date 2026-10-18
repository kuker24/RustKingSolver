---
name: pwn-red-team
description: "Red team / C2: Sliver (+MCP), Havoc, AdaptixC2, Caldera adversary emulation, redirectors, GoPhish, Evilginx, MITRE Engage, eBPF, AD sim. Trigger: c2, sliver, havoc, adaptix, caldera, sandcat, stockpile, phishing, gophish, evilginx, mitre engage, ebpf, spearphish."
---

# pwn-red-team — 12-red-team-web

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/12-red-team-web/`

Provenance (C2 harvest): `skill://hypeking/C2-FRAMEWORKS-IMPORT.md`

**Tools:** `skill://hypeking/C2-TOOLS.md` · `source …/hypeking/scripts/c2-env.sh`


## Routing table

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `operating-sliver-c2` | `…/operating-sliver-c2/scripts/agent.py` | run | Sliver operator (`sliver-py`) + MCP notes |
| `building-c2-infrastructure-with-sliver-framework` | `…/building-c2-infrastructure-with-sliver-framework/scripts/agent.py` | run | Sliver teamserver/listener deploy |
| `operating-havoc-c2` | `…/operating-havoc-c2/scripts/agent.py` | run | Havoc teamserver operator |
| `building-red-team-c2-infrastructure-with-havoc` | `…/building-red-team-c2-infrastructure-with-havoc/scripts/agent.py` | run | Havoc infra builder |
| `operating-adaptix-c2` | `…/operating-adaptix-c2/scripts/agent.py` | run | **NEW** AdaptixC2 install/status + compose |
| `operating-caldera-adversary-emulation` | `…/operating-caldera-adversary-emulation/scripts/agent.py` | run | **NEW** Caldera REST ops / Stockpile |
| `building-c2-redirector-infrastructure` | `…/building-c2-redirector-infrastructure/scripts/agent.py` | run | Redirector configs |
| `performing-red-team-phishing-with-gophish` | `…/performing-red-team-phishing-with-gophish/scripts/agent.py` | run | GoPhish campaign automation (canonical) |
| `conducting-social-engineering-penetration-test` | `…/conducting-social-engineering-penetration-test/scripts/agent.py` | run | Broad SE pentest (GoPhish+) |
| `conducting-spearphishing-simulation-campaign` | `…/conducting-spearphishing-simulation-campaign/scripts/agent.py` | run | Targeted spearphish templates |
| `performing-initial-access-with-evilginx3` | `…/performing-initial-access-with-evilginx3/scripts/agent.py` | run | Evilginx3 AiTM |
| `attacking-oauth-with-device-code-phishing` | `…/attacking-oauth-with-device-code-phishing/scripts/agent.py` | run | Entra device-code phish |
| `executing-active-directory-attack-simulation` | `…/executing-active-directory-attack-simulation/scripts/agent.py` | run | AD attack sim (Impacket) |
| `executing-red-team-engagement-planning` | `…/executing-red-team-engagement-planning/scripts/agent.py` | run | Engagement planning |
| `executing-red-team-exercise` | `…/executing-red-team-exercise/scripts/agent.py` | run | Exercise / ATT&CK tracking |
| `designing-adversary-engagement-with-mitre-engage` | `…/designing-adversary-engagement-with-mitre-engage/SKILL.md` | read | MITRE Engage methodology |
| `ebpf-attacks` | `…/ebpf-attacks/SKILL.md` | read | eBPF post-exploit methodology |

## Usage

```bash
python3 '~/.omp/agent/skills/hypeking/scripts/route.py' --ask 'adaptix listener'
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/12-red-team-web/<skill>/scripts/agent.py' --help
```
