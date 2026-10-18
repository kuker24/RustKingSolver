# Playwright QA Skill Notice

This skill is an OpenCodeHighEnd adaptation of the Playwright CLI interface
originally developed by Microsoft Corporation.

- Upstream project: https://github.com/microsoft/playwright-cli
- Upstream commit: b85c7a736bb473bf55b584e54a09ffa698d6d871
- License: Apache License 2.0 (see vendor/licenses/MICROSOFT-PLAYWRIGHT-CLI-APACHE2.txt)
- Copyright (c) Microsoft Corporation

## Modifications for OpenCodeHighEnd
- Adapted as an in-session exploratory QA tool for local UI changes.
- Scoped browser sessions with task/workspace naming to prevent cross-project collisions.
- Explicit runtime discovery without unprompted background downloads or package mutations.
- Strict separation between OCBF tool invocation and target application dependencies.
- Suite preservation: project Playwright Test and other E2E suites remain authoritative for regressions.
- Added device emulation, session-command media-feature toggles (`set-color-scheme`, `set-reduced-motion`, `resize`), WebMCP command boundaries, and explicit CLI v0.1.22 syntax.
