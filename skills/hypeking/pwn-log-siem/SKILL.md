---
name: pwn-log-siem
description: "Log analysis and SIEM: splunk, sigma rules, elastic, sentinel, qradar, audit logs. 20 skills: analyzing-api-gateway-access-logs, analyzing-azure-activity-logs-for-threats, analyzing-kubernetes-audit-logs, analyzing-linux-audit-logs-for-intrusion, analyzing-office365-audit-logs-for-compromise, analyzing-powershell-script-block-logging, analyzing-security-logs-with-splunk, analyzing-web-server-logs-for-intrusion. Trigger words: analyzing api gateway access logs, analyzing azure activity logs for threats, analyzing kubernetes audit logs, analyzing linux audit logs for intrusion, analyzing office365 audit logs for compromise, analyzing powershell script block logging."
---

# pwn-log-siem — 13-log-siem-web

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/13-log-siem-web/`

## Routing table (20 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `analyzing-api-gateway-access-logs` | `13-log-siem-web/analyzing-api-gateway-access-logs/scripts/agent.py` | run | Agent for analyzing API Gateway access logs for security threats. |
| `analyzing-azure-activity-logs-for-threats` | `13-log-siem-web/analyzing-azure-activity-logs-for-threats/scripts/agent.py` | run | Agent for analyzing Azure activity logs for threat detection. |
| `analyzing-kubernetes-audit-logs` | `13-log-siem-web/analyzing-kubernetes-audit-logs/scripts/agent.py` | run | Agent for analyzing Kubernetes audit logs for security threats. |
| `analyzing-linux-audit-logs-for-intrusion` | `13-log-siem-web/analyzing-linux-audit-logs-for-intrusion/scripts/agent.py` | run | Linux audit log analysis agent for intrusion detection. |
| `analyzing-office365-audit-logs-for-compromise` | `13-log-siem-web/analyzing-office365-audit-logs-for-compromise/scripts/agent.py` | run | Agent for analyzing Office 365 audit logs for compromise indicators via Microsoft Graph. |
| `analyzing-powershell-script-block-logging` | `13-log-siem-web/analyzing-powershell-script-block-logging/scripts/agent.py` | run | PowerShell Script Block Logging Analyzer - Parses Event 4104 from EVTX for obfuscated commands. |
| `analyzing-security-logs-with-splunk` | `13-log-siem-web/analyzing-security-logs-with-splunk/scripts/agent.py` | run | Agent for analyzing security logs with Splunk using splunk-sdk. |
| `analyzing-web-server-logs-for-intrusion` | `13-log-siem-web/analyzing-web-server-logs-for-intrusion/scripts/agent.py` | run | Web Server Log Intrusion Analyzer - Detects SQLi, LFI, XSS, and scanner activity in access logs. |
| `analyzing-windows-event-logs-in-splunk` | `13-log-siem-web/analyzing-windows-event-logs-in-splunk/scripts/agent.py` | run | Agent for analyzing Windows event logs in Splunk for SOC operations. |
| `building-cloud-siem-with-sentinel` | `13-log-siem-web/building-cloud-siem-with-sentinel/scripts/agent.py` | run | Agent for managing Microsoft Sentinel SIEM operations. |
| `building-detection-rule-with-splunk-spl` | `13-log-siem-web/building-detection-rule-with-splunk-spl/scripts/agent.py` | run | Splunk SPL Detection Rule Builder Agent - Generates and validates Splunk detection rules. |
| `building-detection-rules-with-sigma` | `13-log-siem-web/building-detection-rules-with-sigma/scripts/agent.py` | run | Agent for building and converting Sigma detection rules. |
| `correlating-security-events-in-qradar` | `13-log-siem-web/correlating-security-events-in-qradar/scripts/agent.py` | run | IBM QRadar SIEM correlation and offense management agent. |
| `detecting-entra-offensive-tools-in-graph-logs` | `13-log-siem-web/detecting-entra-offensive-tools-in-graph-logs/scripts/agent.py` | run | agent.py - Hunt Entra offensive-tool fingerprints in Graph activity logs. |
| `detecting-oauth-token-theft` | `13-log-siem-web/detecting-oauth-token-theft/scripts/agent.py` | run | OAuth token theft detection agent. |
| `implementing-log-forwarding-with-fluentd` | `13-log-siem-web/implementing-log-forwarding-with-fluentd/scripts/agent.py` | run | Fluentd/Fluent Bit log forwarding configuration generator and tester. |
| `implementing-security-monitoring-with-datadog` | `13-log-siem-web/implementing-security-monitoring-with-datadog/scripts/agent.py` | run | Agent for implementing security monitoring with Datadog. |
| `implementing-siem-correlation-rules-for-apt` | `13-log-siem-web/implementing-siem-correlation-rules-for-apt/scripts/agent.py` | run | SIEM Correlation Rules Agent - Builds and deploys multi-event APT detection rules via Splunk and Sigma. |
| `implementing-syslog-centralization-with-rsyslog` | `13-log-siem-web/implementing-syslog-centralization-with-rsyslog/scripts/agent.py` | run | Rsyslog Centralization Agent - Generates and deploys TLS-secured rsyslog configurations. |
| `performing-threat-hunting-with-elastic-siem` | `13-log-siem-web/performing-threat-hunting-with-elastic-siem/scripts/agent.py` | run | Threat hunting agent for Elastic SIEM using elasticsearch-py. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
