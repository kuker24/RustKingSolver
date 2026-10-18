---
name: pwn-mitre-ics
description: "MITRE ATT&CK ICS techniques (83 TTPs) - search by keyword or browse by tactic TA0100-TA0111. Keywords: T0801_monitor-process-state, T0802_automated-collection, T0811_data-from-information-repositories, T0830_adversary-in-the-middle, T0845_program-upload, T0852_screen-capture, T0861_point-tag-identification, T0868_detect-operating-mode."
---

# pwn-mitre-ics — 21-mitre-ics

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/21-mitre-ics/`
**Format:** methodology-only (bare SKILL.md per technique — read and execute manually).

## Tactic index (83 techniques)

| Tactic dir | Tactic | Techniques |
|---|---|---|
| `TA0100_collection` | TA0100 Collection | 10 |
| `TA0101_command-and-control` | TA0101 Command And Control | 3 |
| `TA0102_discovery` | TA0102 Discovery | 5 |
| `TA0103_evasion` | TA0103 Evasion | 6 |
| `TA0104_execution` | TA0104 Execution | 10 |
| `TA0105_impact` | TA0105 Impact | 12 |
| `TA0106_impair-process-control` | TA0106 Impair Process Control | 3 |
| `TA0107_inhibit-response-function` | TA0107 Inhibit Response Function | 12 |
| `TA0108_initial-access` | TA0108 Initial Access | 12 |
| `TA0109_lateral-movement` | TA0109 Lateral Movement | 4 |
| `TA0110_persistence` | TA0110 Persistence | 5 |
| `TA0111_privilege-escalation` | TA0111 Privilege Escalation | 1 |

## Search recipe

Find techniques by keyword (greps all 83 SKILL.md files):

```bash
grep -ril "<keyword>" ~/.omp/agent/skills/hypeking/всегда побеждать/21-mitre-ics --include=SKILL.md
```

Narrow to one tactic:

```bash
grep -ril "<keyword>" ~/.omp/agent/skills/hypeking/всегда побеждать/21-mitre-ics/TA0100_collection --include=SKILL.md
```

## Usage

1. Ask for a tactic (`TA0001`) or keyword.
2. `read ~/.omp/agent/skills/hypeking/всегда побеждать/21-mitre-ics/<tactic-dir>/<technique-dir>/SKILL.md`
3. Execute the procedure manually — these are methodology playbooks, not scripts.
