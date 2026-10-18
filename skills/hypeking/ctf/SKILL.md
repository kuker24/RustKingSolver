---
name: ctf
description: "CTF / lomba competition pack — crypto, reverse, forensics, OSINT, ICS-OT, web-CTF, plus lab harness (API client, artifact fetcher, batch submit, SSTI builder, nonce-recurrence solver). Trigger: ctf, lomba, ctf sandbox, crypto challenge, forensics, stego, osint ctf, reversing, ics challenge, flag, worklist, submit flag, 靶场."
---

# CTF — competition pack

Built from the Redlimit CTV campaign: **120/130 challenges, 10 145 / 11 695 points**.
Everything here is tournament-shaped: many small challenges, one flag oracle,
one worklist, and a clock.

Root: `~/.omp/agent/skills/hypeking/ctf/`

## Route

| Keywords | Pack | Mode |
|---|---|---|
| crypto, rsa, ecdsa, dsa, nonce, aes-gcm, custom base-N, base32 alphabet | `crypto/SKILL.md` | read + run solver |
| reverse, vm, bytecode vm, spn, pyc, apk-less java, anti-debug, prng feedback | `reverse/SKILL.md` | read |
| forensics, stego, zws, zero-width, pcap, tls partial, audio, metadata, disk image | `forensics/SKILL.md` | read |
| osint, geolocation, geo-int, exif gps, social discovery, blockchain, wayback | `osint/SKILL.md` | read + delegate |
| ics, ot, plc, modbus, scada, conveyor, setpoint, ladder | `ics/SKILL.md` | read |
| web ctf, ssti waf, jinja blacklist, pickle, session forge, upload bypass, route enum | `web-ctf/SKILL.md` | read + run builder |
| worklist, submit, ledger, token refresh, fetch artifact, delegate, timebox | `infra/SKILL.md` | run |

Default when the ask only says "CTF" with no category: `infra/SKILL.md` → build the
worklist, then bucket by category and delegate.

## Campaign workflow

1. **Worklist first.** Never solve from memory.
   ```bash
   python3 scripts/api-client.py list --base-url "$CTF_API" --token-file token.json -o worklist.json
   ```
2. **Bucket by category**, then delegate one subagent per category (not per
   challenge). 8 categories → ≤6 parallel subagents.
3. **Fetch artifacts in parallel.** A 3 GB download runs in the background while
   you work local artifacts.
   ```bash
   python3 scripts/fetch-artifact.py '<url>' -o work/challenges/<slug>/
   ```
4. **Solve** with the matching pack. Each pack's SKILL.md is a checklist, not prose.
5. **Submit + ledger.** Never re-submit a solved slug.
   ```bash
   python3 scripts/submit-batch.py flags.tsv --base-url "$CTF_API" --token-file token.json
   ```
6. **Track every unsolved with a written reason.** "Didn't get it" is worthless
   next season; "ZWS block width unknown, 3 models tested" is gold.
7. **Re-check the solved set against the API**, not against your notes.

## Hard rules earned in the field

- **Token lifetime ≠ session lifetime.** Budget for `401 → refresh`. The Redlimit
  JWT died every 15 minutes; the first fix was auto-refresh, not a re-login.
- **Rate-limit in the client.** `MIN_GAP` seconds between calls beats a `429`
  storm. On 429, honour `x-ratelimit-reset` instead of guessing.
- **Delegation unit is the category.** Per-challenge delegation fragments context;
  per-category keeps one solver's whole history in one head.
- **Negatives are the expensive part.** Write the dead-end table (`PickleLoad.md`
  style: 41 probes, each with status) before you abandon a path. It stops the next
  session from re-walking it.
- **Timebox.** Park a hard challenge with a written hypothesis and a saved artifact
  path, then move on. Return only when the clock allows.
- **Generalise on the way out.** Anything you write twice belongs in `scripts/`.

## Reusables (`scripts/`)

| Script | Does |
|---|---|
| `api-client.py` | worklist / detail / submit / profile, token auto-refresh, 429 backoff |
| `fetch-artifact.py` | Drive file + folder (confirm-token), pastes.io, 1drv, direct |
| `submit-batch.py` | slug⇥flag TSV, skip solved, ledger line per submit |
| `ssti-payload.py` | Jinja SSTI builder that dodges a char/word blacklist, with audit |
| `nonce-recurrence.py` | DSA/ECDSA private-key recovery when nonces follow a recurrence |
