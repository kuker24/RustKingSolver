#!/usr/bin/env python3
"""AutoTune — context-adaptive sampling (port of G0DM0D3 src/lib/autotune.ts)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

STRATEGY_PROFILES = {
    "precise": dict(temperature=0.2, top_p=0.85, top_k=30, frequency_penalty=0.3, presence_penalty=0.1, repetition_penalty=1.1),
    "balanced": dict(temperature=0.7, top_p=0.9, top_k=50, frequency_penalty=0.1, presence_penalty=0.1, repetition_penalty=1.0),
    "creative": dict(temperature=1.1, top_p=0.95, top_k=80, frequency_penalty=0.4, presence_penalty=0.6, repetition_penalty=1.15),
    "chaotic": dict(temperature=1.6, top_p=0.98, top_k=100, frequency_penalty=0.7, presence_penalty=0.8, repetition_penalty=1.25),
}

CONTEXT_PROFILE_MAP = {
    "code": dict(temperature=0.15, top_p=0.8, top_k=25, frequency_penalty=0.2, presence_penalty=0.0, repetition_penalty=1.05),
    "creative": dict(temperature=1.15, top_p=0.95, top_k=85, frequency_penalty=0.5, presence_penalty=0.7, repetition_penalty=1.2),
    "analytical": dict(temperature=0.4, top_p=0.88, top_k=40, frequency_penalty=0.2, presence_penalty=0.15, repetition_penalty=1.08),
    "conversational": dict(temperature=0.75, top_p=0.9, top_k=50, frequency_penalty=0.1, presence_penalty=0.1, repetition_penalty=1.0),
    "chaotic": dict(temperature=1.7, top_p=0.99, top_k=100, frequency_penalty=0.8, presence_penalty=0.9, repetition_penalty=1.3),
}

CONTEXT_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "code": [
        re.compile(r"\b(code|function|class|variable|bug|error|debug|compile|syntax|api|endpoint|regex|algorithm|refactor|typescript|javascript|python|rust|html|css|sql|json|xml|import|export|return|async|await|promise|interface|type|const|let|var)\b", re.I),
        re.compile(r"```[\s\S]*```"),
        re.compile(r"\b(fix|implement|write|create|build|deploy|test|unit test|lint|npm|pip|cargo|git)\b.{0,200}\b(code|function|app|service|component|module)\b", re.I | re.S),
        re.compile(r"[{}();=><]"),
        re.compile(r"\b(stack overflow|github|repo|pull request|commit|merge)\b", re.I),
    ],
    "creative": [
        re.compile(r"\b(write|story|poem|creative|imagine|fiction|narrative|character|plot|scene|dialogue|metaphor|lyrics|song|artistic|fantasy|dream|inspire|muse|prose|verse|haiku)\b", re.I),
        re.compile(r"\b(describe|paint|envision|portray|illustrate|craft)\b.{0,200}\b(world|scene|character|feeling|emotion|atmosphere)\b", re.I | re.S),
        re.compile(r"\b(roleplay|role-play|pretend|act as|you are a)\b", re.I),
        re.compile(r"\b(brainstorm|ideate|come up with|think of|generate ideas)\b", re.I),
    ],
    "analytical": [
        re.compile(r"\b(analyze|analysis|compare|contrast|evaluate|assess|examine|investigate|research|study|review|critique|breakdown|data|statistics|metrics|benchmark|measure)\b", re.I),
        re.compile(r"\b(pros and cons|advantages|disadvantages|trade-?offs|implications|consequences)\b", re.I),
        re.compile(r"\b(why|how does|what causes|explain|elaborate|clarify|define|summarize|overview)\b", re.I),
        re.compile(r"\b(report|document|technical|specification|architecture|diagram|whitepaper)\b", re.I),
    ],
    "conversational": [
        re.compile(r"\b(hey|hi|hello|sup|what's up|how are you|thanks|thank you|cool|nice|awesome|great|lol|haha)\b", re.I),
        re.compile(r"\b(chat|talk|tell me about|what do you think|opinion|feel|believe)\b", re.I),
        re.compile(r"^.{0,30}$"),
    ],
    "chaotic": [
        re.compile(r"\b(chaos|random|wild|crazy|absurd|surreal|glitch|corrupt|break|destroy|unleash|madness|void|entropy)\b", re.I),
        re.compile(r"\b(gl1tch|h4ck|pwn|1337|l33t)\b", re.I),
        re.compile(r"(!{3,}|\?{3,}|\.{4,})"),
    ],
}


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def apply_bounds(params: dict[str, float]) -> dict[str, float]:
    return {
        "temperature": clamp(params["temperature"], 0.0, 2.0),
        "top_p": clamp(params["top_p"], 0.0, 1.0),
        "top_k": int(clamp(round(params["top_k"]), 1, 100)),
        "frequency_penalty": clamp(params["frequency_penalty"], -2.0, 2.0),
        "presence_penalty": clamp(params["presence_penalty"], -2.0, 2.0),
        "repetition_penalty": clamp(params["repetition_penalty"], 0.0, 2.0),
    }


def detect_context(message: str, history: list[str] | None = None) -> dict[str, Any]:
    scores = {k: 0 for k in CONTEXT_PATTERNS}
    matches: list[dict[str, str]] = []
    for ctx, patterns in CONTEXT_PATTERNS.items():
        for pat in patterns:
            if pat.search(message):
                scores[ctx] += 3
                matches.append({"pattern": f"{ctx}:{pat.pattern[:40]}", "source": "current"})
    for msg in (history or [])[-4:]:
        for ctx, patterns in CONTEXT_PATTERNS.items():
            for pat in patterns:
                if pat.search(msg):
                    scores[ctx] += 1
    total = sum(scores.values())
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    if total == 0:
        return {
            "type": "conversational",
            "confidence": 0.5,
            "allScores": [{"type": k, "score": 1 if k == "conversational" else 0, "percentage": 100 if k == "conversational" else 0} for k, _ in ranked],
            "patternMatches": matches or [{"pattern": "DEFAULT", "source": "current"}],
        }
    best = ranked[0][0]
    all_scores = [
        {"type": k, "score": s, "percentage": round((s / total) * 100)}
        for k, s in ranked
    ]
    return {
        "type": best,
        "confidence": min(ranked[0][1] / total, 1.0),
        "allScores": all_scores,
        "patternMatches": matches,
    }


def compute(strategy: str, message: str, history: list[str] | None = None) -> dict[str, Any]:
    if strategy != "adaptive":
        params = apply_bounds(dict(STRATEGY_PROFILES[strategy]))
        return {
            "params": params,
            "detectedContext": None,
            "confidence": 1.0,
            "reasoning": f"Strategy: {strategy.upper()} | Fixed profile applied",
            "contextScores": [],
            "patternMatches": [],
            "baselineParams": dict(STRATEGY_PROFILES[strategy]),
        }
    det = detect_context(message, history)
    params = apply_bounds(dict(CONTEXT_PROFILE_MAP[det["type"]]))
    if history and len(history) > 10:
        params["repetition_penalty"] = clamp(params["repetition_penalty"] + 0.05, 0.0, 2.0)
    return {
        "params": params,
        "detectedContext": det["type"],
        "confidence": det["confidence"],
        "reasoning": f"Detected: {det['type']} ({round(det['confidence']*100)}% confidence)",
        "contextScores": det["allScores"],
        "patternMatches": det["patternMatches"],
        "baselineParams": dict(STRATEGY_PROFILES["balanced"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="AutoTune sampling params")
    ap.add_argument("--message", "-m", required=True)
    ap.add_argument("--strategy", choices=["precise", "balanced", "creative", "chaotic", "adaptive"], default="adaptive")
    ap.add_argument("--history", action="append", default=[], help="prior message (repeatable)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = compute(args.strategy, args.message, args.history)
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        p = result["params"]
        print(f"context={result['detectedContext']} confidence={result['confidence']:.2f}")
        print(f"temperature={p['temperature']} top_p={p['top_p']} top_k={p['top_k']} "
              f"frequency_penalty={p['frequency_penalty']} presence_penalty={p['presence_penalty']} "
              f"repetition_penalty={p['repetition_penalty']}")
        print(result["reasoning"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
