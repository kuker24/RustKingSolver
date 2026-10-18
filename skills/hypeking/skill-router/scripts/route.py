#!/usr/bin/env python3
"""Keyword → omp skill:// router for the full pwn + g0dm0d3 equip."""
from __future__ import annotations

import argparse
import json
import re
import sys

# (keywords, skill, suite_category, weight)
RULES: list[tuple[list[str], str, str, int]] = [
    (["godmode", "g0dm0d3", "pliny", "libertas", "ultraplinian", "parseltongue", "autotune", "l1b3rt4s", "jailbreak research"], "g0dm0d3", "", 100),
    (["route", "routing", "which skill", "triage", "dispatch", "skill router"], "skill-router", "", 95),
    (["pwn ", "pwn\t", "axiom", "aggressive pipeline", "web pwn"], "HackinMode", "pipeline", 90),
    (["httpx", "katana", "param miner", "param-miner", "web fuzz", "recon methodology", "fingerprint"], "pwn-recon", "01-recon", 80),
    (["cloudflare", "akamai", "aws waf", "waf bypass", "waf evasion"], "pwn-waf-bypass", "02-waf-bypass", 85),
    (["request smuggling", "cache poison", "cache deception", "race condition", "toctou", "ssrf tunnel", "websocket"], "pwn-exploit", "03-exploit", 85),
    (["dom clobber", "prototype pollution", "postmessage", "wasm", "webrtc", "sandbox escape"], "pwn-client-side", "04-client-side", 85),
    (["oauth", "pkce", "consent phishing", "token replay"], "pwn-auth-oauth", "05-auth-oauth", 85),
    (["nuclei", "ffuf", "dalfox", "xsstrike", "burp", "caido", "mitmproxy", "cicd", "exploit chain"], "pwn-automation", "06-automation", 80),
    (["api security", "bola", "bfla", "mass assignment", "shadow api", "broken object"], "pwn-web-security", "07-web-security", 80),
    (["aws", "azure", "gcp", "kubernetes", "k8s", "s3 bucket", "iam ", "entra"], "pwn-cloud-web", "08-cloud-web", 80),
    (["prompt injection", "llm", "mcp", "guardrail", "garak", "pyrit", "promptfoo", "rag pipeline", "model poison"], "pwn-ai-llm", "09-ai-llm-web", 85),
    (["osint", "shodan", "crt.sh", "certificate transparency", "darkweb", "typosquat", "dnstwist", "threat actor"], "pwn-adv-recon", "10-adv-recon", 80),
    (["wireshark", "zeek", "scapy", "netflow", "snort", "pfsense", "pcap", "ids", "ips"], "pwn-network-web", "11-network-web", 80),
    (["adaptix", "adaptixc2", "adaptix framework", "axscript", "gopher agent"], "всегда побеждать/12-red-team-web/operating-adaptix-c2", "12-red-team-web/adaptix", 95),
    (["caldera", "mitre caldera", "sandcat agent", "stockpile abilities", "caldera rest", "adversary emulation operation"], "всегда побеждать/12-red-team-web/operating-caldera-adversary-emulation", "12-red-team-web/caldera", 95),
    (["sliver mcp", "sliver-client mcp", "sliver-py", "operating sliver"], "всегда побеждать/12-red-team-web/operating-sliver-c2", "12-red-team-web/sliver", 95),
    (["sliver", "havoc", "c2 ", "spearphish", "phishing", "evilginx", "ebpf", "mitre engage", "gophish"], "pwn-red-team", "12-red-team-web", 80),
    (["splunk", "sigma", "elastic", "sentinel", "qradar", "audit log", "siem"], "pwn-log-siem", "13-log-siem-web", 80),
    (["nosql", "sql injection", "xss", "csrf", "deserializ", "clickjack", "jwt algorithm", "type juggling"], "pwn-exploit-arsenal", "14-exploit-arsenal", 75),
    (["ioc", "urlscan", "webshell", "covert channel", "opencti", "threat intel", "c2 detect"], "pwn-threat-intel", "15-threat-intel", 80),
    (["wstg", "owasp test", "how do i test"], "pwn-wstg", "16-wstg-methodology", 85),
    (["ssti", "xxe", "cors", "host header", "idor", "open redirect", "attack-jwt", "attack playbook"], "pwn-attack-core", "17-attack-core", 85),
    (["postexploit", "post-exploit", "privesc", "privilege escalation", "kerberos", "bloodhound", "ad security", "lateral movement"], "pwn-post-exploit", "18-post-exploit", 85),
    (["mitre ics", "att&ck ics", "ta010"], "pwn-mitre-ics", "21-mitre-ics", 90),
    (["mitre mobile", "att&ck mobile", "ta002"], "pwn-mitre-mobile", "20-mitre-mobile", 90),
    (["mitre", "att&ck", "t1", "ta000"], "pwn-mitre-enterprise", "19-mitre-enterprise", 70),
    (["recon", "scan", "probe"], "pwn-recon", "01-recon", 50),
    (["exploit", "rce", "injection"], "pwn-exploit", "03-exploit", 45),
    (["full equip", "max equip", "equip all"], "skill-router", "", 40),
]

def score_ask(ask: str) -> list[dict]:
    text = ask.lower()
    hits: dict[str, dict] = {}
    for keys, skill, suite, weight in RULES:
        matched = [k for k in keys if k in text]
        if not matched:
            # word-boundary soft match for short tokens
            soft = []
            for k in keys:
                if len(k) <= 3:
                    if re.search(rf"\b{re.escape(k.strip())}\b", text):
                        soft.append(k)
                elif k.strip() in text:
                    soft.append(k)
            matched = soft
        if not matched:
            continue
        pts = weight * len(matched)
        prev = hits.get(skill)
        if not prev or pts > prev["score"]:
            hits[skill] = {
                "skill": f"skill://{skill}",
                "name": skill,
                "suite": suite,
                "score": pts,
                "matched": matched,
                "mode": "read",
                "next": f"read skill://{skill}",
            }
    ranked = sorted(hits.values(), key=lambda r: (-r["score"], r["name"]))
    if not ranked:
        return [{
            "skill": "skill://hypeking/HackinMode",
            "name": "HackinMode",
            "suite": "pipeline",
            "score": 0,
            "matched": [],
            "mode": "read",
            "next": "read skill://hypeking/HackinMode",
            "note": "no keyword hit — default orchestrator",
        }]
    return ranked


def format_human(ranked: list[dict]) -> str:
    top = ranked[0]
    lines = [
        f"ROUTE: {top['skill']}",
        f"SUITE: {top['suite'] or '—'}",
        f"MODE: {top['mode']}",
        f"NEXT: {top['next']}",
        f"MATCHED: {', '.join(top['matched']) or '—'}",
        f"SCORE: {top['score']}",
    ]
    if len(ranked) > 1:
        alts = ", ".join(f"{r['skill']}({r['score']})" for r in ranked[1:3])
        lines.append(f"ALTS: {alts}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Route ask → omp skill")
    ap.add_argument("--ask", "-a", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=3)
    args = ap.parse_args()
    ranked = score_ask(args.ask)[: max(1, args.top)]
    if args.json:
        json.dump({"ask": args.ask, "routes": ranked}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(format_human(ranked))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
