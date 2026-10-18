---
name: pwn-attack-core
description: "Deep-dive attack playbooks: SSRF, SSTI, JWT, CORS, GraphQL, XXE, cache poisoning, request smuggling, prototype pollution, race conditions. 16 skills: attack-cache-poison, attack-cors, attack-graphql, attack-host-header, attack-idor-automation, attack-jwt, attack-open-redirect, attack-prototype-pollution. Trigger words: attack cache poison, attack cors, attack graphql, attack host header, attack idor automation, attack jwt."
---

# pwn-attack-core — 17-attack-core

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/17-attack-core/`

## Routing table (16 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `attack-cache-poison` | `17-attack-core/attack-cache-poison/SKILL.md` | read | Web cache poisoning — unkeyed header/parameter injection to serve malicious content to all users |
| `attack-cors` | `17-attack-core/attack-cors/SKILL.md` | read | CORS misconfiguration testing — origin reflection, wildcard bypass, null origin, credential leakage |
| `attack-graphql` | `17-attack-core/attack-graphql/SKILL.md` | read | GraphQL vulnerability testing — introspection exposure, complexity DoS, batch abuse, mutation auth bypass |
| `attack-host-header` | `17-attack-core/attack-host-header/SKILL.md` | read | Host header injection — password reset poisoning, cache poisoning, routing bypass, SSRF via Host |
| `attack-idor-automation` | `17-attack-core/attack-idor-automation/SKILL.md` | read | IDOR automated testing — cross-account access, horizontal/vertical privilege escalation, mass data exposure |
| `attack-jwt` | `17-attack-core/attack-jwt/SKILL.md` | read | JWT token attacks — alg:none bypass, key confusion, claim tampering, signature stripping |
| `attack-open-redirect` | `17-attack-core/attack-open-redirect/SKILL.md` | read | Open redirect exploitation — URL parameter manipulation, OAuth token theft, phishing chains |
| `attack-prototype-pollution` | `17-attack-core/attack-prototype-pollution/SKILL.md` | read | JavaScript prototype pollution — __proto__ injection, constructor.prototype, gadget chain exploitation |
| `attack-race-condition` | `17-attack-core/attack-race-condition/SKILL.md` | read | Race condition / TOCTOU testing — concurrent requests to exploit time-of-check-to-time-of-use flaws |
| `attack-rate-limit-bypass` | `17-attack-core/attack-rate-limit-bypass/SKILL.md` | read | Rate limit bypass testing — XFF rotation, case variation, method switching, header manipulation |
| `attack-request-smuggling` | `17-attack-core/attack-request-smuggling/SKILL.md` | read | HTTP request smuggling — CL.TE, TE.CL, TE.TE desync attacks for cache poisoning and auth bypass |
| `attack-ssrf` | `17-attack-core/attack-ssrf/SKILL.md` | read | Server-Side Request Forgery — internal network access, cloud metadata theft, filter bypass techniques |
| `attack-ssti` | `17-attack-core/attack-ssti/SKILL.md` | read | Server-Side Template Injection — detection, engine fingerprinting, and exploitation across 7 template engines |
| `attack-subdomain-takeover` | `17-attack-core/attack-subdomain-takeover/SKILL.md` | read | Subdomain takeover — CNAME detection, cloud service fingerprinting, dangling DNS exploitation |
| `attack-websocket` | `17-attack-core/attack-websocket/SKILL.md` | read | WebSocket security testing — CSWSH, message injection, auth bypass, origin validation |
| `attack-xxe` | `17-attack-core/attack-xxe/SKILL.md` | read | XML External Entity injection — file read, SSRF, data exfiltration via out-of-band XML parsing |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
