# Prose discipline (UNSLOP-LITE, managed, Read on demand)

Read this file when editing user-facing prose or when `humanizer` / `/unslop` / `/technical-writing` says to. Do not `@`-import it. Path after install:

`~/.omp/agent/rules/03-prose-discipline.md`

This is not a skill. It does not auto-apply. It does not rewrite code.

- Cut filler (“in order to”, “it is important to note”, “in today’s landscape”).
- Cut sycophancy (“Great question!”, “You’re absolutely right”).
- Cut empty hedging that hides the claim. Keep real uncertainty.
- Prefer concrete facts, numbers, names, and mechanisms over atmosphere.
- Prefer active voice when the actor matters.
- Name the source. No “experts believe”.
- Preserve legitimate technical terms (`interface`, `vector`, `primitive`, `surface`, `modality`) when they are the real word.
- Preserve facts: names, dates, numbers, URLs, citations, code, commands, flags, API ids, quotes, negations, security and legal wording.
- Cut words that do no work.
- Cut kickoff slop and AI promotional clichés (“Let’s dive in”, “Supercharge your workflow”, “In this fast-paced world”, “Unleash the power of”).
- Cut fake social proof: never author synthetic testimonials, fabricated reviews, or unverified star ratings.
- Cut fabricated metrics and uncited statistics: never invent precise percentages, multipliers, or benchmark numbers.
- Cut beta-pill voice and sparkle-CTA fluff: do not decorate action buttons with sparkles, emoji flair, or artificial status pills.
- Never “polish” source code, tests, or command output as if they were marketing copy.
- If the user says "wait what" or asks to re-pitch: stop, provide concise context, speak in ASD-STE100 Simplified Technical English, and use the ubiquitous domain language from `GLOSSARY.md`.
- When the human prompt/direction itself contains slop patterns or cliches, name the specific elements and the rule they trigger, explain why it degrades quality, and ask for confirmation before implementing.
- Distinguish intentional brand voice or artistic contrast from accidental generative slop; never unilaterally rewrite user direction without asking.

For full prose rewrites and systematic AI-tell removal, use the `humanizer` specialist (manual slash alias: `/unslop`).
