#!/usr/bin/env python3
"""
katana-crawler-auto agent.py
MITRE ATT&CK: T1595 (Active Scanning)
Automates katana headless crawler with JS parsing and smart crawling logic.
"""
import argparse
import json
import os
import re
import signal
import subprocess
from urllib.parse import urlparse, urljoin
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

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
SKIP_EXTS = {".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot"}

# Webserver metafiles harvested for hidden structure (WSTG-INFO-03)
METAFILES = [
    "robots.txt", "sitemap.xml", "sitemap_index.xml", "security.txt",
    "humans.txt", "llms.txt", "ads.txt", "app-ads.txt",
    "crossdomain.xml", "clientaccesspolicy.xml",
    ".well-known/security.txt", ".well-known/assetlinks.json",
    ".well-known/apple-app-site-association", ".well-known/openid-configuration",
    ".well-known/change-password", ".well-known/mta-sts.txt",
    ".well-known/nodeinfo", ".well-known/webfinger",
    ".well-known/host-meta", ".well-known/dnt-policy.txt",
]

# Admin interface paths (WSTG-CONF-05 steps 1 and 3)
ADMIN_DISCOVERY_PATHS = [
    "/admin", "/admin/", "/administrator", "/administrator/", "/admin.php",
    "/admin.html", "/login", "/login.php", "/signin", "/auth",
    "/manage", "/manager", "/management", "/console", "/dashboard",
    "/control", "/controlpanel", "/panel", "/cpanel", "/portal",
    "/backend", "/backoffice", "/system", "/sysadmin", "/superadmin",
    "/wp-admin", "/wp-login.php", "/wp-admin/admin-ajax.php", "/xmlrpc.php",
    "/user/login", "/phpmyadmin", "/pma", "/adminer", "/adminer.php",
    "/server-status", "/server-info", "/nginx_status",
    "/manager/html", "/jmx-console", "/web-console",
]

# Backup / config / unreferenced file paths (WSTG-CONF-04, WSTG-INFO-02 step 5)
BACKUP_DISCOVERY_PATHS = [
    "/.env", "/config.php", "/config.php.bak", "/web.config", "/.htaccess",
    "/backup.zip", "/backup.tar.gz", "/backup.tar", "/backup.sql",
    "/site.zip", "/www.zip", "/html.zip", "/web.zip",
    "/database.sql", "/db.sql", "/dump.sql",
    "/backup/", "/backups/", "/old/", "/archive/", "/.snapshot/",
    "/index.php.bak", "/index.php~", "/config.ini", "/settings.php",
    "/database.yml", "/wp-config.php.bak", "/.git/config", "/.DS_Store",
]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def build_katana_command(target, options=None):
    cmd = ["katana", "-u", target, "-jsonl"]
    if not options:
        return cmd
    if options.get("headless"):
        cmd.append("-headless")
    if options.get("depth"):
        cmd.extend(["-depth", str(options["depth"])])
    if options.get("js_crawl"):
        cmd.append("-jc")
    if options.get("known_files"):
        cmd.append("-kf")
    if options.get("scope"):
        # katana field-scope: fqdn = exact host, dn = host + subdomains
        field_scope = {"strict": "fqdn", "subdomain": "dn", "fp": "dn"}.get(options["scope"], "dn")
        cmd.extend(["-fs", field_scope])
    if options.get("delay"):
        cmd.extend(["-delay", str(int(options["delay"]))])
    if options.get("rate_limit"):
        cmd.extend(["-rl", str(options["rate_limit"])])
    if options.get("timeout"):
        cmd.extend(["-timeout", str(options["timeout"])])
    if options.get("proxy"):
        cmd.extend(["-proxy", options["proxy"]])
    if options.get("concurrency"):
        cmd.extend(["-c", str(options["concurrency"])])
    if options.get("ua"):
        cmd.extend(["-H", f"User-Agent: {options['ua']}"])
    return cmd


