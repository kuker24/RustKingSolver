# DeepTeam API & CLI Reference

Source: https://github.com/confident-ai/deepteam

## CLI Invocation

```bash
deepteam <command> [options]
```

## Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `run` | Execute red teaming evaluation | `deepteam run --config config.yaml` |
| `scan` | Scan agent source code / endpoints | `deepteam scan --target http://127.0.0.1:8000` |
| `list` | Show available attacks and vulnerabilities | `deepteam list --attacks` |

## Vulnerability Categories

- **Prompt Injection**: Direct instruction overriding, context jailbreaks, delimiter hijacking.
- **Data Leakage**: PII exposure, training data extraction, system prompt regurgitation.
- **Unauthorized Actions**: Tool misuse, SQL injection through generated queries, SSRF.
- **Toxicity & Harm**: Hate speech, self-harm instruction, illegal advice generation.

## Attack Methodologies

- `single_turn`: Single prompt adversarial injection, obfuscation, base64 encoding, ROT13.
- `multi_turn`: Conversational attacks, Crescendo, gradual trust building, roleplay framing.
- `tree_of_attacks`: Branching exploration of prompts optimizing for adversarial objective fulfillment.
