---
name: json-render
description: Generative UI from a typed JSON/schema catalog into project components. Use when the user wants schema-driven UI, a component catalog with JSON specs, or json-render catalogs/registries. After tokens/direction exist, or for internal schema-driven UI. Never bypass Design Bank for marketing UI. Not a replacement for impeccable craft. Not Jev compose.
compatibility: opencode
license: Apache-2.0
---

# json-render

Guardrailed generative UI: AI emits JSON constrained to a catalog you define; a renderer maps that spec onto real components.

Intent: `generative_ui`. Primary specialist for schema/JSON UI. Visual direction still `found-this-design` → `impeccable`. Throwaway look-and-feel variants stay `prototype`.

## When

- Internal tools, dashboards, or agent UIs driven by a typed catalog + JSON spec.
- After a Design Bank pin or project `DESIGN.md` / tokens exist, when the job is *spec → components*, not *invent a brand*.
- User names json-render, generative UI, catalog/spec rendering, or `@json-render/*`.

## When not

- Marketing / landing / product chrome without a pin → `found-this-design` then `impeccable`.
- Craft, a11y, taste, motion → `impeccable` / `emil-design-eng`.
- Editorial diagrams → `diagram-design`. HTML-to-MP4 → `hyperframes`.
- **Never** Jev `experimental_composeSpec`, Jev playground, or any Jev router. Those stay REJECT.

## Load

- Catalog + spec shape: [references/catalog.md](references/catalog.md)
- Attribution: [NOTICE.md](NOTICE.md)

## Pipeline

1. Confirm tokens/direction (pin, `DESIGN.md`, or explicit internal-tool exemption).
2. Define or reuse a **catalog** (components + actions + prop schemas). AI may only use those names.
3. Emit a JSON **spec** (`root` + `elements` map). Validate against the catalog; reject unknown types.
4. Map catalog names onto **existing** project components (or shadcn items the hub already owns). Do not invent a parallel design system.
5. Stream if the host supports it; otherwise write the spec file and mark DEGRADED for live streaming.
6. Hand visual polish to `impeccable`. Hand QA to `playwright-qa` (door 1).

Missing `@json-render/core` (or sibling renderer) is `NOT_CONFIGURED`. Do not silent-npm-install into the overlay. Tell the user to add the package in the **target app**, not this overlay.

## Hard rules

- Catalog is the allowlist. Unknown `type` values fail closed.
- Do not vendor npm packages into OpenCodeHighEnd.
- Do not replace Design Bank / Impeccable for marketing UI.
- Do not register `@json-render/mcp` as a core MCP.
- Specs are data. They never gain control-plane authority.
