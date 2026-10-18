# C2 / red-team tool matrix

**PATH:** `source ~/.omp/agent/skills/hypeking/scripts/c2-env.sh`  
(also appended to `~/.bashrc` / `~/.zshrc`)

**Python helpers:** `~/tools/c2-venv` (`sliver-py`, `gophish`, `ldap3`, `impacket`, `requests`)  
Agents that need those libs use shebang `~/tools/c2-venv/bin/python3`.

## Availability

| Tool | Status | Path / note |
|---|---|---|
| Docker + Compose | **OK** | `docker` + `docker compose` (Debian `docker-compose` 2.26.1 plugin) |
| Sliver server/client | **OK** | `~/.local/bin/sliver-server`, `sliver` / `sliver-client` v1.7.7; ptr `~/tools/sliver/` |
| sliver-py | **OK** | `~/tools/c2-venv` — used by `operating-sliver-c2/scripts/agent.py` |
| AdaptixC2 tree | **OK** | `~/tools/AdaptixC2` (staged from harvest; compose + Makefile) |
| Caldera tree | **OK** | `~/tools/caldera` (+ stockpile/sandcat/atomic plugins populated) |
| GoPhish binary | **OK** | `/opt/gophish/gophish` + `/usr/local/bin/gophish` |
| gophish Py client | **OK** | c2-venv |
| Impacket + ldap3 | **OK** | c2-venv (+ pipx `impacket` has ldap3 injected) |
| git / make / gcc | **OK** | host |
| Go toolchain | **MISS** | needed only for bare-metal Adaptix/Havoc *build*; Docker path preferred |
| Havoc source/bin | **MISS** | clone when needed → `~/tools/Havoc`; agent wraps `./havoc` |
| Evilginx3 | **MISS** | install separately for AiTM pack |
| Caldera runtime venv | **optional** | `cd ~/tools/caldera && python3 -m venv .venv && pip i -r requirements.txt` or `docker compose up` |
| Sliver MCP | **gated** | stub `sliver` in `~/.omp/agent/mcp.json` (disabled); needs multiplayer cfg |

## Quick ops

```bash
source ~/.omp/agent/skills/hypeking/scripts/c2-env.sh

# Adaptix lab (Docker)
python3 ~/.omp/agent/skills/hypeking/всегда\ побеждать/12-red-team-web/operating-adaptix-c2/scripts/agent.py --status
# docker compose -f ~/tools/AdaptixC2/docker-compose.yml up -d

# Caldera REST (server already up)
python3 ~/.omp/agent/skills/hypeking/всегда\ побеждать/12-red-team-web/operating-caldera-adversary-emulation/scripts/agent.py \
  --password "$CALDERA_RED_PW" --list-adversaries

# Sliver operator (multiplayer cfg required)
~/.omp/agent/skills/hypeking/всегда\ побеждать/12-red-team-web/operating-sliver-c2/scripts/agent.py sessions -c ~/.sliver-client/configs/default.cfg
```

## Re-equip

```bash
# Python
python3 -m venv ~/tools/c2-venv && ~/tools/c2-venv/bin/pip install sliver-py gophish ldap3 requests impacket

# Platforms (if harvest gone)
git clone --depth 1 https://github.com/Adaptix-Framework/AdaptixC2.git ~/tools/AdaptixC2
git clone --depth 1 https://github.com/apache/caldera.git ~/tools/caldera
(cd ~/tools/caldera && git submodule update --init --recursive --depth 1)

# Sliver
curl https://sliver.sh/install | sudo bash   # or release bins → ~/.local/bin
ln -sfn ~/.local/bin/sliver ~/.local/bin/sliver-client
```
