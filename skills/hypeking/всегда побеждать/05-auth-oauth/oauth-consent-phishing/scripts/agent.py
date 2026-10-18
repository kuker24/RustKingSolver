#!/usr/bin/env python3
"""
OAuth Consent Phishing Simulation Tool
Tests for scope escalation vulnerabilities and consent page
origin/domain validation weaknesses.

MITRE ATT&CK:
  T1525 - Implant Container Image
  T1190 - Exploit Public-Facing Application
"""

import argparse
import sys
import signal
import urllib.parse
from typing import Optional, Dict, List

import requests
from colorama import init, Fore, Style

init(autoreset=True)

RUNNING = True


def signal_handler(sig, frame):
    global RUNNING
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Exiting gracefully...{Style.RESET_ALL}")
    RUNNING = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class ConsentPhishingTester:
    def __init__(self, auth_url: str, client_id: str, redirect_uri: str, timeout: int = 15):
        self.auth_url = auth_url
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ConsentPhishingTester/1.0",
            "Accept": "text/html,application/json,*/*",
        })

    def build_auth_url(self, scope: str, state: str = "test_state",
                       additional_params: Optional[Dict[str, str]] = None) -> str:
        """Build an authorization URL with custom scope and optional params."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state,
        }
        if additional_params:
            params.update(additional_params)
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def test_flow(self, url: str) -> Optional[requests.Response]:
        """Send the authorization request and return the response."""
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            return resp
        except requests.exceptions.Timeout:
            print(f"  {Fore.RED}[TIMEOUT] Request timed out after {self.timeout}s{Style.RESET_ALL}")
        except requests.exceptions.ConnectionError as e:
            print(f"  {Fore.RED}[CONNECTION ERROR] {e}{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"  {Fore.RED}[REQUEST ERROR] {e}{Style.RESET_ALL}")
        return None

    def analyze_consent_page(self, resp: requests.Response, test_name: str) -> int:
        """Analyze the consent page response. Returns number of vulnerabilities found."""
        vuln_count = 0
        body = resp.text
        body_lower = body.lower()
        status = resp.status_code

        print(f"  {Fore.CYAN}HTTP {status} | Content-Length: {len(body)}{Style.RESET_ALL}")

        # Check for scope escalation - if scope changes propagate
        scope_in_body = any(s in body_lower for s in [
            "scope", "permissions", "access to", "authorize",
            "this application will", "grant access",
        ])
        if scope_in_body:
            granted = self._extract_scopes(body)
            if granted:
                print(f"  {Fore.YELLOW}[SCOPE] Permissions displayed: {', '.join(granted)}{Style.RESET_ALL}")

        # Check for origin/domain validation
        redirect_domain = urllib.parse.urlparse(self.redirect_uri).netloc
        if redirect_domain in body:
            print(f"  {Fore.GREEN}[+] Redirect URI domain '{redirect_domain}' "
                  f"appears in consent page{Style.RESET_ALL}")

        # Check consent page security headers
        headers = resp.headers
        sec_headers = {
            "X-Frame-Options": "DENY" not in headers.get("X-Frame-Options", ""),
            "Content-Security-Policy": "frame-ancestors" not in headers.get("Content-Security-Policy", ""),
        }
        missing = [h for h, risky in sec_headers.items() if risky]
        if missing:
            print(f"  {Fore.YELLOW}[!] Missing anti-clickjacking headers: "
                  f"{', '.join(missing)}{Style.RESET_ALL}")

        # Check for open redirect in response
        location = headers.get("Location", "")
        if location and not location.startswith(self.redirect_uri.rstrip("/")):
            print(f"  {Fore.RED}[VULNERABLE] Redirect target differs from "
                  f"registered redirect_uri!{Style.RESET_ALL}")
            vuln_count += 1

        # Detect if scope escalation succeeded
        code_returned = "code=" in resp.url.lower()
        if code_returned:
            print(f"  {Fore.RED}[VULNERABLE] Server returned auth code for "
                  f"'{test_name}' - scope escalation possible{Style.RESET_ALL}")
            vuln_count += 1

        # Check for parameter injection
        reflected_params = ["admin", "admin_scope", "full_access", "*", "all"]
        for param in reflected_params:
            if param in body_lower or param in resp.url.lower():
                print(f"  {Fore.YELLOW}[!] Parameter '{param}' reflected in "
                      f"response{Style.RESET_ALL}")

        return vuln_count

    def _extract_scopes(self, body: str) -> List[str]:
        """Extract scope descriptions from consent page body."""
        found = []
        markers = [
            "scope", "permission", "access to your", "read your",
            "write your", "manage your", "view your", "edit your",
            "delete your", "create",
        ]
        lines = body.split("\n")
        for line in lines:
            lower = line.lower()
            for m in markers:
                if m in lower and len(line.strip()) > 10:
                    found.append(line.strip()[:60])
                    break
        return found[:5]

    def check_cors_origin(self) -> int:
        """Test CORS origin validation on the consent endpoint."""
        vuln = 0
        test_origins = [
            "https://evil.com",
            "https://attacker.evil.com",
            "null",
        ]
        for origin in test_origins:
            if not RUNNING:
                break
            try:
                resp = self.session.options(
                    self.auth_url,
                    headers={"Origin": origin},
                    timeout=self.timeout,
                )
                acao = resp.headers.get("Access-Control-Allow-Origin", "")
                if origin in acao or acao == "*":
                    print(f"  {Fore.RED}[VULNERABLE] CORS allows origin: "
                          f"{origin}{Style.RESET_ALL}")
                    vuln += 1
                else:
                    print(f"  {Fore.GREEN}[SECURE] CORS blocks origin: "
                          f"{origin}{Style.RESET_ALL}")
            except requests.exceptions.RequestException:
                pass
        return vuln


def main():
    parser = argparse.ArgumentParser(
        description="OAuth Consent Phishing Simulation - Test for scope escalation "
                    "and consent page security weaknesses",
        epilog="MITRE ATT&CK: T1525 (Implant Container Image), T1190 (Exploit Public-Facing Application)"
    )
    parser.add_argument("-u", "--auth-url", required=True,
                        help="OAuth authorization endpoint URL")
    parser.add_argument("-c", "--client-id", required=True,
                        help="OAuth client ID")
    parser.add_argument("-r", "--redirect-uri", required=True,
                        help="Redirect URI registered with the client")
    parser.add_argument("-t", "--timeout", type=int, default=15,
                        help="Request timeout in seconds (default: 15)")
    args = parser.parse_args()

    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  OAuth Consent Phishing Simulation Tool{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  Target: {args.auth_url}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")

    tester = ConsentPhishingTester(args.auth_url, args.client_id, args.redirect_uri, args.timeout)
    total_vulns = 0

    # Test 1: Standard scope (baseline)
    print(f"\n{Fore.BLUE}[*] Test 1: Standard scope (openid profile) - baseline{Style.RESET_ALL}")
    url = tester.build_auth_url("openid profile")
    resp = tester.test_flow(url)
    if resp:
        total_vulns += tester.analyze_consent_page(resp, "standard scope")
    if not RUNNING:
        sys.exit(0)

    # Test 2: Escalated scope
    print(f"\n{Fore.BLUE}[*] Test 2: Escalated scope (admin/full_access){Style.RESET_ALL}")
    url = tester.build_auth_url("openid profile admin full_access")
    resp = tester.test_flow(url)
    if resp:
        total_vulns += tester.analyze_consent_page(resp, "escalated scope")
    if not RUNNING:
        sys.exit(0)

    # Test 3: Sensitive API scopes
    print(f"\n{Fore.BLUE}[*] Test 3: Sensitive API scope escalation{Style.RESET_ALL}")
    url = tester.build_auth_url("user.read.all mail.read contacts.write files.read.all")
    resp = tester.test_flow(url)
    if resp:
        total_vulns += tester.analyze_consent_page(resp, "sensitive scope")
    if not RUNNING:
        sys.exit(0)

    # Test 4: Scope injection via custom params
    print(f"\n{Fore.BLUE}[*] Test 4: Scope injection via prompt parameter{Style.RESET_ALL}")
    url = tester.build_auth_url("openid", additional_params={"prompt": "consent"})
    resp = tester.test_flow(url)
    if resp:
        total_vulns += tester.analyze_consent_page(resp, "prompt consent")
    if not RUNNING:
        sys.exit(0)

    # Test 5: CORS origin check
    print(f"\n{Fore.BLUE}[*] Test 5: CORS origin validation{Style.RESET_ALL}")
    total_vulns += tester.check_cors_origin()

    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    if total_vulns > 0:
        print(f"{Fore.RED}[!] VULNERABLE: Found {total_vulns} consent page "
              f"weakness(es){Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[+] SECURE: No consent page weaknesses detected{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
