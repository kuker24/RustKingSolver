---
name: operating-adaptix-c2
description: "Operate AdaptixC2 (Adaptix-Framework) for authorized post-exploitation: server/client install, listeners (HTTP/DNS/SMB/TCP + Gopher mTLS), Beacon/Gopher agents, AxScript, SOCKS, BOF, Extension-Kit. Trigger: adaptix, adaptixc2, adaptix framework, axscript, gopher agent, adaptix beacon."
---

# operating-adaptix-c2

**Upstream:** [Adaptix-Framework/AdaptixC2](https://github.com/Adaptix-Framework/AdaptixC2) (GPL-3.0) · docs: https://adaptix-framework.gitbook.io/adaptix-framework


**Tools:** tree staged at `~/tools/AdaptixC2` · `source skill://hypeking → …/scripts/c2-env.sh` · matrix `skill://hypeking/C2-TOOLS.md`
Helper: `scripts/agent.py --status|--clone|--compose-up`

Portable operator playbook — **do not** vendor the full Go/Qt tree into skills. Clone/build under `~/tools/AdaptixC2` when needed.

## ACTION REQUIRED

1. Confirm engagement scope + C2 redirector plan (`building-c2-redirector-infrastructure`).
2. Install deps → build/run server → GUI client → create listener → generate agent.
3. Prefer Docker (`references/docker-compose.yml`) for lab; bare-metal via `references/pre_install_linux_all.sh`.
4. Extension-Kit: https://github.com/Adaptix-Framework/Extension-Kit

## Features (operator surface)

| Area | Notes |
|---|---|
| Architecture | Server (Go) + multiplayer GUI client (Qt) |
| Listeners | HTTP/S Beacon, DNS/DoH, SMB, TCP Beacon; TCP/mTLS Gopher |
| Agents | Beacon (Win/Linux/macOS), Gopher |
| Ops | Remote shell, file/process browser, creds/targets managers |
| Pivot | SOCKS4/5(+auth), local/reverse portfwd, agent linking graph |
| Ext | AxScript engine, BOF / Async BOF, plugins (Extender) |
| Control | KillDate, WorkingTime, health checker |

## Lab install (Linux)

```bash
# deps (needs sudo) — see references/pre_install_linux_all.sh
git clone --depth 1 https://github.com/Adaptix-Framework/AdaptixC2.git ~/tools/AdaptixC2
cd ~/tools/AdaptixC2
# Docker lab:
docker compose up -d
# or follow gitbook Getting Started / Makefile targets
```

## Operator checklist

1. Stand up teamserver; note operator auth + listener bind (prefer redirector front).
2. Create listener matching egress (HTTPS preferred; DNS/SMB for constrained nets).
3. Generate Beacon/Gopher agent for target OS/arch; stage via approved channel.
4. On callback: health check → situational awareness → creds/files → pivot (SOCKS/portfwd).
5. AxScript / Extension-Kit for repeatable task packs; log tasks/jobs for debrief.
6. Enforce KillDate/WorkingTime before leaving implant resident.

## Complements

| Need | Pack |
|---|---|
| Sliver MCP / gRPC | `operating-sliver-c2` |
| Havoc | `operating-havoc-c2` / `building-red-team-c2-infrastructure-with-havoc` |
| Caldera ATT&CK ops | `operating-caldera-adversary-emulation` |
| Redirectors | `building-c2-redirector-infrastructure` |

## References

- `references/README.md` — upstream README
- `references/docker-compose.yml`
- `references/pre_install_linux_all.sh`
- Wiki: https://adaptix-framework.gitbook.io/adaptix-framework
