#!/usr/bin/env python3
"""AdaptixC2 lab helper — path/status checks + docker compose hints.

Does not speak a native Adaptix API (GUI/AxScript primary). Use for install
verification and compose lifecycle in authorized labs.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path(os.path.expanduser("~/tools/AdaptixC2"))


def run(cmd: list[str], cwd: Path | None = None) -> dict:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        return {"cmd": cmd, "code": p.returncode, "stdout": p.stdout[-4000:], "stderr": p.stderr[-2000:]}
    except FileNotFoundError as e:
        return {"cmd": cmd, "error": str(e)}
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "error": "timeout"}


def status(root: Path) -> dict:
    return {
        "root": str(root),
        "exists": root.is_dir(),
        "docker_compose": (root / "docker-compose.yml").is_file(),
        "makefile": (root / "Makefile").is_file(),
        "pre_install": (root / "pre_install_linux_all.sh").is_file(),
        "docker": shutil.which("docker"),
        "go": shutil.which("go"),
        "git": shutil.which("git"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--clone", action="store_true", help="git clone shallow into --root")
    ap.add_argument("--compose-up", action="store_true")
    ap.add_argument("--compose-down", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results: dict = {}
    if args.clone:
        if args.root.exists():
            results["clone"] = {"skipped": True, "reason": "root exists"}
        else:
            args.root.parent.mkdir(parents=True, exist_ok=True)
            results["clone"] = run(
                ["git", "clone", "--depth", "1", "https://github.com/Adaptix-Framework/AdaptixC2.git", str(args.root)]
            )
    if args.compose_up:
        results["compose_up"] = run(["docker", "compose", "up", "-d"], cwd=args.root)
    if args.compose_down:
        results["compose_down"] = run(["docker", "compose", "down"], cwd=args.root)
    if args.status or not results:
        results["status"] = status(args.root)

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
