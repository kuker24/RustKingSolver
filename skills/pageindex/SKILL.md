---
name: pageindex
description: Tree and reasoning-based navigation of long complex documents before answering. Use for vectorless long-doc RAG, filings, manuals, textbooks, and hierarchical TOC reasoning. Not Graphiti/Cognee. Not a second codebase-memory. Prefer local/offline; degrade NOT_CONFIGURED without deps.
compatibility: opencode
license: MIT
---

# pageindex

Vectorless long-document navigation: build a **tree index**, then **reason** down it. Similarity search is not this skill.

Intent: `longdoc_nav`. `research` keeps primary-source lookup. `academic` keeps scholarly IMRaD. `smartdoc` keeps per-job contracts/OCR/render. `codebase-memory-mcp` keeps **code** graphs. Graphiti/Cognee stay REJECT.

## When

- Long structured professional docs (filings, manuals, textbooks, regulatory PDFs) where the question needs the right section, not a similar chunk.
- User names PageIndex, tree index, vectorless RAG, or “reason through the document”.

## When not

- Short docs that already fit in context → `smartdoc` / `research`.
- Codebase symbols → Codebase Memory MCP.
- Knowledge graphs / temporal entity memory → not this overlay (Graphiti/Cognee REJECT).
- Do not add a PageIndex MCP (cloud or local) to core servers.

## Load

- Tree method: [references/tree.md](references/tree.md)
- Attribution: [NOTICE.md](NOTICE.md)

## Pipeline

1. Confirm the artifact is a long structured document (or a small set of them).
2. Prefer **local** tree build: outline / TOC / heading walk first (no extra package).
3. If `pageindex` Python SDK is installed in the **user** environment, local flash index is allowed. Do not `pip install` into the overlay venv.
4. Retrieve by walking the tree with reasons (“this heading, because…”). Cite page or section. Do not dump similar chunks.
5. Answers remain bound to primary sources. The tree is a map, not a citation owner.

If the SDK, model key, or PDF parser is missing: `NOT_CONFIGURED`. Answer only from text already extracted (`smartdoc` / `markitdown`) or stop with `ask_user`. Never fake a tree.

Cloud PageIndex (`PAGEINDEX_API_KEY`, hosted MCP) is FOREIGN_ON_DEMAND and **off**. Do not enable it. Do not write API keys.

## Hard rules

- Not a core MCP. Not a second codebase-memory.
- Not Graphiti, Cognee, WeKnora, OpenMAIC, or Open WebUI.
- Do not vendor the PageIndex Python package.
- Degrade closed when deps are absent.
