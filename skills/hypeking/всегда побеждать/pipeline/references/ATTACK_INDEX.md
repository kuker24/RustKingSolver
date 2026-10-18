# Attack Categories Index

63 attack categories across 11 domains (original index).

> The live engine reference data is loaded from SQLite via `db/seed.py` and is a
> superset of this index: **69 attack categories across 16 domains**, 75 tools,
> 39 checklists. Verify with: `python3 db/seed.py --force --db $PENTEST_DB`.

## Injection (9 types)
- SQL Injection | NoSQL Injection | Command Injection
- SSTI | XXE | LDAP/XPath Injection
- File Inclusion (LFI/RFI) | SAML Injection | Type Juggling
**Agent**: `injection-tester` (SQLi, NoSQLi, CMDi); `pentester-executor` (SSTI, XXE, LDAP, LFI, SAML, type juggling)

## Client-Side (6 types)
- XSS (Reflected/Stored/DOM) | CSRF | Clickjacking
- CORS Misconfiguration | Prototype Pollution | DOM-based Attacks
**Agent**: `xss-tester`, `csrf-tester`; `pentester-executor` (clickjacking, CORS, CSP bypass, prototype pollution)

## Server-Side (6 types)
- SSRF | HTTP Smuggling | Path Traversal
- File Upload | Deserialization | Host Header Injection
**Agent**: `pentester-executor`

## Authentication (4 types)
- Auth Bypass | JWT Attacks | OAuth Misconfiguration | Password Attacks
**Agent**: `password-attack-agent` (password attacks); `pentester-executor` (auth bypass, JWT, OAuth)

## API Security (4 types)
- GraphQL | REST API | WebSockets | Web LLM / Prompt Injection
**Agent**: `pentester-executor`

## Web Applications (9 types)
- Business Logic | Race Conditions | Access Control
- Cache Poisoning | Cache Deception | Info Disclosure
- Mass Assignment | OAuth Misconfiguration | Open Redirect
**Agent**: `pentester-executor`

## Cloud & Containers (5 types)
- AWS | Azure | GCP | Docker | Kubernetes
**Agent**: `cloud-security-agent`

## System / Post-Exploitation (8 types)
- Active Directory | Privilege Escalation | Exploit Development
- Hash Cracking | Persistence | Network Pivoting | Evasion | Reverse Shells
**Agent**: `post-exploitation-agent` (PrivEsc, lateral, pivot); `password-attack-agent` (hash cracking); `network-pentest-agent` (AD)

## IP Infrastructure (8 types)
- Port Scanning | DNS Attacks | SMB/NetBIOS | MITM
- Sniffing | IPv6 Attacks | VLAN Hopping | DoS/DDoS
**Agent**: `network-pentest-agent` (port scan, SMB, DNS); `recon-agent` (port scanning)

## Physical & Social (1 type)
- Social Engineering (phishing, vishing, BEC, USB baiting)
**Agent**: Requires explicit written authorization

## Essential Skills (3 types)
- Burp Suite | Methodology (PTES, OWASP WSTG) | Reporting
**Agent**: Human-performed; `report-generator` agent assists

## Domain → Agent Routing

| Target Type | Skill Coordinator | Notes |
|-------------|------------------|-------|
| Web application | web-application-mapping → common-appsec-patterns | Full inventory before testing |
| API | cve-testing + domain-assessment | No browser surface |
| Cloud | pentester-executor → cloud-attacks | — |
| Network | pentester-executor → ip-infrastructure | — |
| Full scope | All coordinators | Confirm authorization |
