# Tree then reason

Pin: `VectifyAI/PageIndex@6d23caf416858f2ca136840305d1f479a86f6ef7` (v0.2.21, MIT).

## Why a tree

Vector RAG retrieves by similarity. Long professional documents need
**relevance**, which takes a map of sections and a reason to open one.
PageIndex-style retrieval is two steps:

1. **Index** — hierarchical tree (title, summary, start_index, end_index, page/section span, children).
2. **Retrieve** — LLM (or this session) walks the tree, recording why each node
   was opened, then reads only those leaves.

No vector DB. No blind chunking.

## Tree Node Schema (v0.2.21)

Every node in the hierarchical tree structure carries explicit range boundaries:

- `title`: Heading text or section name.
- `summary`: Abstract or distillation of the section content (≤150 words).
- `start_index`: 1-based physical page number.
- `end_index`: 1-based physical page number (inclusive end).
- `page_span`: Human-readable page interval (e.g. `pp. 14–22`). **OCH-derived** — not present in upstream schema.
- `node_id`: Unique identifier for a node within the tree (upstream field).
- `nodes`: Nested list of child tree nodes.

### Upstream helper functions

`utils.py:1396–1419` provides four helpers for tree traversal:

- `get_node(tree, node_id)` — look up a node by its `node_id`.
- `get_node_parent(tree, node_id)` — return the parent of the given node.
- `get_node_path(tree, node_id)` — return the root-to-node path as a list.
- `get_node_map(tree)` — build a flat `{node_id: node}` dict for O(1) lookups.

## Local overlay path (no extra deps)

When the SDK is absent:

1. Extract text via `smartdoc` or `markitdown` (existing tools).
2. Build a heading tree from TOC / `h1–h3` / numbered sections.
3. Summarize each node in ≤150 words from its own text (do not invent).
4. Walk: start at root, pick children with a one-line reason, stop at leaves.
5. Quote spans with page or heading provenance.

This is DEGRADED relative to upstream flash indexing, but it is honest.
Missing extractors → `NOT_CONFIGURED`.

## Optional SDK (user machine)

```text
pageindex Python package on PATH or importable
→ local flash index allowed
→ never pip-install into OpenCodeHighEnd
```

Cloud `index="cloud"` / `PAGEINDEX_API_KEY` / PageIndex MCP: do not configure.

## Boundaries

| Need | Route |
|---|---|
| Tree/reasoning over a long doc | **pageindex** |
| Official docs / API facts | `research` |
| Scholarly IMRaD | `academic` |
| Contract/OCR/render | `smartdoc` |
| Code symbols | codebase-memory-mcp |
| Entity knowledge graphs | REJECT (Graphiti/Cognee) |
