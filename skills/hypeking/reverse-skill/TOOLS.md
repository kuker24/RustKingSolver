# reverse-skill — tool equip matrix

**Tools root:** `~/tools` (`REVERSE_SKILL_TOOLS_DIR`)  
**PATH helper:** `source ~/.omp/agent/skills/hypeking/reverse-skill/scripts/env.sh`  
**Bootstrap:** `bash ~/.omp/agent/skills/hypeking/reverse-skill/scripts/bootstrap-reverse.sh <caps…> --mcp-host=none`  
**Index refresh:** `bash …/scripts/refresh-tool-index.sh` → `tool-index.md` / `tool-index.json`

## Status legend

| mark | meaning |
|---|---|
| ✅ | installed & on PATH (this host) |
| 📦 | apt / pipx / github release — re-run bootstrap if missing |
| 🔐 | commercial / manual license |
| 🔌 | MCP stub in `~/.omp/agent/mcp.json` (disabled until service live) |

## Pack → tools

| Pack | Required CLIs | Status | Install |
|---|---|---|---|
| **apk-reverse** | `jadx` `apktool` `frida*` `adb` `java` | ✅ | bootstrap `jadx apktool frida` + apt `adb` |
| **mobile-reverse** | above + `objection` | ✅ | `pipx install objection` |
| **js-reverse** | Node/`npx`, optional jshook MCP | ✅/🔌 | `npx -y @jshookmcp/jshook@0.3.4` |
| **ida-reverse** | IDA Pro + `ida-pro-mcp` | 🔐/🔌 | license + `pipx install ida-pro-mcp` → port 13337 |
| **ghidra-reverse** | Ghidra `analyzeHeadless` + GhidraMCP | 📦/🔌 | bootstrap `ghidra-mcp`; plugin → `:8765` |
| **radare2** | `r2` `rabin2` `rasm2` | ✅ | apt `radare2` |
| **binary-ninja-reverse** | Binary Ninja | 🔐 | Vector 35 license |
| **ghidra-reverse** | Ghidra `analyzeHeadless` + GhidraMCP | ✅/🔌 | `/opt/ghidra` + `/usr/local/bin/ghidra`; MCP plugin → `:8765` |
| **dotnet-reverse** | `ilspycmd` / dnSpyEx (wine) | 📦 optional | `dotnet tool install -g ilspycmd` |
| **protocol-reverse** | `tshark` `protoc` `scapy` | ✅ | apt `tshark` `protobuf-compiler` |
| **firmware-pentest** | `binwalk` `foremost` `qemu-user-static` | ✅ | apt |
| **digital-forensics** | `vol`/`volshell` `exiftool` `foremost` | ✅ | `~/tools/re-venv` + apt |
| **pwn-chain** | `pwntools`/`pwn` `checksec` `ropper` `gdb` | ✅ | pipx + apt + re-venv |
| **malware-analysis** | `yara` `r2` `pefile`/`lief` | ✅ | apt + re-venv |
| **browser-extension-reverse** | Node + unzip/`jq` | ✅ | system |
| **windows-ad** | Impacket / BloodHound (optional) | 📦 | `pipx install impacket` when needed |
| **ctf-sandbox** | union of above + CTF orchestrator | ✅ base | per-challenge bootstrap |
| **thick-client** | `jadx`/`dnSpy`/`r2` + proxy | ✅ base | — |
| **hardware-security** | UART/JTAG hardware (lab) | 🔐 lab | physical tooling |
| **burp-mcp** | Burp + `burp-mcp-full` jar | 🔐/🔌 | build jar → Burp Extensions → `:9876` |
| **reverse-engineering** | gdb / frida / angr (optional) | ✅ base | angr: heavy; install on demand in re-venv |

## Host inventory (post-equip)

| Tool | Path / note |
|---|---|
| jadx | `~/tools/jadx/bin/jadx` **1.5.6** |
| apktool | `~/tools/apktool/apktool` **3.0.2** (apt also 2.7.0) |
| frida / frida-ps / frida-trace | `~/.local/bin` via pipx **frida-tools 14.10.4** (runtime may report newer) |
| objection | `~/.local/bin/objection` **1.12.5** |
| adb | `/usr/bin/adb` |
| r2 / radare2 | `/usr/bin/r2` **6.2.2** |
| binwalk | `/usr/bin/binwalk` **2.4.3** |
| foremost | `/usr/bin/foremost` |
| yara | `/usr/bin/yara` **4.5.2** |
| nmap | `/usr/bin/nmap` |
| checksec | pipx pwntools / apt |
| pwn / pwntools | `~/.local/bin/pwn` **4.15.0** |
| protoc | `/usr/bin/protoc` **3.21.12** |
| tshark | `/usr/bin/tshark` |
| qemu-user-static | `/usr/bin/qemu-*-static` |
| gdb | `/usr/bin/gdb` |
| exiftool | `/usr/bin/exiftool` |
| ropper / vol / androguard | `~/tools/re-venv/bin` (+ `~/.local/bin` links) |
| java | OpenJDK 21 |
| node / npm / npx | `~/.local/bin` |
| SecLists | `~/tools/SecLists` ✅ |
| Ghidra | `/usr/local/bin/ghidra` → `/opt/ghidra` ✅ |
| scapy / impacket | re-venv + pipx ✅ |

## MCP (`~/.omp/agent/mcp.json`) — all disabled until live

| Server | When to enable |
|---|---|
| `jshook` | JS reverse runtime hook |
| `idapro` | IDA + ida-pro-mcp on `127.0.0.1:13337` |
| `ghidra` | GhidraMCP on `:8765` |
| `scopesentry` / `playwright` | prior ARTEX stubs |

Enable: set URL/key → remove from `disabledServers` → `/mcp reload`.

## Gated / not auto-installed

| Capability | Why |
|---|---|
| IDA Pro / JEB / Binary Ninja | commercial license |
| Burp Suite + burp-mcp jar | commercial + local build |
| GhidraMCP plugin | download zip → Ghidra Install Extensions |
| angr | heavy optional; `~/tools/re-venv/bin/pip install angr` on demand |
| Android build-tools (`zipalign`/`apksigner`) | SDK; apk rebuild needs sdkmanager |
| frida-server on device | push matching arch binary to rooted/jailbroken target |

## Re-equip one-liner

```bash
source ~/.omp/agent/skills/hypeking/reverse-skill/scripts/env.sh
bash ~/.omp/agent/skills/hypeking/reverse-skill/scripts/bootstrap-reverse.sh \
  jadx apktool frida pwntools seclists ghidra-mcp binwalk yara r2 nmap \
  --mcp-host=none
bash ~/.omp/agent/skills/hypeking/reverse-skill/scripts/refresh-tool-index.sh
```
