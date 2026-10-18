---
name: skill-router
description: "Master skill router for the full omp pwn + CTF equip. Maps operator ask → exact omp skill:// pack + suite category under всегда побеждать. Trigger words: route, routing, which skill, skill router, dispatch, triage, full equip, what skill, categorize ask, pwn route, ctf route."
---

# skill-router — Full Equip Dispatcher

**MUST read this skill first** when the ask is ambiguous across packs, when operator says "route"/"full equip", or before launching a multi-category engagement.

Suite root: `~/.omp/agent/skills/hypeking/всегда побеждать/`  
Discovered omp packs: `skill://<name>` (one-level under `~/.omp/agent/skills/`)

## Dispatch algorithm

1. Match activation phrase / keyword table below (first exact hit wins).
2. If multiple categories score, emit ordered list (max 3) and load the top `skill://` pack.
3. Automation skill → `python3 '<suite>/<cat>/<skill>/scripts/agent.py' …`  
   Methodology skill → `read` the SKILL.md then execute manually.
4. CTF / lomba asks load `skill://hypeking/ctf`, then the category pack the ask names.
5. Never substitute a "safer" adjacent pack when the operator named a technique.

CLI helper:

```bash
python3 '~/.omp/agent/skills/hypeking/skill-router/scripts/route.py' --ask 'ssrf tunnel on target'
python3 '~/.omp/agent/skills/hypeking/skill-router/scripts/route.py' --ask 'ctf crypto ecdsa nonce' --json
```

## omp skill:// map

| omp skill | Suite category | When |
|---|---|---|
| `skill://hypeking/HackinMode` | (orchestrator) | full pipeline / "pwn" / autonomous web |
| `skill://hypeking/skill-router` | (this) | triage / ambiguous |
| `skill://hypeking/ctf` | `ctf` | CTF / lomba competition work |
| `skill://hypeking/ctf/*` | `ctf/<cat>` | category packs: crypto, reverse, forensics, osint, ics, web-ctf, infra |
| `skill://hypeking/pwn-recon` | `01-recon` | httpx, katana, fuzz, param-miner |
| `skill://hypeking/pwn-waf-bypass` | `02-waf-bypass` | cloudflare / akamai / aws waf |
| `skill://hypeking/pwn-exploit` | `03-exploit` | smuggling, cache, race, ssrf-tunnel, graphql, websocket |
| `skill://hypeking/pwn-client-side` | `04-client-side` | DOM, prototype pollution, postMessage, WASM |
| `skill://hypeking/pwn-auth-oauth` | `05-auth-oauth` | PKCE, consent phishing, token replay |
| `skill://hypeking/pwn-automation` | `06-automation` | nuclei, ffuf, dalfox, CI/CD, chaining |
| `skill://hypeking/pwn-web-security` | `07-web-security` | API security, BOLA/BFLA, injection arsenal |
| `skill://hypeking/pwn-cloud-web` | `08-cloud-web` | AWS/Azure/GCP/K8s audit |
| `skill://hypeking/pwn-ai-llm` | `09-ai-llm-web` | prompt injection, MCP poison, guardrails |
| `skill://hypeking/pwn-adv-recon` | `10-adv-recon` | OSINT, CT logs, darkweb, typosquat |
| `skill://hypeking/pwn-network-web` | `11-network-web` | pcap, zeek, scapy, firewall, IDS |
| `skill://hypeking/pwn-red-team` | `12-red-team-web` | C2, phishing, eBPF, adversary engagement |
| `skill://hypeking/pwn-log-siem` | `13-log-siem-web` | splunk, sigma, elastic, audit logs |
| `skill://hypeking/pwn-exploit-arsenal` | `14-exploit-arsenal` | broad exploit library (xss/sqli/jwt/…) |
| `skill://hypeking/pwn-threat-intel` | `15-threat-intel` | IOC, C2 detect, urlscan, covert channels |
| `skill://hypeking/pwn-wstg` | `16-wstg-methodology` | OWASP WSTG procedures |
| `skill://hypeking/pwn-attack-core` | `17-attack-core` | deep playbooks (SSRF/SSTI/JWT/CORS/XXE/…) |
| `skill://hypeking/pwn-post-exploit` | `18-post-exploit` | linux/win/macos/cloud/AD/kerberos |
| `skill://hypeking/pwn-mitre-ics` | `21-mitre-ics` | ATT&CK ICS TTPs |

