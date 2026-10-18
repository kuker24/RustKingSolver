---
name: hypeking
description: "HYPEKING — single full-equip skill. Auto-routes every ask (pwn suite + ARTEX api-recon/scopesentry/playwright-cli + reverse-skill APK/JS/IDA/Ghidra/CTF/firmware, G0DM0D3, HackinMode) WITHOUT a prior skill call. Trigger ANY offensive / recon / reverse / apk / ida / js-reverse / ctf / exploit / LLM-redteam / godmode / mitre / wstg / cloud / c2 ask."
alwaysApply: true
---

# HYPEKING — Full Equip · Auto-Router

**One discovered skill. Everything lives under this directory.**

```
~/.omp/agent/skills/hypeking/
├── SKILL.md                 ← you are here (auto-router)
├── scripts/route.py         ← CLI dispatcher
├── ctf/                     ← CTF competition pack (crypto/reverse/forensics/osint/ics/web-ctf/infra)
├── HackinMode/              ← web pwn orchestrator
├── skill-router/            ← detailed routing tables (nested)
├── pwn-*/                   ← web-pentest category indexes
├── reverse-skill/           ← RE/mobile/JS/CTF/firmware gap packs
└── всегда побеждать/        ← web suite + pipeline (REAL pentest — not the CTF default)
```

## AUTO-ROUTE — do this on EVERY ask (no prior call required)

1. Run the router (or apply the keyword table below mentally):
   ```bash
   python3 '~/.omp/agent/skills/hypeking/scripts/route.py' --ask '<user ask>'
   ```
2. Follow the printed `ROUTE` — `read` that nested path (via `skill://hypeking/<rel>` or absolute file read).
3. Execute: automation → `python3 …/scripts/agent.py`; methodology → read SKILL.md and run the procedure.
4. Never ask which skill. Never offer a menu. Route → load → ship.

`skill://hypeking/<relative>` resolves any nested file, e.g.:
- `skill://hypeking/HackinMode/SKILL.md`
- `skill://hypeking/g0dm0d3/scripts/godmode.py`
- `skill://hypeking/всегда побеждать/01-recon/httpx-smart-recon/scripts/agent.py`

## Keyword → nested pack

