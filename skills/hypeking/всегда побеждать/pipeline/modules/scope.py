#!/usr/bin/env python3
"""Deterministic scope guard — ported from opencode-pentester engine/scope_guard.py.

No LLM reasoning involved — pure O(1) checks. The only network activity is
DNS resolution of the target itself.
"""
import ipaddress
import socket
import sys
from urllib.parse import urlsplit

BANNED_NETWORKS = [
    "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8",
    "169.254.0.0/16", "172.16.0.0/12", "192.0.0.0/24",
    "192.0.2.0/24", "192.168.0.0/16", "198.18.0.0/15",
    "198.51.100.0/24", "203.0.113.0/24",
    "224.0.0.0/4", "240.0.0.0/4",
    "::/128", "::1/128", "fc00::/7", "fe80::/10", "ff00::/8", "2001:db8::/32"
]

_BANNED = [ipaddress.ip_network(net, strict=False) for net in BANNED_NETWORKS]


def normalize_target(target_str: str) -> str:
    """Extract hostname from a URL or bare host. Empty string if malformed."""
    value = (target_str or "").strip()
    if not value:
        return ""
    try:
        parsed = urlsplit(value if "://" in value else f"//{value}")
        hostname = parsed.hostname
    except ValueError:
        return ""
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return ""
    if parsed.username or parsed.password:
        return ""
    return hostname or ""


def is_banned_ip(ip_str: str) -> bool:
    """Check if IP falls in a banned (private/reserved/multicast) range."""
    try:
        addr = ipaddress.ip_address(ip_str)
        for net in _BANNED:
            if addr in net:
                return True
        return addr.is_private
    except ValueError:
        return True


def resolve_target(target_str: str):
    """Resolve a target to all addresses.

    Returns (addresses, hostname) where addresses is [] on failure.
    """
    value = (target_str or "").strip()
    try:
        literal = ipaddress.ip_address(value)
        return [str(literal)], ""
    except ValueError:
        pass
    hostname = normalize_target(value)
    if not hostname:
        return [], value
    previous_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(3.0)
    try:
        try:
            records = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        except socket.gaierror:
            return [], hostname
        addresses = []
        for record in records:
            address = record[4][0]
            if address not in addresses:
                addresses.append(address)
        return addresses, hostname
    finally:
        socket.setdefaulttimeout(previous_timeout)


def validate_target(url: str, lab: bool = False):
    """Validate a target against the banned network list.

    Returns (allowed, reason). lab=True permits private/loopback targets so
    local test environments are never blocked.
    """
    addresses, hostname = resolve_target(url)
    if not addresses:
        return False, f"DNS_RESOLVE_FAILED: could not resolve '{url.strip()}'"
    banned = next((addr for addr in addresses if is_banned_ip(addr)), None)
    if banned:
        if lab:
            return True, f"LAB_MODE: private/reserved target {banned} allowed by --lab"
        return False, (
            f"PRIVATE_IP: {banned} resolves into a banned network "
            f"({hostname or url.strip()}). Local labs require --lab."
        )
    return True, f"OK: {addresses[0]}"


def main() -> int:
    args = [a for a in sys.argv[1:] if a not in ("-h", "--help")]
    if not args:
        print(f"Usage: {sys.argv[0]} <url> [--lab]", file=sys.stderr)
        return 1
    lab = "--lab" in args
    target = args[0]
    allowed, reason = validate_target(target, lab=lab)
    status = "ALLOWED" if allowed else "REFUSED"
    print(f"[{status}] {reason}")
    return 0 if allowed else 1


if __name__ == "__main__":
    sys.exit(main())
