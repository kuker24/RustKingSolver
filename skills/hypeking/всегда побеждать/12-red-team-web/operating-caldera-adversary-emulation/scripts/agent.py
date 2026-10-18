#!/usr/bin/env python3
"""Caldera REST helper for authorized adversary-emulation labs.

Talks to Apache Caldera API v2 (basic auth). Does not start the server.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from base64 import b64encode
from typing import Any


def _auth_header(user: str, password: str) -> str:
    token = b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {token}"


def api(
    base: str,
    path: str,
    user: str,
    password: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> Any:
    url = base.rstrip("/") + path
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": _auth_header(user, password),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise SystemExit(f"HTTP {e.code} {path}: {detail}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"connect failed: {e}") from e


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default="http://127.0.0.1:8888")
    p.add_argument("--user", default="red")
    p.add_argument("--password", required=True)
    p.add_argument("--list-agents", action="store_true")
    p.add_argument("--list-adversaries", action="store_true")
    p.add_argument("--list-operations", action="store_true")
    p.add_argument("--list-abilities", action="store_true")
    p.add_argument("--adversary", help="adversary UUID")
    p.add_argument("--name", default="lab-operation")
    p.add_argument("--group", default="red")
    p.add_argument("--planner", default="aaa7c857-37a0-4b4c-b699-11b1dd0e8b6b",
                   help="planner UUID (atomic default may vary by install)")
    p.add_argument("--start-operation", action="store_true")
    p.add_argument("--get-operation", metavar="OP_ID")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    out: Any = None
    if args.list_agents:
        out = api(args.base, "/api/v2/agents", args.user, args.password)
    elif args.list_adversaries:
        out = api(args.base, "/api/v2/adversaries", args.user, args.password)
    elif args.list_operations:
        out = api(args.base, "/api/v2/operations", args.user, args.password)
    elif args.list_abilities:
        out = api(args.base, "/api/v2/abilities", args.user, args.password)
    elif args.get_operation:
        out = api(args.base, f"/api/v2/operations/{args.get_operation}", args.user, args.password)
    elif args.start_operation:
        if not args.adversary:
            raise SystemExit("--adversary UUID required with --start-operation")
        body = {
            "name": args.name,
            "adversary": {"adversary_id": args.adversary},
            "planner": {"id": args.planner},
            "group": args.group,
            "state": "running",
            "auto_close": False,
            "visibility": 50,
        }
        out = api(args.base, "/api/v2/operations", args.user, args.password, method="POST", body=body)
    else:
        p.print_help()
        return 2

    if args.json or not isinstance(out, list):
        print(json.dumps(out, indent=2, default=str))
    else:
        for item in out:
            if isinstance(item, dict):
                key = item.get("name") or item.get("paw") or item.get("ability_id") or item.get("adversary_id")
                print(f"{key}\t{item.get('adversary_id') or item.get('id') or item.get('paw') or ''}")
            else:
                print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
