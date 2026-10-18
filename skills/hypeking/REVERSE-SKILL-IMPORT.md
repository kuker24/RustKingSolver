# reverse-skill import provenance

Source: https://github.com/zhaoxuya520/reverse-skill (MIT) — harvested 2026-10-10.

Imported under `hypeking/reverse-skill/` (nested; omp still discovers only `hypeking`):
Gap-fill vs existing web/MITRE/WSTG suite — mobile/APK RE, native binary RE (IDA/Ghidra/r2/Binja),
JS crypto reverse, protocol/PCAP, firmware, forensics, binary pwn-chain, malware, CTF orchestrator,
Windows AD, thick-client, hardware.

Pruned 2026-10-18 (post-CTF review): `reverse-skill/burp-mcp/` — Burp MCP source pack,
never opened during the CTV campaign and redundant with the `ctf/web-ctf/` pack.

Skipped as OVERLAP with hypeking: api-security, cloud-k8s, llm-security, pentest-tools,
attack-chain, browser-automation, threat-intelligence, ot-ics, identity-federation (thin overlap
with auth/oauth + mitre), supply-chain (partial — not imported this pass).

MCP stubs (disabled) in `~/.omp/agent/mcp.json`: jshook, idapro, ghidra
(prior scopesentry/playwright stubs are orphaned — their playbooks were pruned 2026-10-18).
