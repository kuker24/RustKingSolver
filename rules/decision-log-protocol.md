# Decision-log protocol (managed, not a skill)

Used by `/figure-it-out` and any long unattended run that needs an audit trail. Do **not** invoke `/decision-log` from another manual skill unless the user typed that slash. Path after install:

`~/.omp/agent/rules/decision-log-protocol.md`

## What this is

One append-only TSV of **operational decisions**. Not a dump of hidden reasoning. Never ask the model to reveal chain-of-thought or “think out loud for the log”.

Columns:

| ts | phase | decision | why | evidence | result |
| --- | --- | --- | --- | --- | --- |

- **ts** — ISO8601 UTC
- **phase** — workstream name
- **decision** — what was chosen or done, one line
- **why** — plain reason (constraint, measurement, user call). Not a principle-skill tag.
- **evidence** — pointer only: commit SHA, `file:line`, test name, artifact path, log path, PR number. Mandatory for any completion, milestone, or "done" claim; model judgment without an evidence pointer cannot close a task.
- **result** — outcome category and predicate state:
  - `FACT: <outcome>` — blocking mechanical proof (e.g. `FACT: tests green`, `FACT: exit 0`, `FACT: pixel-diff 0`). Blocking for done-gates.
  - `JUDGMENT: <assessment>` — advisory model evaluation (e.g. `JUDGMENT: visual hierarchy improved`). Advisory only; cannot override failed or missing FACT evidence.
  - Traditional status tokens (`tests green`, `reverted`, `INCONCLUSIVE`, `open`, a measured delta) default to mechanical FACT when supported by evidence.

## Typed-Gate Verification Discipline (Jev/Canny Pattern MERGE)

Absorbed as offline rules without external server dependencies:
- **Assertions ≠ Proof**: Unverified claims in user requests, tickets, or PR descriptions are hypotheses until recorded as a verified `FACT:` row.
- **Missing Facts Halt Progress**: If an essential dependency, test command, or acceptance criterion is missing or ambiguous, halt and record `ask_user` or `investigate` rather than advancing.
- **Bands**: `auto` progression requires explicit mechanical `FACT:` rows and low blast radius; otherwise hold at `review` or stop.

## Where

Default: `decisions.tsv` in the work dir, or `.audit/<task-slug>.tsv`. Leave it uncommitted unless a reviewer needs the trail.

## How to write a row

Prefer `~/.omp/agent/skills/decision-log/scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>` when that skill is installed. The helper:

- writes the header on first use
- strips tabs/newlines
- prefixes cells that start with `=`, `+`, `-`, or `@` with a single quote (spreadsheet formula injection)

## Transcript

If you audit the log against the session, use only the **active** transcript path the system prompt names. Do not glob Claude, Cursor, or OpenCode session transcript directories. If no safe path exists, write a short session digest instead.

## Rules

- One row = one decision or checkpoint.
- Append-only. A wrong call gets a new row.
- Do not log hidden reasoning, scratch thoughts, or every tool call.
