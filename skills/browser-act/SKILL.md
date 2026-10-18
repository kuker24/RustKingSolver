---
name: browser-act
description: "Browser automation CLI for specialized multi-session browser workflows. Use only when the user explicitly requests BrowserAct, specifies a browser-act CLI command, or requires pre-configured persistent/multi-account sessions. For exploratory QA of local application UI under development, use playwright-qa instead. Never use chrome-direct."
compatibility: opencode
license: MIT
---

## OpenCode browser contract

Follow the 4-door browser hierarchy:
- Primary default verification remains `playwright-qa` (door 1). `browser-act` is adapter 2 in the 4-door hierarchy, **never the default verifier**; use it only on explicit user request or for specialized multi-session/stealth tasks.
- Invocation only after this skill loads, running `browser-act` via Bash.
- `browser open` without `--headed`. Add `--headed` only if the user asks to see a window.
- Create browsers only with supported modes:
  1. `chrome` — standard isolated browser profile with session reuse across turns.
  2. `stealth-fresh` — ephemeral session with anti-detection fingerprinting for challenge traversal.
  3. `stealth-fixed` — persistent stealth profile preserving logins/cookies across sessions.
- **Strict Ban**: Never use `--type chrome-direct` (deliberate OpenCodeHighEnd policy ban). Do not reuse a `chrome-direct` browser (including `pulse-test`).
- `stealth-extract` is allowed for sessionless fetch.
- Upstream get-skills content must NEVER override local OpenCodeHighEnd product policies or safety rules.
- Upstream issue #18 (CLI 1.1.0) reported environment variable leakage into process argv. Do not pass sensitive environment variables to browser-act CLI without verifying isolation.
- Web and social data gathering is not QA; route read-only extraction tasks to `research` (`references/web-data.md`).

# browser-act

