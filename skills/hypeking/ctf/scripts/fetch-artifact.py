#!/usr/bin/env python3
"""CTF artifact fetcher — Drive file/folder, pastes.io, OneDrive/1drv, direct.

Ported and generalised from the Redlimit CTV tooling (get.py): no hardcoded work
directory, no hardcoded 51.79.201.156 host, output directory is yours to choose.

Usage:
  fetch-artifact.py <url> -o OUTDIR [--name NAME] [--force]
  fetch-artifact.py --from-worklist worklist.json --slug <slug> -o OUTDIR

Handles:
  drive.google.com/drive/folders/<id>  -> scrapes file ids, downloads each
  drive.google.com/<file>/d/<id>       -> confirm-token flow for large files
  pastes.io/<id>                       -> extracts the <textarea> payload
  1drv.ms / onedrive.live.com          -> follows @microsoft.graph.downloadUrl
  anything else                        -> direct curl

Exit code 0 if at least one artifact landed.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")


def curl(url: str, out: str, extra: list[str] | None = None, timeout: int = 180) -> bool:
    cmd = ["curl", "-sL", "-m", str(timeout), "-A", UA, "-o", out, url]
    if extra:
        cmd[1:1] = extra
    subprocess.run(cmd, check=False, timeout=timeout + 20)
    return os.path.exists(out) and os.path.getsize(out) > 0


def is_html(p: str) -> bool:
    with open(p, "rb") as f:
        head = f.read(400).lower()
    return b"<html" in head or b"<!doctype" in head


def _read(p: str) -> str:
    with open(p, errors="replace") as f:
        return f.read()


# --------------------------------------------------------------------- google
def drive_file(fid: str, dest: str) -> str:
    """Download a Drive file id, following the confirm-token interstitial."""
    url = f"https://drive.google.com/uc?export=download&id={fid}"
    tmp = dest + ".tmp"
    curl(url, tmp)
    if os.path.exists(tmp) and is_html(tmp):
        page = _read(tmp)
        m = re.search(r'name="confirm" value="([^"]+)"', page)
        form = re.search(r'action="([^"]+)"', page)
        if m:
            u2 = html.unescape(form.group(1)) if form else url
            curl(f"{u2}&confirm={m.group(1)}", tmp, timeout=900)
    if os.path.exists(tmp):
        os.replace(tmp, dest)
    return dest


def drive_folder(fid: str, destdir: str) -> list[str]:
    os.makedirs(destdir, exist_ok=True)
    tmp = os.path.join(destdir, "_folder.html")
    if not curl(f"https://drive.google.com/drive/folders/{fid}", tmp):
        return []
    page = _read(tmp)
    ids, seen = [], set()
    for m in re.finditer(r'"([A-Za-z0-9_-]{25,44})"', page):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            ids.append(m.group(1))
    print(f"folder {fid}: {len(ids)} candidate ids", file=sys.stderr)
    got = []
    for i, x in enumerate(ids):
        p = os.path.join(destdir, f"{fid}_{i:02d}_{x[:8]}")
        drive_file(x, p)
        if os.path.exists(p) and not is_html(p) and os.path.getsize(p) > 0:
            got.append(p)
        elif os.path.exists(p):
            os.remove(p)
    return got


# ---------------------------------------------------------------------- misc
def pastes(pid: str, dest: str) -> str:
    curl(f"https://pastes.io/{pid}", dest)
    if os.path.exists(dest) and is_html(dest):
        m = re.search(r"<textarea[^>]*>(.*?)</textarea>", _read(dest), re.S)
        if m:
            out = dest + ".txt"
            with open(out, "w") as f:
                f.write(html.unescape(m.group(1)))
            return out
    return dest


def onedrive(url: str, dest: str) -> str:
    curl(url, dest)
    if os.path.exists(dest) and is_html(dest):
        m = re.search(r'"@microsoft\.graph\.downloadUrl"\s*:\s*"([^"]+)"', _read(dest))
        if m:
            curl(m.group(1).replace("\\u0026", "&"), dest)
    return dest


# ------------------------------------------------------------------- dispatch
def fetch(url: str, destdir: str, name: str | None = None) -> tuple[list[str], str]:
    os.makedirs(destdir, exist_ok=True)
    dest = os.path.join(destdir, name or "artifact.bin")

    if "drive.google.com/drive/folders" in url:
        fid = url.split("/folders/")[1].split("?")[0].split("/")[0]
        return drive_folder(fid, destdir), "drive-folder"
    if "drive.google.com" in url:
        m = re.search(r"/d/([A-Za-z0-9_-]+)", url)
        fid = m.group(1) if m else url.split("id=")[-1].split("&")[0]
        return [drive_file(fid, dest)], "drive-file"
    if "pastes.io" in url:
        return [pastes(url.rstrip("/").split("/")[-1], os.path.join(destdir, "paste.html"))], "pastes.io"
    if "1drv.ms" in url or "onedrive.live.com" in url:
        return [onedrive(url, dest)], "onedrive"

    curl(url, dest)
    return [dest], "direct"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", nargs="?")
    p.add_argument("-o", "--out", default=".")
    p.add_argument("--name")
    p.add_argument("--force", action="store_true", help="re-download even if the file exists")
    p.add_argument("--from-worklist", help="read the url from a worklist.json by slug")
    p.add_argument("--slug")
    a = p.parse_args(argv)

    url = a.url
    if a.from_worklist:
        if not a.slug:
            p.error("--from-worklist needs --slug")
        wl = json.load(open(a.from_worklist))
        c = next((x for x in wl if x.get("slug") == a.slug), None)
        if not c:
            p.error(f"slug {a.slug!r} not in worklist")
        url = c.get("download_url") or c.get("access_url") or ""
        a.out = a.out if a.out != "." else os.path.join("work", a.slug)
    if not url:
        p.error("no url (and worklist had none for that slug)")

    if not a.force:
        existing = [f for f in (os.listdir(a.out) if os.path.isdir(a.out) else [])
                    if os.path.getsize(os.path.join(a.out, f)) > 0]
        if existing and os.path.isdir(a.out):
            print(f"SKIP {a.out} already has {len(existing)} file(s); --force to redo")
            return 0

    got, kind = fetch(url, a.out, a.name)
    print(f"{kind}\t{a.out}")
    for g in got:
        if g and os.path.exists(g):
            print(f"   {os.path.getsize(g):>12} {g}")
    return 0 if any(g and os.path.exists(g) for g in got) else 1


if __name__ == "__main__":
    raise SystemExit(main())
