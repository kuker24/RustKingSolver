#!/usr/bin/env python3
"""
param-miner-advanced agent.py
MITRE ATT&CK: T1595 (Active Scanning), T1190 (Exploit Public-Facing Application)
Advanced parameter mining tool replicating Burp Param Miner logic for hidden parameter discovery.
"""
import argparse
import concurrent.futures
import json
import os
import signal
from datetime import datetime
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
import requests
from colorama import Fore, Style, init
init(autoreset=True)

import sys as _sys
_PIPELINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'pipeline'))
if _PIPELINE not in _sys.path:
    _sys.path.insert(0, _PIPELINE)
try:
    from modules import opsec
except ImportError:
    import opsec

OPSEC_PROFILE = None


def _profile():
    return OPSEC_PROFILE if OPSEC_PROFILE is not None else opsec.DEFAULT


def _session():
    global _OPSEC_SESSION
    try:
        return _OPSEC_SESSION
    except NameError:
        _OPSEC_SESSION = opsec.http_session(_profile())
        return _OPSEC_SESSION


def _throttled_get(url, **kwargs):
    return opsec.throttled(_session(), url, method="GET", profile=_profile(), **kwargs)


SHOULD_EXIT = False

COMMON_PARAMS = [
    "id", "page", "file", "path", "doc", "debug", "test", "cmd", "exec",
    "action", "token", "session", "auth", "key", "api_key", "secret",
    "redirect", "return", "next", "url", "link", "user_id",
    "cat", "category", "type", "mode", "lang", "locale", "format",
    "callback", "jsonp", "include", "template", "view", "layout",
    "sort", "order", "limit", "offset", "q", "query", "search", "term",
    "name", "title", "desc", "description", "content", "body", "text",
    "email", "phone", "address", "uid", "gid", "ref",
    "source", "src", "host", "port", "server", "domain",
    "method", "_method", "do", "func", "f", "cmd", "command",
    "data", "input", "output", "upload", "download",
    "admin", "root", "sudo", "config", "setting", "option",
    "r", "route", "class", "func", "function", "module",
    "error", "err", "msg", "message", "status", "state", "step",
]

POLLUTION_PARAMS = ["__proto__", "constructor[prototype]", "prototype"]

# IDOR / automation parameter names (attack-idor-automation: guessable
# sequential object identifiers across common resource types)
_IDOR_BASES = [
    "user", "account", "order", "customer", "invoice", "doc", "file",
    "record", "item", "message", "profile", "transaction", "booking",
    "ticket", "payment", "project", "team", "org", "role", "member",
    "employee", "post", "article", "comment", "attachment", "lead",
    "vendor", "contract",
]
_IDOR_EXTRA = [f"{base}_id" for base in _IDOR_BASES] + [f"{base}Id" for base in _IDOR_BASES[:10]] + [
    "id_num", "object_id", "entity_id", "resource_id", "external_id",
    "internal_id", "reference_id", "row_id", "key_id",
]
for _param in _IDOR_EXTRA:
    if _param not in COMMON_PARAMS:
        COMMON_PARAMS.append(_param)

# Host header probing values (attack-host-header / WSTG-INPV-17)
HOST_PROBE_MARKER = "pwn-host-probe.example.com"
HOST_OVERRIDE_HEADERS = ["X-Forwarded-Host", "X-Host", "X-Forwarded-Server", "X-HTTP-Host-Override"]
PATH_OVERRIDE_HEADERS = ["X-Original-URL", "X-Rewrite-URL"]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down gracefully...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def test_parameter(base_url, param, value="x", timeout=8, baseline=None):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)
    new_params = params.copy()
    new_params[param] = [value]
    url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(new_params, doseq=True), parsed.fragment))
    result = {"param": param, "url": url, "status": None, "length": 0, "reflected": False, "param_reflected": False, "length_diff": 0, "length_diff_signal": False, "status_change": False}
    try:
        resp = _throttled_get(url, timeout=timeout, verify=False, allow_redirects=True)
        result["status"] = resp.status_code
        result["length"] = len(resp.text)
        if value.lower() in resp.text.lower():
            result["reflected"] = True
        if param.lower() in resp.text.lower():
            result["param_reflected"] = True
        if baseline:
            result["length_diff"] = abs(result["length"] - baseline.get("length", 0))
            result["length_diff_signal"] = result["length_diff"] > 100
            if baseline.get("status") is not None and resp.status_code != baseline["status"]:
                result["status_change"] = True
    except requests.exceptions.RequestException:
        result["error"] = "request_failed"
    return result


