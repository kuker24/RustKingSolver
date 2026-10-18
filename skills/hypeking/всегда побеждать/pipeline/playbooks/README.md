# Playbooks

Structured penetration testing playbooks with **compulsory tool enforcement**.
Each playbook defines a sequence of phases, each with specific objectives,
tools, and command variants. Agents MUST follow these exactly — every tool
in every phase is mandatory.

## Format

```yaml
---
name: Playbook Name
description: What this playbook covers
mode: agent|crew
max_phases: 5
mandatory_tools: [tool1, tool2, ...]
preflight_checks: [check1, check2, ...]
---

## Phase N: Phase Name

**Objective**: What this phase achieves

- Run `tool_command_variant` against target
- Parse output and store as output/path
```

## Pre-Flight Requirement

Before executing ANY playbook, the orchestrator MUST run:

```bash
bash db/doctor.sh --json          # Verify all required tools are present
bash db/doctor.sh --inventory     # Generate capability table for agents
```

If `doctor.sh` reports missing required tools, the phase MUST NOT proceed.
Document the gap and reduce scope accordingly.

## Tool Registry

Every tool with its command variants, output formats, and parse instructions
is documented in `docs/reference/TOOL_REGISTRY.md`. Agents MUST consult this
before executing any tool command.

## Mandatory Execution

- Every phase lists exact tool commands with flags — no vague descriptions
- Every tool must produce the specified output format
- If a tool fails, document the failure and try the fallback tool
- Aggregate all outputs through the surface-analyzer agent

## Playbooks

| Playbook | Target | Phases | Compulsory Tools |
|----------|--------|--------|-----------------|
| Reconnaissance | Any target | Passive Recon → Active Recon → Correlate | 20 tools (subfinder, amass, dnsx, httpx, nmap, masscan, katana, gau, waybackurls, whatweb, ffuf, gobuster, feroxbuster, dirsearch, arjun, paramspider, kiterunner, nuclei, nikto, etc.) |
| Web Application | Web apps | Discovery → Exploitation → Verification | 35+ tools (all recon + sqlmap, dalfox, commix, tplmap, jwt_tool, hydra, playwright, testssl.sh, nuclei) |
| Network Pentest | Network services | Enumeration → Exploitation → Post-Exploit | 25+ tools (nmap, masscan, hydra, john, hashcat, bloodhound, impacket, chisel, ligolo-ng, crackmapexec, kerbrute, certipy, linpeas, winpeas) |
