# The Correct Doctrine: Durable Invariant Enforcement

Durable error elimination doctrine for recurring agent mistakes.
Adapted from [cursor/plugins](https://github.com/cursor/plugins) (`9511e60321f7e533a187d62854a3d53a53752874`, MIT, Lauren Tan) into OpenCodeHighEnd reflection standards.

When operators repeatedly correct agents for the same category of mistake, modifying prompt instructions is insufficient. Restructure the repository so the next agent is mechanically prevented from repeating the error.

---

## 1. Operating Assumption

Assume every future contributor is an agent that:
- Inspects only the files it directly opened,
- Duplicates the nearest visible pattern or code example,
- Takes the shortest path that successfully compiles.

Architect the repository so that a change appearing sound from the vantage of a single file is safe across the entire repository.

---

## 2. Identify Recurring Mistake Classes

Review recent git commits, reverted changes, PR review feedback, agent transcripts, and comments explaining workarounds.
- Group recurring friction into distinct **mistake classes**.
- A pattern qualifies as a mistake class once it has occurred at least twice.

---

## 3. The Five-Level Enforcement Hierarchy

Remediate each mistake class at the highest possible layer in this strict hierarchy:

### Level 1: Eliminate with Architecture
- Assign each piece of state exactly one authoritative owner.
- Establish a single supported mechanism for each core operation.
- Encapsulate subsystem internals so invalid cross-boundary imports fail to compile.
- Remove deprecated patterns, fallback shims, and dead code so the nearest visible example is the canonical implementation.

### Level 2: Make Unrepresentable in Types
- Leverage discriminating unions, branded types, and strict nominal types so illegal states cannot be constructed.
- Replace permissive optional fields with required inputs where defaults cause silent failure.
- Ensure type narrowing rejects ambiguous shapes at compile time.

### Level 3: Static Linting with Actionable Diagnostics
- If type systems cannot express the invariant, author a lint rule (Oxlint, ESLint, Ruff, Clippy, or custom script).
- The lint diagnostic must explicitly state:
  1. What invariant was violated,
  2. The exact remediation to apply,
  3. Why the constraint exists.

### Level 4: Automated Regression Tests
- If static linting cannot detect the pattern, construct a test (unit, integration, or property-based).
- Ensure the test fails when the historical mistake is reintroduced and passes cleanly once corrected.

### Level 5: Documentation & Prompt Rules (Last Resort)
- Guidance in `AGENTS.md`, guidelines, or prompt prose is the weakest layer: agents skip, misinterpret, or forget text under high context pressure.
- Document rules in prose only when mechanical layers (Levels 1–4) are technically impossible.

---

## 4. Prove the Remediation

For every applied structural fix:
1. Reintroduce the historical mistake or replay the failing commit.
2. Run the build, typecheck, lint, or test suite.
3. Confirm that the check fails with a clear, actionable error.
4. Restore the fix and confirm the suite passes cleanly with zero warnings.

---

## 5. Invariant Ledger

Record durable enforcements in the repository's verification or reflection notes:

| Mistake Class | Historical Incident | Enforcement Layer | Mechanical Check |
|---|---|---|---|
| _(class)_ | _(incident)_ | _(level)_ | _(check)_ |

### Enforcement rules (5-level OCH adaptation; upstream pstack combines types and lint into 4 levels)

- If a pattern is already common in the codebase, a test or check should fail only when a change adds more of it — not on pre-existing occurrences.
- Exceptions must be documented at the relevant line with the rationale, an expiration date, and explicit human approval.
- Delete tests that continue passing even when the function under test returns empty or no-op — they provide no enforcement.
- Local commands must match CI commands exactly; drift between local and CI checks invalidates local verification.
- Reflect workflow: always display the proposed modification first; edit only after explicit human approval.