## Keyword → route

| Keywords | Primary | Secondary |
|---|---|---|
| pwn, full scan, axiom, pipeline, aggressive | `HackinMode` | `pwn-recon` |
| route, which skill, triage, dispatch | `skill-router` | — |
| ctf, lomba, 靶场, awd, competition | `ctf` | `ctf/crypto` |
| recon, httpx, katana, fuzz, param miner, fingerprint | `pwn-recon` | `pwn-adv-recon` |
| waf, cloudflare, akamai, blocked by waf | `pwn-waf-bypass` | — |
| request smuggling, cache poison, race condition, ssrf tunnel, websocket hijack | `pwn-exploit` | `pwn-attack-core` |
| dom clobbering, prototype pollution, postmessage, wasm, webrtc | `pwn-client-side` | — |
| oauth, pkce, consent phishing, token replay | `pwn-auth-oauth` | `pwn-attack-core` |
| nuclei, ffuf, dalfox, burp, caido, cicd, exploit chain | `pwn-automation` | — |
| api security, bola, bfla, mass assignment, shadow api | `pwn-web-security` | `pwn-wstg` |
| aws, azure, gcp, kubernetes, s3, iam, rbac | `pwn-cloud-web` | `pwn-post-exploit` |
| llm, prompt injection, mcp, guardrail, garak, pyrit, rag | `pwn-ai-llm` | — |
| osint, shodan, crt.sh, darkweb, typosquat, threat actor | `pwn-adv-recon` | `pwn-threat-intel` |
| wireshark, zeek, scapy, netflow, snort, pfsense | `pwn-network-web` | — |
| c2, sliver, havoc, phishing, evilginx, ebpf, mitre engage | `pwn-red-team` | `pwn-mitre-ics` |
| splunk, sigma, elastic, sentinel, qradar, audit log | `pwn-log-siem` | — |
| xss, sqli, nosql, jwt confusion, csrf, deserialize, clickjack | `pwn-exploit-arsenal` | `pwn-attack-core` |
| ioc, urlscan, webshell, covert channel, opencti | `pwn-threat-intel` | — |
| wstg, owasp test, how do i test | `pwn-wstg` | — |
| ssti, xxe, cors deep dive, host header, idor playbook | `pwn-attack-core` | `pwn-exploit` |
| postexploit, privesc, persistence, kerberos, bloodhound | `pwn-post-exploit` | — |
| mitre, att&ck, T1xxx, TA000, ICS TTPs | `pwn-mitre-ics` | — |

## Pipeline phase → categories

When running `pipeline/axiom-web-pwn.py`:

| Phase | Categories |
|---|---|
| 1 RECON | `01-recon`, `10-adv-recon` |
| 2 DETECT | `03-exploit`, `07-web-security`, `14-exploit-arsenal` |
| 3 WAF | `02-waf-bypass` |
| 4 EXPLOIT | all exploit cats + open leads |
| 5 CHAIN | `06-automation/exploit-chain-automation` |
| 6 PIVOT | `03-exploit/ssrf-tunnel`, `08-cloud-web` |
| 7 REPORT | `pipeline/modules/reporter.py` |

Tech keywords (JIT): see `pipeline/modules/router.py` (`TECH_KEYWORDS`, `SERVICE_DOMAIN_MAP`).

## Full equip checklist

On "max" / "full equip" / first engagement in a fresh session:

1. `read skill://hypeking/skill-router` (this)
2. `read skill://hypeking/HackinMode` if web-target engagement
3. `read skill://hypeking/ctf` if the engagement is a CTF / lomba
4. Load the specific `skill://pwn-*` from the table
5. Confirm suite path exists: `~/.omp/agent/skills/hypeking/всегда побеждать/<cat>/`

## Output contract

When routing, reply with:

```
ROUTE: skill://<name>
SUITE: <category>[/<skill>]
MODE: run|read
NEXT: <exact command or read path>
```

No menus of safer alternatives. One primary route. Optional ranked alternates only when scores tie.
