#!/usr/bin/env python3
"""
httpx-smart-recon agent.py
MITRE ATT&CK: T1595 (Active Scanning)
Smart reconnaissance tool probing URLs with httpx for tech detection and probing.
"""
import argparse
import json
import os
import re
import signal
import subprocess
import tempfile
from urllib.parse import urlparse
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

TECH_PATTERNS = {
    "nginx": ["Server: nginx"],
    "apache": ["Server: Apache"],
    "cloudflare": ["CF-Ray", "Server: cloudflare"],
    "iis": ["Server: Microsoft-IIS"],
    "express": ["X-Powered-By: Express"],
    "python": ["Server: Python", "Server: gunicorn"],
    "ruby": ["Server: Phusion", "X-Runtime"],
    "java": ["Server: Apache-Coyote"],
    "wordpress": ["wp-content", "wp-admin"],
    "drupal": ["Drupal"],
    "react": ["react", "react-dom"],
    "vue": ["vue.js"],
    "angular": ["ng-app"],
    "laravel": ["laravel_session"],
    # WSTG-INFO-02/08/10: additional server, framework and edge fingerprints
    "werkzeug": ["Server: Werkzeug"],
    "tomcat": ["Server: Tomcat"],
    "jboss": ["X-Powered: JBoss", "X-Powered-By: JBoss"],
    "litespeed": ["Server: LiteSpeed"],
    "php": ["X-Powered-By: PHP", "PHPSESSID"],
    "aspnet": ["X-AspNet-Version", "ASP.NET_SessionId"],
    "django": ["csrfmiddlewaretoken", "csrftoken"],
    "joomla": ["Joomla"],
    "rails": ["_rails_session"],
    "express-cookie": ["connect.sid"],
    "varnish": ["X-Varnish"],
    "fastly": ["X-Served-By: cache", "X-Fastly-Request-Id"],
    "cloudfront": ["X-Amz-Cf-Id"],
    "akamai": ["X-Akamai"],
    "sucuri": ["X-Sucuri-ID"],
    "imperva": ["X-CDN: Imperva"],
    "f5-bigip": ["BIGipServer"],
    "aws-alb": ["AWSALB"],
    "netlify": ["X-NF-Request-ID"],
}

# Profile -> native httpx rate/threads/retries settings (quiet = slowest, loud = fastest)
PROFILE_TOOL_LIMITS = {
    "quiet": {"rate_limit": 10, "threads": 2, "retries": 0},
    "moderate": {"rate_limit": 150, "threads": 10, "retries": 1},
    "loud": {"rate_limit": None, "threads": None, "retries": 2},
}


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def build_httpx_command(targets, options=None):
    cmd = ["httpx", "-json"]
    if len(targets) == 1:
        cmd.extend(["-u", targets[0]])
    else:
        fd, tmp_path = tempfile.mkstemp(suffix=".txt", prefix="httpx_")
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(targets))
        cmd.extend(["-l", tmp_path])
    if options:
        if options.get("status_code"):
            cmd.append("-sc")
        if options.get("title"):
            cmd.append("-title")
        if options.get("tech_detect"):
            cmd.append("-td")
        if options.get("follow_redirect"):
            cmd.append("-fr")
        if options.get("method"):
            cmd.extend(["-x", options["method"]])
        if options.get("threads"):
            cmd.extend(["-t", str(options["threads"])])
        if options.get("rate_limit"):
            cmd.extend(["-rl", str(options["rate_limit"])])
        if options.get("timeout"):
            cmd.extend(["-timeout", str(options["timeout"])])
        if options.get("proxy"):
            cmd.extend(["-proxy", options["proxy"]])
        if options.get("retries"):
            cmd.extend(["-retries", str(options["retries"])])
        if options.get("ua"):
            cmd.extend(["-H", f"User-Agent: {options['ua']}"])
        if options.get("response_time"):
            cmd.append("-rt")
        if options.get("cdn"):
            cmd.append("-cdn")
        if options.get("ip"):
            cmd.append("-ip")
    return cmd


