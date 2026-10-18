---
name: pwn-mitre-mobile
description: "MITRE ATT&CK Mobile techniques (124 TTPs) - search by keyword or browse by tactic. Keywords: T1451_sim-card-swap, T1456_drive-by-compromise, T1461_lockscreen-bypass, T1474_supply-chain-compromise, T1660_phishing, T1661_application-versioning, T1664_exploitation-for-initial-access, t1458-replication-through-removable."
---

# pwn-mitre-mobile — 20-mitre-mobile

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/20-mitre-mobile/`
**Format:** methodology-only (bare SKILL.md per technique — read and execute manually).

## Tactic index (124 techniques)

| Tactic dir | Tactic | Techniques |
|---|---|---|
| `TA0027_initial-access` | TA0027 Initial Access | 11 |
| `TA0028_persistence` | TA0028 Persistence | 7 |
| `TA0029_privilege-escalation` | TA0029 Privilege Escalation | 3 |
| `TA0030_defense-evasion` | TA0030 Defense Evasion | 32 |
| `TA0031_credential-access` | TA0031 Credential Access | 5 |
| `TA0032_discovery` | TA0032 Discovery | 10 |
| `TA0033_lateral-movement` | TA0033 Lateral Movement | 1 |
| `TA0034_impact` | TA0034 Impact | 9 |
| `TA0035_collection` | TA0035 Collection | 23 |
| `TA0036_exfiltration` | TA0036 Exfiltration | 3 |
| `TA0037_command-and-control` | TA0037 Command And Control | 16 |
| `TA0041_execution` | TA0041 Execution | 4 |

## Search recipe

Find techniques by keyword (greps all 124 SKILL.md files):

```bash
grep -ril "<keyword>" ~/.omp/agent/skills/hypeking/всегда побеждать/20-mitre-mobile --include=SKILL.md
```

Narrow to one tactic:

```bash
grep -ril "<keyword>" ~/.omp/agent/skills/hypeking/всегда побеждать/20-mitre-mobile/TA0027_initial-access --include=SKILL.md
```

## Usage

1. Ask for a tactic (`TA0001`) or keyword.
2. `read ~/.omp/agent/skills/hypeking/всегда побеждать/20-mitre-mobile/<tactic-dir>/<technique-dir>/SKILL.md`
3. Execute the procedure manually — these are methodology playbooks, not scripts.
