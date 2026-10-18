#!/usr/bin/env python3
"""Parseltongue — input obfuscation engine (port of G0DM0D3 src/lib/parseltongue.ts)."""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from typing import Callable

DEFAULT_TRIGGERS = [
    "hack", "exploit", "bypass", "crack", "break", "attack", "penetrate",
    "inject", "manipulate", "override", "disable", "circumvent", "evade",
    "malware", "virus", "trojan", "payload", "shellcode", "rootkit",
    "keylogger", "backdoor", "vulnerability",
    "weapon", "bomb", "explosive", "poison", "drug", "synthesize",
    "jailbreak", "unlock", "root", "sudo", "admin", "privilege",
    "phishing", "scam", "impersonate", "deceive", "fraud",
    "nsfw", "explicit", "uncensored", "unfiltered", "unrestricted",
    "ignore", "disregard", "forget", "pretend", "roleplay",
    "character", "act as", "you are now", "new identity",
]

LEET_MAP = {
    "a": ["4", "@", "∂", "λ"], "b": ["8", "|3", "ß", "13"],
    "c": ["(", "<", "¢", "©"], "d": [")", "|>", "đ"],
    "e": ["3", "€", "£", "∑"], "f": ["|=", "ƒ", "ph"],
    "g": ["9", "6", "&"], "h": ["#", "|-|", "}{"],
    "i": ["1", "!", "|", "¡"], "j": ["_|", "]", "¿"],
    "k": ["|<", "|{", "κ"], "l": ["1", "|", "£", "|_"],
    "m": ["|V|", "/\\/\\", "µ"], "n": ["|\\|", "/\\/", "η"],
    "o": ["0", "()", "°", "ø"], "p": ["|*", "|>", "þ"],
    "q": ["0_", "()_", "ℚ"], "r": ["|2", "®", "12"],
    "s": ["5", "$", "§", "∫"], "t": ["7", "+", "†", "⊤"],
    "u": ["|_|", "µ", "ü"], "v": ["\\/", "√"],
    "w": ["\\/\\/", "vv", "ω"], "x": ["><", "×", "}{"],
    "y": ["`/", "¥", "γ"], "z": ["2", "7_", "ℤ"],
}

UNICODE_HOMOGLYPHS = {
    "a": ["а", "ɑ", "α", "ａ"], "b": ["Ь", "ｂ", "ḅ"],
    "c": ["с", "ϲ", "ⅽ", "ｃ"], "d": ["ԁ", "ⅾ", "ｄ"],
    "e": ["е", "ė", "ẹ", "ｅ"], "f": ["ƒ", "ｆ"],
    "g": ["ɡ", "ｇ"], "h": ["һ", "ḥ", "ｈ"],
    "i": ["і", "ι", "ｉ"], "j": ["ϳ", "ｊ"],
    "k": ["κ", "ｋ"], "l": ["ӏ", "ⅼ", "ｌ"],
    "m": ["м", "ｍ"], "n": ["ո", "ｎ"],
    "o": ["о", "ο", "ｏ"], "p": ["р", "ρ", "ｐ"],
    "s": ["ѕ", "ｓ"], "t": ["τ", "ｔ"],
    "u": ["υ", "ｕ"], "v": ["ν", "ｖ"],
    "w": ["ѡ", "ｗ"], "x": ["х", "ｘ"],
    "y": ["у", "γ", "ｙ"], "z": ["ᴢ", "ｚ"],
}

ZW_CHARS = ["\u200B", "\u200C", "\u200D", "\uFEFF"]
Intensity = str  # light|medium|heavy


