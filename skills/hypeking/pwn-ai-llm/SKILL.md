---
name: pwn-ai-llm
description: "AI/LLM security: prompt injection, RAG pipeline attacks, guardrails, MCP auditing, red-teaming. 15 skills: assessing-vector-and-embedding-weaknesses, auditing-mcp-servers-for-tool-poisoning, continuous-llm-red-teaming-with-promptfoo, defending-llms-with-guardrails, detecting-ai-model-prompt-injection-attacks, detecting-data-and-model-poisoning, detecting-indirect-prompt-injection, detecting-model-extraction-attacks. Trigger words: assessing vector and embedding weaknesses, auditing mcp servers for tool poisoning, continuous llm red teaming with promptfoo, defending llms with guardrails, detecting ai model prompt injection attacks, detecting data and model poisoning."
---

# pwn-ai-llm — 09-ai-llm-web

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/09-ai-llm-web/`

## Routing table (15 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `assessing-vector-and-embedding-weaknesses` | `09-ai-llm-web/assessing-vector-and-embedding-weaknesses/scripts/agent.py` | run | Vector/embedding weakness assessor. |
| `auditing-mcp-servers-for-tool-poisoning` | `09-ai-llm-web/auditing-mcp-servers-for-tool-poisoning/scripts/agent.py` | run | MCP tool-poisoning audit agent. |
| `continuous-llm-red-teaming-with-promptfoo` | `09-ai-llm-web/continuous-llm-red-teaming-with-promptfoo/scripts/agent.py` | run | Continuous LLM red-teaming helper for Promptfoo + DeepTeam. |
| `defending-llms-with-guardrails` | `09-ai-llm-web/defending-llms-with-guardrails/scripts/agent.py` | run | Guardrail validation harness. |
| `detecting-ai-model-prompt-injection-attacks` | `09-ai-llm-web/detecting-ai-model-prompt-injection-attacks/scripts/agent.py` | run | Prompt Injection Detection Agent |
| `detecting-data-and-model-poisoning` | `09-ai-llm-web/detecting-data-and-model-poisoning/scripts/agent.py` | run | Data and model poisoning detection agent. |
| `detecting-indirect-prompt-injection` | `09-ai-llm-web/detecting-indirect-prompt-injection/scripts/agent.py` | run | Indirect prompt-injection detection agent. |
| `detecting-model-extraction-attacks` | `09-ai-llm-web/detecting-model-extraction-attacks/scripts/agent.py` | run | Model-extraction detection helper. |
| `implementing-llm-guardrails-for-security` | `09-ai-llm-web/implementing-llm-guardrails-for-security/scripts/agent.py` | run | LLM Guardrails Security Agent |
| `llm-security` | `09-ai-llm-web/llm-security/SKILL.md` | read | OWASP LLM Top 10 security testing - prompt injection, system prompt leakage, excessive agency, sensitive data disclosure |
| `orchestrating-llm-attacks-with-pyrit` | `09-ai-llm-web/orchestrating-llm-attacks-with-pyrit/scripts/agent.py` | run | PyRIT multi-turn LLM attack runner. |
| `red-teaming-llms-with-garak` | `09-ai-llm-web/red-teaming-llms-with-garak/scripts/agent.py` | run | garak red-team automation helper. |
| `securing-agentic-ai-tool-invocation` | `09-ai-llm-web/securing-agentic-ai-tool-invocation/scripts/agent.py` | run | Agentic AI tool-invocation policy gate. |
| `testing-for-system-prompt-leakage` | `09-ai-llm-web/testing-for-system-prompt-leakage/scripts/agent.py` | run | System-prompt leakage tester. |
| `testing-prompt-injection-in-rag-pipelines` | `09-ai-llm-web/testing-prompt-injection-in-rag-pipelines/scripts/agent.py` | run | RAG prompt-injection testing agent. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```

## Prompt-architecture stack

The `g0dm0d3` pack (parseltongue / godmode / autotune) was removed 2026-10-18 —
it was never opened across the Redlimit CTV campaign. Prompt-architecture and
input-obfuscation work now runs from the 15 skills above; for open-ended
multi-approach ideation use the `adhd` skill.

Ambiguous cross-pack asks → `read skill://hypeking/skill-router`.

