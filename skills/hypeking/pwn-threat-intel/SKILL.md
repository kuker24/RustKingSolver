---
name: pwn-threat-intel
description: "Threat intelligence: IOC hunting, C2 detection, webshells, urlscan, covert channels. 22 skills: analyzing-command-and-control-communication, analyzing-malicious-url-with-urlscan, analyzing-network-covert-channels-in-malware, analyzing-ransomware-network-indicators, building-ioc-enrichment-pipeline-with-opencti, building-threat-intelligence-platform, detecting-api-enumeration-attacks, detecting-command-and-control-over-dns. Trigger words: analyzing command and control communication, analyzing malicious url with urlscan, analyzing network covert channels in malware, analyzing ransomware network indicators, building ioc enrichment pipeline with opencti, building threat intelligence platform."
---

# pwn-threat-intel — 15-threat-intel

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/15-threat-intel/`

## Routing table (22 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `analyzing-command-and-control-communication` | `15-threat-intel/analyzing-command-and-control-communication/scripts/agent.py` | run | C2 communication analysis agent for beacon detection and protocol decoding. |
| `analyzing-malicious-url-with-urlscan` | `15-threat-intel/analyzing-malicious-url-with-urlscan/scripts/agent.py` | run | URLScan.io Malicious URL Analysis Agent - Submits and analyzes URLs via the urlscan.io API. |
| `analyzing-network-covert-channels-in-malware` | `15-threat-intel/analyzing-network-covert-channels-in-malware/scripts/agent.py` | run | Network covert channel detection agent for malware traffic analysis. |
| `analyzing-ransomware-network-indicators` | `15-threat-intel/analyzing-ransomware-network-indicators/scripts/agent.py` | run | Detect ransomware network indicators: C2 beaconing, TOR connections, data exfiltration via Zeek/NetFlow. |
| `building-ioc-enrichment-pipeline-with-opencti` | `15-threat-intel/building-ioc-enrichment-pipeline-with-opencti/scripts/agent.py` | run | IOC enrichment pipeline using OpenCTI and the pycti Python client. |
| `building-threat-intelligence-platform` | `15-threat-intel/building-threat-intelligence-platform/scripts/agent.py` | run | Threat intelligence platform builder. |
| `detecting-api-enumeration-attacks` | `15-threat-intel/detecting-api-enumeration-attacks/scripts/agent.py` | run | API enumeration attack detection agent. |
| `detecting-command-and-control-over-dns` | `15-threat-intel/detecting-command-and-control-over-dns/scripts/agent.py` | run | DNS C2 Detection Agent |
| `detecting-compromised-cloud-credentials` | `15-threat-intel/detecting-compromised-cloud-credentials/scripts/agent.py` | run | Compromised cloud credential detection agent using AWS CloudTrail and GuardDuty. |
| `detecting-dependency-confusion` | `15-threat-intel/detecting-dependency-confusion/scripts/agent.py` | run | Dependency confusion detection helper. |
| `detecting-dns-exfiltration-with-dns-query-analysis` | `15-threat-intel/detecting-dns-exfiltration-with-dns-query-analysis/scripts/agent.py` | run | DNS exfiltration detection agent using entropy analysis and query pattern anomalies. |
| `detecting-exfiltration-over-dns-with-zeek` | `15-threat-intel/detecting-exfiltration-over-dns-with-zeek/scripts/agent.py` | run | Detect DNS exfiltration from Zeek dns.log by analyzing entropy and query patterns. |
| `detecting-shadow-api-endpoints` | `15-threat-intel/detecting-shadow-api-endpoints/scripts/agent.py` | run | Agent for discovering undocumented (shadow) API endpoints via traffic analysis. |
| `detecting-shadow-it-cloud-usage` | `15-threat-intel/detecting-shadow-it-cloud-usage/scripts/agent.py` | run | Agent for detecting shadow IT cloud usage via proxy logs, DNS queries, and netflow. |
| `detecting-supply-chain-attacks-in-ci-cd` | `15-threat-intel/detecting-supply-chain-attacks-in-ci-cd/scripts/agent.py` | run | Agent for detecting supply chain attacks in CI/CD pipelines. |
| `detecting-suspicious-oauth-application-consent` | `15-threat-intel/detecting-suspicious-oauth-application-consent/scripts/agent.py` | run | Agent for detecting suspicious OAuth application consent grants in Azure AD / Entra ID. |
| `hunting-for-command-and-control-beaconing` | `15-threat-intel/hunting-for-command-and-control-beaconing/scripts/agent.py` | run | Agent for hunting C2 beaconing across multiple data sources. |
| `hunting-for-domain-fronting-c2-traffic` | `15-threat-intel/hunting-for-domain-fronting-c2-traffic/scripts/agent.py` | run | Detect domain fronting C2 traffic via SNI/Host header mismatch and TLS certificate analysis. |
| `hunting-for-living-off-the-land-binaries` | `15-threat-intel/hunting-for-living-off-the-land-binaries/scripts/agent.py` | run | Agent for hunting Living-off-the-Land Binaries (LOLBins) execution patterns. |
| `hunting-for-spearphishing-indicators` | `15-threat-intel/hunting-for-spearphishing-indicators/scripts/agent.py` | run | Agent for hunting spearphishing indicators across email and endpoint logs. |
| `hunting-for-webshell-activity` | `15-threat-intel/hunting-for-webshell-activity/scripts/agent.py` | run | Agent for hunting web shell activity on web servers via process tree and log analysis. |
| `performing-threat-hunting-with-yara-rules` | `15-threat-intel/performing-threat-hunting-with-yara-rules/scripts/agent.py` | run | Threat hunting agent using YARA rules. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