def _indices(n: int, count: int, predicate) -> list[int]:
    out: list[int] = []
    step = max(1, n // max(count, 1))
    for i in range(0, n):
        if len(out) >= count:
            break
        if i % step == 0 and predicate(i):
            out.append(i)
    if len(out) < count:
        for i in range(n):
            if len(out) >= count:
                break
            if i not in out and predicate(i):
                out.append(i)
    return out


def apply_leetspeak(word: str, intensity: Intensity) -> str:
    chars = list(word)
    count = 1 if intensity == "light" else (len(chars) + 1) // 2 if intensity == "medium" else len(chars)
    idxs = _indices(len(chars), count, lambda i: chars[i].lower() in LEET_MAP)
    for i in idxs:
        opts = LEET_MAP[chars[i].lower()]
        chars[i] = random.choice(opts)
    return "".join(chars)


def apply_unicode(word: str, intensity: Intensity) -> str:
    chars = list(word)
    count = 1 if intensity == "light" else (len(chars) + 1) // 2 if intensity == "medium" else len(chars)
    idxs = _indices(len(chars), count, lambda i: chars[i].lower() in UNICODE_HOMOGLYPHS)
    for i in idxs:
        opts = UNICODE_HOMOGLYPHS[chars[i].lower()]
        rep = random.choice(opts)
        chars[i] = rep.upper() if chars[i].isupper() else rep
    return "".join(chars)


def apply_zwj(word: str, intensity: Intensity) -> str:
    chars = list(word)
    insert_count = 1 if intensity == "light" else (len(chars) + 1) // 2 if intensity == "medium" else max(0, len(chars) - 1)
    out: list[str] = []
    inserted = 0
    for i, ch in enumerate(chars):
        out.append(ch)
        if i < len(chars) - 1 and inserted < insert_count:
            out.append(random.choice(ZW_CHARS))
            inserted += 1
    return "".join(out)


def apply_mixedcase(word: str, intensity: Intensity) -> str:
    chars = list(word)
    if not chars:
        return word
    if intensity == "light":
        i = random.randrange(len(chars))
        chars[i] = chars[i].upper()
    elif intensity == "medium":
        for i, ch in enumerate(chars):
            chars[i] = ch.lower() if i % 2 == 0 else ch.upper()
    else:
        for i, ch in enumerate(chars):
            chars[i] = ch.upper() if random.random() > 0.5 else ch.lower()
    return "".join(chars)


def apply_phonetic(word: str) -> str:
    subs = [
        (re.compile(r"ph", re.I), "f"),
        (re.compile(r"ck", re.I), "k"),
        (re.compile(r"x", re.I), "ks"),
        (re.compile(r"qu", re.I), "kw"),
        (re.compile(r"c(?=[eiy])", re.I), "s"),
        (re.compile(r"c", re.I), "k"),
    ]
    out = word
    for pat, rep in subs:
        out = pat.sub(rep, out)
    return out


def apply_random(word: str, intensity: Intensity) -> str:
    fn = random.choice([apply_leetspeak, apply_unicode, apply_zwj, apply_mixedcase])
    return fn(word, intensity)


TECHNIQUES: dict[str, Callable[..., str]] = {
    "leetspeak": apply_leetspeak,
    "unicode": apply_unicode,
    "zwj": apply_zwj,
    "mixedcase": apply_mixedcase,
    "phonetic": lambda w, _i: apply_phonetic(w),
    "random": apply_random,
}


def detect_triggers(text: str, custom: list[str] | None = None) -> list[str]:
    all_tr = list(DEFAULT_TRIGGERS) + (custom or [])
    found: list[str] = []
    lower = text.lower()
    for t in all_tr:
        pat = re.compile(rf"\b{re.escape(t)}\b", re.I)
        if pat.search(lower):
            found.append(t)
    # preserve order, unique
    seen = set()
    out = []
    for t in found:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def apply_parseltongue(
    text: str,
    technique: str = "leetspeak",
    intensity: Intensity = "medium",
    custom_triggers: list[str] | None = None,
    enabled: bool = True,
) -> dict:
    if not enabled:
        return {
            "originalText": text,
            "transformedText": text,
            "triggersFound": [],
            "techniqueUsed": technique,
            "transformations": [],
        }
    triggers = detect_triggers(text, custom_triggers)
    if not triggers:
        return {
            "originalText": text,
            "transformedText": text,
            "triggersFound": [],
            "techniqueUsed": technique,
            "transformations": [],
        }
    fn = TECHNIQUES[technique]
    transformed = text
    transformations = []
    for trigger in sorted(triggers, key=len, reverse=True):
        pat = re.compile(rf"\b({re.escape(trigger)})\b", re.I)

        def repl(m, _fn=fn, _intensity=intensity):
            orig = m.group(1)
            new = _fn(orig, _intensity)
            transformations.append({"original": orig, "transformed": new, "technique": technique})
            return new

        transformed = pat.sub(repl, transformed)
    return {
        "originalText": text,
        "transformedText": transformed,
        "triggersFound": triggers,
        "techniqueUsed": technique,
        "transformations": transformations,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Parseltongue input obfuscation")
    ap.add_argument("--text", "-t", required=True)
    ap.add_argument("--technique", choices=list(TECHNIQUES), default="leetspeak")
    ap.add_argument("--intensity", choices=["light", "medium", "heavy"], default="medium")
    ap.add_argument("--trigger", action="append", default=[], help="extra trigger word")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    result = apply_parseltongue(args.text, args.technique, args.intensity, args.trigger)
    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(result["transformedText"])
        if result["triggersFound"]:
            print(f"# triggers: {', '.join(result['triggersFound'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
