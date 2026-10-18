---
name: pwn-web-security
description: "API and web security testing: broken access control, mass assignment, injection, JWT testing. 45 skills: auditing-foundry-smart-contract-security, bypassing-authentication-with-forced-browsing, conducting-api-security-testing, detecting-api-enumeration-attacks, detecting-broken-object-property-level-authorization, detecting-shadow-api-endpoints, detecting-sql-injection-via-waf-logs, exploiting-api-injection-vulnerabilities. Trigger words: auditing foundry smart contract security, bypassing authentication with forced browsing, conducting api security testing, detecting api enumeration attacks, detecting broken object property level authorization, detecting shadow api endpoints."
---

# pwn-web-security — 07-web-security

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/07-web-security/`

## Routing table (45 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `auditing-foundry-smart-contract-security` | `07-web-security/auditing-foundry-smart-contract-security/scripts/agent.py` | run | Foundry Smart Contract Security Agent. |
| `bypassing-authentication-with-forced-browsing` | `07-web-security/bypassing-authentication-with-forced-browsing/scripts/agent.py` | run | Forced Browsing Authentication Bypass Agent - Tests for unprotected endpoints. |
| `conducting-api-security-testing` | `07-web-security/conducting-api-security-testing/scripts/agent.py` | run | API Security Testing Agent - Tests REST/GraphQL APIs for OWASP API Top 10 vulnerabilities. |
| `detecting-api-enumeration-attacks` | `07-web-security/detecting-api-enumeration-attacks/scripts/agent.py` | run | API enumeration attack detection agent. |
| `detecting-broken-object-property-level-authorization` | `07-web-security/detecting-broken-object-property-level-authorization/scripts/agent.py` | run | BOPLA vulnerability scanner for OWASP API3:2023 Broken Object Property Level Authorization. |
| `detecting-shadow-api-endpoints` | `07-web-security/detecting-shadow-api-endpoints/scripts/agent.py` | run | Agent for discovering undocumented (shadow) API endpoints via traffic analysis. |
| `detecting-sql-injection-via-waf-logs` | `07-web-security/detecting-sql-injection-via-waf-logs/scripts/agent.py` | run | SQL Injection WAF Log Analysis Agent - Detects SQLi attacks from ModSecurity and WAF logs. |
| `exploiting-api-injection-vulnerabilities` | `07-web-security/exploiting-api-injection-vulnerabilities/scripts/agent.py` | run | Agent for testing API injection vulnerabilities (SQL, NoSQL, command injection). |
| `exploiting-broken-function-level-authorization` | `07-web-security/exploiting-broken-function-level-authorization/scripts/agent.py` | run | Agent for testing Broken Function Level Authorization (BFLA) in APIs. |
| `exploiting-excessive-data-exposure-in-api` | `07-web-security/exploiting-excessive-data-exposure-in-api/scripts/agent.py` | run | Agent for detecting excessive data exposure (OWASP API3) in API responses. |
| `exploiting-http-request-smuggling` | `07-web-security/exploiting-http-request-smuggling/scripts/agent.py` | run | HTTP request smuggling detection agent using raw socket and requests. |
| `exploiting-idor-vulnerabilities` | `07-web-security/exploiting-idor-vulnerabilities/scripts/agent.py` | run | IDOR vulnerability detection agent using requests with multi-session comparison. |
| `exploiting-insecure-deserialization` | `07-web-security/exploiting-insecure-deserialization/scripts/agent.py` | run | Insecure deserialization detection agent for identifying serialized data in HTTP traffic. |
| `exploiting-mass-assignment-in-rest-apis` | `07-web-security/exploiting-mass-assignment-in-rest-apis/scripts/agent.py` | run | Agent for detecting mass assignment vulnerabilities in REST APIs. |
| `exploiting-oauth-misconfiguration` | `07-web-security/exploiting-oauth-misconfiguration/scripts/agent.py` | run | OAuth 2.0 misconfiguration detection agent for testing redirect URI, state, and PKCE. |
| `exploiting-prototype-pollution-in-javascript` | `07-web-security/exploiting-prototype-pollution-in-javascript/scripts/agent.py` | run | Agent for detecting prototype pollution vulnerabilities in JavaScript applications. |
| `exploiting-server-side-request-forgery` | `07-web-security/exploiting-server-side-request-forgery/scripts/agent.py` | run | SSRF vulnerability detection agent with cloud metadata and filter bypass testing. |
| `exploiting-sql-injection-vulnerabilities` | `07-web-security/exploiting-sql-injection-vulnerabilities/scripts/agent.py` | run | SQL injection detection agent using requests for manual technique-based testing. |
| `exploiting-sql-injection-with-sqlmap` | `07-web-security/exploiting-sql-injection-with-sqlmap/scripts/agent.py` | run | sqlmap automation agent for orchestrating SQL injection scans via subprocess. |
| `exploiting-template-injection-vulnerabilities` | `07-web-security/exploiting-template-injection-vulnerabilities/scripts/agent.py` | run | Server-Side Template Injection (SSTI) detection agent using requests. |
| `exploiting-websocket-vulnerabilities` | `07-web-security/exploiting-websocket-vulnerabilities/scripts/agent.py` | run | WebSocket vulnerability assessment agent using websockets and requests. |
| `implementing-api-gateway-security-controls` | `07-web-security/implementing-api-gateway-security-controls/scripts/agent.py` | run | Agent for auditing API gateway security controls (Kong, AWS API Gateway). |
| `implementing-api-key-security-controls` | `07-web-security/implementing-api-key-security-controls/scripts/agent.py` | run | Agent for implementing and auditing API key security controls. |
| `implementing-api-rate-limiting-and-throttling` | `07-web-security/implementing-api-rate-limiting-and-throttling/scripts/agent.py` | run | Agent for implementing and testing API rate limiting and throttling. |
| `implementing-api-schema-validation-security` | `07-web-security/implementing-api-schema-validation-security/scripts/agent.py` | run | Agent for auditing API schema validation security using OpenAPI specs. |
| `implementing-api-security-posture-management` | `07-web-security/implementing-api-security-posture-management/scripts/agent.py` | run | Agent for API Security Posture Management - discovery, classification, and risk scoring. |
| `implementing-api-security-testing-with-42crunch` | `07-web-security/implementing-api-security-testing-with-42crunch/scripts/agent.py` | run | Agent for API security testing using 42Crunch audit methodology. |
| `implementing-api-threat-protection-with-apigee` | `07-web-security/implementing-api-threat-protection-with-apigee/scripts/agent.py` | run | Agent for implementing API threat protection policies with Google Apigee. |
| `implementing-cloud-waf-rules` | `07-web-security/implementing-cloud-waf-rules/scripts/agent.py` | run | Cloud WAF rules management agent using AWS WAFv2 boto3 client. |
| `integrating-dast-with-owasp-zap-in-pipeline` | `07-web-security/integrating-dast-with-owasp-zap-in-pipeline/scripts/agent.py` | run | Agent for running OWASP ZAP DAST scans and parsing results for CI/CD integration. |
| `performing-api-fuzzing-with-restler` | `07-web-security/performing-api-fuzzing-with-restler/scripts/agent.py` | run | RESTler API fuzzing orchestration and result analysis agent. |
| `performing-api-inventory-and-discovery` | `07-web-security/performing-api-inventory-and-discovery/scripts/agent.py` | run | API inventory and discovery agent for attack surface mapping. |
| `performing-api-rate-limiting-bypass` | `07-web-security/performing-api-rate-limiting-bypass/scripts/agent.py` | run | API rate limiting bypass testing agent. |
| `performing-api-security-testing-with-postman` | `07-web-security/performing-api-security-testing-with-postman/scripts/agent.py` | run | Postman API security testing orchestration agent using Newman CLI. |
| `performing-content-security-policy-bypass` | `07-web-security/performing-content-security-policy-bypass/scripts/agent.py` | run | Content Security Policy (CSP) analysis and bypass testing agent. |
| `performing-graphql-security-assessment` | `07-web-security/performing-graphql-security-assessment/scripts/agent.py` | run | Agent for performing GraphQL security assessment. |
| `performing-security-headers-audit` | `07-web-security/performing-security-headers-audit/scripts/agent.py` | run | Agent for performing security headers audit. |
| `performing-web-application-firewall-bypass` | `07-web-security/performing-web-application-firewall-bypass/scripts/agent.py` | run | Agent for testing WAF bypass techniques. |
| `performing-web-application-penetration-test` | `07-web-security/performing-web-application-penetration-test/scripts/agent.py` | run | Web application penetration test agent using requests and subprocess. |
| `performing-web-application-vulnerability-triage` | `07-web-security/performing-web-application-vulnerability-triage/scripts/agent.py` | run | Agent for web application vulnerability triage. |
| `testing-api-authentication-weaknesses` | `07-web-security/testing-api-authentication-weaknesses/scripts/agent.py` | run | Agent for testing API authentication weaknesses. |
| `testing-api-security-with-owasp-top-10` | `07-web-security/testing-api-security-with-owasp-top-10/scripts/agent.py` | run | Agent for automated API security testing against OWASP API Security Top 10. |
| `testing-jwt-token-security` | `07-web-security/testing-jwt-token-security/scripts/agent.py` | run | Agent for testing JWT token security during authorized assessments. |
| `testing-oauth2-implementation-flaws` | `07-web-security/testing-oauth2-implementation-flaws/scripts/agent.py` | run | Agent for testing OAuth 2.0 implementation flaws. |
| `testing-websocket-api-security` | `07-web-security/testing-websocket-api-security/scripts/agent.py` | run | Agent for testing WebSocket API security. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
