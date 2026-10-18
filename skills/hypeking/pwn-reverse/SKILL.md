---
name: pwn-reverse
description: "Reverse-engineering umbrella from reverse-skill: APK/mobile, JS crypto, IDA/Ghidra/r2/Binja, Go/Rust/.NET, protocol/PCAP, firmware, forensics, pwn-chain, malware, CTF, Windows AD, thick-client, hardware. Trigger: reverse, apk, jadx, frida, ida, ghidra, radare2, jshook, sourcemap, firmware, binwalk, pcap protocol, ctf, malware yara, mach-o, dnspy."
---

# pwn-reverse — reverse-skill gap pack

**Root:** `~/.omp/agent/skills/hypeking/reverse-skill/`

Net-new vs web/MITRE suite: native + mobile + JS crypto RE, CTF sidecar, firmware/forensics/protocol.

## Tools

Full matrix: `skill://hypeking/reverse-skill/TOOLS.md`

```bash
source '~/.omp/agent/skills/hypeking/reverse-skill/scripts/env.sh'
bash '~/.omp/agent/skills/hypeking/reverse-skill/scripts/bootstrap-reverse.sh' --list
bash '~/.omp/agent/skills/hypeking/reverse-skill/scripts/refresh-tool-index.sh'
```


## Auto-route

```bash
python3 '~/.omp/agent/skills/hypeking/scripts/route.py' --ask '<task>'
# or upstream ladder:
bash '~/.omp/agent/skills/hypeking/reverse-skill/scripts/master-route.sh' --hint '<task>'
```

PRIMARY ladder: `skill://hypeking/reverse-skill/MASTER-ROUTING.md`

## Packs (nested)

| Pack | Path | Keywords |
|---|---|---|
| apk-reverse | `reverse-skill/apk-reverse/` | apk, jadx, apktool, smali, frida |
| mobile-reverse | `reverse-skill/mobile-reverse/` | ipa, ios, objection, mobsf, ssl pinning |
| js-reverse | `reverse-skill/js-reverse/` | js reverse, jshook, 签名, 前端加密, sourcemap |
| reverse-engineering | `reverse-skill/reverse-engineering/` | ollvm, unpack, anti-debug, dsl vm |
| ida-reverse | `reverse-skill/ida-reverse/` | ida, ida mcp, decompile |
| ghidra-reverse | `reverse-skill/ghidra-reverse/` | ghidra, headless analyze |
| radare2 | `reverse-skill/radare2/` | radare2, r2, rizin |
| binary-ninja-reverse | `reverse-skill/binary-ninja-reverse/` | binary ninja, hlil, mlil |
| go-rust-reverse | `reverse-skill/go-rust-reverse/` | go binary, rust binary, pclntab |
| dotnet-reverse | `reverse-skill/dotnet-reverse/` | dnspy, de4dot, confuserex, clr |
| protocol-reverse | `reverse-skill/protocol-reverse/` | protobuf, grpc, custom protocol, pcap |
| firmware-pentest | `reverse-skill/firmware-pentest/` | firmware, binwalk, emba, iot |
| digital-forensics | `reverse-skill/digital-forensics/` | memory dump, timeline, volatility, ir |
| pwn-chain | `reverse-skill/pwn-chain/` | rop, heap, exploit chain binary |
| malware-analysis | `reverse-skill/malware-analysis/` | yara, sandbox, ioc malware |
| browser-extension-reverse | `reverse-skill/browser-extension-reverse/` | chrome extension, firefox addon |
| windows-ad | `reverse-skill/windows-ad/` | kerberos, adcs, bloodhound, ntlm relay |
| ctf-sandbox | `reverse-skill/ctf-sandbox/` → `CTF-Sandbox-Orchestrator/` | ctf, awd, 靶场 |
| thick-client | `reverse-skill/thick-client/` | thick client, desktop ipc |
| hardware-security | `reverse-skill/hardware-security/` | uart, jtag, secure boot |
| burp-mcp | `reverse-skill/burp-mcp/` | burp mcp extension sources |

## MCP (disabled stubs in `~/.omp/agent/mcp.json`)

| Server | Enable when |
|---|---|
| `jshook` | JS runtime hook / CDP |
| `idapro` | IDA + ida-pro-mcp listening |
| `ghidra` | GhidraMCP plugin up |
| `scopesentry` / `playwright` | prior ARTEX stubs |

Ref: `skill://hypeking/reverse-skill/mcp-kali-example.json`

## Complements (already in hypeking)

| Need | Pack |
|---|---|
| Web pipeline | `HackinMode` |
| SPA API harvest | `pwn-api-recon` |
| MITRE / WSTG | `pwn-mitre-*` / `pwn-wstg` |
| LLM redteam | `g0dm0d3` / `pwn-ai-llm` |

Provenance: [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill) MIT — `skill://hypeking/REVERSE-SKILL-IMPORT.md`