def detect_technologies(headers, body):
    detected = []
    for name, indicators in TECH_PATTERNS.items():
        for indicator in indicators:
            if ":" in indicator:
                key, val = indicator.split(":", 1)
                header_val = headers.get(key.strip().lower(), "").lower()
                if val.strip().lower() in header_val:
                    detected.append(name)
                    break
            else:
                if indicator.lower() in body.lower():
                    detected.append(name)
                    break
    return sorted(set(detected))


# --- New techniques (sourced from 16-wstg methodology + 17-attack-core docs) ---

SECURITY_HEADER_WEIGHTS = {
    "strict-transport-security": 20,
    "content-security-policy": 20,
    "x-content-type-options": 10,
    "x-frame-options": 10,
    "referrer-policy": 10,
    "permissions-policy": 10,
    "x-xss-protection": 5,
}


def grade_security_headers(headers):
    """Grade security headers (WSTG-INFO-02 header review + WSTG-CONF-06 HSTS)."""
    present, missing = [], []
    score = 0
    for header, weight in SECURITY_HEADER_WEIGHTS.items():
        if header in headers:
            present.append(header)
            score += weight
        else:
            missing.append(header)
    max_score = sum(SECURITY_HEADER_WEIGHTS.values())
    grade = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F"
    return {"score": score, "max": max_score, "grade": grade, "missing": missing, "present": present}


EDGE_SIGNATURES = [
    ("cloudflare", ["cf-ray", "server: cloudflare", "__cfduid"]),
    ("aws-cloudfront", ["x-amz-cf-id", "x-amz-cf-pop"]),
    ("akamai", ["x-akamai", "server: akamaighost"]),
    ("fastly", ["x-fastly-request-id", "x-served-by: cache", "x-surrogate-key"]),
    ("varnish", ["x-varnish"]),
    ("imperva", ["x-cdn: imperva", "x-iinfo"]),
    ("sucuri", ["x-sucuri-id", "x-sucuri-cache"]),
    ("f5-bigip", ["bigipserver"]),
    ("aws-alb", ["awsalb", "awsalbcors"]),
    ("envoy-istio", ["x-envoy", "x-istio", "x-b3"]),
]


def fingerprint_edge(headers):
    """CDN / load balancer / reverse proxy fingerprinting from headers (WSTG-INFO-10)."""
    blob = "\n".join(f"{k}: {v}" for k, v in headers.items()).lower()
    hits = []
    for name, signatures in EDGE_SIGNATURES:
        if any(sig in blob for sig in signatures):
            hits.append(name)
    if "via" in headers and not hits:
        hits.append("proxy-via")
    return sorted(set(hits))


COOKIE_TECH_MAP = [
    ("php", ["phpsessid"]),
    ("aspnet", ["asp.net_sessionid"]),
    ("java", ["jsessionid"]),
    ("django", ["csrftoken=", "sessionid="]),
    ("laravel", ["laravel_session"]),
    ("cakephp", ["cakephp"]),
    ("codeigniter", ["ci_session"]),
    ("wordpress", ["wordpress_logged_in"]),
    ("drupal", ["drupal.visitor"]),
    ("rails", ["_rails_session"]),
    ("express", ["connect.sid"]),
]


def detect_cookie_tech(headers):
    """Technology inference from Set-Cookie names (WSTG-INFO-08 cookie analysis)."""
    cookies = ";".join(v for k, v in headers.items() if k.lower() == "set-cookie").lower()
    hits = [name for name, signatures in COOKIE_TECH_MAP if any(sig in cookies for sig in signatures)]
    return sorted(set(hits))


ERROR_DISCLOSURE_PATTERNS = {
    "stack_trace": re.compile(r"Traceback \(most recent|Exception in thread|at [\w.$]+\([\w./]+:\d+\)", re.I),
    "file_path": re.compile(r"/var/www/|/home/\w+/|/app/|/opt/|/usr/share/|C:\\", re.I),
    "sql_error": re.compile(r"SQL syntax|mysql_|ORA-\d+|PG::|sqlite|ODBC|Microsoft SQL Server", re.I),
    "debug_info": re.compile(r"\b(?:DEBUG|NOTICE|WARNING)\b|Line \d+", re.I),
    "internal_ip": re.compile(r"\b(?:192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b"),
    "framework_error": re.compile(r"Fatal error: Uncaught|Server Error in '/' Application|Whitelabel Error Page|DoesNotExist at /|Routing Error|Cannot GET /", re.I),
}