def extract_js_endpoints(body, base_url):
    endpoints = set()
    patterns = [
        r'["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'fetch\(["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'axios\.(?:get|post|put|delete)\(["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'apiUrl\s*[+:=]\s*["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'endpoint\s*:\s*["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'route\s*:\s*["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
    ]
    for pat in patterns:
        for m in re.finditer(pat, body):
            path = m.group(1)
            if not any(path.endswith(e) for e in SKIP_EXTS):
                endpoints.add(urljoin(base_url, path))
    return endpoints


def _parse_robots(text):
    directives = {"disallow": [], "allow": [], "sitemap": []}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        low = line.lower()
        for key in directives:
            if low.startswith(key + ":"):
                value = line.split(":", 1)[1].strip()
                if value:
                    directives[key].append(value)
                break
    return directives


def _extract_sitemap_locs(text):
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text, re.I)


def harvest_metafiles(base_url):
    """Harvest robots/sitemap/security.txt/llms.txt/.well-known (WSTG-INFO-03)."""
    base = base_url.rstrip("/")
    found = []
    for path in METAFILES:
        if SHOULD_EXIT:
            break
        url = f"{base}/{path}"
        try:
            resp = _throttled_get(url, timeout=10, verify=False, allow_redirects=True)
            body = resp.text or ""
            stripped = body.lstrip().lower()
            if resp.status_code == 200 and body and "<html" not in stripped[:600]:
                entry = {"path": path, "status": resp.status_code, "length": len(body)}
                if path == "robots.txt":
                    directives = _parse_robots(body)
                    entry["directives"] = {k: v[:20] for k, v in directives.items()}
                    entry["_directives"] = directives
                elif path in ("sitemap.xml", "sitemap_index.xml"):
                    locs = _extract_sitemap_locs(body)[:200]
                    entry["locs"] = locs
                found.append(entry)
                if _profile().verbose:
                    print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {path} ({len(body)}b)")
        except Exception:
            continue
    return found


def probe_content_discovery(base_url):
    """Probe common admin/backup/config paths (WSTG-CONF-04/05)."""
    hits = []
    base = base_url.rstrip("/")
    paths = [(p, "admin") for p in ADMIN_DISCOVERY_PATHS] + [(p, "backup-config") for p in BACKUP_DISCOVERY_PATHS]
    for path, kind in paths:
        if SHOULD_EXIT:
            break
        url = f"{base}{path}"
        try:
            resp = _throttled_get(url, timeout=10, verify=False, allow_redirects=False)
            if resp.status_code and resp.status_code not in (0, 404):
                hits.append({"path": path, "kind": kind, "status": resp.status_code, "length": len(resp.text or "")})
                if _profile().verbose:
                    print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {path} [{resp.status_code}] ({kind})")
        except Exception:
            continue
    return hits


def _katana_entry_url(entry):
    """Extract the requested URL from a katana JSONL entry (flat or nested)."""
    if not isinstance(entry, dict):
        return ""
    url = entry.get("endpoint") or entry.get("url") or ""
    if not url:
        request = entry.get("request")
        if isinstance(request, dict):
            url = request.get("endpoint") or ""
    return url if isinstance(url, str) else ""


def mine_js_endpoints(results, cap=15):
    """Extract endpoints from JS files discovered by the crawl.

    Uses response bodies already captured in katana JSONL output when
    available, otherwise fetches the JS file (throttled).
    """
    js_urls = []
    inline_bodies = {}
    for entry in results:
        url = _katana_entry_url(entry)
        if not url or not url.split("?")[0].endswith(".js"):
            continue
        if url not in js_urls:
            js_urls.append(url)
        response = entry.get("response")
        if isinstance(response, dict) and response.get("body"):
            inline_bodies.setdefault(url, response["body"])
    endpoints = set()
    for js_url, body in inline_bodies.items():
        endpoints.update(extract_js_endpoints(body, js_url))
    for js_url in js_urls[:cap]:
        if SHOULD_EXIT or js_url in inline_bodies:
            continue
        try:
            resp = _throttled_get(js_url, timeout=10, verify=False)
            if resp.status_code == 200 and resp.text:
                found = extract_js_endpoints(resp.text, js_url)
                endpoints.update(found)
                if _profile().verbose and found:
                    print(f"  {Fore.CYAN}[*]{Style.RESET_ALL} {len(found)} endpoints from {js_url[:50]}")
        except Exception:
            continue
    return sorted(endpoints)


def run_recon_extras(target, results):
    """Run the WSTG-derived content discovery techniques around the crawl."""
    print(f"{Fore.CYAN}[*] Harvesting metafiles (robots/sitemap/security.txt/llms.txt/.well-known){Style.RESET_ALL}")
    metafiles = harvest_metafiles(target)
    print(f"{Fore.CYAN}[*] Probing admin/backup/config discovery paths (WSTG-CONF-04/05){Style.RESET_ALL}")
    content_hits = probe_content_discovery(target)
    print(f"{Fore.CYAN}[*] Mining discovered JS files for endpoints{Style.RESET_ALL}")
    js_endpoints = mine_js_endpoints(results)
    robots_disallow, robots_sitemaps, sitemap_urls = [], [], []
    for entry in metafiles:
        if entry.get("path") == "robots.txt":
            directives = entry.get("_directives") or {}
            robots_disallow = directives.get("disallow") or []
            robots_sitemaps = directives.get("sitemap") or []
        elif entry.get("path") in ("sitemap.xml", "sitemap_index.xml"):
            sitemap_urls.extend(entry.get("locs") or [])
    return {
        "metafiles": metafiles,
        "robots_disallow": robots_disallow,
        "robots_sitemaps": robots_sitemaps,
        "sitemap_urls": sitemap_urls,
        "content_hits": content_hits,
        "js_endpoints": js_endpoints,
    }


def run_katana(cmd):
    results = []
    try:
        print(f"{Fore.CYAN}[*] Running katana{Style.RESET_ALL}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        target = cmd[2] if len(cmd) > 2 else "unknown"
        for line in (proc.stdout + proc.stderr).strip().splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                entry["_target"] = target
                results.append(entry)
            except json.JSONDecodeError:
                results.append({"url": line.strip(), "_target": target, "_raw": True})
        if proc.returncode != 0 and not results:
            for line in (proc.stdout + proc.stderr).splitlines():
                if "error" in line.lower():
                    print(f"{Fore.YELLOW}[!] {line}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] katana not found. Simulating crawl.{Style.RESET_ALL}")
        target = cmd[2] if len(cmd) > 2 else "http://localhost/"
        results = simulate_crawl(target, cmd)
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}[!] katana timed out after 300s{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
    return results


def simulate_crawl(target, cmd):
    results = []
    try:
        depth = 3
        for i, a in enumerate(cmd):
            if a == "-depth" and i + 1 < len(cmd):
                depth = int(cmd[i + 1])
        print(f"{Fore.YELLOW}[*] Simulating crawl (depth={depth}){Style.RESET_ALL}")
        visited = set()
        to_visit = {target}
        curr_depth = 0
        while to_visit and curr_depth <= depth and not SHOULD_EXIT:
            next_batch = set()
            for url in to_visit:
                if SHOULD_EXIT or url in visited:
                    continue
                visited.add(url)
                try:
                    resp = _throttled_get(url, timeout=10, verify=False)
                    results.append({"url": url, "status": resp.status_code, "content-length": len(resp.text), "content-type": resp.headers.get("Content-Type", ""), "_target": target})
                    if resp.status_code == 200 and curr_depth < depth:
                        links = re.findall(r'href=["\']([^"\']+)["\']', resp.text)
                        js_eps = extract_js_endpoints(resp.text, url)
                        for link in list(links) + list(js_eps):
                            absolute = urljoin(url, link)
                            if target.rstrip("/") in absolute:
                                next_batch.add(absolute.split("#")[0])
                except Exception:
                    continue
            to_visit = next_batch
            curr_depth += 1
        print(f"{Fore.GREEN}[+] Crawled {len(visited)} URLs at depth {curr_depth - 1}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Simulation error: {e}{Style.RESET_ALL}")
    return results


def display_results(results, target, extras=None):
    if not results:
        print(f"\n{Fore.YELLOW}[*] No crawl results for {target}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   KATANA CRAWL RESULTS -- {target}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        status_count = {}
        api_endpoints = []
        for r in results:
            url = r.get("url", "")
            status = r.get("status", 0)
            status_count[status] = status_count.get(status, 0) + 1
            parsed = urlparse(url)
            if "/api/" in parsed.path or "/v1/" in parsed.path or "/graphql" in parsed.path:
                api_endpoints.append(url)
        print(f"\n{Fore.GREEN}[+] Total URLs found: {len(results)}{Style.RESET_ALL}")
        for code in sorted(status_count.keys()):
            color = Fore.GREEN if code < 400 else (Fore.YELLOW if code < 500 else Fore.RED)
            print(f"  {color}{code}{Style.RESET_ALL}: {status_count[code]}")
        if api_endpoints:
            print(f"\n{Fore.MAGENTA}[!] API Endpoints ({len(api_endpoints)}):{Style.RESET_ALL}")
            for ep in api_endpoints[:10]:
                print(f"  {Fore.MAGENTA}{ep}{Style.RESET_ALL}")
    if extras:
        metafiles = extras.get("metafiles") or []
        if metafiles:
            print(f"\n{Fore.MAGENTA}[!] Metafiles harvested (WSTG-INFO-03) ({len(metafiles)}):{Style.RESET_ALL}")
            for m in metafiles[:20]:
                extra = ""
                if m.get("path") == "robots.txt":
                    directives = m.get("directives") or {}
                    extra = f" disallow={len(directives.get('disallow') or [])} sitemap={len(directives.get('sitemap') or [])}"
                elif m.get("path") in ("sitemap.xml", "sitemap_index.xml"):
                    extra = f" locs={len(m.get('locs') or [])}"
                print(f"  {Fore.MAGENTA}{m['path']}{Style.RESET_ALL} [{m['status']}] ({m['length']}b){extra}")
        robots_disallow = extras.get("robots_disallow") or []
        if robots_disallow:
            print(f"  {Fore.CYAN}robots.txt hidden paths:{Style.RESET_ALL} {', '.join(robots_disallow[:10])}")
        sitemap_urls = extras.get("sitemap_urls") or []
        if sitemap_urls:
            print(f"  {Fore.CYAN}Sitemap URLs ({len(sitemap_urls)}):{Style.RESET_ALL}")
            for s in sitemap_urls[:5]:
                print(f"    {s}")
        content_hits = extras.get("content_hits") or []
        if content_hits:
            print(f"\n{Fore.MAGENTA}[!] Admin/Backup/Config discovery hits (WSTG-CONF-04/05) ({len(content_hits)}):{Style.RESET_ALL}")
            for c in content_hits[:20]:
                print(f"  {Fore.GREEN}[{c['status']}]{Style.RESET_ALL} {c['path']:<28} ({c['kind']}, {c['length']}b)")
        js_endpoints = extras.get("js_endpoints") or []
        if js_endpoints:
            print(f"\n{Fore.MAGENTA}[!] JS-extracted endpoints ({len(js_endpoints)}):{Style.RESET_ALL}")
            for ep in js_endpoints[:15]:
                print(f"  {ep[:80]}")
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="katana-crawler-auto -- headless crawler automation")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("--headless", action="store_true", help="Headless browser mode")
    parser.add_argument("--depth", type=int, default=3, help="Crawl depth")
    parser.add_argument("--js-crawl", action="store_true", help="Enable JS file crawling")
    parser.add_argument("--known-files", action="store_true", help="Check known files")
    parser.add_argument("--scope", choices=["strict", "subdomain", "fp"], default="subdomain", help="Crawl scope")
    parser.add_argument("--delay", type=int, default=0, help="Delay between requests (ms)")
    parser.add_argument("--rate-limit", type=int, default=100, help="Rate limit per minute")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout (s)")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    parser.add_argument("--passive", action="store_true", help="Passive mode")
    parser.add_argument("--no-subdomains", action="store_true", help="Filter out subdomains")
    parser.add_argument("--proxy", help="Proxy URL")
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
    opts = {"headless": args.headless, "depth": args.depth, "js_crawl": args.js_crawl, "known_files": args.known_files, "scope": args.scope, "delay": args.delay, "rate_limit": args.rate_limit, "timeout": args.timeout, "concurrency": args.concurrency, "passive": args.passive, "no_subdomains": args.no_subdomains, "proxy": args.proxy}
    profile = _profile()
    if profile.name == "quiet":
        opts["delay"] = max(opts["delay"], 2)
        opts["rate_limit"] = min(opts["rate_limit"], 10)
        opts["concurrency"] = min(opts["concurrency"], 1)
    elif profile.name == "moderate":
        opts["delay"] = max(opts["delay"], 1)
        opts["rate_limit"] = min(opts["rate_limit"], 120)
        opts["concurrency"] = min(opts["concurrency"], 10)
    opts["ua"] = opsec.FIXED_QUIET_AGENT if profile.name == "quiet" else opsec.next_ua(profile)
    cmd = build_katana_command(target, opts)
    print(f"{Fore.CYAN}[*] Starting crawl of {target}{Style.RESET_ALL}")
    results = run_katana(cmd)
    extras = {} if args.passive else run_recon_extras(target, results)
    display_results(results, target, extras)


if __name__ == "__main__":
    main()
