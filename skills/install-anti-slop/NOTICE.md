# Anti-Slop Skill Notice

This skill vendors and adapts the Anti-Slop Oxlint plugin originally authored by Dillon Mulroy.

- Upstream repository: https://github.com/dmmulroy/anti-slop
- Upstream commit: c44ef22ca116d0ba62a3ff663a0bd13a3f3fa40b
- Upstream version: 0.1.2+c44ef22 (untagged main, post-v0.1.2)
- License: MIT License (see vendor/licenses/DMMULROY-ANTI-SLOP-MIT.txt)
- Copyright (c) 2026 Dillon Mulroy

## Bundled Third-Party Code
- **eslint-stylistic**: Vendored under `assets/anti-slop/vendor/eslint-stylistic/`.
  - Upstream source: https://github.com/eslint-stylistic/eslint-stylistic
  - Commit: `435c3ea0fd26a5fef9042c4b36b6e165fbbf8d08` (tag `v6.0.0-beta.6`)
  - License: MIT License (see `vendor/licenses/ESLINT-STYLISTIC-MIT.txt` and `assets/anti-slop/vendor/eslint-stylistic/LICENSE`)
  - Copyright OpenJS Foundation and other contributors, <www.openjsf.org>
  - Copyright (c) 2023-PRESENT ESLint Stylistic contributors
  - Note: Adapted and ported to Oxlint AST types by Dillon Mulroy upstream (see `assets/anti-slop/vendor/eslint-stylistic/UPSTREAM.md`), not by OpenCodeHighEnd.

## Modifications for OpenCodeHighEnd
- Vendored 38 assets under `assets/anti-slop/` are byte-identical to upstream `c44ef22` (zero local modifications to linter rule assets).
- Adapted as an opt-in model-invoked skill for TypeScript/JavaScript projects.
- Added `scripts/manage.mjs` supporting 5 explicit modes:
  - `audit`: isolated discovery reporting findings per rule and file category without repo mutations.
  - `recommended`: curated high-signal profile (`no-chained-type-assertions`, `no-widen-then-assert`, audit on `no-known-value-widening`, audit/warn on `require-safety-comment-for-type-assertion`).
  - `strict`: full 18-rule generic ruleset from upstream snapshot plus native companion `oxc/no-accumulating-spread`.
  - `custom`: project-configured rules.
  - `update`: non-destructive dry-run comparison (`[ADD]`, `[CHANGE]`, `[SAME]`, `[LOCAL-ONLY]`) following upstream `references/update.md` merge doctrine; mutations applied only with `--force`.
  - `effect`: 5 opt-in Effect architectural rules for direct Effect dependencies.
- Added safe removal, non-destructive update, idempotency checks, and collision detection.
- Restored `scripts/install.mjs` to byte-identical upstream snapshot (`db1f155b`).
- Added `references/update.md` byte-identical to upstream snapshot (`b2e7f675`).
- Strictly segregated from core OCBF Python dependencies (no Oxlint forced onto OCBF itself).

## Additional Attribution
UI and copy named patterns in `rules/03-prose-discipline.md`, `skills/impeccable/reference/taste-guard.md`, and `skills/writing-for-agents/SKILL.md` also draw on [miqdadbadjuber/anti-slop](https://github.com/miqdadbadjuber/anti-slop) MIT (v3.2.x patterns; no verbatim dump, zero extra catalog skills or external runtime dependencies added).
