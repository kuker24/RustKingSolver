---
name: install-anti-slop
description: Install, audit, configure, or remove opinionated Anti-Slop Oxlint rules in local TypeScript or JavaScript repositories. Use ONLY when explicitly requested to add anti-slop rules, audit TS/JS anti-patterns, configure anti-slop profiles, or migrate/remove an anti-slop setup. Skip for Python/Go/Rust, prose editing (use /unslop), and ordinary coding tasks.
compatibility: opencode
license: MIT
---

# install-anti-slop

OpenCodeHighEnd adapter for installing, auditing, configuring, or removing Anti-Slop Oxlint rules.
Vendored from [dmmulroy/anti-slop](https://github.com/dmmulroy/anti-slop) (MIT, Dillon Mulroy, commit `c44ef22ca116d0ba62a3ff663a0bd13a3f3fa40b`, version `0.1.2+c44ef22 (untagged main, post-v0.1.2)`).

## Core Boundaries

1. **Opt-In Only**: Load this skill ONLY when the user explicitly requests Anti-Slop (e.g. "pasang anti-slop", "audit anti-slop", "hapus anti-slop"). Never auto-load during ordinary coding or non-TS/JS tasks.
2. **Distinct from `/unslop` and UI Craft**: `/unslop` and `rules/03-prose-discipline.md` handle prose cleanup. UI template anti-patterns live in `skills/impeccable/reference/taste-guard.md`. `install-anti-slop` is strictly for static Oxlint linting of TypeScript/JavaScript code.
3. **No OCBF Core Coupling**: Never add Oxlint or Anti-Slop to OCBF's core Python codebase or dependencies.
4. **Exact Version Coupling**: Keep `oxlint` and `@oxlint/plugins` on the exact same version (1.78.0).
5. **No Blind Global Rewrites**: Linter findings identify patterns; resolve root causes with inference, `satisfies`, and boundary validation rather than casts or fake comments.

## The 5 Modes

| Mode | Behavior |
|---|---|
| `audit` | Evaluates rules against source/test/tooling; reports findings without modifying files or dependencies. |
| `recommended` | Installs curated OCBF profile (4 high-signal assertions) after baseline review. |
| `strict` | Enables all 18 generic upstream rules + native companion `oxc/no-accumulating-spread` (requires explicit user confirmation). |
| `custom` | Enables user-selected rule set. |
| `update` | Non-destructive dry-run comparison (ADD/CHANGE/SAME/LOCAL-ONLY); applies overwrite and reconciliation only with `--force` (see [references/update.md](references/update.md)). |

*Effect Rule Group*: Opt-in separately (`--with-effect`) only if `effect` is a direct project dependency (5 rules).
*Vendored Dependencies*: Includes upstream-adapted `eslint-stylistic` (MIT) under `assets/anti-slop/vendor/eslint-stylistic/`; retain its `LICENSE` and `UPSTREAM.md`.

## Usage

From the target project repository root:

```bash
# 1. Audit without project modifications
node <skill-base-dir>/scripts/manage.mjs audit

# 2. Install recommended profile (default)
node <skill-base-dir>/scripts/manage.mjs install --profile recommended

# 3. Install strict profile (when requested)
node <skill-base-dir>/scripts/manage.mjs install --profile strict

# 4. Install with Effect rules (when project uses Effect)
node <skill-base-dir>/scripts/manage.mjs install --profile recommended --with-effect

# 5. Non-destructive update review (dry run)
node <skill-base-dir>/scripts/manage.mjs update

# 6. Apply update with force
node <skill-base-dir>/scripts/manage.mjs update --force --profile recommended

# 7. Safe removal
node <skill-base-dir>/scripts/manage.mjs remove
```

## References

- Detailed profile definitions: [references/profiles.md](references/profiles.md)
- Complete rule documentation & fixes: [references/rules.md](references/rules.md)
- Update workflow & merge doctrine: [references/update.md](references/update.md)
