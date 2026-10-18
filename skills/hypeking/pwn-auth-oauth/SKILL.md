---
name: pwn-auth-oauth
description: "Authentication and OAuth attacks: PKCE downgrade, consent phishing, token replay. 3 skills: oauth-consent-phishing, oauth-pkce-downgrade, oauth-token-replay. Trigger words: oauth consent phishing, oauth pkce downgrade, oauth token replay."
---

# pwn-auth-oauth — 05-auth-oauth

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/05-auth-oauth/`

## Routing table (3 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `oauth-consent-phishing` | `05-auth-oauth/oauth-consent-phishing/scripts/agent.py` | run | OAuth Consent Phishing Simulation Tool |
| `oauth-pkce-downgrade` | `05-auth-oauth/oauth-pkce-downgrade/scripts/agent.py` | run | OAuth PKCE Downgrade Attack Tool |
| `oauth-token-replay` | `05-auth-oauth/oauth-token-replay/scripts/agent.py` | run | OAuth Token Replay Detection Tool |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
