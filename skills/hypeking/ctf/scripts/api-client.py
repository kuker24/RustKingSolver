#!/usr/bin/env python3
"""CTF lab API client — chrome UA, client-side rate limit, 401 auto-refresh, 429 backoff.

Ported and generalised from the Redlimit CTV campaign tooling (rlx.py):
no hardcoded host, no hardcoded token path, no hardcoded ledger path.

Usage:
  api-client.py list    --base-url URL --token-file token.json [-o worklist.json]
  api-client.py detail  --base-url URL --token-file token.json <slug>
  api-client.py submit  --base-url URL --token-file token.json <slug> <flag>
  api-client.py solved  --base-url URL --token-file token.json
  api-client.py profile --base-url URL --token-file token.json <user>

Env fallbacks: CTF_API, CTF_TOKEN_FILE, CTF_MIN_GAP
Token file shape: {"token": "...", "refreshToken": "..."}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")


class Client:
    """Rate-limited, token-refreshing client for a CTF lab API."""

    def __init__(self, base_url: str, token_file: str | None = None,
                 min_gap: float = 1.5, refresh_path: str = "/auth/refresh",
                 challenges_path: str = "/challenges", timeout: int = 45):
        self.base = base_url.rstrip("/")
        self.token_file = token_file
        self.min_gap = float(min_gap)
        self.refresh_path = refresh_path
        self.challenges_path = challenges_path
        self.timeout = timeout
        self._last = 0.0

    # ------------------------------------------------------------------ token
    def _read_token_file(self) -> dict:
        if not self.token_file:
            raise SystemExit("no --token-file and no CTF_TOKEN_FILE set")
        with open(self.token_file) as f:
            return json.load(f)

    def token(self) -> str:
        if not self.token_file:
            tok = os.environ.get("CTF_TOKEN")
            if not tok:
                raise SystemExit("no token: pass --token-file or set CTF_TOKEN")
            return tok
        return self._read_token_file()["token"]

    def refresh(self) -> str:
        """Exchange refreshToken for a new token; persist. Returns the new token."""
        d = self._read_token_file()
        body = {"refreshToken": d["refreshToken"]}
        req = urllib.request.Request(
            self.base + self.refresh_path, data=json.dumps(body).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", UA)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            out = json.loads(r.read() or b"{}")
        d["token"] = out["token"]
        if out.get("refreshToken"):
            d["refreshToken"] = out["refreshToken"]
        with open(self.token_file, "w") as f:
            json.dump(d, f)
        sys.stderr.write("[token] refreshed\n")
        return d["token"]

    # ------------------------------------------------------------------- call
    def _throttle(self, gap: float | None = None) -> None:
        g = self.min_gap if gap is None else float(gap)
        wait = g - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()

    def api(self, path: str, method: str = "GET", body=None, gap: float | None = None,
            retries: int = 6):
        """Return (status, parsed_body). Handles 429 wait and 401 refresh."""
        for attempt in range(retries):
            self._throttle(gap)
            data = json.dumps(body).encode() if body is not None else None
            req = urllib.request.Request(self.base + path, data=data, method=method)
            req.add_header("Authorization", "Bearer " + self.token())
            req.add_header("User-Agent", UA)
            if data:
                req.add_header("Content-Type", "application/json")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read()
                    return r.status, (json.loads(raw) if raw else None)
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    rst = e.headers.get("x-ratelimit-reset") or e.headers.get("ratelimit-reset")
                    delay = 65
                    if rst and rst.isdigit():
                        delay = max(5, int(rst) - int(time.time()) + 3)
                    sys.stderr.write(f"[429] sleeping {delay}s\n")
                    time.sleep(delay)
                    continue
                if e.code == 401 and attempt < retries - 1 and self.token_file:
                    self.refresh()
                    continue
                raw = e.read()
                try:
                    return e.code, json.loads(raw)
                except Exception:
                    return e.code, {"raw": raw[:400].decode("utf-8", "replace")}
            except urllib.error.URLError as ex:
                if attempt == retries - 1:
                    raise
                sys.stderr.write(f"[net] {ex}; retry in 4s\n")
                time.sleep(4)
        return 0, {"error": "retries exhausted"}

    # -------------------------------------------------------------- shortcuts
    def challenges(self):
        return self.api(self.challenges_path)[1]

    def detail(self, slug: str):
        d = self.api(f"{self.challenges_path}/{slug}")[1]
        return d.get("data", d) if isinstance(d, dict) else d

    def submit(self, slug_or_id: str, flag: str):
        return self.api(f"{self.challenges_path}/{slug_or_id}/submit", "POST",
                        {"flag": flag}, gap=max(2.0, self.min_gap))

    def solved_set(self):
        return {c["slug"] for c in (self.challenges() or []) if c.get("solved")}


def append_ledger(path: str, slug: str, flag: str, points, status) -> None:
    """One line per submission: slug, flag, points, status, iso-timestamp."""
    with open(path, "a") as f:
        f.write(f"{slug}\t{flag}\t{points}\t{status}\t"
                f"{datetime.now(timezone.utc).isoformat()}\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["list", "detail", "submit", "solved", "profile"])
    p.add_argument("arg", nargs="?")
    p.add_argument("flag", nargs="?")
    p.add_argument("--base-url", default=os.environ.get("CTF_API"))
    p.add_argument("--token-file", default=os.environ.get("CTF_TOKEN_FILE"))
    p.add_argument("--min-gap", type=float, default=float(os.environ.get("CTF_MIN_GAP", 1.5)))
    p.add_argument("--challenges-path", default="/challenges")
    p.add_argument("--refresh-path", default="/auth/refresh")
    p.add_argument("-o", "--out", default="worklist.json")
    p.add_argument("--ledger", default="flags.tsv")
    a = p.parse_args(argv)

    if not a.base_url:
        p.error("--base-url (or CTF_API) is required")
    c = Client(a.base_url, a.token_file, a.min_gap, a.refresh_path, a.challenges_path)

    if a.cmd == "list":
        cs = c.challenges() or []
        with open(a.out, "w") as f:
            json.dump(cs, f, indent=2)
        print(f"{len(cs)} challenges, {sum(1 for x in cs if x.get('solved'))} solved -> {a.out}")
    elif a.cmd == "detail":
        print(json.dumps(c.detail(a.arg), indent=2))
    elif a.cmd == "solved":
        print("\n".join(sorted(c.solved_set())))
    elif a.cmd == "profile":
        print(json.dumps(c.api("/users/" + a.arg)[1], indent=2))
    elif a.cmd == "submit":
        st, body = c.submit(a.arg, a.flag)
        ok = isinstance(body, dict) and body.get("success")
        points = body.get("points") if isinstance(body, dict) else None
        append_ledger(a.ledger, a.arg, a.flag, points, "OK" if ok else st)
        print(f"{'OK' if ok else 'FAIL'} {st} {json.dumps(body)[:200]}")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
