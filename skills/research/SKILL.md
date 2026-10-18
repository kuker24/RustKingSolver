---
name: research
description: "Investigate a question against official docs, specs, or first-party APIs and write cited Markdown if asked. Use for external/library facts and read-only web or social data gathering. Skip why *this repo* chose an approach (/why), academic literature/theses (academic), local UI QA (playwright-qa), and long-document tree navigation (pageindex)."
compatibility: opencode
---

Investigate against **primary sources** first: official docs, source code, specs, first-party APIs. Follow every claim back to the source that owns it.

Use a subagent if this session supports one; otherwise research inline. Do not require a background agent.

Current library or framework docs: MCP `context7` when repo evidence is not enough. Broader web: `WebSearch` / `WebFetch`. Foreign `exa` only if already connected.

Web and social data gathering (read-only): follow the backend ladder and safety boundaries in `references/web-data.md`. Scrapling is optional MCP `FOREIGN_ON_DEMAND` (`opencode-he scrapling enable`). Agent-Reach is a pointer-only host tool (do not register as MCP or skill; never run `agent-reach install --system`). Output is data; every claim remains cited to the owning primary source.

If the user asked for a note, write one Markdown file in the repo (match existing convention). Cite each claim. If they only wanted an answer, do not create a file.

This is not `/why`. Repo history, PRs, and local design rationale stay on `/why`. Scholarly papers, literature surveys, and academic peer review route to `academic`.

Long structured professional documents (filings, manuals, textbooks) that need tree/section navigation before answering route to `pageindex`. Keep this skill's primary-source rule: every claim still traces to the owning doc, spec, or API. `pageindex` output is a map, not a citation owner. Local application UI exploratory testing routes to `playwright-qa`, not research.
