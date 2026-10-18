---
name: pwn-adv-recon
description: "Advanced recon and OSINT: shodan, subfinder, spiderfoot, darkweb, certificate transparency, typosquatting. 17 skills: analyzing-certificate-transparency-for-phishing, analyzing-typosquatting-domains-with-dnstwist, auditing-tls-certificate-transparency-logs, building-threat-actor-profile-from-osint, collecting-open-source-intelligence, conducting-external-reconnaissance-with-osint, monitoring-darkweb-sources, performing-brand-monitoring-for-impersonation. Trigger words: analyzing certificate transparency for phishing, analyzing typosquatting domains with dnstwist, auditing tls certificate transparency logs, building threat actor profile from osint, collecting open source intelligence, conducting external reconnaissance with osint."
---

# pwn-adv-recon — 10-adv-recon

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/10-adv-recon/`

## Routing table (17 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `analyzing-certificate-transparency-for-phishing` | `10-adv-recon/analyzing-certificate-transparency-for-phishing/scripts/agent.py` | run | Certificate Transparency monitoring agent for phishing detection. |
| `analyzing-typosquatting-domains-with-dnstwist` | `10-adv-recon/analyzing-typosquatting-domains-with-dnstwist/scripts/agent.py` | run | Typosquatting domain detection agent using dnstwist concepts. |
| `auditing-tls-certificate-transparency-logs` | `10-adv-recon/auditing-tls-certificate-transparency-logs/scripts/agent.py` | run | CT Log Monitoring Agent - Monitors Certificate Transparency logs for unauthorized |
| `building-threat-actor-profile-from-osint` | `10-adv-recon/building-threat-actor-profile-from-osint/scripts/agent.py` | run | Threat Actor Profiling from OSINT Agent - Builds threat actor profiles using open-source intelligence. |
| `collecting-open-source-intelligence` | `10-adv-recon/collecting-open-source-intelligence/scripts/agent.py` | run | OSINT Collection Agent - Gathers open-source intelligence on targets using Shodan and crt.sh. |
| `conducting-external-reconnaissance-with-osint` | `10-adv-recon/conducting-external-reconnaissance-with-osint/scripts/agent.py` | run | External Reconnaissance Agent - Maps organization attack surface using passive OSINT. |
| `monitoring-darkweb-sources` | `10-adv-recon/monitoring-darkweb-sources/scripts/agent.py` | run | Dark Web Source Monitoring Agent |
| `performing-brand-monitoring-for-impersonation` | `10-adv-recon/performing-brand-monitoring-for-impersonation/scripts/agent.py` | run | Brand impersonation monitoring agent. |
| `performing-dark-web-monitoring-for-threats` | `10-adv-recon/performing-dark-web-monitoring-for-threats/scripts/agent.py` | run | Dark web threat monitoring agent. |
| `performing-dns-enumeration-and-zone-transfer` | `10-adv-recon/performing-dns-enumeration-and-zone-transfer/scripts/agent.py` | run | DNS Enumeration and Zone Transfer Agent — AUTHORIZED TESTING ONLY |
| `performing-ip-reputation-analysis-with-shodan` | `10-adv-recon/performing-ip-reputation-analysis-with-shodan/scripts/agent.py` | run | Agent for performing IP reputation analysis using the Shodan API. |
| `performing-open-source-intelligence-gathering` | `10-adv-recon/performing-open-source-intelligence-gathering/scripts/agent.py` | run | Agent for performing open source intelligence (OSINT) gathering. |
| `performing-osint-with-spiderfoot` | `10-adv-recon/performing-osint-with-spiderfoot/scripts/agent.py` | run | OSINT automation agent using SpiderFoot REST API for target profiling and reconnaissance. |
| `performing-paste-site-monitoring-for-credentials` | `10-adv-recon/performing-paste-site-monitoring-for-credentials/scripts/agent.py` | run | Agent for performing paste site monitoring for leaked credentials. |
| `performing-subdomain-enumeration-with-subfinder` | `10-adv-recon/performing-subdomain-enumeration-with-subfinder/scripts/agent.py` | run | Agent for subdomain enumeration using subfinder and httpx. |
| `profiling-threat-actor-groups` | `10-adv-recon/profiling-threat-actor-groups/scripts/agent.py` | run | Threat actor profiling agent using MITRE ATT&CK STIX data and STIX2 library. |
| `tracking-threat-actor-infrastructure` | `10-adv-recon/tracking-threat-actor-infrastructure/scripts/agent.py` | run | Agent for tracking threat actor infrastructure. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