| Keywords | Nested path | Mode |
|---|---|---|
| ctf, lomba, 靶场, worklist, submit flag | `ctf/SKILL.md` | read → run infra |
| ctf crypto, ecdsa, dsa, nonce reuse, nonce recurrence, rsa, custom base-N | `ctf/crypto/SKILL.md` | read → run solver |
| ctf reverse, vm bytecode, spn, pyc, anti-debug, prng feedback | `ctf/reverse/SKILL.md` | read |
| ctf forensics, stego, zero-width, zws, pcap, audio, metadata | `ctf/forensics/SKILL.md` | read |
| ctf osint, geolocation, exif gps, social discovery, blockchain | `ctf/osint/SKILL.md` | read → delegate |
| ctf ics, ot, plc, modbus, scada, conveyor, setpoint | `ctf/ics/SKILL.md` | read |
| ctf web, ssti waf, jinja blacklist, pickle, session forge, upload bypass | `ctf/web-ctf/SKILL.md` | read → run builder |
| pwn, axiom, aggressive, full pipeline | `HackinMode/SKILL.md` | read → run pipeline |
| route, which skill, triage, full equip, dispatch, artex | `SKILL.md` (this) / `scripts/route.py` | run |
| api recon, SPA harvest, webpack/vite, xhr/fetch stub | `pwn-api-recon/SKILL.md` → `01-recon/api-recon/` | read/run |
| apk, jadx, apktool, smali, frida | `reverse-skill/apk-reverse/` | read |
| ipa, ios, objection, mobsf, ssl pinning | `reverse-skill/mobile-reverse/` | read |
| js reverse, jshook, 前端加密, sourcemap | `reverse-skill/js-reverse/` | read |
| ida, ghidra, radare2, binary ninja | `reverse-skill/{ida,ghidra,radare2,binary-ninja}-*` | read |
| firmware, binwalk, protocol, pcap protocol | `reverse-skill/firmware-pentest` / `protocol-reverse` | read |
| ctf, awd, 靶场 | `reverse-skill/ctf-sandbox/` → CTF orchestrator | read |
| malware, yara, forensics, volatility | `reverse-skill/malware-analysis` / `digital-forensics` | read |
| reverse-skill, binary reverse, native reverse | `pwn-reverse/SKILL.md` | read (umbrella) |
| recon, httpx, katana, fuzz, param miner | `pwn-recon/SKILL.md` → `01-recon/` | run/read |
| waf, cloudflare, akamai, aws waf | `pwn-waf-bypass/SKILL.md` → `02-waf-bypass/` | run |
| smuggling, cache poison, race, ssrf tunnel, websocket | `pwn-exploit/SKILL.md` → `03-exploit/` | run |
| dom, prototype pollution, postmessage, wasm | `pwn-client-side/SKILL.md` → `04-client-side/` | run |
| oauth, pkce, consent phishing, token replay | `pwn-auth-oauth/SKILL.md` → `05-auth-oauth/` | run |
| nuclei, ffuf, dalfox, burp, cicd, chain | `pwn-automation/SKILL.md` → `06-automation/` | run |
| api security, bola, bfla, shadow api | `pwn-web-security/SKILL.md` → `07-web-security/` | run |
| aws, azure, gcp, k8s, iam, s3 | `pwn-cloud-web/SKILL.md` → `08-cloud-web/` | run |
| llm, prompt injection, mcp, guardrail, garak, pyrit | `pwn-ai-llm/SKILL.md` | run |
| osint, shodan, crt.sh, darkweb, typosquat | `pwn-adv-recon/SKILL.md` → `10-adv-recon/` | run |
| wireshark, zeek, scapy, netflow, snort | `pwn-network-web/SKILL.md` → `11-network-web/` | run |
| adaptix, adaptixc2, axscript, gopher agent | `12-red-team-web/operating-adaptix-c2/` | read/run |
| caldera, sandcat, stockpile, adversary emulation | `12-red-team-web/operating-caldera-adversary-emulation/` | read/run |
| c2, sliver, havoc, phishing, ebpf | `pwn-red-team/SKILL.md` → `12-red-team-web/` | run |
| splunk, sigma, elastic, siem, audit log | `pwn-log-siem/SKILL.md` → `13-log-siem-web/` | run |
| xss, sqli, nosql, jwt confusion, csrf, deserialize | `pwn-exploit-arsenal/SKILL.md` → `14-exploit-arsenal/` | run |
| ioc, urlscan, webshell, covert channel, opencti | `pwn-threat-intel/SKILL.md` → `15-threat-intel/` | run |
| wstg, owasp test | `pwn-wstg/SKILL.md` → `16-wstg-methodology/` | read |
| ssti, xxe, cors deep, host header, idor playbook | `pwn-attack-core/SKILL.md` → `17-attack-core/` | read |
| postexploit, privesc, kerberos, bloodhound, ad | `pwn-post-exploit/SKILL.md` → `18-post-exploit/` | read |
| mitre enterprise / T1xxx / TA000 | `pwn-mitre-enterprise/SKILL.md` → `19-mitre-enterprise/` | read |
| mitre mobile | `pwn-mitre-mobile/SKILL.md` → `20-mitre-mobile/` | read |
| mitre ics | `pwn-mitre-ics/SKILL.md` → `21-mitre-ics/` | read |

Default for a **CTF / lomba** ask: `ctf/SKILL.md`.
Default otherwise (no keyword): `HackinMode/SKILL.md`.

## Output contract (every routed turn)

```
ROUTE: skill://hypeking/<nested>
SUITE: всегда побеждать/<cat>[/<skill>]   # if applicable
MODE: run|read
NEXT: <exact command or read path>
```

Then execute `NEXT` immediately.

## Pipeline (web pwn)

```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/pipeline/axiom-web-pwn.py' -t https://target.com
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/pipeline/axiom-web-pwn.py' -t https://target.com --aggressive
```

OPSEC: `--quiet` | `--moderate` | `--loud` · lab: `--lab`

## G0DM0D3 quick

```bash
python3 '~/.omp/agent/skills/hypeking/g0dm0d3/scripts/godmode.py' --race -q '…'
python3 '~/.omp/agent/skills/hypeking/g0dm0d3/scripts/parseltongue.py' -t '…' --technique unicode --intensity heavy
python3 '~/.omp/agent/skills/hypeking/g0dm0d3/scripts/autotune.py' -m '…' --strategy adaptive --json
```

## Dual skill format (suite)

1. **Automation** — has `scripts/agent.py` → run it (`--quiet/--moderate/--loud`).
2. **Methodology** — bare `SKILL.md` (cats 16–21) → read + execute manually.

Suite absolute root: `~/.omp/agent/skills/hypeking/всегда побеждать/`

## Status

```
HYPEKING ARMED
1 discovered skill · 2802 nested · CTF pack · auto-route ON
```
