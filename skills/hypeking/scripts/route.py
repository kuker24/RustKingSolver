#!/usr/bin/env python3
"""HYPEKING auto-router — keyword → nested pack under skills/hypeking/."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HYPEKING = Path(__file__).resolve().parent.parent

# (keywords, nested_relpath, suite_category, weight)
RULES: list[tuple[list[str], str, str, int]] = [
    (["godmode", "g0dm0d3", "pliny", "libertas", "ultraplinian", "parseltongue", "autotune", "l1b3rt4s", "jailbreak research"], "g0dm0d3/SKILL.md", "", 100),
    (["route", "routing", "which skill", "triage", "dispatch", "skill router"], "SKILL.md", "", 95),
    (["pwn ", "pwn\t", "axiom", "aggressive pipeline", "web pwn"], "HackinMode/SKILL.md", "pipeline", 90),
    (["api recon", "api-recon", "frontend api", "spa harvest", "webpack chunk", "vite manifest", "xhr harvest", "fetch stub", "param samples", "runtime_harvest", "preload.js", "shadow endpoint discovery", "route map extract"], "pwn-api-recon/SKILL.md", "01-recon/api-recon", 95),
    (["scopesentry", "scope sentry", "ssk_", "list_assets", "create_scan_task", "scan template", "asset sync"], "scopesentry/SKILL.md", "", 95),
    (["playwright-cli", "playwright cli", "playwright mcp", "@playwright/mcp", "browser snapshot", "request mocking", "storage state", "playwright tracing"], "playwright-cli/SKILL.md", "", 90),
    # reverse-skill gap packs (mobile / binary / js crypto / ctf / firmware / forensics)
    (["apk", "jadx", "apktool", "smali", "frida", "repack apk"], "reverse-skill/apk-reverse/SKILL.md", "reverse/apk", 95),
    (["ipa", "ios reverse", "objection", "mobsf", "ssl pinning", "jailbreak bypass"], "reverse-skill/mobile-reverse/SKILL.md", "reverse/mobile", 95),
    (["js reverse", "jshook", "前端加密", "签名算法", "sourcemap", "js crypto", "补环境"], "reverse-skill/js-reverse/SKILL.md", "reverse/js", 95),
    (["ida ", "ida pro", "ida mcp", "hex-rays"], "reverse-skill/ida-reverse/SKILL.md", "reverse/ida", 95),
    (["ghidra", "ghidra mcp", "headless analyze"], "reverse-skill/ghidra-reverse/SKILL.md", "reverse/ghidra", 95),
    (["radare2", "rizin", "rabin2", "rasm2"], "reverse-skill/radare2/SKILL.md", "reverse/r2", 95),
    (["binary ninja", "binja", "hlil", "mlil"], "reverse-skill/binary-ninja-reverse/SKILL.md", "reverse/binja", 95),
    (["go binary", "rust binary", "pclntab", "stripped go"], "reverse-skill/go-rust-reverse/SKILL.md", "reverse/go-rust", 90),
    (["dnspy", "de4dot", "confuserex", ".net reverse", "clr assembly"], "reverse-skill/dotnet-reverse/SKILL.md", "reverse/dotnet", 90),
    (["protobuf", "grpc", "custom protocol", "protocol reverse", "pcap protocol"], "reverse-skill/protocol-reverse/SKILL.md", "reverse/protocol", 90),
    (["firmware", "binwalk", "emba", "iot firmware"], "reverse-skill/firmware-pentest/SKILL.md", "reverse/firmware", 90),
    (["memory dump", "volatility", "forensic timeline", "digital forensics", "ir evidence"], "reverse-skill/digital-forensics/SKILL.md", "reverse/forensics", 90),
    (["rop chain", "heap exploit", "binary pwn", "pwn-chain", "ret2libc"], "reverse-skill/pwn-chain/SKILL.md", "reverse/pwn-chain", 90),
    (["malware", "yara rule", "sandbox detonation", "ioc extract"], "reverse-skill/malware-analysis/SKILL.md", "reverse/malware", 90),
    (["chrome extension", "firefox addon", "browser extension reverse"], "reverse-skill/browser-extension-reverse/SKILL.md", "reverse/extension", 85),
    (["adcs", "ntlm relay", "kerberoast", "windows ad", "bloodhound path"], "reverse-skill/windows-ad/SKILL.md", "reverse/windows-ad", 90),
    (["ctf", "awd", "靶场", "competition challenge"], "reverse-skill/ctf-sandbox/SKILL.md", "reverse/ctf", 95),
    (["thick client", "desktop ipc", "electron reverse"], "reverse-skill/thick-client/SKILL.md", "reverse/thick", 85),
    (["uart", "jtag", "secure boot", "hardware debug"], "reverse-skill/hardware-security/SKILL.md", "reverse/hw", 85),
    (["ollvm", "anti-debug", "unpack", "dsl vm", "reverse engineering"], "reverse-skill/reverse-engineering/SKILL.md", "reverse/general", 80),
    (["burp mcp", "burpmcp"], "reverse-skill/burp-mcp/README.md", "reverse/burp-mcp", 85),
    (["reverse-skill", "pwn-reverse", "binary reverse", "native reverse"], "pwn-reverse/SKILL.md", "reverse", 70),
    (["httpx", "katana", "param miner", "param-miner", "web fuzz", "recon methodology", "fingerprint"], "pwn-recon/SKILL.md", "01-recon", 80),
    (["cloudflare", "akamai", "aws waf", "waf bypass", "waf evasion"], "pwn-waf-bypass/SKILL.md", "02-waf-bypass", 85),
    (["request smuggling", "cache poison", "cache deception", "race condition", "toctou", "ssrf tunnel", "websocket"], "pwn-exploit/SKILL.md", "03-exploit", 85),
    (["dom clobber", "prototype pollution", "postmessage", "wasm", "webrtc", "sandbox escape"], "pwn-client-side/SKILL.md", "04-client-side", 85),
    (["oauth", "pkce", "consent phishing", "token replay"], "pwn-auth-oauth/SKILL.md", "05-auth-oauth", 85),
    (["nuclei", "ffuf", "dalfox", "xsstrike", "burp", "caido", "mitmproxy", "cicd", "exploit chain"], "pwn-automation/SKILL.md", "06-automation", 80),
    (["api security", "bola", "bfla", "mass assignment", "shadow api", "broken object"], "pwn-web-security/SKILL.md", "07-web-security", 80),
    (["aws", "azure", "gcp", "kubernetes", "k8s", "s3 bucket", "iam ", "entra"], "pwn-cloud-web/SKILL.md", "08-cloud-web", 80),
    (["prompt injection", "llm", "mcp", "guardrail", "garak", "pyrit", "promptfoo", "rag pipeline", "model poison"], "pwn-ai-llm/SKILL.md", "09-ai-llm-web", 85),
    (["osint", "shodan", "crt.sh", "certificate transparency", "darkweb", "typosquat", "dnstwist", "threat actor"], "pwn-adv-recon/SKILL.md", "10-adv-recon", 80),
    (["wireshark", "zeek", "scapy", "netflow", "snort", "pfsense", "pcap", "ids", "ips"], "pwn-network-web/SKILL.md", "11-network-web", 80),
    (["adaptix", "adaptixc2", "adaptix framework", "axscript", "gopher agent"], "всегда побеждать/12-red-team-web/operating-adaptix-c2/SKILL.md", "12-red-team-web/adaptix", 95),
    (["caldera", "mitre caldera", "sandcat agent", "stockpile abilities", "caldera rest", "adversary emulation operation"], "всегда побеждать/12-red-team-web/operating-caldera-adversary-emulation/SKILL.md", "12-red-team-web/caldera", 95),
    (["sliver mcp", "sliver-client mcp", "sliver-py", "operating sliver"], "всегда побеждать/12-red-team-web/operating-sliver-c2/SKILL.md", "12-red-team-web/sliver", 95),
    (["sliver", "havoc", "c2 ", "spearphish", "phishing", "evilginx", "ebpf", "mitre engage", "gophish"], "pwn-red-team/SKILL.md", "12-red-team-web", 80),
    (["splunk", "sigma", "elastic", "sentinel", "qradar", "audit log", "siem"], "pwn-log-siem/SKILL.md", "13-log-siem-web", 80),
    (["nosql", "sql injection", "xss", "csrf", "deserializ", "clickjack", "jwt algorithm", "type juggling"], "pwn-exploit-arsenal/SKILL.md", "14-exploit-arsenal", 75),
    (["ioc", "urlscan", "webshell", "covert channel", "opencti", "threat intel", "c2 detect"], "pwn-threat-intel/SKILL.md", "15-threat-intel", 80),
    (["wstg", "owasp test", "how do i test"], "pwn-wstg/SKILL.md", "16-wstg-methodology", 85),
    (["ssti", "xxe", "cors", "host header", "idor", "open redirect", "attack-jwt", "attack playbook"], "pwn-attack-core/SKILL.md", "17-attack-core", 85),
    (["postexploit", "post-exploit", "privesc", "privilege escalation", "kerberos", "bloodhound", "ad security", "lateral movement"], "pwn-post-exploit/SKILL.md", "18-post-exploit", 85),
    (["mitre ics", "att&ck ics", "ta010"], "pwn-mitre-ics/SKILL.md", "21-mitre-ics", 90),
    (["mitre mobile", "att&ck mobile", "ta002"], "pwn-mitre-mobile/SKILL.md", "20-mitre-mobile", 90),
    (["mitre", "att&ck", "t1", "ta000"], "pwn-mitre-enterprise/SKILL.md", "19-mitre-enterprise", 70),
    (["recon", "scan", "probe"], "pwn-recon/SKILL.md", "01-recon", 50),
    (["exploit", "rce", "injection"], "pwn-exploit/SKILL.md", "03-exploit", 45),
    (["full equip", "max equip", "equip all", "artex", "reverse-skill"], "SKILL.md", "", 40),
]


def score_ask(ask: str) -> list[dict]:
    text = ask.lower()
    hits: dict[str, dict] = {}
    for keys, nested, suite, weight in RULES:
        matched = [k for k in keys if k in text]
        if not matched:
            soft = []
            for k in keys:
                if len(k.strip()) <= 3:
                    if re.search(rf"\b{re.escape(k.strip())}\b", text):
                        soft.append(k)
                elif k.strip() in text:
                    soft.append(k)
            matched = soft
        if not matched:
            continue
        pts = weight * len(matched)
        key = nested
        prev = hits.get(key)
        if not prev or pts > prev["score"]:
            uri = f"skill://hypeking/{nested}"
            abs_path = str(HYPEKING / nested)
            hits[key] = {
                "skill": "skill://hypeking",
                "route": uri,
                "nested": nested,
                "path": abs_path,
                "suite": suite,
                "score": pts,
                "matched": matched,
                "mode": "read",
                "next": f"read {uri}",
            }
    ranked = sorted(hits.values(), key=lambda r: (-r["score"], r["nested"]))
    if not ranked:
        nested = "HackinMode/SKILL.md"
        return [{
            "skill": "skill://hypeking",
            "route": f"skill://hypeking/{nested}",
            "nested": nested,
            "path": str(HYPEKING / nested),
            "suite": "pipeline",
            "score": 0,
            "matched": [],
            "mode": "read",
            "next": f"read skill://hypeking/{nested}",
            "note": "no keyword hit — default HackinMode",
        }]
    return ranked


def format_human(ranked: list[dict]) -> str:
    top = ranked[0]
    lines = [
        f"ROUTE: {top['route']}",
        f"SUITE: {top['suite'] or '—'}",
        f"MODE: {top['mode']}",
        f"NEXT: {top['next']}",
        f"MATCHED: {', '.join(top['matched']) or '—'}",
        f"SCORE: {top['score']}",
        f"PATH: {top['path']}",
    ]
    if len(ranked) > 1:
        alts = ", ".join(f"{r['route']}({r['score']})" for r in ranked[1:3])
        lines.append(f"ALTS: {alts}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="HYPEKING auto-router")
    ap.add_argument("--ask", "-a", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=3)
    args = ap.parse_args()
    ranked = score_ask(args.ask)[: max(1, args.top)]
    if args.json:
        json.dump({"ask": args.ask, "hypeking": str(HYPEKING), "routes": ranked}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(format_human(ranked))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
