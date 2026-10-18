# Notice: ninerouter

- Gateway integration: [decolua/9router](https://github.com/decolua/9router)
- Pinned commit: `a99cf57239ff778b61e434c2786009d5ed1c412c` (v0.5.95; `f01fb90` base)
- License: MIT
- Status: First-party gateway stub (`FOREIGN_ON_DEMAND`). Upstream skills are fetched on-demand; not vendored into overlay core.
- **TLS Auto-Fallback Warning** (v0.5.95): upstream proxy auto-falls back to TLS-insecure mode on self-signed certificate errors (`open-sse/utils/proxyFetch.js`). Connections through the gateway to upstream providers should not be assumed TLS-verified.