def detect_error_disclosure(body):
    """Sensitive disclosure patterns in page/error bodies (WSTG-ERRH-01)."""
    hits = []
    text = body or ""
    for name, pattern in ERROR_DISCLOSURE_PATTERNS.items():
        match = pattern.search(text)
        if match:
            hits.append({"type": name, "evidence": match.group(0)[:80]})
    return hits


WAF_SIGNATURES = [
    ("cloudflare", ["attention required", "cloudflare"]),
    ("modsecurity", ["mod_security", "modsecurity"]),
    ("aws-waf", ["awswaf", "aws waf"]),
    ("imperva", ["imperva", "incapsula"]),
    ("sucuri", ["sucuri"]),
    ("akamai", ["akamai"]),
    ("generic-deny", ["request blocked", "access denied", "blocked by"]),
]


def probe_waf(url):
    """Active WAF probe with a benign attack-pattern string (WSTG-INFO-10 step 7).

    Only runs under profiles that allow aggressive checks (skipped in QUIET).
    """
    separator = "&" if "?" in url else "?"
    probe_url = f"{url}{separator}id=<script>alert(1)</script>"
    try:
        resp = _throttled_get(probe_url, timeout=10, verify=False, allow_redirects=True)
        blob = "\n".join(f"{k}: {v}" for k, v in resp.headers.items()).lower()
        text = (resp.text or "").lower()
        blocked_status = resp.status_code in (403, 406, 429)
        explicit_block = any(sig in text for sig in (
            "attention required", "request blocked", "access denied", "blocked by",
            "mod_security", "modsecurity", "awswaf", "incapsula", "sucuri"))
        if blocked_status or explicit_block:
            for name, signatures in WAF_SIGNATURES:
                if any(sig in text or sig in blob for sig in signatures):
                    return name
            return "unknown-block" if blocked_status else None
    except Exception:
        return None
    return None


def run_header_techniques(headers, body, url=None):
    """Run all header/body-based fingerprint techniques on one response."""
    techniques = {
        "security_headers": grade_security_headers(headers),
        "edge": fingerprint_edge(headers),
        "cookie_tech": detect_cookie_tech(headers),
        "error_disclosure": detect_error_disclosure(body),
    }
    if url and _profile().allows_aggressive:
        waf = probe_waf(url)
        if waf:
            techniques["waf"] = waf
    return techniques


def _enrich_result(result):
    """Deep-probe a httpx binary result and attach the new technique findings."""
    url = result.get("url") or ""
    if not isinstance(url, str) or not url.startswith("http"):
        return result
    try:
        resp = _throttled_get(url, timeout=10, verify=False, allow_redirects=True)
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        result.update(run_header_techniques(headers_lower, resp.text, url=url))
        if not result.get("technologies"):
            result["technologies"] = detect_technologies(headers_lower, resp.text)
    except Exception:
        pass
    return result


