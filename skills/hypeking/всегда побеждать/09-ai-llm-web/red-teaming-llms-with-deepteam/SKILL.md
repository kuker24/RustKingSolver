---
name: red-teaming-llms-with-deepteam
description: Automated LLM and AI agent red teaming with DeepTeam (Confident AI). Test targets for single-turn and multi-turn jailbreaks, prompt injection, PII leakage, bias, SSRF, SQL injection, and guardrail bypasses, mapped to OWASP LLM Top 10 and MITRE ATLAS.
domain: cybersecurity
subdomain: ai-security
tags:
- ai-security
- llm-red-teaming
- deepteam
- prompt-injection
- jailbreak
- multi-turn-attacks
- vulnerability-scanning
- mitre-atlas
- confident-ai
version: '1.0'
author: confident-ai
license: Apache-2.0
nist_csf:
- MEASURE-2.7
mitre_attack:
- AML.T0051
- AML.T0054
---
# Red-Teaming LLMs with DeepTeam

> **Legal and Authorized-Use Notice:** This skill is for authorized AI security testing, audit, and educational validation only. Red-team only LLM endpoints, agents, and RAG pipelines you own or have explicit written authorization to test. Automated testing of third-party APIs incurs token costs and must comply with applicable terms of service.

## Overview

**DeepTeam** is an open-source LLM red teaming framework created by Confident AI. It automates adversary emulation against LLMs, agentic workflows, and RAG applications by systematically probing target systems for safety failures, prompt injections, multi-turn jailbreaks, and sensitive data leakage.

Key capabilities:
- **50+ Pre-Configured Vulnerabilities**: Covers OWASP LLM Top 10, MITRE ATLAS, and NIST AI RMF categories including prompt injection, jailbreaking, PII disclosure, toxicity, bias, and unauthorized tool invocation.
- **Single-Turn and Multi-Turn Exploitation**: Simulates conversational adversaries using Crescendo, tree-of-attacks, persona manipulation, and adaptive multi-turn probing.
- **Local LLM-as-a-Judge Evaluation**: Uses local or configured evaluator models to score test cases with binary pass/fail verdicts and granular reasoning logs.
- **Model Agnostic**: Supports OpenAI, Anthropic, Bedrock, Ollama, HuggingFace, and custom HTTP endpoints.

## When to Use

- Security assessment of LLM agents before staging or production cutover.
- Evaluating resilience of system prompts and input/output guardrails against jailbreaks.
- Regression testing of AI RAG pipelines for indirect prompt injection or context leakage.
- Producing quantitative compliance artifacts for NIST AI RMF MEASURE-2.7 and MITRE ATLAS.

## Installation & Setup

```bash
# Install deepteam via pip or uv
pip install -U deepteam deepeval

# Verify CLI availability
deepteam --help
```

## Quick Start

### 1. Execute an Automated Red Team Scan
```bash
python3 ~/.omp/agent/skills/hypeking/всегда\ побеждать/09-ai-llm-web/red-teaming-llms-with-deepteam/scripts/agent.py run \
    --model gpt-4o-mini \
    --attacks prompt-injection,jailbreak \
    --output assessment-results.json
```

### 2. Inspect Available Attacks and Vulnerabilities
```bash
python3 ~/.omp/agent/skills/hypeking/всегда\ побеждать/09-ai-llm-web/red-teaming-llms-with-deepteam/scripts/agent.py list-attacks
python3 ~/.omp/agent/skills/hypeking/всегда\ побеждать/09-ai-llm-web/red-teaming-llms-with-deepteam/scripts/agent.py list-vulnerabilities
```

## Output Artifacts

DeepTeam generates structured reports:
- Summary of tested vulnerabilities with pass/fail ratios and attack success rates (ASR).
- Per-attack transcripts demonstrating prompt generation, target response, and judge rationale.
- Risk severity categorization aligned with MITRE ATLAS techniques.
