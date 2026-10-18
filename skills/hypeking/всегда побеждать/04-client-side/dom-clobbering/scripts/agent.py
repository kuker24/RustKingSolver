#!/usr/bin/env python3
"""
DOM Clobbering Scanner — id/name Collision & document.write Injection

MITRE ATT&CK Mapping:
  T1059 - Command and Scripting Interpreter (client-side JS manipulation)
  T1203 - Exploitation for Client Execution (DOM clobbering payload delivery)

Scans for HTML elements whose id or name attributes conflict with JavaScript
global variables (window, document named access), enabling DOM clobbering attacks.
"""

import argparse
import html.parser
import json
import os
import re
import signal
import sys
import urllib.parse

import requests
from colorama import Fore, Style, init

init(autoreset=True)

SHOULD_EXIT = False


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted.{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
BANNER = f"{Fore.YELLOW}DOM Clobbering Scanner v1{Fore.RESET}"

# Common JS globals that DOM clobbering can override
CLOBBERABLE_GLOBALS = {
    "innerWidth", "innerHeight", "outerWidth", "outerHeight",
    "screenX", "screenY", "pageXOffset", "pageYOffset",
    "location", "navigator", "document", "window", "history",
    "frames", "self", "parent", "top", "opener",
    "name", "status", "closed", "defaultStatus",
    "length", "origin", "isSecureContext",
    "devicePixelRatio", "scrollX", "scrollY",
}

# Named access targets on document that are clobberable via id/name
NAMED_ACCESS_TARGETS = {
    "body", "head", "title", "forms", "images", "links",
    "anchors", "applets", "embeds", "plugins", "scripts",
    "cookie", "domain", "referrer", "URL", "baseURI",
    "activeElement", "characterSet", "compatMode",
    "designMode", "dir", "hidden", "lastModified",
    "readyState", "title", "visibilityState",
}


class DOMClobberParser(html.parser.HTMLParser):
    """Extract id/name attributes from HTML elements."""

    def __init__(self):
        super().__init__()
        self.elements = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        elem_id = attrs_dict.get("id", "")
        elem_name = attrs_dict.get("name", "")
        if elem_id or elem_name:
            self.elements.append({
                "tag": tag,
                "id": elem_id,
                "name": elem_name,
                "attrs": attrs_dict,
            })

    def handle_data(self, data):
        stripped = data.strip()
        if stripped and "<script" in stripped.lower():
            self.scripts.append(stripped)


def fetch_page(url, timeout_sec):
    """Fetch target page and return raw HTML."""
    try:
        resp = requests.get(url, timeout=timeout_sec, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        return resp.status_code, resp.text, resp.url
    except requests.RequestException as e:
        return None, str(e), None


def scan_clobberable_elements(html_content, base_url):
    """Scan HTML for elements whose id/name collide with globals or named access."""
    parser = DOMClobberParser()
    try:
        parser.feed(html_content)
    except Exception:
        pass

    findings = []
    for elem in parser.elements:
        elem_id = elem["id"]
        elem_name = elem["name"]

        # Check id collision with globals
        if elem_id and elem_id in CLOBBERABLE_GLOBALS:
            findings.append({
                "type": "global_collision",
                "attribute": "id",
                "value": elem_id,
                "tag": elem["tag"],
                "target": f"window.{elem_id}",
            })

        # Check id collision with named access on document
        if elem_id and elem_id in NAMED_ACCESS_TARGETS:
            findings.append({
                "type": "named_access_collision",
                "attribute": "id",
                "value": elem_id,
                "tag": elem["tag"],
                "target": f"document.{elem_id}",
            })

        # Check name colliding with globals (form elements especially)
        if elem_name and elem_name in CLOBBERABLE_GLOBALS:
            findings.append({
                "type": "global_collision",
                "attribute": "name",
                "value": elem_name,
                "tag": elem["tag"],
                "target": f"window.{elem_name}",
            })

        # Forms with name attribute create named access on document
        if elem["tag"] == "form" and elem_name:
            findings.append({
                "type": "form_named_access",
                "attribute": "name",
                "value": elem_name,
                "tag": "form",
                "target": f"document.forms['{elem_name}'] / document.{elem_name}",
            })

        # Anchor tags with name or id create named access
        if elem["tag"] == "a" and (elem_id or elem_name):
            findings.append({
                "type": "anchor_named_access",
                "attribute": "id" if elem_id else "name",
                "value": elem_id or elem_name,
                "tag": "a",
                "target": f"window.{elem_id or elem_name}",
            })

    return findings


def check_document_write_patterns(html_content):
    """Check for document.write usage that could enable DOM clobbering injection."""
    patterns = []
    if re.search(r'document\.write\s*\(', html_content, re.IGNORECASE):
        patterns.append("document.write() detected — potential injection sink")
    if re.search(r'document\.writeln\s*\(', html_content, re.IGNORECASE):
        patterns.append("document.writeln() detected — potential injection sink")
    if re.search(r'innerHTML\s*=', html_content, re.IGNORECASE):
        patterns.append("innerHTML assignment detected — DOM clobbering may propagate")
    if re.search(r'outerHTML\s*=', html_content, re.IGNORECASE):
        patterns.append("outerHTML assignment detected — DOM clobbering may propagate")
    if re.search(r'insertAdjacentHTML', html_content, re.IGNORECASE):
        patterns.append("insertAdjacentHTML() detected — DOM clobbering may propagate")
    return patterns


def generate_clobbering_proof(host, clobber_targets):
    """Generate a simple demonstration of how the clobbering works."""
    if not clobber_targets:
        return None
    # Pick the first viable clobber target
    target = clobber_targets[0]
    return (
        f"<!-- DOM Clobbering Proof: overrides {target['target']} -->\n"
        f"<{target['tag']} id=\"{target['value']}\" "
        f"onclick=\"console.log('Clobbered {target['target']}');\"></{target['tag']}>"
    )


def run_scan(target_url, timeout_sec):
    """Run full DOM clobbering scan."""
    print(f"\n{Fore.CYAN}[*] Target: {target_url}{Style.RESET_ALL}")

    status_code, content, final_url = fetch_page(target_url, timeout_sec)
    if status_code is None:
        print(f"{Fore.RED}[X] Failed to fetch target: {content}{Style.RESET_ALL}")
        return None

    print(f"{Fore.CYAN}[*] HTTP {status_code} | {len(content)} bytes{Style.RESET_ALL}")

    findings = scan_clobberable_elements(content, final_url)
    doc_write_patterns = check_document_write_patterns(content)

    result = {
        "target": target_url,
        "final_url": final_url,
        "http_status": status_code,
        "clobberable_elements": findings,
        "dangerous_patterns": doc_write_patterns,
        "element_count": len(findings),
    }

    print(f"\n{Fore.CYAN}  DOM Clobbering Scan Results:{Style.RESET_ALL}")

    if not findings:
        print(f"  {Fore.GREEN}  No clobberable elements detected.{Style.RESET_ALL}")
    else:
        by_type = {}
        for f in findings:
            by_type.setdefault(f["type"], []).append(f)
        for ftype, items in by_type.items():
            print(f"  {Fore.YELLOW}  [{ftype}] {len(items)} element(s){Style.RESET_ALL}")
            for item in items:
                print(f"    <{item['tag']} {item['attribute']}=\"{item['value']}\" "
                      f"-> {item['target']}")

    if doc_write_patterns:
        print(f"\n  {Fore.YELLOW}  Dangerous JS Patterns:{Style.RESET_ALL}")
        for p in doc_write_patterns:
            print(f"    {Fore.YELLOW}[!]{Style.RESET_ALL} {p}")

    if findings:
        proof = generate_clobbering_proof(final_url, findings)
        if proof:
            print(f"\n  {Fore.CYAN}  Clobbering PoC:{Style.RESET_ALL}")
            for line in proof.split("\n"):
                print(f"    {Fore.CYAN}{line}{Style.RESET_ALL}")

    return result


def print_report(result):
    """Print final assessment."""
    if not result:
        return
    print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  DOM CLOBBERING SCAN REPORT{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
    print(f"  Target : {result['target']}")
    print(f"  Status : HTTP {result['http_status']}")
    print(f"  Elements flagged : {result['element_count']}")

    if result["element_count"] > 0:
        print(f"\n  {Fore.RED}VERDICT: POTENTIALLY VULNERABLE{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  Found {result['element_count']} elements that may enable DOM clobbering.{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  An attacker who can inject HTML (via XSS or widget) can override{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  JavaScript globals and subvert application logic.{Style.RESET_ALL}")
    else:
        print(f"\n  {Fore.GREEN}VERDICT: No clobberable elements detected{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}  No id/name collisions with known clobberable targets.{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="DOM Clobbering Scanner — id/name Collision Detection — MITRE T1059, T1203",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py -u https://target.com/page
  python agent.py -u https://target.com/app -t 15
  python agent.py -u https://target.com/page -o results.json
        """,
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL to scan")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    parser.add_argument("-o", "--output", help="Save results to JSON file")
    args = parser.parse_args()

    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)

    result = run_scan(args.url, args.timeout)
    print_report(result)

    if args.output and result:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Results saved to {args.output}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}[*] Scan complete.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
