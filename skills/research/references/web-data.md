# Web and Social Data Gathering Reference

This guide governs read-only web and social data gathering in OpenCodeHighEnd under the `research` skill. All operations remain subject to the primary-source rule: output is structured data, and every claim must be traceable to the owning primary source.

## Backend Selection Ladder

When retrieving data from the web or public feeds, always progress up the ladder from lightest to heaviest tool. Never reach for a browser or stealth runner when lightweight HTTP suffices.

1. **Lightweight HTTP & Search (`WebSearch` / `WebFetch` / `curl`)**
   - Default tier for static pages, search queries, documentation, and standard APIs.
   - Zero additional runtime overhead.

2. **Article Content Extraction (MCP `crawl4ai` when CONFIGURED)**
   - Use when extracting markdown from long-form articles, documentation sites, or blog posts.
   - Requires user-configured Crawl4AI local container (`http://127.0.0.1:11235/mcp`) or cloud endpoint.

3. **Structured Scraping (MCP `scrapling` when CONFIGURED)**
   - Use when extracting structured data with CSS/XPath selectors, adaptive element tracking, or JSON APIs.
   - Enable via `opencode-he scrapling enable` (runs stdio MCP via `uvx`).
   - Order of operations: prefer `make_request` or `bulk_get` first; invoke browser-backed `fetch` only if JavaScript execution is strictly required to render target data.

4. **Background XHR Capture (Scrapling Python Scripting)**
   - When public dynamic web apps load data through internal API calls, use Scrapling's `DynamicSession(capture_xhr=...)` to capture raw JSON payloads directly rather than parsing rendered DOM.
   - Any helper script must be written to `/tmp` (e.g. `/tmp/scrape_xhr.py`) or a user-specified project path. **Never write scripts into the OpenCodeHighEnd overlay directory.**

5. **Zero-Config Feeds & Developer Endpoints (Agent-Reach CLI)**
   - Pointer-only host tool for specialized zero-config sources: YouTube subtitles (`yt-dlp`), GitHub data (`gh`), public RSS feeds, and V2EX.
   - OCH does not vendor or install Agent-Reach. If the user desires to install it themselves:
     `pipx install 'git+https://github.com/Panniantong/agent-reach.git@f65526cbaaad3879473acc1ba6dbefd195caf2be'`
   - **Strict prohibition**: Never run `agent-reach install --system` (it mutates system packages and copies foreign skills into `~/.omp/agent/skills/`).

6. **Authenticated Social Platforms (X, Reddit, Xiaohongshu, Facebook, Instagram, LinkedIn)**
   - Access only when the user explicitly requests platform data AND has already configured their own credentials or environment.
   - OpenCodeHighEnd and its tools **never hold, store, or extract user session cookies or passwords**.

7. **Multi-Session or Persistent Browser Workflows (`browser-act`)**
   - For interactive sessions requiring persistent login state across turns, route explicitly to `browser-act`.
   - Never use `browser-act` as an exploratory QA replacement (`playwright-qa` remains the QA verifier).

---

## Ethical and Safety Boundaries

1. **Explicit Consent for Stealth**:
   - `stealthy_fetch` and anti-bot challenge bypass are disabled by default. Use them only upon explicit user instruction, where the user confirms they have authorization and site Terms of Service allow data access.

2. **Robots.txt & Polite Crawling**:
   - Always respect target site directives (`robots_txt_obey=True` on spiders).
   - Enforce polite download delays and sensible concurrency limits. Do not hammer endpoints.

3. **No Credential or Login-Wall Bypasses**:
   - Never bypass paywalls, private member portals, or login walls.
   - Never extract authentication tokens or cookies from user desktop browsers (`--from-browser` is banned).

4. **No Deceptive Proxy Rotation**:
   - Do not use proxy rotators to disguise abuse or circumvent defensive rate limits.

5. **Third-Party Relay Transparency**:
   - If using services like `r.jina.ai` to convert pages to markdown, explicitly inform the user that the target URL is being sent to a third-party service.

6. **Data Grounding**:
   - Scraping results represent raw input data. Output claims must accurately cite the primary source URL, timestamp, and author or domain.
