---
name: pwn-mitre-enterprise
description: "MITRE ATT&CK Enterprise techniques (691 TTPs) - search by keyword or browse by tactic TA0001-TA0043. Keywords: T1189_drive-by-compromise, T1190_exploit-public-facing-application, T1195_supply-chain-compromise, T1199_trusted-relationship, T1200_hardware-additions, T1566.001_spearphishing-attachment, T1566.002_spearphishing-link, T1566.003_spearphishing-via-service."
---

# pwn-mitre-enterprise — 19-mitre-enterprise

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/19-mitre-enterprise/`
**Format:** methodology-only (bare SKILL.md per technique — read and execute manually).

## Tactic index (691 techniques)

| Tactic dir | Tactic | Techniques |
|---|---|---|
| `TA0001_initial-access` | TA0001 Initial Access | 15 |
| `TA0002_execution` | TA0002 Execution | 45 |
| `TA0003_persistence` | TA0003 Persistence | 80 |
| `TA0004_privilege-escalation` | TA0004 Privilege Escalation | 25 |
| `TA0005_defense-evasion` | TA0005 Defense Evasion | 183 |
| `TA0006_credential-access` | TA0006 Credential Access | 62 |
| `TA0007_discovery` | TA0007 Discovery | 43 |
| `TA0008_lateral-movement` | TA0008 Lateral Movement | 17 |
| `TA0009_collection` | TA0009 Collection | 36 |
| `TA0010_exfiltration` | TA0010 Exfiltration | 19 |
| `TA0011_command-and-control` | TA0011 Command And Control | 41 |
| `TA0040_impact` | TA0040 Impact | 33 |
| `TA0042_resource-development` | TA0042 Resource Development | 47 |
| `TA0043_reconnaissance` | TA0043 Reconnaissance | 45 |

## Search recipe

Find techniques by keyword (greps all 691 SKILL.md files):

```bash
grep -ril "<keyword>" ~/.omp/agent/skills/hypeking/всегда побеждать/19-mitre-enterprise --include=SKILL.md
```

Narrow to one tactic:

```bash
grep -ril "<keyword>" ~/.omp/agent/skills/hypeking/всегда побеждать/19-mitre-enterprise/TA0001_initial-access --include=SKILL.md
```

## Usage

1. Ask for a tactic (`TA0001`) or keyword.
2. `read ~/.omp/agent/skills/hypeking/всегда побеждать/19-mitre-enterprise/<tactic-dir>/<technique-dir>/SKILL.md`
3. Execute the procedure manually — these are methodology playbooks, not scripts.
