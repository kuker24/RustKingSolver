# Tool Index

- Generated at: 2026-10-10 17:21:30 +0700
- Platform: linux (Linux 6.12.111+deb13-amd64)
- Script: `skills/scripts/refresh-tool-index.sh`
- Note: This script detects tools only. It does not install tools.

| Tool | Skill | Purpose | Available | Path | Version | Source | Install hint |
|---|---|---|---|---|---|---|---|
| java | core-runtime | Java runtime for jadx/apktool/Burp/Ghidra | yes | /usr/bin/java | openjdk version "21.0.12.1" 2026-08-18 | command | apt: sudo apt install openjdk-17-jdk |
| python3 | core-runtime | Python runtime for helper scripts and pipx tools | yes | /usr/bin/python3 | Python 3.13.5 | command | apt: sudo apt install python3 python3-venv python3-pip pipx |
| pipx | core-runtime | Isolated Python CLI installer | yes | /usr/bin/pipx | 1.7.1 | command | see PLATFORMS.md and docs/platforms/linux.md |
| node | core-runtime | Node.js runtime for MCP bridges | yes | /home/fahmi/.local/bin/node | v22.23.3 | command | apt/nvm: sudo apt install nodejs npm; prefer NodeSource or nvm for newer Node |
| npm | core-runtime | Node package manager | yes | /home/fahmi/.local/bin/npm | 10.9.9 | command | see PLATFORMS.md and docs/platforms/linux.md |
| npx | core-runtime | Run npm MCP packages | yes | /home/fahmi/.local/bin/npx | 10.9.9 | command | see PLATFORMS.md and docs/platforms/linux.md |
| jadx | apk-reverse | APK Java/Kotlin decompiler | yes | /home/fahmi/tools/jadx/bin/jadx | 1.5.6 | command | GitHub release: download jadx ZIP to ~/tools/jadx |
| apktool | apk-reverse | APK decode and rebuild | yes | /home/fahmi/tools/apktool/apktool | 3.0.2 | command | apt or jar: sudo apt install apktool; or official apktool.jar |
| adb | apk-reverse | Android device bridge | yes | /usr/bin/adb | Android Debug Bridge version 1.0.41 | command | apt or Android platform-tools: sudo apt install adb |
| frida | reverse-engineering | Dynamic instrumentation CLI | yes | /home/fahmi/.local/bin/frida | 17.23.3 | command | pipx: pipx install frida-tools |
| frida-ps | reverse-engineering | Frida process listing | yes | /home/fahmi/.local/bin/frida-ps | 17.23.3 | command | see PLATFORMS.md and docs/platforms/linux.md |
| r2 | radare2 | radare2 CLI analysis | yes | /usr/bin/r2 | radare2 6.2.2 +1 abi:142 @ linux-x86_64 | command | GitHub/source preferred; apt if available |
| rabin2 | radare2 | Binary metadata extraction | yes | /usr/bin/rabin2 | rabin2 6.2.2 +1 abi:142 @ linux-x86_64 | command | see PLATFORMS.md and docs/platforms/linux.md |
| ghidra | reverse-engineering | Ghidra reverse-engineering suite | yes | /usr/local/bin/ghidra | — | command | GitHub release ZIP or Flatpak; Java required |
| idapro | ida-reverse | IDA Pro commercial reverse-engineering suite | no | — | — | — | see PLATFORMS.md and docs/platforms/linux.md |
| burpsuite | burp-mcp | BurpSuite desktop application | no | — | — | — | manual installer/jar; then load burp-mcp-full jar |
| graphviz | diagram-generator | Graphviz diagram rendering | yes | /usr/bin/dot | dot - graphviz version 2.42.4 (0) | command | see PLATFORMS.md and docs/platforms/linux.md |
| plantuml | diagram-generator | PlantUML diagram rendering | no | — | — | — | see PLATFORMS.md and docs/platforms/linux.md |
| nmap | pentest-tools | Network scanner | yes | /usr/bin/nmap | Nmap version 7.95 ( https://nmap.org ) | command | see PLATFORMS.md and docs/platforms/linux.md |
| sqlmap | pentest-tools | SQL injection testing tool | yes | /home/fahmi/.local/bin/sqlmap | 1.10.9#pip | command | see PLATFORMS.md and docs/platforms/linux.md |
| ffuf | pentest-tools | Web fuzzer | yes | /usr/local/bin/ffuf | ffuf version: 2.1.0-dev | command | see PLATFORMS.md and docs/platforms/linux.md |
| hashcat | pentest-tools | Password recovery | yes | /usr/bin/hashcat | v6.2.6 | command | see PLATFORMS.md and docs/platforms/linux.md |
| nuclei | pentest-tools | Template-based vulnerability scanner | yes | /usr/local/bin/nuclei | [[34mINF[0m] Nuclei Engine Version: v3.11.1 | command | GitHub release or go install; apt may be unavailable |
| binwalk | firmware-pentest | Firmware extraction and analysis | yes | /usr/bin/binwalk | — | command | apt: sudo apt install binwalk |
| binaryninja | binary-ninja-reverse | Binary Ninja commercial reverse-engineering platform | no | — | — | — | see PLATFORMS.md and docs/platforms/linux.md |
| seclists | pentest-tools | Security wordlists | yes | /home/fahmi/tools/SecLists | — | path-probe | git clone https://github.com/danielmiessler/SecLists ~/tools/SecLists |
| jshookmcp | js-reverse | JS/CDP/Hook MCP capability (requires registration + npx runtime) | no | — | — | — | npx: npx -y @jshookmcp/jshook@0.3.4 |
| reqable-mcp | pentest-tools | Reqable MCP capability (requires registration + npx runtime) | no | — | — | — | npx: npx -y reqable-mcp-server@1.0.1; install Reqable desktop separately |
| xquik-mcp | threat-intelligence | Remote public X threat-intelligence MCP (requires registration + OAuth) | no | — | — | — | remote MCP: register https://xquik.com/mcp in the selected host, then complete OAuth |
| jeb-pro | apk-reverse | Commercial Android/ARM decompiler (manual licensed install) | no | — | — | — | manual licensed install: https://www.pnfsoftware.com/jeb/ |
| anything-analyzer | browser-automation | Browser/HTTP analyzer MCP project | no | — | — | — | git clone + pnpm install + pnpm dev |
| burp-mcp-full | burp-mcp | Local Burp MCP extension and stdio bridge | no | — | — | — | see PLATFORMS.md and docs/platforms/linux.md |
| yara | malware-analysis | Malware rule matching engine | yes | /usr/bin/yara | 4.5.2 | command | apt: sudo apt install yara |
| pwntools | reverse-engineering | CTF pwn exploit development framework | yes | /home/fahmi/.local/bin/pwn | [*] Pwntools v4.15.0 | command | pipx: pipx install pwntools |

---

## Next steps

- Read `docs/platforms/linux.md` for ordinary Linux setup.
- If the host is Kali, read `kali/README-kali.md` instead.
- Register MCP servers in your Agent client; tool availability does not imply MCP registration.

---

## 能力状态视图 (Capability Status)

| 能力 | 工具可用 | Ready | MCP 已注册 | 服务在线 | MCP HTTP | 可自动安装 | 安装方式 |
|------|---------|-------|-----------|---------|----------|-----------|---------|
| jadx | ✓ | ✓ | — | — | — | ✓ | github-release-zip |
| apktool | ✓ | ✓ | — | — | — | ✓ | github-release-jar-wrapper |
| jeb-pro | ✗ | ✗ | — | — | — | ✗ | manual |
| frida | ✓ | ✓ | — | — | — | ✓ | pip-package |
| frida-ps | ✓ | ✓ | — | — | — | ✓ | pip-package |
| idalib-mcp | ✗ | ✗ | — | — | — | ✓ | pip-package |
| binaryninja | ✗ | ✗ | — | — | — | ✗ | manual |
| reqable-mcp | ✗ | ✗ | — | — | — | ✓ | npm-mcp |
| jshookmcp | ✗ | ✗ | — | — | — | ✓ | npm-mcp |
| xquik-mcp | ✗ | ✗ | — | — | — | ✓ | remote-http-mcp |
| anything-analyzer | ✗ | ✗ | — | — | — | ✓ | local-http-mcp |
| idapro | ✗ | ✗ | — | — | — | ✓ | local-http-mcp |
| r2 | ✓ | ✓ | — | — | — | ✓ | github-release-zip |
| rabin2 | ✓ | ✓ | — | — | — | ✓ | github-release-zip |
| adb | ✓ | ✓ | — | — | — | ✓ | winget-package |
| agent-browser | ✗ | ✗ | — | — | — | ✓ | npm-global |
| ghidra-mcp | ✗ | ✗ | — | — | — | ✓ | github-release-zip |
| seclists | ✓ | ✓ | — | — | — | ✓ | git-clone |
| proxycat | ✗ | ✗ | — | — | — | ✓ | git-clone |
| burpsuite-mcp | ✗ | ✗ | — | — | — | ✗ | local-http-mcp |
| nmap | ✓ | ✓ | — | — | — | ✓ | winget-package |
| pentestswarm | ✗ | ✗ | — | — | — | ✓ | go-install |
| binwalk | ✓ | ✓ | — | — | — | ✗ | manual |
| yara | ✓ | ✓ | — | — | — | ✓ | winget-package |
| pwntools | ✓ | ✓ | — | — | — | ✓ | pip-package |
| bkcrack | ✗ | ✗ | — | — | — | ✓ | github-release-zip |

> ✓ = 是 | ✗ = 否 | — = 不适用或未检测。npm-mcp 的 Ready 使用 MCP 注册状态 + npx runtime；npx 本身不会让某个 MCP capability 变成工具可用。

