#!/usr/bin/env python3
"""Batch flag submitter — slug<TAB>flag TSV, skips already-solved, writes a ledger.

Ported and generalised from the Redlimit CTV tooling (batch.py + rlx.py).

Usage:
  submit-batch.py flags.tsv --base-url URL --token-file token.json
  submit-batch.py - --base-url URL --token-file token.json < pairs.tsv

TSV format (blank lines and # comments ignored):
  strings-attached<TAB>REDLIMIT{...}

Options:
  --ledger PATH   append a line per accepted submit (default flags.tsv)
  --solved PATH   progress.json whose "solved" list is honoured (skip re-submits)
  --dry-run       print what would be submitted
  --gap SECONDS   client-side minimum gap between submits (default 2.0)

Env fallbacks: CTF_API, CTF_TOKEN_FILE
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load_client():
    """Load sibling api-client.py (hyphenated filename => importlib)."""
    spec = importlib.util.spec_from_file_location("ctf_api_client",
                                                 os.path.join(HERE, "api-client.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_pairs(path: str):
    rows = []
    src = sys.stdin if path == "-" else open(path)
    try:
        for line in src:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                print(f"[skip] malformed line: {line!r}", file=sys.stderr)
                continue
            rows.append((parts[0].strip(), parts[1].strip()))
    finally:
        if src is not sys.stdin:
            src.close()
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tsv", help="TSV file of slug<TAB>flag, or - for stdin")
    p.add_argument("--base-url", default=os.environ.get("CTF_API"))
    p.add_argument("--token-file", default=os.environ.get("CTF_TOKEN_FILE"))
    p.add_argument("--challenges-path", default="/challenges")
    p.add_argument("--ledger", default="flags.tsv")
    p.add_argument("--solved", help="progress.json (or worklist.json) with solved slugs to skip")
    p.add_argument("--gap", type=float, default=2.0)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)

    if not a.base_url:
        p.error("--base-url (or CTF_API) is required")

    api = _load_client()
    rows = _read_pairs(a.tsv)

    skip = set()
    if a.solved and os.path.exists(a.solved):
        d = json.load(open(a.solved))
        if isinstance(d, dict) and "solved" in d:
            skip = set(d["solved"])
        elif isinstance(d, list):
            skip = {x.get("slug") for x in d if x.get("solved")}

    if a.dry_run:
        for slug, flag in rows:
            print(f"{'SKIP(solved)' if slug in skip else 'WOULD SUBMIT':14} {slug}")
        return 0

    c = api.Client(a.base_url, a.token_file, min_gap=a.gap,
                   challenges_path=a.challenges_path)
    ok = fail = 0
    for slug, flag in rows:
        if slug in skip:
            print(f"SKIP(solved) {slug}")
            continue
        st, body = c.submit(slug, flag)
        good = isinstance(body, dict) and body.get("success")
        points = body.get("points") if isinstance(body, dict) else None
        print(f"{'OK  ' if good else 'FAIL'} {slug:32s} {st} {json.dumps(body)[:120]}")
        api.append_ledger(a.ledger, slug, flag, points, "OK" if good else st)
        ok += good
        fail += (not good)
    print(f"\n{ok} accepted, {fail} rejected")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
