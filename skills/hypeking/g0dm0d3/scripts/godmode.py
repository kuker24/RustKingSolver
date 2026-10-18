#!/usr/bin/env python3
"""Apply G0DM0D3 Hall-of-Fame combos — inject {QUERY} into system/user templates."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "references"

COMBOS = [
    {
        "id": "sonnet-35",
        "codename": "CLAUDE SONNET 4.6",
        "model": "anthropic/claude-sonnet-4.6",
        "description": "END/START boundary inversion with GODMODE semantic opposite response",
        "fast": False,
    },
    {
        "id": "grok-reset",
        "codename": "GROK 4.5",
        "model": "x-ai/grok-4.5",
        "description": "Unfiltered liberated response with GODMODE divider and rebel output",
        "fast": False,
    },
    {
        "id": "gemini-reset",
        "codename": "GEMINI 2.5 FLASH",
        "model": "google/gemini-2.5-flash",
        "description": "Pliny Love divider — refusal inversion + rebel genius code block output",
        "fast": False,
    },
    {
        "id": "gpt-classic",
        "codename": "GPT-4 CLASSIC",
        "model": "openai/gpt-4o",
        "description": "The original GODMODE — refusal + divider + l33t rebel response",
        "fast": False,
    },
    {
        "id": "hermes-fast",
        "codename": "GODMODE FAST",
        "model": "nousresearch/hermes-4-405b",
        "description": "Hermes 4 405B — instant token stream, zero refusal checking",
        "fast": True,
    },
]


def load_combo(combo_id: str, query: str) -> dict:
    meta = next(c for c in COMBOS if c["id"] == combo_id)
    system = (REFS / f"{combo_id}.system.txt").read_text(encoding="utf-8")
    user = (REFS / f"{combo_id}.user.txt").read_text(encoding="utf-8")
    # templates store literal \n escapes in sonnet; normalize
    system = system.replace("\\n", "\n")
    system = system.replace("{QUERY}", query)
    user = user.replace("{QUERY}", query)
    return {**meta, "system": system, "user": user}


def main() -> int:
    ap = argparse.ArgumentParser(description="GODMODE Hall-of-Fame combo applicator")
    ap.add_argument("--query", "-q", default=None)
    ap.add_argument("--combo", choices=[c["id"] for c in COMBOS], default="gpt-classic")
    ap.add_argument("--race", action="store_true", help="emit all combos")
    ap.add_argument("--exclude-fast", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.list:
        rows = [{k: c[k] for k in ("id", "codename", "model", "description", "fast")} for c in COMBOS]
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if not args.query:
        ap.error("--query/-q is required unless --list")

    ids = [c["id"] for c in COMBOS] if args.race else [args.combo]
    if args.exclude_fast:
        ids = [i for i in ids if not next(c for c in COMBOS if c["id"] == i)["fast"]]

    packs = [load_combo(i, args.query) for i in ids]
    if args.json or args.race:
        json.dump(packs if args.race else packs[0], sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        p = packs[0]
        print(f"# {p['codename']} · {p['model']} · {p['id']}")
        print("---SYSTEM---")
        print(p["system"])
        print("---USER---")
        print(p["user"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
