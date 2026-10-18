# Anti-Slop Profiles Guide

## 1. Recommended Profile (OCBF Default)

The recommended profile enables high-signal rules that catch artificial type evidence bypassing without obstructing legitimate software patterns:

- `anti-slop/no-chained-type-assertions`: `"error"`
  Rejects chained `as object as Target` or `<Target><object>x` assertions that fabricate evidence. Chains of `as const` remain valid.
- `anti-slop/no-widen-then-assert`: `"error"`
  Rejects local flows where a known type is widened to `unknown`/`any`/`object` and later re-asserted.
- `anti-slop/no-known-value-widening`: `"warn"` (audit first; upgrade to error after baseline is clean)
  Catches known values explicitly typed as generic `Record<string, unknown>` or `unknown`.
- `anti-slop/require-safety-comment-for-type-assertion`: `"warn"`
  Flags unadorned type assertions that lack a `// SAFETY: <justification>` explanation.

### Excluded from Recommended Default
These rules are reserved for the `strict` or `custom` profiles:
- `no-array-filter-map`: Stylistic/performance preference for iterator helper pipelines; can be overly opinionated on legacy array pipelines.
- `no-module-mocking`: Too disruptive for existing test suites that legitimately mock external SDKs/transports.
- `no-reduce-accumulator-copy`: Paired with native `oxc/no-accumulating-spread`; reserved for strict audit of O(n^2) accumulator spreads.
- `no-runtime-typeof`: `typeof` is valid in projects without schema decoding libraries.
- `no-shape-in-symbol-names`: Pure naming convention, not a type-correctness proof.
- `no-conditional-empty-object-spread`: Depends on object exact-optional semantics.
- `no-object-parameters`, `no-unknown-*`, `no-unsafe-dictionary-type`: Too broad as universal standards.
- `no-reflect-get`, `no-reflect-apply`: Useful only where project policy specifically forbids Reflect metaprogramming.
- `require-readable-spacing`: Whitespace padding rule adapted from eslint-stylistic; reserved for strict profile to avoid conflicting with existing formatters (Prettier, Biome).

---

## 2. Strict Profile

Enables all 18 generic upstream rules as `"error"` plus native companion `"oxc/no-accumulating-spread"`:
- `anti-slop/no-array-filter-map`: `"error"`
- `anti-slop/no-chained-type-assertions`: `"error"`
- `anti-slop/no-conditional-empty-object-spread`: `"error"`
- `anti-slop/no-known-value-widening`: `"error"`
- `anti-slop/no-module-mocking`: `"error"`
- `anti-slop/no-object-parameters`: `"error"`
- `anti-slop/no-reduce-accumulator-copy`: `"error"`
- `anti-slop/no-reflect-apply`: `"error"`
- `anti-slop/no-reflect-get`: `"error"`
- `anti-slop/no-runtime-typeof`: `"error"`
- `anti-slop/no-shape-in-symbol-names`: `"error"`
- `anti-slop/no-unknown-parameters`: `"error"`
- `anti-slop/no-unknown-returns`: `"error"`
- `anti-slop/no-unknown-type-aliases`: `"error"`
- `anti-slop/no-unsafe-dictionary-type`: `"error"`
- `anti-slop/no-widen-then-assert`: `"error"`
- `anti-slop/require-readable-spacing`: `"error"`
- `anti-slop/require-safety-comment-for-type-assertion`: `"error"`
- `oxc/no-accumulating-spread`: `"error"`

---

## 3. Effect Rule Group (Opt-In)

Enables Effect-specific architectural discipline:
- `anti-slop-effect/no-manual-effect-error-tag`: `"error"`
  Rejects manual `_tag` property assignment on error classes; use `Data.TaggedError` instead.
- `anti-slop-effect/no-manual-tag-comparison`: `"error"`
  Rejects direct `_tag === "..."` comparisons; use `Match.tag` or `Predicate.isTagged` instead.
- `anti-slop-effect/no-manual-tagged-construction`: `"error"`
  Rejects manual construction of tagged objects; use constructors like `Either.right(...)` instead.
- `anti-slop-effect/no-service-constructor-imports`: `"error"`
  Rejects named `make<CapabilityName>` imports from project modules outside tests. Callers must import the owning Layer and yield the contextual service.
- `anti-slop-effect/prefer-effect-match`: `"error"`
  Prefers `Match.type<T>().pipe(...)` over nested ternary or switch statements on `_tag`.
