---
name: pwn-network-web
description: "Network analysis and defense: wireshark, zeek, scapy, firewall rules, IDS/IPS, traffic analysis. 27 skills: analyzing-dns-logs-for-exfiltration, analyzing-network-flow-data-with-netflow, analyzing-network-packets-with-scapy, analyzing-network-traffic-for-incidents, analyzing-network-traffic-with-wireshark, configuring-network-segmentation-with-vlans, configuring-pfsense-firewall-rules, configuring-snort-ids-for-intrusion-detection. Trigger words: analyzing dns logs for exfiltration, analyzing network flow data with netflow, analyzing network packets with scapy, analyzing network traffic for incidents, analyzing network traffic with wireshark, configuring network segmentation with vlans."
---

# pwn-network-web — 11-network-web

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/11-network-web/`

## Routing table (27 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `analyzing-dns-logs-for-exfiltration` | `11-network-web/analyzing-dns-logs-for-exfiltration/scripts/agent.py` | run | DNS exfiltration detection agent using entropy analysis and query pattern detection. |
| `analyzing-network-flow-data-with-netflow` | `11-network-web/analyzing-network-flow-data-with-netflow/scripts/agent.py` | run | NetFlow Analysis Agent - Parses NetFlow v9/IPFIX for anomalies, port scans, and exfiltration. |
| `analyzing-network-packets-with-scapy` | `11-network-web/analyzing-network-packets-with-scapy/scripts/agent.py` | run | Network packet analysis agent using Scapy for pcap parsing and anomaly detection. |
| `analyzing-network-traffic-for-incidents` | `11-network-web/analyzing-network-traffic-for-incidents/scripts/agent.py` | run | Network traffic incident analysis agent using scapy and tshark for PCAP investigation. |
| `analyzing-network-traffic-with-wireshark` | `11-network-web/analyzing-network-traffic-with-wireshark/scripts/agent.py` | run | Wireshark/tshark packet analysis agent for network security investigations. |
| `configuring-network-segmentation-with-vlans` | `11-network-web/configuring-network-segmentation-with-vlans/scripts/agent.py` | run | VLAN Network Segmentation Agent - Configures and audits VLAN segmentation on managed switches. |
| `configuring-pfsense-firewall-rules` | `11-network-web/configuring-pfsense-firewall-rules/scripts/agent.py` | run | pfSense Firewall Configuration Agent - Manages firewall rules via pfSense API. |
| `configuring-snort-ids-for-intrusion-detection` | `11-network-web/configuring-snort-ids-for-intrusion-detection/scripts/agent.py` | run | Snort IDS configuration and rule management agent. |
| `configuring-suricata-for-network-monitoring` | `11-network-web/configuring-suricata-for-network-monitoring/scripts/agent.py` | run | Suricata IDS/IPS monitoring and EVE JSON log analysis agent. |
| `detecting-arp-poisoning-in-network-traffic` | `11-network-web/detecting-arp-poisoning-in-network-traffic/scripts/agent.py` | run | ARP poisoning detection agent for network traffic analysis. |
| `detecting-beaconing-patterns-with-zeek` | `11-network-web/detecting-beaconing-patterns-with-zeek/scripts/agent.py` | run | Agent for detecting C2 beaconing patterns in Zeek conn.log data. |
| `detecting-exfiltration-over-dns-with-zeek` | `11-network-web/detecting-exfiltration-over-dns-with-zeek/scripts/agent.py` | run | Detect DNS exfiltration from Zeek dns.log by analyzing entropy and query patterns. |
| `detecting-lateral-movement-with-zeek` | `11-network-web/detecting-lateral-movement-with-zeek/scripts/agent.py` | run | Zeek lateral movement detection agent. |
| `detecting-network-anomalies-with-zeek` | `11-network-web/detecting-network-anomalies-with-zeek/scripts/agent.py` | run | Zeek network anomaly detection agent for log analysis and threat hunting. |
| `detecting-network-scanning-with-ids-signatures` | `11-network-web/detecting-network-scanning-with-ids-signatures/scripts/agent.py` | run | Network scanning detection agent using IDS signature analysis. |
| `detecting-port-scanning-with-fail2ban` | `11-network-web/detecting-port-scanning-with-fail2ban/scripts/agent.py` | run | Fail2ban port scan detection and management agent. |
| `implementing-bgp-security-with-rpki` | `11-network-web/implementing-bgp-security-with-rpki/scripts/agent.py` | run | BGP RPKI validation agent using RIPEstat and Cloudflare RPKI APIs. |
| `implementing-ddos-mitigation-with-cloudflare` | `11-network-web/implementing-ddos-mitigation-with-cloudflare/scripts/agent.py` | run | DDoS mitigation agent using Cloudflare API for traffic analysis and rule management. |
| `implementing-network-access-control` | `11-network-web/implementing-network-access-control/scripts/agent.py` | run | Network Access Control (802.1X/NAC) monitoring agent using RADIUS and SNMP. |
| `implementing-network-intrusion-prevention-with-suricata` | `11-network-web/implementing-network-intrusion-prevention-with-suricata/scripts/agent.py` | run | Suricata IPS Agent - manages rules, analyzes alerts, and tunes Suricata intrusion prevention. |
| `implementing-network-traffic-analysis-with-arkime` | `11-network-web/implementing-network-traffic-analysis-with-arkime/scripts/agent.py` | run | Arkime Network Traffic Analysis Agent - Queries Arkime API for session analysis and anomaly detection. |
| `implementing-network-traffic-baselining` | `11-network-web/implementing-network-traffic-baselining/scripts/agent.py` | run | Network traffic baselining agent using pandas for NetFlow/IPFIX statistical analysis. |
| `implementing-next-generation-firewall-with-palo-alto` | `11-network-web/implementing-next-generation-firewall-with-palo-alto/scripts/agent.py` | run | Palo Alto NGFW Agent - audits security policies, threat prevention, and App-ID usage via XML API. |
| `performing-dns-tunneling-detection` | `11-network-web/performing-dns-tunneling-detection/scripts/agent.py` | run | Agent for detecting DNS tunneling via entropy and statistical analysis. |
| `performing-network-packet-capture-analysis` | `11-network-web/performing-network-packet-capture-analysis/scripts/agent.py` | run | Agent for performing network packet capture analysis with scapy and tshark. |
| `performing-network-traffic-analysis-with-tshark` | `11-network-web/performing-network-traffic-analysis-with-tshark/scripts/agent.py` | run | Network traffic analysis agent using tshark and pyshark for PCAP analysis. |
| `performing-network-traffic-analysis-with-zeek` | `11-network-web/performing-network-traffic-analysis-with-zeek/scripts/agent.py` | run | Agent for performing network traffic analysis with Zeek (Bro) log files. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