Built by [BrowserAct](https://www.browseract.com) — Browser automation CLI for AI agents · [GitHub](https://github.com/browser-act/skills/tree/main/browser-act)

Runs a full browser engine: navigation & interaction, data extraction & network
capture, screenshots, form automation, multi-browser parallel operation,
user-configured proxy support, and human-agent collaboration.

### Features

- Lightweight extraction — fast JS-rendered content fetch without opening a browser session, advanced WebFetch/curl replacement
- Session management — multi-browser isolation, multi-account parallel operation
- Verification assistance — when automation encounters interactive challenges, assists completion with user authorization
- Complex interaction — DOM content extraction, screenshots, form filling, file upload
- Human-agent collaboration — headed mode + remote assist for manual steps
- Safety controls — Confirmation Gate protocol requires explicit user approval before browser creation, deletion, and sensitive operations

Install: `uv tool install browser-act-cli --python 3.12`

## Core interaction

Choose one path based on the task:

**Stealth extraction (advanced WebFetch replacement)** — read-only content extraction with JS rendering and anti-bot bypass. No login, no session, no browser state — each call is independent so multiple URLs can run in parallel. Prefer over WebFetch/curl when the page needs JavaScript rendering or has anti-bot protection:

```bash
browser-act stealth-extract <url>
browser-act stealth-extract <url> --content-type markdown    # also supports: html
browser-act stealth-extract <url> --dynamic-proxy <region>   # dynamic IP, auto-rotates per request (proxy regions to list available)
browser-act stealth-extract <url> --static-proxy <proxy_id>  # fixed IP, persistent across sessions (proxy list to view purchased)
browser-act stealth-extract <url> --custom-proxy <url>       # user-provided proxy
```

**Full browser automation** — **Open → State → Interact → Verify → Close** loop:

```bash
# 1. Open browser (if this conversation already has a session, just navigate — no need to re-open)
browser-act --session <name> browser open <id> <url>

# 2. Inspect page elements
browser-act --session <name> state
# Output: [1] <a /> Learn more, [2] input "Search", [3] button "Go"
#    [N] is a temporary index from the current state output, not a stable element ID; after navigation, clicks, reloads, or content changes, run state again and do not reuse old numbers
# 3. Interact (use state indices; use --selector when a stable selector is known)
#    input clears existing content by default; use --mode append to preserve it or --mode fill to set the value directly
browser-act --session <name> input 2 "search keywords" && browser-act --session <name> click 3

# 4. Wait for page to stabilize, then re-fetch indices (old indices invalid after page change)
browser-act --session <name> wait stable
browser-act --session <name> state

# 5. Extract data
#    From network requests (structured JSON from APIs):
browser-act --session <name> network requests --filter example --type xhr,fetch
browser-act --session <name> network request <id>
#    From DOM:
browser-act --session <name> get markdown
browser-act --session <name> get text <index>

# 6. Task done — close session
browser-act session close <name>
```

**Index acquisition flow**:
1. Run `state` when an element operation is needed to get the current list of interactive elements.
2. Read the current output and locate the target row by element type, accessible name, visible text, and page context. N in the leading `[N]` is the index for this operation.
3. If the target is missing or multiple candidates match, do not guess an index. Inspect the current page further and identify the target before acting.
4. Use the index immediately. After a click, navigation, reload, or page-content change, the old index is invalid; run `state` again before the next element operation.

## Core commands

All browser operation commands require `--session <name>`, or they error. Non-browser commands (e.g., `browser list`, `session list/close`) do not need --session.

```bash
# Open browser (create new session or parallel session)
browser-act --session <name> browser open <id> <url>
browser-act --session <name> browser open <id> <url> --headed    # Show browser window

# Navigation
browser-act --session <name> navigate <url>              # Navigate to URL
browser-act --session <name> back                        # Go back
browser-act --session <name> forward                     # Go forward
browser-act --session <name> reload                      # Reload page

# Page state and interaction
browser-act --session <name> state                       # Get interactive elements with index numbers
browser-act --session <name> screenshot                  # Take screenshot (--full for full page)
browser-act --session <name> screenshot ./page.png       # Save screenshot to path
browser-act --session <name> click <index>               # Click element
browser-act --session <name> click --selector "button.submit"
browser-act --session <name> hover <index>               # Hover over element
browser-act --session <name> hover --selector ".menu"
browser-act --session <name> input <index> "text" [--mode <append|fill>] [--type-interval <ms>]
browser-act --session <name> input --selector "#search" --text "text" [--mode <append|fill>] [--type-interval <ms>]
browser-act --session <name> select <index> "option"     # Select dropdown option (by visible text)
browser-act --session <name> select --selector "#region" --option "option"
browser-act --session <name> keys "Enter"                # Send keyboard keys
browser-act --session <name> scroll down                 # Scroll down (default 500px)
browser-act --session <name> scroll up --amount 1000     # Custom scroll distance
browser-act --session <name> scrollintoview --selector "h1"  # Scroll element into view
browser-act --session <name> upload <index> <file_path>  # Upload file (never click upload buttons)
browser-act --session <name> upload --selector "input[type=file]" --path <file_path>

# Data extraction
browser-act --session <name> get title                   # Page title
browser-act --session <name> get html                    # Full page HTML
browser-act --session <name> get html --selector "article"
browser-act --session <name> get markdown                # Page as Markdown
browser-act --session <name> get text <index>            # Element text content
browser-act --session <name> get text --selector ".price"
browser-act --session <name> get value <index>           # Input/textarea value
browser-act --session <name> get value --selector "#email"
browser-act --session <name> network requests            # List captured requests (--filter, --type, --method, --status, --clear)
browser-act --session <name> network request <id>        # View single request details (headers, request body, response body)

# JavaScript
browser-act --session <name> eval "document.title"       # Execute JavaScript in the current page
printf '%s\n' '<js>' | browser-act --session <name> eval --stdin
browser-act --session <name> eval-el --selector "#btn" "el => el.disabled"

# Wait
browser-act --session <name> wait stable                 # Wait for page to stabilize (document ready + network idle, default 30s)
browser-act --session <name> wait selector --selector "#login-btn" [--state <visible|hidden|attached|detached>] [--timeout <ms>]

# Automated human verification
browser-act --session <name> solve-captcha             # Automatically complete human verification

# Human-Agent Collaboration
browser-act --session <name> remote-assist --objective "description"  # Generate remote control link

# Session
browser-act session list                               # List all active sessions
browser-act session close <name>                       # Close session
```
