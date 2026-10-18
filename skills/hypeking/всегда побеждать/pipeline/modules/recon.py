#!/usr/bin/env python3
"""
AXIOM RECON ENGINE — Phase 1 of Web Pwn Pipeline
Discovers endpoints, technologies, parameters, and attack surface.
"""

import os, sys, json, subprocess, concurrent.futures
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    from modules import opsec
except ImportError:
    import opsec

try:
    import requests
except ImportError:
    import urllib.request, urllib.error

    class requests:
        class Session:
            def get(self, url, **kwargs):
                req = urllib.request.Request(url)
                for k, v in kwargs.get('headers', {}).items():
                    req.add_header(k, v)
                try:
                    resp = urllib.request.urlopen(req, timeout=kwargs.get('timeout', 10))
                    return type('Response', (), {
                        'status_code': resp.getcode(),
                        'text': resp.read().decode('utf-8', errors='replace'),
                        'headers': dict(resp.info()),
                        'elapsed': type('E', (), {'total_seconds': lambda s: 0})()
                    })()
                except Exception as e:
                    return type('Response', (), {
                        'status_code': 0, 'text': str(e), 'headers': {}
                    })()


class ReconEngine:
    """Discovers attack surface for a target."""

    def __init__(self, target: str, output_dir: str,
                 cookie: str = None, proxy: str = None,
                 threads: int = 10, timeout: int = 10,
                 profile: "opsec.Profile" = None):
        self.target = target
        self.output_dir = output_dir
        self.cookie = cookie
        self.proxy = proxy
        self.threads = threads
        self.timeout = timeout
        self.profile = profile if isinstance(profile, opsec.Profile) else opsec.DEFAULT
        self.session = opsec.http_session(self.profile, proxy=proxy, timeout=timeout)
        self.results = {
            "alive": False,
            "status_code": 0,
            "title": "",
            "server": "",
            "technologies": [],
            "endpoints": [],
            "parameters": [],
            "forms": [],
            "cookies": {},
            "headers": {}
        }

    def run(self) -> Dict:
        """Execute all recon modules."""
        print("  ┌─ Reconnaissance Phase")
        self._probe_target()
        if not self.results["alive"]:
            print("  └─ [!] Target unreachable")
            return self.results
        self._fingerprint_tech()
        self._extract_metadata()
        self._crawl_endpoints()
        print("  └─ Recon complete")
        self._save()
        return self.results

    def _probe_target(self):
        """Check if target is alive and get basic info."""
        print("  ├─ Probing target...")
        try:
            headers = {"User-Agent": opsec.next_ua(self.profile)}
            if self.cookie:
                headers["Cookie"] = self.cookie
            r = opsec.throttled(self.session, self.target, profile=self.profile,
                                headers=headers, timeout=self.timeout, verify=False)
            self.results["alive"] = True
            self.results["status_code"] = r.status_code
            self.results["headers"] = dict(r.headers)
            self.results["server"] = r.headers.get("Server", "unknown")

            # Extract title
            import re
            m = re.search(r'<title>(.*?)</title>', r.text, re.IGNORECASE | re.DOTALL)
            self.results["title"] = m.group(1).strip() if m else ""

            # Cookies
            if hasattr(r, 'cookies'):
                for c in r.cookies:
                    self.results["cookies"][c.name] = c.value

            print(f"  ├─ Status: {r.status_code} | Server: {self.results['server']}")
        except Exception as e:
            print(f"  ├─ [!] Probe failed: {e}")

    def _fingerprint_tech(self):
        """Identify technologies using header/HTML patterns."""
        print("  ├─ Fingerprinting technologies...")
        tech_patterns = {
            "nginx": {"headers": ["server: nginx"], "body": []},
            "apache": {"headers": ["server: apache"], "body": []},
            "cloudflare": {"headers": ["server: cloudflare", "cf-ray"], "body": []},
            "akamai": {"headers": ["server: akamai", "x-akamai"], "body": []},
            "aws": {"headers": ["x-amz-", "aws"], "body": []},
            "php": {"headers": ["x-powered-by: php"], "body": [r"\.php"]},
            "asp.net": {"headers": ["x-aspnet", "x-powered-by: asp"], "body": [r"__viewstate"]},
            "node.js/express": {"headers": ["x-powered-by: express"], "body": []},
            "wordpress": {"headers": [], "body": [r"/wp-content", r"/wp-admin"]},
            "drupal": {"headers": [], "body": [r"drupal"]},
            "jquery": {"headers": [], "body": [r"jquery"]},
            "react": {"headers": [], "body": [r"react", r"next\.js"]},
            "vue": {"headers": [], "body": [r"vue\.js"]},
            "angular": {"headers": [], "body": [r"angular"]},
            "graphql": {"headers": [], "body": [r"graphql"]},
            "waf": {"headers": ["x-sucuri", "x-safed", "x-waf", "server: cloudflare"],
                    "body": [r"attention required", r"challenge platform"]}
        }

        import re
        body_text = ""
        try:
            r = opsec.throttled(self.session, self.target, profile=self.profile,
                                timeout=self.timeout, verify=False)
            body_text = r.text
        except Exception:
            pass

        for tech, patterns in tech_patterns.items():
            found = False
            for h_pattern in patterns["headers"]:
                for k, v in self.results["headers"].items():
                    if h_pattern.lower() in f"{k}: {v}".lower():
                        found = True
                        break
            if not found:
                for b_pattern in patterns["body"]:
                    if re.search(b_pattern, body_text, re.IGNORECASE):
                        found = True
                        break
            if found:
                self.results["technologies"].append({"name": tech, "confidence": "high"})

        if self.results["technologies"]:
            techs = ", ".join([t["name"] for t in self.results["technologies"]])
            print(f"  ├─ Detected: {techs}")

    def _extract_metadata(self):
        """Extract forms, links, and endpoints from the main page."""
        print("  ├─ Extracting metadata...")
        try:
            r = opsec.throttled(self.session, self.target, profile=self.profile,
                                timeout=self.timeout, verify=False)
            import re

            # Forms
            form_pattern = re.compile(r'<form[^>]*action=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</form>',
                                      re.IGNORECASE | re.DOTALL)
            for m in form_pattern.finditer(r.text):
                action = m.group(1)
                fields = re.findall(r'<input[^>]*name=[\'"]([^\'"]*)[\'"]', m.group(2))
                self.results["forms"].append({
                    "action": action,
                    "method": re.search(r'method=[\'"]([^\'"]*)[\'"]', m.group(0), re.IGNORECASE),
                    "fields": fields
                })

            # Links
            link_pattern = re.compile(r'href=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
            for m in link_pattern.finditer(r.text):
                url = m.group(1)
                if url and not url.startswith("#") and not url.startswith("javascript"):
                    self.results["endpoints"].append(url)

            # Scripts
            script_pattern = re.compile(r'src=[\'"]([^\'"]+\.js[^\'"]*)[\'"]', re.IGNORECASE)
            for m in script_pattern.finditer(r.text):
                self.results["endpoints"].append(m.group(1))

            print(f"  ├─ Found: {len(self.results['forms'])} forms, {len(self.results['endpoints'])} endpoints")
        except Exception as e:
            print(f"  ├─ [!] Metadata extraction failed: {e}")

    def _crawl_endpoints(self):
        """Probe discovered endpoints for accessibility."""
        if not self.results["endpoints"]:
            return
        print(f"  ├─ Probing {min(len(self.results['endpoints']), 20)} endpoints...")

        def check_endpoint(url_path):
            full_url = url_path if url_path.startswith("http") else f"{self.target.rstrip('/')}/{url_path.lstrip('/')}"
            try:
                r = opsec.throttled(self.session, full_url, profile=self.profile,
                                    timeout=self.timeout, verify=False)
                return {"path": url_path, "status": r.status_code, "size": len(r.text)}
            except Exception:
                return {"path": url_path, "status": 0, "size": 0}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = [ex.submit(check_endpoint, ep) for ep in self.results["endpoints"][:20]]
            for f in concurrent.futures.as_completed(futures):
                result = f.result()
                if result["status"] and result["status"] < 400:
                    print(f"  ├─ [{result['status']}] {result['path']}")

    def _save(self):
        path = f"{self.output_dir}/recon-results.json"
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"  └─ Saved: {path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AXIOM Recon Engine")
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-o", "--output", default=".")
    args = parser.parse_args()
    engine = ReconEngine(args.target, args.output)
    engine.run()
