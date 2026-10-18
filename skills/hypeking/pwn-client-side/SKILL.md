---
name: pwn-client-side
description: "Client-side attacks: DOM clobbering, prototype pollution, postMessage abuse, WebRTC, WASM reverse engineering. 7 skills: browser-extension-hack, dom-clobbering, nodejs-sandbox-escape, postmessage-abuse, prototype-pollution-web, wasm-reverse-engineering, webrtc-hijack. Trigger words: browser extension hack, dom clobbering, nodejs sandbox escape, postmessage abuse, prototype pollution web, wasm reverse engineering."
---

# pwn-client-side — 04-client-side

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/04-client-side/`

## Routing table (7 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `browser-extension-hack` | `04-client-side/browser-extension-hack/scripts/agent.py` | run | browser-extension-hack/scripts/agent.py |
| `dom-clobbering` | `04-client-side/dom-clobbering/scripts/agent.py` | run | DOM Clobbering Scanner — id/name Collision & document.write Injection |
| `nodejs-sandbox-escape` | `04-client-side/nodejs-sandbox-escape/scripts/agent.py` | run | Node.js Sandbox Escape Scanner — eval Injection, VM Escape, child_process Abuse |
| `postmessage-abuse` | `04-client-side/postmessage-abuse/scripts/agent.py` | run | postMessage Listener Hijacking Scanner — Origin Validation Bypass Detection |
| `prototype-pollution-web` | `04-client-side/prototype-pollution-web/scripts/agent.py` | run | Prototype Pollution Scanner — Client-side & Server-side Detection |
| `wasm-reverse-engineering` | `04-client-side/wasm-reverse-engineering/scripts/agent.py` | run | WebAssembly Reverse Engineering Tool |
| `webrtc-hijack` | `04-client-side/webrtc-hijack/scripts/agent.py` | run | WebRTC Security Scanner |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