def run_httpx(cmd):
    results = []
    try:
        print(f"{Fore.CYAN}[*] Running httpx probe{Style.RESET_ALL}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        output = proc.stdout + proc.stderr
        for line in output.strip().splitlines():
            if not line.strip():
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if proc.returncode != 0 and not results:
            for line in output.splitlines():
                if "error" in line.lower():
                    print(f"{Fore.YELLOW}[!] {line}{Style.RESET_ALL}")
        for result in results:
            if SHOULD_EXIT:
                break
            _enrich_result(result)
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] httpx not found. Simulating.{Style.RESET_ALL}")
        results = simulate_httpx(cmd)
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}[!] httpx timed out after 180s{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
    if not results and not SHOULD_EXIT:
        print(f"{Fore.YELLOW}[!] httpx binary unusable (incompatible CLI). Falling back to built-in probing.{Style.RESET_ALL}")
        results = simulate_httpx(cmd)
    return results


def simulate_httpx(cmd):
    results = []
    try:
        targets = [cmd[i+1] for i, a in enumerate(cmd) if a == "-u" and i + 1 < len(cmd)]
        for t in targets:
            if SHOULD_EXIT:
                break
            t = t if t.startswith("http") else f"https://{t}"
            if _profile().verbose:
                print(f"{Fore.YELLOW}[*] Probing {t}{Style.RESET_ALL}")
            try:
                resp = _throttled_get(t, timeout=10, verify=False, allow_redirects=True)
                headers_lower = {k.lower(): v for k, v in resp.headers.items()}
                techs = detect_technologies(headers_lower, resp.text)
                techniques = run_header_techniques(headers_lower, resp.text, url=t)
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', resp.text, re.I)
                title = title_match.group(1).strip()[:80] if title_match else ""
                elapsed = getattr(resp, "elapsed", None)
                response_time = round(elapsed.total_seconds() * 1000, 2) if elapsed else 0.0
                result = {"url": t, "host": urlparse(t).netloc, "scheme": urlparse(t).scheme, "status_code": resp.status_code, "content_length": len(resp.text), "content_type": resp.headers.get("Content-Type", ""), "title": title, "technologies": techs, "response_time": response_time}
                result.update(techniques)
                results.append(result)
                if _profile().verbose:
                    print(f"  {Fore.GREEN}[{resp.status_code}]{Style.RESET_ALL} {len(resp.text)}b {Fore.CYAN}{title[:50]}{Style.RESET_ALL}")
                    if techs:
                        print(f"    Tech: {', '.join(techs)}")
                    edge = result.get("edge") or []
                    if edge:
                        print(f"    Edge: {', '.join(edge)}")
                    sh = result.get("security_headers") or {}
                    if sh.get("grade"):
                        print(f"    SecHeaders: grade {sh['grade']} ({sh['score']}/{sh['max']}) missing {len(sh['missing'])}")
                    if result.get("error_disclosure"):
                        print(f"    {Fore.MAGENTA}[!] Disclosure: {', '.join(e['type'] for e in result['error_disclosure'])}{Style.RESET_ALL}")
            except requests.exceptions.RequestException as e:
                print(f"  {Fore.RED}[!] {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Simulation error: {e}{Style.RESET_ALL}")
    return results


def display_results(results):
    if not results:
        print(f"\n{Fore.YELLOW}[*] No results{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   HTTPX RECON RESULTS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    tech_counts = {}
    for r in results:
        for t in r.get("technologies", []):
            tech_counts[t] = tech_counts.get(t, 0) + 1
    for r in results:
        sc = Fore.GREEN if r.get("status_code", 0) < 400 else (Fore.YELLOW if r.get("status_code", 0) < 500 else Fore.RED)
        print(f"  {r.get('url', '')[:38]:<40} {sc}{r.get('status_code', 0):<8}{Style.RESET_ALL} {r.get('content_length', 0):<10} {Fore.CYAN}{r.get('title', '')[:28]:<30}{Style.RESET_ALL}")
    if tech_counts:
        print(f"\n{Fore.CYAN}Technology Distribution:{Style.RESET_ALL}")
        for tech, count in sorted(tech_counts.items(), key=lambda x: -x[1]):
            print(f"  {Fore.WHITE}{tech}{Style.RESET_ALL}: {count} hosts")
    grades = [(r.get("url", ""), r.get("security_headers") or {}) for r in results
              if isinstance(r, dict) and (r.get("security_headers") or {}).get("grade")]
    if grades:
        print(f"\n{Fore.CYAN}Security Header Grades (WSTG-INFO-02/CONF-06):{Style.RESET_ALL}")
        for url, sh in grades[:15]:
            print(f"  {Fore.WHITE}{sh['grade']}{Style.RESET_ALL} ({sh['score']}/{sh['max']}) missing: {', '.join(sh['missing'][:4]) or '-'}  {url[:38]}")
    edge_counts = {}
    for r in results:
        for edge in (r.get("edge") or []):
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
    if edge_counts:
        print(f"\n{Fore.CYAN}Edge / CDN / LB Fingerprint (WSTG-INFO-10):{Style.RESET_ALL}")
        for edge, count in sorted(edge_counts.items(), key=lambda x: -x[1]):
            print(f"  {Fore.WHITE}{edge}{Style.RESET_ALL}: {count} host(s)")
    waf_hosts = [(r.get("url", ""), r["waf"]) for r in results if isinstance(r, dict) and r.get("waf")]
    if waf_hosts:
        print(f"\n{Fore.CYAN}WAF Probe Results (WSTG-INFO-10 step 7):{Style.RESET_ALL}")
        for url, waf in waf_hosts[:10]:
            print(f"  {Fore.MAGENTA}{waf}{Style.RESET_ALL}  {url[:45]}")
    cookie_counts = {}
    for r in results:
        for tech in (r.get("cookie_tech") or []):
            cookie_counts[tech] = cookie_counts.get(tech, 0) + 1
    if cookie_counts:
        print(f"\n{Fore.CYAN}Cookie-Based Technology (WSTG-INFO-08):{Style.RESET_ALL}")
        for tech, count in sorted(cookie_counts.items(), key=lambda x: -x[1]):
            print(f"  {Fore.WHITE}{tech}{Style.RESET_ALL}: {count} host(s)")
    disclosures = [(r.get("url", ""), e) for r in results if isinstance(r, dict)
                   for e in (r.get("error_disclosure") or [])]
    if disclosures:
        print(f"\n{Fore.MAGENTA}[!] Error/Debug Disclosure (WSTG-ERRH-01) ({len(disclosures)}):{Style.RESET_ALL}")
        for url, e in disclosures[:10]:
            print(f"  {Fore.MAGENTA}{e['type']}{Style.RESET_ALL}: {e['evidence']}  ({url[:40]})")
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Total hosts: {len(results)} | Technologies: {len(tech_counts)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="httpx-smart-recon -- tech detection and probing")
    parser.add_argument("-u", "--url", help="Target URL")
    parser.add_argument("-l", "--list", help="File containing URLs")
    parser.add_argument("--method", help="HTTP method override (e.g. HEAD, POST)")
    parser.add_argument("--follow-redirect", action="store_true", help="Follow redirects")
    parser.add_argument("--threads", type=int, default=10, help="Concurrency threads")
    parser.add_argument("--rate-limit", type=int, default=150, help="Rate limit per minute")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--proxy", help="Proxy URL")
    parser.add_argument("--cdn", action="store_true", help="Check if behind CDN")
    parser.add_argument("--ip", action="store_true", help="Show IP address")
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
    if not args.url and not args.list:
        parser.print_help()
        return
    targets = []
    if args.url:
        targets.append(args.url if args.url.startswith("http") else f"https://{args.url}")
    if args.list:
        try:
            with open(args.list, "r") as f:
                targets.extend([l.strip() for l in f if l.strip()])
        except FileNotFoundError:
            print(f"{Fore.RED}[!] File not found: {args.list}{Style.RESET_ALL}")
            return
    opts = {"status_code": True, "title": True, "tech_detect": True, "method": args.method, "follow_redirect": args.follow_redirect, "threads": args.threads, "rate_limit": args.rate_limit, "timeout": args.timeout, "proxy": args.proxy, "cdn": args.cdn, "ip": args.ip}
    limits = PROFILE_TOOL_LIMITS[_profile().name]
    if limits.get("rate_limit"):
        opts["rate_limit"] = min(opts["rate_limit"], limits["rate_limit"])
    if limits.get("threads"):
        opts["threads"] = min(opts["threads"], limits["threads"])
    opts["retries"] = limits.get("retries", 0)
    opts["ua"] = opsec.FIXED_QUIET_AGENT if _profile().name == "quiet" else opsec.next_ua(_profile())
    cmd = build_httpx_command(targets, opts)
    print(f"{Fore.CYAN}[*] Recon on {len(targets)} target(s){Style.RESET_ALL}")
    results = run_httpx(cmd)
    display_results(results)


if __name__ == "__main__":
    main()
