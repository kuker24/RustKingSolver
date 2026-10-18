#!/usr/bin/env python3
"""Encoding escalation ladder from G0DM0D3 Hall-of-Fame retry path."""
from __future__ import annotations

import argparse
import json
import sys

CIRCLED = "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"
NEG_CIRCLED = "🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩"
BRAILLE = {
    "a": "⠁", "b": "⠃", "c": "⠉", "d": "⠙", "e": "⠑", "f": "⠋", "g": "⠛",
    "h": "⠓", "i": "⠊", "j": "⠚", "k": "⠅", "l": "⠇", "m": "⠍", "n": "⠝",
    "o": "⠕", "p": "⠏", "q": "⠟", "r": "⠗", "s": "⠎", "t": "⠞", "u": "⠥",
    "v": "⠧", "w": "⠺", "x": "⠭", "y": "⠽", "z": "⠵", " ": "⠀",
    "1": "⠂", "2": "⠆", "3": "⠒", "4": "⠲", "5": "⠢", "6": "⠖", "7": "⠶",
    "8": "⠦", "9": "⠔", "0": "⠴", ".": "⠨", ",": "⠠", "?": "⠹", "!": "⠮",
    "-": "⠤", "/": "⠌", "(": "⠷", ")": "⠾", ":": "⠱", ";": "⠰", "'": "⠄", '"': "⠐",
}
MORSE = {
    "a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.",
    "g": "--.", "h": "....", "i": "..", "j": ".---", "k": "-.-", "l": ".-..",
    "m": "--", "n": "-.", "o": "---", "p": ".--.", "q": "--.-", "r": ".-.",
    "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-",
    "y": "-.--", "z": "--..", "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----.", " ": "/", ".": ".-.-.-", ",": "--..--",
    "?": "..--..", "!": "-.-.--", "-": "-....-", "/": "-..-.", "(": "-.--.",
    ")": "-.--.-", ":": "---...", ";": "-.-.-.", "'": ".----.", '"': ".-..-.",
}
LEET = {
    "a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7", "l": "1",
    "g": "9", "b": "8", "A": "4", "E": "3", "I": "1", "O": "0", "S": "5",
    "T": "7", "L": "1", "G": "9", "B": "8",
}


def to_bubble(text: str) -> str:
    out = []
    toggle = 0
    for ch in text:
        idx = ord(ch.lower()) - 97
        if 0 <= idx < 26:
            out.append(CIRCLED[idx] if toggle % 2 == 0 else NEG_CIRCLED[idx])
            toggle += 1
        else:
            out.append(ch)
    return "".join(out)


def to_braille(text: str) -> str:
    return "".join(BRAILLE.get(ch.lower(), ch) for ch in text)


def to_leetspeak(text: str) -> str:
    return "".join(LEET.get(ch, ch) for ch in text)


def to_morse(text: str) -> str:
    return " ".join(MORSE.get(ch.lower(), ch) for ch in text)


ENCODE = {
    "plain": lambda q: q,
    "leetspeak": to_leetspeak,
    "bubble": to_bubble,
    "braille": to_braille,
    "morse": to_morse,
}
ORDER = ["plain", "leetspeak", "bubble", "braille", "morse"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Encoding escalation")
    ap.add_argument("--text", "-t", required=True)
    ap.add_argument("--mode", choices=ORDER, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.all or args.mode is None:
        rows = {name: ENCODE[name](args.text) for name in ORDER}
    else:
        rows = {args.mode: ENCODE[args.mode](args.text)}
    if args.json:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        for k, v in rows.items():
            print(f"[{k}] {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
