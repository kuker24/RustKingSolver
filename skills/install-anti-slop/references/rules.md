# Anti-Slop Rule Fixes & Principles

Guidelines for addressing Anti-Slop linter findings correctly without compromising code quality.

## Correct Fixing Principles

1. **Address Root Causes**:
   - Use TypeScript type inference rather than manual widening.
   - Validate input boundaries with parsers (Zod, ArkType, Schema) instead of type assertions.
   - Use `satisfies` to validate types without widening object literals.
2. **Never Cheat the Linter**:
   - DO NOT replace `unknown` with `any`.
   - DO NOT add extra casts to circumvent checks.
   - DO NOT invent generic or copy-pasted `// SAFETY: safe` comments without real reasoning.
   - DO NOT delete valid regression tests to silence `no-module-mocking`.
   - DO NOT weaken public API signatures without assessing breaking impact.

## Generic Rule Summaries

- **`no-array-filter-map`**: `arr.filter(predicate).map(fn)` -> Use a single-pass combination (e.g. `flatMap` or loop), or iterator helpers `.values().filter().map().toArray()` only when the runtime environment supports ECMAScript iterator helpers.
- **`no-chained-type-assertions`**: `x as object as User` -> Validate input at boundary with schema.
- **`no-conditional-empty-object-spread`**: `...(cond ? { a } : {})` -> Assign conditionally or assemble object imperatively.
- **`no-known-value-widening`**: `const m: Record<string, T> = { k: v }` -> Use `satisfies Record<string, T>`.
- **`no-module-mocking`**: `vi.mock("./store")` -> Inject test doubles through constructor/function parameters.
- **`no-object-parameters`**: `function f(opts: object)` -> Define explicit interface or type alias for parameters.
- **`no-reduce-accumulator-copy`**: `arr.reduce((acc, x) => ({ ...acc, [x.id]: x }), {})` -> Mutate accumulator in-place `acc[x.id] = x; return acc;` or use `Object.fromEntries` to avoid O(n^2) shallow cloning.
- **`no-reflect-apply`**: `Reflect.apply(fn, ctx, args)` -> Call function directly or via `fn.apply(ctx, args)`.
- **`no-reflect-get`**: `Reflect.get(obj, key)` -> Access properties directly with bracket or dot notation.
- **`no-runtime-typeof`**: `typeof x === "string"` -> Use schema parsing or tagged unions rather than raw typeof.
- **`no-shape-in-symbol-names`**: Naming symbols with shape words (e.g. `IUser`, `UserType`) -> Use canonical domain names.
- **`no-unknown-parameters`**: `function f(x: unknown)` -> Constrain parameter types with generics or schemas.
- **`no-unknown-returns`**: `function f(): unknown` -> Return concrete types or discriminated unions.
- **`no-unknown-type-aliases`**: `type T = unknown` -> Define concrete or branded types.
- **`no-unsafe-dictionary-type`**: `Record<string, any>` -> Use typed key/value pairs or schema boundaries.
- **`no-widen-then-assert`**: `const x: unknown = val; (x as Target)` -> Preserve variable's original static type.
- **`require-readable-spacing`**: Enforces readable newline padding between logical statement blocks (adapted from `eslint-stylistic/padding-line-between-statements`).
- **`require-safety-comment-for-type-assertion`**: Add `// SAFETY: <justification why invariant holds>`.

## Effect Rule Summaries

- **`no-manual-effect-error-tag`**: `class MyError { readonly _tag = "MyError"; }` -> Use `Data.TaggedError("MyError")`.
- **`no-manual-tag-comparison`**: `if (val._tag === "SomeTag")` -> Use `Match.tag` or `Predicate.isTagged` from Effect.
- **`no-manual-tagged-construction`**: `{ _tag: "Right", right: value }` -> Use constructor functions like `Either.right(value)`.
- **`no-service-constructor-imports`**: Named `make<Capability>` imports -> Import the owning Layer and yield the contextual service.
- **`prefer-effect-match`**: Nested ternary or switch on `_tag` -> Use `Match.type<T>().pipe(Match.tag(...), Match.exhaustive)`.
