#!/usr/bin/env python3
"""
nuclei-custom-templates agent.py
MITRE ATT&CK: T1595 (Active Scanning)
Generates and tests custom nuclei YAML templates against targets.
"""
import argparse
import json
import os
import signal
import subprocess
import tempfile
from datetime import datetime
import requests
from colorama import Fore, Style, init
init(autoreset=True)
SHOULD_EXIT = False


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down gracefully...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

RATE_FLAGS = {
    "quiet": ["-rl", "10", "-c", "2"],
    "moderate": ["-rl", "25", "-c", "5"],
    "loud": ["-rl", "50", "-c", "10"],
}


def _rate_flags(profile="moderate"):
    return RATE_FLAGS.get(profile, RATE_FLAGS["moderate"])


VULN_TEMPLATES = {
    "xss": {"p": "/{{param}}=<script>alert(1)</script>", "w": ["<script>alert(1)</script>"], "b": "body", "s": "medium", "d": "Reflected XSS"},
    "sqli": {"p": "/{{param}}=' OR '1'='1", "w": ["SQL syntax", "mysql_fetch", "ORA-", "Unclosed quotation"], "b": "body", "s": "critical", "d": "SQL injection"},
    "lfi": {"p": "/{{param}}=../../../etc/passwd", "w": ["root:x:0:0:", "daemon:x:1:1:"], "b": "body", "s": "high", "d": "Local file inclusion"},
    "rce": {"p": "/{{param}}=;id", "w": ["uid=", "gid=", "www-data"], "b": "body", "s": "critical", "d": "Remote command execution"},
    "redirect": {"p": "/{{param}}=https://evil.com/test", "w": ["https://evil.com/test"], "b": "location", "s": "medium", "d": "Open redirect"},
}


def generate_yaml(vuln_type, param):
    t = VULN_TEMPLATES.get(vuln_type)
    if not t:
        raise ValueError(f"Unknown type: {vuln_type}")
    path = t["p"].replace("{{param}}", param)
    template = {
        "id": f"nuclei-custom-{datetime.now():%Y%m%d%H%M%S}",
        "info": {"name": t["d"], "author": "agent", "severity": t["s"], "description": t["d"]},
        "requests": [{"method": "GET", "path": [path], "matchers": [{"type": "word", "words": t["w"], "part": t["b"]}]}],
    }
    return json.dumps(template, indent=2)


def run_nuclei(template_content, target, profile="moderate"):
    fd, tmp_path = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w") as f:
        f.write(template_content)
    results = []
    try:
        print(f"{Fore.CYAN}[*] Running nuclei against {target}{Style.RESET_ALL}")
        proc = subprocess.run(
            ["nuclei", "-target", target, "-t", tmp_path, "-json", "-silent"] + _rate_flags(profile),
            capture_output=True, text=True, timeout=60,
        )
        for line in proc.stdout.strip().splitlines():
            if not line.strip():
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                results.append({"raw": line})
        if proc.returncode != 0 and proc.stderr:
            for line in proc.stderr.strip().splitlines():
                if line.strip():
                    print(f"{Fore.RED}[!] {line}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] nuclei binary not found. Running simulated scan.{Style.RESET_ALL}")
        results = simulate_scan(template_content, target)
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}[!] nuclei timed out after 60s{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
    finally:
        os.unlink(tmp_path)
    return results


def simulate_scan(template_content, target):
    print(f"{Fore.YELLOW}[*] Simulating template scan (nuclei not found){Style.RESET_ALL}")
    results = []
    try:
        parsed = json.loads(template_content)
        req = parsed["requests"][0]
        path = req["path"][0]
        url = target.rstrip("/") + "/" + path.lstrip("/")
        resp = requests.get(url, timeout=10, verify=False, allow_redirects=True)
        matched = False
        matched_words = []
        for matcher in req.get("matchers", []):
            if matcher["type"] != "word":
                continue
            part = matcher.get("part", "body")
            body = resp.text if part == "body" else resp.headers.get("Location", "")
            for word in matcher["words"]:
                if word.lower() in body.lower():
                    matched = True
                    matched_words.append(word)
        results.append({
            "template-id": parsed["id"],
            "type": parsed["info"].get("severity", "unknown"),
            "url": url,
            "status-code": resp.status_code,
            "matched": matched,
            "matched-words": matched_words,
            "simulated": True,
        })
        if matched:
            print(f"{Fore.GREEN}[+] Match found: {matched_words}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[-] No match (status {resp.status_code}){Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Request failed: {e}{Style.RESET_ALL}")
    return results


def display_results(results):
    if not results:
        print(f"{Fore.YELLOW}[*] No results returned{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   NUCLEI SCAN RESULTS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    sev_colors = {"critical": Fore.RED, "high": Fore.RED, "medium": Fore.YELLOW, "low": Fore.BLUE}
    for r in results:
        tid = r.get("template-id", "unknown")
        sev = r.get("type", "info")
        url = r.get("url", "N/A")
        matched = r.get("matched", False)
        print(f"\n{Fore.GREEN if matched else Fore.WHITE}[{tid}]{Style.RESET_ALL}")
        print(f"  URL:     {url}")
        print(f"  Status:  {r.get('status-code', 0)}")
        print(f"  Severity: {sev_colors.get(sev.lower(), Fore.WHITE)}{sev}{Style.RESET_ALL}")
        print(f"  Matched: {Fore.GREEN if matched else Fore.RED}{matched}{Style.RESET_ALL}")
        if matched and "matched-words" in r and r["matched-words"]:
            print(f"  Words:   {', '.join(r['matched-words'])}")


def main():
    parser = argparse.ArgumentParser(description="nuclei-custom-templates -- generate and test nuclei templates")
    parser.add_argument("-t", "--target", required=True, help="Target URL")
    parser.add_argument("-v", "--vuln", choices=list(VULN_TEMPLATES.keys()), default="xss", help="Vulnerability type")
    parser.add_argument("-p", "--param", default="q", help="Parameter name to test")
    parser.add_argument("--no-run", action="store_true", help="Only generate template, don't run")
    parser.add_argument("--list", action="store_true", help="List vulnerability types")
    noise = parser.add_mutually_exclusive_group()
    noise.add_argument("--quiet", dest="profile", action="store_const", const="quiet", help="Low-noise: rate limit 10 rps, 2 concurrent requests")
    noise.add_argument("--moderate", dest="profile", action="store_const", const="moderate", help="Moderate noise: rate limit 25 rps, 5 concurrent requests (default)")
    noise.add_argument("--loud", dest="profile", action="store_const", const="loud", help="High-noise: rate limit 50 rps, 10 concurrent requests")
    parser.set_defaults(profile="moderate")
    args = parser.parse_args()
    if args.list:
        for v in VULN_TEMPLATES:
            t = VULN_TEMPLATES[v]
            print(f"  {v}: {t['d']} (severity: {t['s']})")
        return
    target = args.target if args.target.startswith("http") else f"https://{args.target}"
    print(f"{Fore.CYAN}[*] Generating {args.vuln} template for {target}{Style.RESET_ALL}")
    yaml_content = generate_yaml(args.vuln, args.param)
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   GENERATED TEMPLATE{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{yaml_content}{Style.RESET_ALL}")
    if args.no_run or SHOULD_EXIT:
        return
    results = run_nuclei(yaml_content, target, args.profile)
    display_results(results)


if __name__ == "__main__":
    main()