def mine_parameters(target, threads=10, timeout=8):
    baseline = {}
    try:
        resp = _throttled_get(target, timeout=timeout, verify=False, allow_redirects=True)
        baseline = {"status": resp.status_code, "length": len(resp.text)}
        if _profile().verbose:
            print(f"{Fore.CYAN}[*] Baseline: status={resp.status_code} length={baseline['length']}{Style.RESET_ALL}")
    except requests.exceptions.RequestException:
        baseline = {}
    print(f"{Fore.CYAN}[*] Mining {len(COMMON_PARAMS)} parameters against {target}{Style.RESET_ALL}")
    found = []
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=1 if _profile().name == "quiet" else threads) as executor:
        futures = {executor.submit(test_parameter, target, p, timeout=timeout, baseline=baseline): p for p in COMMON_PARAMS}
        for future in concurrent.futures.as_completed(futures):
            if SHOULD_EXIT:
                break
            completed += 1
            param = futures[future]
            try:
                result = future.result()
                if result.get("reflected") or result.get("param_reflected") or result.get("length_diff_signal"):
                    found.append(result)
                    flags = []
                    if result.get("reflected"):
                        flags.append(f"{Fore.MAGENTA}REFLECTED{Style.RESET_ALL}")
                    if result.get("param_reflected"):
                        flags.append(f"{Fore.CYAN}PARAM{Style.RESET_ALL}")
                    if result.get("length_diff_signal"):
                        flags.append(f"{Fore.BLUE}LENGTH-DIFF({result.get('length_diff', 0)}){Style.RESET_ALL}")
                    flag_str = " [" + " | ".join(flags) + "]" if flags else ""
                    print(f"  [{completed}/{len(COMMON_PARAMS)}] {Fore.GREEN}[+]{Style.RESET_ALL} {param}{flag_str}")
                elif completed % 30 == 0 and _profile().verbose:
                    print(f"  [{completed}/{len(COMMON_PARAMS)}] scanning...")
            except Exception:
                continue
    return found


