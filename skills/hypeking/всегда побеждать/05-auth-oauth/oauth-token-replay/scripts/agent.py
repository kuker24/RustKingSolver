#!/usr/bin/env python3
"""
OAuth Token Replay Detection Tool
Tests if OAuth tokens are accepted from different IPs and User-Agents,
detecting missing token binding (DPoP / mTLS).

MITRE ATT&CK:
  T1525 - Implant Container Image
  T1190 - Exploit Public-Facing Application
"""

import argparse
import sys
import signal
from typing import Optional, Dict

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


class TokenReplayTester:
    def __init__(self, token_endpoint: str, access_token: str,
                 resource_url: str = "https://api.example.com/userinfo",
                 timeout: int = 15):
        self.token_endpoint = token_endpoint
        self.access_token = access_token
        self.resource_url = resource_url
        self.timeout = timeout
        self.session = requests.Session()

    def _request_with_headers(self, headers: Dict[str, str]) -> Optional[requests.Response]:
        """Make a request with the given headers."""
        headers.setdefault("Authorization", f"Bearer {self.access_token}")
        try:
            resp = self.session.get(
                self.resource_url,
                headers=headers,
                timeout=self.timeout,
            )
            return resp
        except requests.exceptions.Timeout:
            print(f"  {Fore.RED}[TIMEOUT] Request timed out after {self.timeout}s{Style.RESET_ALL}")
        except requests.exceptions.ConnectionError as e:
            print(f"  {Fore.RED}[CONNECTION ERROR] {e}{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"  {Fore.RED}[REQUEST ERROR] {e}{Style.RESET_ALL}")
        return None

    def test_baseline(self) -> Optional[requests.Response]:
        """Test with default headers to establish baseline."""
        print(f"  {Fore.CYAN}Baseline request (normal IP, normal UA){Style.RESET_ALL}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "X-Forwarded-For": "192.168.1.100",
        }
        resp = self._request_with_headers(headers)
        if resp:
            print(f"  {Fore.CYAN}HTTP {resp.status_code} | {len(resp.text)} bytes{Style.RESET_ALL}")
        return resp

    def test_different_ip(self) -> bool:
        """Replay with a different X-Forwarded-For IP."""
        print(f"  {Fore.CYAN}Replay from different IP (X-Forwarded-For){Style.RESET_ALL}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "X-Forwarded-For": "203.0.113.50",
        }
        resp = self._request_with_headers(headers)
        return self._check_replayed(resp, "different IP")

    def test_foreign_ip_geo(self) -> bool:
        """Replay with foreign IP and different User-Agent."""
        print(f"  {Fore.CYAN}Replay from foreign IP + different UA{Style.RESET_ALL}")
        headers = {
            "User-Agent": "curl/8.0.1",
            "X-Forwarded-For": "45.33.32.156",
            "X-Real-IP": "45.33.32.156",
            "CF-Connecting-IP": "45.33.32.156",
        }
        resp = self._request_with_headers(headers)
        return self._check_replayed(resp, "foreign IP + curl UA")

    def test_mobile_ua(self) -> bool:
        """Replay with mobile User-Agent and different IP."""
        print(f"  {Fore.CYAN}Replay from mobile UA + different IP{Style.RESET_ALL}")
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                          "AppleWebKit/605.1.15 Mobile/15E148",
            "X-Forwarded-For": "10.0.0.55",
        }
        resp = self._request_with_headers(headers)
        return self._check_replayed(resp, "mobile UA")

    def test_xff_spoofing(self) -> bool:
        """Replay with multiple X-Forwarded-For hops."""
        print(f"  {Fore.CYAN}Replay with X-Forwarded-For chain (tor exit){Style.RESET_ALL}")
        headers = {
            "User-Agent": "python-requests/2.31.0",
            "X-Forwarded-For": "198.51.100.7, 192.0.2.44, 10.0.0.1",
            "X-Real-IP": "198.51.100.7",
        }
        resp = self._request_with_headers(headers)
        return self._check_replayed(resp, "XFF chain spoof")

    def test_empty_headers(self) -> bool:
        """Replay without IP headers, minimal User-Agent."""
        print(f"  {Fore.CYAN}Replay with minimal headers (no IP info){Style.RESET_ALL}")
        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)",
        }
        resp = self._request_with_headers(headers)
        return self._check_replayed(resp, "minimal headers")

    def _check_replayed(self, resp: Optional[requests.Response], test_name: str) -> bool:
        """Check if the replayed request was accepted. Returns True if vulnerable."""
        if resp is None:
            return False
        status = resp.status_code
        body = resp.text

        print(f"  {Fore.CYAN}HTTP {status} | {len(body)} bytes{Style.RESET_ALL}")

        # Successful response means token was accepted (vulnerable to replay)
        if status in (200, 200, 204):
            print(f"  {Fore.RED}[VULNERABLE] Token accepted for {test_name} - "
                  f"no token binding!{Style.RESET_ALL}")
            return True

        # Auth error means server validated context
        if status in (401, 403):
            print(f"  {Fore.GREEN}[SECURE] Token rejected for {test_name} "
                  f"(HTTP {status}){Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}[WARN] Unexpected status {status} for {test_name}{Style.RESET_ALL}")

        return False

    def check_dpop_support(self) -> None:
        """Check if the server advertises DPoP support."""
        try:
            resp = self.session.get(
                self.token_endpoint,
                headers={"User-Agent": "TokenReplayTester/1.0"},
                timeout=self.timeout,
            )
            www_auth = resp.headers.get("WWW-Authenticate", "")
            if "dpop" in www_auth.lower():
                print(f"  {Fore.GREEN}[+] Server advertises DPoP support "
                      f"(token binding available){Style.RESET_ALL}")
            elif "bearer" in www_auth.lower():
                print(f"  {Fore.YELLOW}[!] Server advertises Bearer only - "
                      f"no token binding{Style.RESET_ALL}")
            else:
                print(f"  {Fore.YELLOW}[!] No token binding advertisement detected{Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            print(f"  {Fore.YELLOW}[!] Could not check DPoP advertisement{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="OAuth Token Replay Detection - Test if tokens are accepted "
                    "from different IPs/User-Agents (token binding validation)",
        epilog="MITRE ATT&CK: T1525 (Implant Container Image), T1190 (Exploit Public-Facing Application)"
    )
    parser.add_argument("-t", "--token-endpoint", required=True,
                        help="OAuth token endpoint URL")
    parser.add_argument("-k", "--token", required=True,
                        help="Access token to test replay with")
    parser.add_argument("-r", "--resource-url",
                        default="https://api.example.com/userinfo",
                        help="Resource URL to test the token against (default: "
                             "https://api.example.com/userinfo)")
    parser.add_argument("--timeout", type=int, default=15,
                        help="Request timeout in seconds (default: 15)")
    args = parser.parse_args()

    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  OAuth Token Replay Detection Tool{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  Token Endpoint: {args.token_endpoint}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  Resource URL:   {args.resource_url}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")

    tester = TokenReplayTester(
        args.token_endpoint, args.token, args.resource_url, args.timeout
    )

    # Step 1: Check DPoP / token binding advertisement
    print(f"\n{Fore.BLUE}[*] Step 1: Token binding capability check{Style.RESET_ALL}")
    tester.check_dpop_support()
    if not RUNNING:
        sys.exit(0)

    # Step 2: Baseline
    print(f"\n{Fore.BLUE}[*] Step 2: Baseline request (same context){Style.RESET_ALL}")
    baseline = tester.test_baseline()
    if baseline is None:
        print(f"  {Fore.RED}[!] Baseline failed - target unreachable{Style.RESET_ALL}")
        sys.exit(1)
    if not RUNNING:
        sys.exit(0)

    baseline_accepted = baseline.status_code in (200, 200, 204)
    if not baseline_accepted:
        print(f"  {Fore.YELLOW}[!] Token rejected even in baseline - "
              f"token may be invalid or expired{Style.RESET_ALL}")

    # Step 3-7: Replay tests
    tests = [
        ("Step 3: Different IP", tester.test_different_ip),
        ("Step 4: Foreign IP + curl UA", tester.test_foreign_ip_geo),
        ("Step 5: Mobile UA", tester.test_mobile_ua),
        ("Step 6: XFF chain spoofing", tester.test_xff_spoofing),
        ("Step 7: Minimal headers", tester.test_empty_headers),
    ]

    vulnerable_count = 0
    for label, test_func in tests:
        if not RUNNING:
            break
        print(f"\n{Fore.BLUE}[*] {label}{Style.RESET_ALL}")
        if test_func():
            vulnerable_count += 1

    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    if vulnerable_count > 0:
        print(f"{Fore.RED}[!] VULNERABLE: {vulnerable_count}/5 replay tests "
              f"succeeded - token binding missing{Style.RESET_ALL}")
        print(f"{Fore.RED}[!] Implement DPoP, mTLS, or token binding{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[+] SECURE: All replay tests rejected - "
              f"token binding is enforced{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
