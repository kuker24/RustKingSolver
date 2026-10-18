# Catalog and spec

Pin: `vercel-labs/json-render@c2600d73908ed505e6d726f5b6f969ba8f597ce7` (Apache-2.0).

## Catalog

A catalog names every component and action the model may emit. Typical fields:

- `components.<Name>.props` — schema (zod or JSON Schema).
- `components.<Name>.description` — one-line purpose for the prompt.
- `actions.<name>.description` — allowed side effects (`setState`, domain actions).

The catalog prompt (`catalog.prompt()` in upstream) is the system fence. Do not
widen it with “any HTML” or “any React node”.

Prefer project components already in the tree. `@json-render/shadcn` is optional
when the target app already uses shadcn; it is not an overlay dependency.

## Spec

Flat spec (web UI):

```json
{
  "root": "card-1",
  "elements": {
    "card-1": {
      "type": "Card",
      "props": { "title": "Hello" },
      "children": ["button-1"]
    },
    "button-1": {
      "type": "Button",
      "props": { "label": "Click me", "action": "refresh_data" },
      "children": []
    }
  }
}
```

Reject specs that:

- use a `type` not in the catalog
- pass props outside the schema
- embed raw HTML/JS
- call Jev `experimental_composeSpec` / `experimental_createEvaluator`

## Renderers (target app, not overlay)

React `@json-render/react`, Vue, Svelte, Solid, React Native, Next, Ink, etc.
Pick the renderer that matches the project. Video/PDF/email renderers are
out of scope here (`hyperframes`, `smartdoc`, Impeccable `email.md`).

## Streaming

If `@json-render/core` `createSpecStreamCompiler` is available in the app,
stream patches into the renderer. If not, write `.scratch/json-render/<slug>.json`
and mark streaming `NOT_CONFIGURED`.