def test_pollution(target):
    results = []
    print(f"{Fore.YELLOW}[*] Testing parameter pollution...{Style.RESET_ALL}")
    parsed = urlparse(target)
    params = parse_qs(parsed.query)
    for pp in POLLUTION_PARAMS:
        if SHOULD_EXIT:
            break
        test_params = params.copy()
        test_params[pp] = ["test"]
        url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(test_params, doseq=True), parsed.fragment))
        try:
            resp = _throttled_get(url, timeout=8, verify=False)
            if "test" in resp.text.lower() or pp.lower() in resp.text.lower():
                results.append({"param": pp, "type": "prototype_pollution", "reflected": True})
                print(f"  {Fore.MAGENTA}[!] Prototype pollution candidate: {pp}{Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            continue
    print(f"{Fore.YELLOW}[*] Testing HTTP parameter pollution (duplicate params)...{Style.RESET_ALL}")
    existing_params = list(params.keys())
    for pn in existing_params[:10]:
        if SHOULD_EXIT:
            break
        test_params = params.copy()
        test_params[pn] = ["legit", "polluted"]
        url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(test_params, doseq=True), parsed.fragment))
        try:
            resp = _throttled_get(url, timeout=8, verify=False)
            if "polluted" in resp.text.lower():
                results.append({"param": pn, "type": "hpp", "reflected": True})
                print(f"  {Fore.YELLOW}[!] HPP on {pn}: duplicate value reflected{Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            continue
    return results


def probe_host_headers(target, timeout=8):
    """Host header injection probing (attack-host-header / WSTG-INPV-17).

    Checks whether host-override headers are reflected in the response and
    whether path-override headers change the served resource.
    """
    findings = []
    baseline_status, baseline_length = None, 0
    try:
        base_resp = _throttled_get(target, timeout=timeout, verify=False, allow_redirects=True)
        baseline_status, baseline_length = base_resp.status_code, len(base_resp.text or "")
    except requests.exceptions.RequestException:
        pass
    print(f"{Fore.YELLOW}[*] Probing host-header overrides (attack-host-header)...{Style.RESET_ALL}")
    for header in HOST_OVERRIDE_HEADERS:
        if SHOULD_EXIT:
            break
        try:
            resp = _throttled_get(target, timeout=timeout, verify=False, headers={header: HOST_PROBE_MARKER}, allow_redirects=True)
            if HOST_PROBE_MARKER.split(".")[0] in (resp.text or "").lower():
                findings.append({"type": "host_header_reflection", "header": header, "status": resp.status_code, "evidence": HOST_PROBE_MARKER})
                print(f"  {Fore.MAGENTA}[!] {header} reflected in response{Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            continue
    for header in PATH_OVERRIDE_HEADERS:
        if SHOULD_EXIT:
            break
        try:
            resp = _throttled_get(target, timeout=timeout, verify=False, headers={header: "/admin"}, allow_redirects=True)
            length_diff = abs(len(resp.text or "") - baseline_length)
            if baseline_status is not None and (resp.status_code != baseline_status or length_diff > 200):
                findings.append({"type": "path_override", "header": header, "status": resp.status_code, "baseline_status": baseline_status, "length_diff": length_diff})
                print(f"  {Fore.YELLOW}[!] {header}=/admin changed response (status {baseline_status} -> {resp.status_code}, diff {length_diff}){Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            continue
    return findings


def display_results(found, pollution, host_findings=None):
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   PARAM MINER RESULTS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if found:
        print(f"\n{Fore.GREEN}[+] Discovered {len(found)} hidden parameter(s):{Style.RESET_ALL}")
        for f in sorted(found, key=lambda x: x["param"]):
            param = f["param"]
            flags = []
            if f.get("reflected"):
                flags.append("REFLECTED")
            if f.get("param_reflected"):
                flags.append("PARAM-REFLECTED")
            if f.get("length_diff_signal"):
                flags.append(f"LENGTH-DIFF({f.get('length_diff', 0)})")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {param:<25} [{f.get('status', '?')}]{flag_str}")
    else:
        print(f"\n{Fore.YELLOW}[*] No hidden parameters found{Style.RESET_ALL}")
    if pollution:
        print(f"\n{Fore.YELLOW}[!] Pollution findings ({len(pollution)}):{Style.RESET_ALL}")
        for p in pollution:
            print(f"  {Fore.YELLOW}[!]{Style.RESET_ALL} {p['param']} ({p['type']})")
    if host_findings:
        print(f"\n{Fore.YELLOW}[!] Host header probe findings ({len(host_findings)}):{Style.RESET_ALL}")
        for h in host_findings:
            print(f"  {Fore.YELLOW}[!]{Style.RESET_ALL} {h['type']} via {h.get('header')} [{h.get('status', '?')}]")
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Hidden params: {len(found)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] Pollution candidates: {len(pollution)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] Host header findings: {len(host_findings or [])}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="param-miner-advanced -- hidden parameter discovery tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Thread count")
    parser.add_argument("--no-pollution", action="store_true", help="Skip pollution tests")
    parser.add_argument("--timeout", type=int, default=8, help="Request timeout")
    parser.add_argument("-o", "--output", help="Output results to JSON file")
    noise = parser.add_mutually_exclusive_group()
    noise.add_argument('--quiet', dest='profile', action='store_const', const='quiet',
                       help='QUIET: 2.0s+-1.0s delay, fixed UA, no aggressive checks')
    noise.add_argument('--moderate', dest='profile', action='store_const', const='moderate',
                       help='MODERATE: 0.5s+-0.25s delay, rotating UA (default)')
    noise.add_argument('--loud', dest='profile', action='store_const', const='loud',
                       help='LOUD: no artificial delay, full parallelism')
    parser.set_defaults(profile='moderate')
    args = parser.parse_args()
    globals()["OPSEC_PROFILE"] = opsec.Profile(args.profile)
    opsec.apply(_profile())
    target = args.url if args.url.startswith("http") else f"https://{args.url}"
    requests.DEFAULT_TIMEOUT = (args.timeout, args.timeout)
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   PARAM MINER ADVANCED -- {target}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    threads = 1 if _profile().name == "quiet" else args.threads
    found = mine_parameters(target, threads, args.timeout)
    if SHOULD_EXIT:
        return
    pollution = []
    if not args.no_pollution:
        pollution = test_pollution(target)
    host_findings = probe_host_headers(target, args.timeout)
    display_results(found, pollution, host_findings)
    if args.output:
        with open(args.output, "w") as f:
            json.dump({"target": target, "ts": datetime.now().isoformat(), "params_found": found, "pollution": pollution, "host_header_probes": host_findings}, f, indent=2)
        print(f"{Fore.GREEN}[+] Results saved to {args.output}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
