#!/usr/bin/env python3
"""
WebRTC Security Scanner

Tests for WebRTC local IP leakage, STUN/TURN configuration exposure,
and media stream security vulnerabilities in web applications.

MITRE ATTACK:
  T1046 - Network Service Scanning
  T1190 - Exploit Public-Facing Application
"""

import argparse
import json
import signal
import socket
import struct
import sys
import time
from urllib.parse import urlparse

try:
    import requests
    from colorama import Fore, Style, init
except ImportError:
    raise SystemExit("Missing dependencies: pip install requests colorama")

init(autoreset=True)
stop_flag = False


def sigint_handler(sig, frame):
    global stop_flag
    print(f"\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
    stop_flag = True
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


STUN_SERVERS = [
    "stun.l.google.com:19302",
    "stun1.l.google.com:19302",
    "stun2.l.google.com:19302",
    "stun3.l.google.com:19302",
    "stun4.l.google.com:19302",
    "stun.stunprotocol.org:3478",
]


def banner():
    print(f"""{Fore.CYAN}
  WebRTC Security Scanner
  IP leak / STUN TURN / media security
{Style.RESET_ALL}""")


def stun_request(server, timeout=5):
    """Send a STUN binding request to detect reflexive address."""
    try:
        host, port = server.split(":")
        port = int(port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)

        transaction_id = struct.pack("!I", 0x2112A442) + b"\x00" * 12
        msg_type = 0x0001
        msg_len = 0
        header = struct.pack("!HH", msg_type, msg_len) + transaction_id
        sock.sendto(header, (host, port))

        data, addr = sock.recvfrom(1024)
        sock.close()

        if len(data) >= 20:
            resp_type = struct.unpack("!H", data[0:2])[0]
            if resp_type == 0x0101:
                return {"server": server, "reachable": True, "response": True}
        return {"server": server, "reachable": True, "response": False}
    except (socket.timeout, OSError, ValueError) as e:
        return {"server": server, "reachable": False, "error": str(e)}


def check_turn_config(url, timeout=10):
    """Fetch TURN configuration from common endpoints."""
    endpoints = [
        "/turn", "/turn/credentials", "/webrtc/turn",
        "/api/turn", "/v1/turn", "/turnconfig",
    ]
    results = []
    base = url.rstrip("/")
    for ep in endpoints:
        if stop_flag:
            break
        try:
            resp = requests.get(f"{base}{ep}", timeout=timeout, verify=False)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if "uris" in data or "iceServers" in data:
                        results.append({"endpoint": ep, "exposed": True, "config": data})
                    else:
                        results.append({"endpoint": ep, "exposed": False})
                except json.JSONDecodeError:
                    results.append({"endpoint": ep, "exposed": False})
            else:
                results.append({"endpoint": ep, "exposed": False})
        except requests.RequestException:
            results.append({"endpoint": ep, "exposed": False, "error": "timeout"})
    return results


def check_local_ip_leak(target, timeout=10):
    """Fetch target page and look for WebRTC IP leak patterns."""
    try:
        resp = requests.get(target, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        })
        body = resp.text.lower()
        findings = {
            "rtcpeerconnection": "RTCPeerConnection" in body,
            "createoffer": "createOffer" in body,
            "createanswer": "createAnswer" in body,
            "localip": any(x in body for x in ["10.0.", "192.168.", "172.16.", "127.0.0.1"]),
            "stun_url": "stun:" in body,
            "turn_url": "turn:" in body,
            "ice_servers": "iceServers" in body,
        }
        sip = body.count("stun:")
        tip = body.count("turn:")
        return findings, sip, tip
    except requests.RequestException as e:
        return {"error": str(e)}, 0, 0


def scan_webrtc(target, stun_test, turn_test, timeout):
    print(f"{Fore.YELLOW}[*] Target: {target}{Style.RESET_ALL}\n")

    print(f"{Fore.CYAN}[>] Checking for WebRTC in page source...{Style.RESET_ALL}")
    findings, stun_count, turn_count = check_local_ip_leak(target, timeout)
    if "error" in findings:
        print(f"{Fore.RED}[!] Error fetching page: {findings['error']}{Style.RESET_ALL}")
        return

    if findings.get("rtcpeerconnection"):
        print(f"{Fore.RED}[!] RTCPeerConnection detected (WebRTC active){Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[+] No RTCPeerConnection found in page source{Style.RESET_ALL}")

    if stun_count > 0:
        print(f"{Fore.RED}[!] STUN URLs found: {stun_count}{Style.RESET_ALL}")
    if turn_count > 0:
        print(f"{Fore.RED}[!] TURN URLs found: {turn_count}{Style.RESET_ALL}")
    if findings.get("ice_servers"):
        print(f"{Fore.RED}[!] iceServers configuration exposed in source{Style.RESET_ALL}")
    if findings.get("localip"):
        print(f"{Fore.YELLOW}[*] Local IP patterns detected in content{Style.RESET_ALL}")
    print()

    if stun_test:
        print(f"{Fore.CYAN}[>] Testing STUN server reachability...{Style.RESET_ALL}")
        for server in STUN_SERVERS:
            if stop_flag:
                break
            result = stun_request(server, timeout)
            if result["reachable"]:
                print(f"{Fore.GREEN}[+] {server}: reachable{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[-] {server}: unreachable ({result.get('error', 'timeout')}){Style.RESET_ALL}")
        print()

    if turn_test:
        print(f"{Fore.CYAN}[>] Checking TURN config endpoints...{Style.RESET_ALL}")
        configs = check_turn_config(target, timeout)
        for c in configs:
            if c.get("exposed"):
                print(f"{Fore.RED}[!] TURN config exposed at {c['endpoint']}: {json.dumps(c['config'], indent=2)}{Style.RESET_ALL}")
            elif "error" in c:
                print(f"{Fore.YELLOW}[-] {c['endpoint']}: timeout{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[+] {c['endpoint']}: no exposure{Style.RESET_ALL}")
        print()

    print(f"{Fore.CYAN}[>] Security recommendations:{Style.RESET_ALL}")
    if findings.get("rtcpeerconnection"):
        print("  - Use iceServers with authentication for TURN")
        print("  - Implement STUN-only mode for internal networks")
        print("  - Set 'RTCConfiguration.iceTransportPolicy = relay' for sensitive apps")
    if findings.get("ice_servers"):
        print("  - Do not hardcode ICE server credentials in page source")
        print("  - Use ephemeral TURN credentials with short TTL")


def main():
    parser = argparse.ArgumentParser(description="WebRTC Security Scanner")
    parser.add_argument("-t", "--target", required=True, help="Target URL")
    parser.add_argument("--stun", action="store_true", default=True, help="Test STUN server reachability")
    parser.add_argument("--no-stun", action="store_false", dest="stun", help="Skip STUN tests")
    parser.add_argument("--turn", action="store_true", default=True, help="Check TURN config endpoints")
    parser.add_argument("--no-turn", action="store_false", dest="turn", help="Skip TURN config check")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    args = parser.parse_args()
    banner()
    scan_webrtc(args.target, args.stun, args.turn, args.timeout)


if __name__ == "__main__":
    main()
