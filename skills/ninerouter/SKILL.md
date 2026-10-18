---
name: ninerouter
description: Route model inference, image generation, TTS, STT, embeddings, or web fetch/search through a local or remote 9Router gateway. Use when user mentions 9router, NINEROUTER_URL, gateway models, or multi-provider fallbacks. Not a core MCP server or credential store; degrades gracefully to NOT_CONFIGURED when gateway is absent.
compatibility: opencode
license: MIT
---

# ninerouter

First-party gateway stub connecting to a user-managed **9Router** instance for multi-provider LLM routing, image/video generation, text-to-speech, transcription, embeddings, and web tools.

Intent: `gateway_llm`. 9Router is a `FOREIGN_ON_DEMAND` gateway, not an extra core MCP server. Core MCP remains strictly `codebase-memory-mcp`, `context7`, and `shadcn`.

## Configuration & Environment

9Router is configured strictly via environment variables:

- `NINEROUTER_URL`: Gateway base URL (defaults to `http://127.0.0.1:20128`).
- `NINEROUTER_KEY`: Gateway API key (required only if `requireApiKey` is enabled). Passed as `Authorization: Bearer <key>`. Never log or hardcode key values.

### Fail-Closed Security Rules

- **Zero-Bind Prohibition**: If `NINEROUTER_URL` contains `0.0.0.0` or binds all interfaces, fail closed immediately.
- **Graceful Absence**: If `NINEROUTER_URL` is unreachable or unconfigured, report `NOT_CONFIGURED`. This is an optional gateway, never an installer or `opencode-he doctor` failure.
- **TLS Certificate Validation**: When connecting to a remote 9Router gateway via HTTPS, standard TLS verification must remain active. Enforce valid TLS certificates for non-localhost endpoints. For internal self-signed CAs, configure `NODE_EXTRA_CA_CERTS` or `SSL_CERT_FILE` in the host environment; never bypass certificate verification using `--insecure` or `NODE_TLS_REJECT_UNAUTHORIZED=0` in production.
- **TLS Auto-Fallback Warning** (v0.5.95): upstream proxy auto-falls back to TLS-insecure mode on self-signed certificate errors (`open-sse/utils/proxyFetch.js`). Connections through the gateway to upstream providers should not be assumed TLS-verified.

## Health & Discovery

Verify connectivity:
```bash
curl -s "$NINEROUTER_URL/api/health"
# Expected response: {"ok":true}
```

Available model endpoints:
- Chat / LLM: `/v1/models`
- Image generation: `/v1/models/image`
- Text-to-speech: `/tts`
- Speech-to-text: `/stt`
- Embeddings: `/embedding`
- Web search / fetch: `/web`

## On-Demand Capability Skills

Do not vendor upstream skills. Fetch raw definitions on-demand from `https://github.com/decolua/9router` (`master` @ `a99cf57` / v0.5.95; legacy `f01fb90`):
- `skills/9router/SKILL.md` (entry / setup)
- `skills/9router-chat/SKILL.md`
- `skills/9router-image/SKILL.md`
- `skills/9router-video/SKILL.md`
- `skills/9router-tts/SKILL.md`
- `skills/9router-stt/SKILL.md`
- `skills/9router-embeddings/SKILL.md`
- `skills/9router-web-search/SKILL.md`
- `skills/9router-web-fetch/SKILL.md`
