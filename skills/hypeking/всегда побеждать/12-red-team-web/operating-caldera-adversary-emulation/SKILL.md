---
name: operating-caldera-adversary-emulation
description: "Operate Apache Caldera for ATT&CK adversary emulation: server REST API, Sandcat agent, Stockpile abilities/adversaries, Atomic plugin, operation planners. Trigger: caldera, mitre caldera, sandcat agent, stockpile abilities, adversary emulation operation, caldera rest api."
---

# operating-caldera-adversary-emulation

**Upstream:** [apache/caldera](https://github.com/apache/caldera) (Apache-2.0) · docs: https://caldera.readthedocs.io/


**Tools:** tree staged at `~/tools/caldera` · `source …/hypeking/scripts/c2-env.sh` · matrix `skill://hypeking/C2-TOOLS.md`

Plugins are git submodules (stockpile/sandcat/atomic empty until `git submodule update --init`). Portable skill ships sample adversary YAML + REST operator helper — full platform stays in `~/tools/caldera`.

## ACTION REQUIRED

1. Deploy Caldera (venv or Docker) with plugins enabled in `conf/default.yml`.
2. Start Sandcat agent on lab target; verify beacon in UI/API.
3. Pick adversary profile (Stockpile / Atomic / Emu) → create Operation → run planner.
4. Export operation results → debrief (`plugins/debrief`) / ATT&CK coverage (`compass`).

## Core pieces

| Component | Role |
|---|---|
| Core server | `server.py` + REST/Web UI; async C2 |
| **sandcat** | Default agent (gocat) |
| **stockpile** | Abilities, adversaries, planners, payloads |
| **atomic** | Atomic Red Team TTPs |
| **access / emu / compass / debrief** | Initial access, CTID plans, ATT&CK viz, reporting |

## Lab install

```bash
git clone --depth 1 https://github.com/apache/caldera.git ~/tools/caldera
cd ~/tools/caldera
git submodule update --init --recursive --depth 1
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py --insecure   # lab only; prefer HTTPS + auth in real eng
# UI default: http://127.0.0.1:8888  (check conf/default.yml for users)
```

Docker: upstream `docker-compose.yml`.

## REST operator (helper)

```bash
python3 scripts/agent.py --base http://127.0.0.1:8888 \
  --user red --password <from conf> \
  --list-adversaries
python3 scripts/agent.py --base http://127.0.0.1:8888 \
  --user red --password <pw> \
  --start-operation --adversary <uuid> --name lab-op1
```

API patterns (Caldera v5-ish): `/api/v2/adversaries`, `/api/v2/abilities`, `/api/v2/operations`, `/api/v2/agents`.

## Operation checklist

1. Scope + rules of engagement mapped to ATT&CK techniques.
2. Agent group created; Sandcat (or Manx/SSH) healthy.
3. Adversary profile selected — start from Stockpile packs in `references/stockpile-adversaries/`.
4. Planner: atomic vs batched; fact sources clean.
5. Monitor links/facts; pause on out-of-scope.
6. Export reports; map gaps to manual Sliver/Adaptix/Havoc follow-up.

## Complements

| Need | Pack |
|---|---|
| Manual C2 implant ops | `operating-sliver-c2` / `operating-adaptix-c2` / `operating-havoc-c2` |
| MITRE Engage design | `designing-adversary-engagement-with-mitre-engage` |
| ATT&CK enterprise | `pwn-mitre-enterprise` |
| Phishing initial access | GoPhish / Evilginx packs |

## References

- `references/README.md`, `default.yml`, `requirements.txt`
- `references/stockpile-adversaries/` — copied adversary profiles
- `references/stockpile-abilities-sample/` — sample ability YAML
- `references/sandcat-README.md`, `stockpile-README.md`
