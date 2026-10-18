---
name: pwn-automation
description: "Tool automation: nuclei, ffuf, dalfox, XSStrike, exploit chaining, CI/CD attacks, proxy scripting. 10 skills: burp-bambda-scripting, caido-scripting, cicd-attacks, dalfox-advanced, exploit-chain-automation, ffuf-advanced, mitmproxy-advanced, nuclei-custom-templates. Trigger words: burp bambda scripting, caido scripting, cicd attacks, dalfox advanced, exploit chain automation, ffuf advanced."
---

# pwn-automation — 06-automation

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/06-automation/`

## Routing table (10 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `burp-bambda-scripting` | `06-automation/burp-bambda-scripting/scripts/agent.py` | run | burp-bambda-scripting/scripts/agent.py |
| `caido-scripting` | `06-automation/caido-scripting/scripts/agent.py` | run | caido-scripting/scripts/agent.py |
| `cicd-attacks` | `06-automation/cicd-attacks/SKILL.md` | read | CI/CD pipeline attacks for secret extraction, pipeline injection, and supply chain compromise via GitHub/Jenkins/GitLab |
| `dalfox-advanced` | `06-automation/dalfox-advanced/scripts/agent.py` | run | Wraps dalfox XSS scanner with custom payloads and structured output parsing. |
| `exploit-chain-automation` | `06-automation/exploit-chain-automation/scripts/agent.py` | run | exploit-chain-automation/scripts/agent.py |
| `ffuf-advanced` | `06-automation/ffuf-advanced/scripts/agent.py` | run | ffuf-advanced/scripts/agent.py |
| `mitmproxy-advanced` | `06-automation/mitmproxy-advanced/scripts/agent.py` | run | mitmproxy-advanced/scripts/agent.py |
| `nuclei-custom-templates` | `06-automation/nuclei-custom-templates/scripts/agent.py` | run | Generates and tests custom nuclei YAML templates against targets. |
| `turbo-intruder-automation` | `06-automation/turbo-intruder-automation/scripts/agent.py` | run | turbo-intruder-automation/scripts/agent.py |
| `xsstrike-advanced` | `06-automation/xsstrike-advanced/scripts/agent.py` | run | Wraps XSStrike with advanced DOM scanning and structured output parsing. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
