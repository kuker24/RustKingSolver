---
name: playwright-qa
description: Primary exploratory browser QA adapter for web applications under development. Use to navigate local UI, exercise forms, inspect rendered DOM/state, take snapshots and screenshots, and verify visual flows via Playwright CLI. Respects existing project test suites (Playwright Test/Cypress) for regressions. Skip for backend-only tasks, explicit BrowserAct requests, or deep observed-failure diagnostics (chrome-devtools-axi).
compatibility: opencode
license: Apache-2.0
---

# playwright-qa

OpenCodeHighEnd adapter for exploratory browser QA using Playwright CLI.
Adapted from [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli) (Apache-2.0, Microsoft Corporation).

This skill provides an interactive, token-efficient browser interface for agents to verify UI changes in the application under development without installing large MCP servers or polluting application dependencies.

## Core Rules

1. **Primary Exploratory QA**: Use Playwright CLI to explore and verify UI changes built in the current session (navigation, form inputs, button clicks, state assertions, screenshots).
2. **Respect Project Test Suites**: If the project already configures Playwright Test, Cypress, or another runner, run regressions through the project's own package manager and scripts (e.g. `npx playwright test`). Never replace or shadow the project's config.
3. **No Phantom Installations**: Check actual runtime capabilities before executing browser commands. Never run unguided `npx` that triggers implicit downloads during discovery.
4. **Isolated Task Sessions**: Every browser interaction must use a scoped session name (`-s=<task-id>`) bound to the current task/workspace. Never use global `close-all` or `kill-all`.
5. **Headless & Chromium Default**: Default to headless Chromium with an isolated profile. Never bind to personal Google Chrome profiles or force Chrome executables unless explicitly requested.
6. **Port Separation**: Port 9223 is reserved for `opencode-chromium-cdp` / `chrome-devtools-axi`. Do not force Playwright sessions through port 9223.
7. **Privacy & Hygiene**: Storage state, cookies, HAR recordings, traces, and screenshots must never be committed to git or printed with sensitive credentials.
8. **No Browser for Backend**: Never start browser sessions when only backend, API, database, or non-UI code changed.
9. **No Data Gathering**: Web and social data gathering is not UI QA; route extraction tasks to `research` (`references/web-data.md`).
10. **Emulation & Responsive QA**: Emulate devices (`open --device`), resize viewports (`resize <w> <h>`), and toggle media features (`set-color-scheme`, `set-reduced-motion`, `set-forced-colors`, `set-contrast`, `set-media`). Timezone, locale, and geolocation are configured via `.playwright/cli.config.json` (`contextOptions`, with `permissions: ["geolocation"]`), or runtime via `run-code` (cross-browser API for geolocation; Chromium CDP for timezone/locale).

## Workflow

Follow the QA loop: **understand flow -> run app -> open session -> observe/interact -> assert state -> close session**.

```bash
# 1. Open isolated task session
playwright-cli -s=task-ui open http://localhost:3000

# 2. Inspect page structure (captures semantic refs e1, e2...)
playwright-cli -s=task-ui snapshot

# 3. Locate & interact using snapshot refs or search
playwright-cli -s=task-ui find "Sign In"
playwright-cli -s=task-ui click e4
playwright-cli -s=task-ui fill e7 "test user"
playwright-cli -s=task-ui press Enter

# 4. Verify outcome with fresh snapshot, screenshot, or trace
playwright-cli -s=task-ui snapshot
playwright-cli -s=task-ui screenshot --filename=artifacts/qa-verify.png

# 5. Clean up task session
playwright-cli -s=task-ui close
```

## Evidence ledger

A PASS claim needs FACT rows: snapshot (or path), screenshot path, process exit 0. Optional flake: `playwright-cli -s=task-ui tracing start` then `tracing stop`. Missing artifact = `NOT_CONFIGURED`, not PASS. Never vendor browser-use; never make it door 0. Door 1 remains this skill.

## References

- Operational QA flow & assertions: [references/workflow.md](references/workflow.md)
- Session isolation & cleanup: [references/sessions.md](references/sessions.md)
- Setup, runtime discovery, & dependency boundaries: [references/setup.md](references/setup.md)
- Layout shift (CLS) observation recipe: [references/cls.md](references/cls.md)
