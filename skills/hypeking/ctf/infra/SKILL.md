---
name: ctf-infra
description: "CTF lab infrastructure — build the worklist, API client with token refresh and rate limiting, artifact fetching, batch flag submission with ledger, per-category subagent delegation, timeboxing and progress tracking. Trigger: ctf worklist, submit flag, flag oracle, rate limit, token refresh, fetch artifact, delegate category, timebox, progress tracking, ledger."
---

# CTF infra — worklist, submit, delegate

The harness that made 130 challenges survivable. Read this first when a CTF starts.

## 1. Worklist

```bash
export CTF_API="https://<host>/api"
python3 ~/.omp/agent/skills/hypeking/ctf/scripts/api-client.py list \
    --base-url "$CTF_API" --token-file token.json -o worklist.json
python3 - <<'PY'
import json, collections
wl=json.load(open('worklist.json'))
c=collections.Counter(x.get('category') for x in wl)
print(dict(c))
print("unsolved:", [x['slug'] for x in wl if not x.get('solved')])
PY
```

Token shape is usually `token.json` = `{"token": "...", "refreshToken": "..."}`.
The client refreshes on `401` automatically. **Budget for refresh, not re-login.**

## 2. Rate limiting

`api-client.py` enforces a client-side gap (default 1.5 s, 2.0 s for submit) and
honours `x-ratelimit-reset` on 429. Do not flood — one 429 window costs more than
the entire challenge.

## 3. Submit + ledger

Every submit writes a ledger line: `slug \t flag \t points \t iso-timestamp`.
Never re-submit a solved slug.

```bash
python3 scripts/submit-batch.py flags.tsv --base-url "$CTF_API" --token-file token.json
```

TSV format, one per line, `#` comments allowed:

```
strings-attached	REDLIMIT{...}
rota	REDLIMIT{...}
```

## 4. Per-category delegation

**Delegation unit = category.** Never one subagent per challenge.

| Subagent | Owns |
|---|---|
| `SubCrypto` | all crypto |
| `SubReverse` | all reverse |
| `SubForensics` | all forensics |
| `SubOsint*` | one OSINT **chain** each (bird-lovers, pace, …) |
| `SubWeb` | all web |
| `SubIcs` | all ICS/OT |

Each subagent gets: the full challenge descriptions (never the truncated list), the
artifact paths already fetched, and the expected flag format. It returns a
`*.md` report + the flag.

CTV ran subagents named exactly like this and kept the main thread free to work the
port-series itself.

## 5. Artifacts

```bash
python3 scripts/fetch-artifact.py '<drive|pastes.io|1drv|direct url>' -o work/<slug>/
```

Handles: Drive file (with `confirm` token), Drive **folder** (scrapes file ids),
`pastes.io` (`<textarea>` extract), OneDrive/`1drv.ms` (`graph.downloadUrl`),
direct hosts. Multi-GB transfers: run in the background, poll size, never block.

## 6. Timebox + parking

Park a hard challenge with:
- a written hypothesis,
- the artifact path,
- the negative table so far.

Then move on. A parked challenge with a hypothesis is worth more than an hour of
silent brute force.

## 7. Progress file

Keep `progress.json` = `{"solved": [...], "unsolved": {...}, "unsolved_reason": {...}}`.
Update it on every result. On resume, re-check against the API — memory drifts,
the oracle does not.

## Output contract

```
WORKLIST: <n> challenges, <k> solved, by category
DELEGATED: <category → subagent>
SUBMITTED: <slug → OK|FAIL>
PARKED: <slug → hypothesis>
```
