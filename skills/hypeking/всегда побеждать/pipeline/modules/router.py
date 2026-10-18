#!/usr/bin/env python3
"""JIT service/tech -> skill router — ported from opencode-pentester engine/router.py.

Domain mapping is a verbatim port of Router._domain_for_service; domains are
then mapped onto this suite's category directories. File-based only — no
database, no network calls.
"""
import os
from typing import Dict, List

SUITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Verbatim from engine/router.py _domain_for_service.
SERVICE_DOMAIN_MAP = {
    "http": "Discovery", "https": "Discovery", "http-proxy": "Discovery",
    "ssh": "Network", "ftp": "Network", "telnet": "Network",
    "smtp": "Network", "pop3": "Network", "imap": "Network",
    "dns": "Network", "dhcp": "Network",
    "mysql": "Injection", "postgresql": "Injection", "postgres": "Injection",
    "mssql": "Injection", "oracle": "Injection", "redis": "Injection",
    "mongod": "Injection", "mongodb": "Injection",
    "ldap": "Network", "ldaps": "Network",
    "smb": "Network", "netbios-ssn": "Network", "microsoft-ds": "Network",
    "kerberos": "Auth", "kpasswd": "Auth",
    "rpc": "Network", "msrpc": "Network",
    "winrm": "Post", "exec": "Post",
    "s3": "Cloud", "aws": "Cloud",
    "git": "SAST", "svn": "SAST",
}

WEB_PORTS = {80, 443, 8080, 8443, 3000, 5000, 8000, 8888, 9090, 9443}

# Suite categories reachable by each domain.
DOMAIN_CATEGORIES = {
    "Discovery": ["01-recon", "10-adv-recon"],
    "Network": ["11-network-web"],
    "Injection": ["14-exploit-arsenal"],
    "Auth": ["05-auth-oauth"],
    "Post": ["18-post-exploit"],
    "Cloud": ["08-cloud-web"],
    "SAST": ["06-automation"],
}

# Example skills per domain (category/skill relative to SUITE_ROOT).
DOMAIN_EXAMPLE_SKILLS = {
    "Discovery": [
        "01-recon/httpx-smart-recon",
        "01-recon/katana-crawler-auto",
        "01-recon/recon-methodology",
    ],
    "Network": [
        "11-network-web/analyzing-network-packets-with-scapy",
        "11-network-web/detecting-exfiltration-over-dns-with-zeek",
    ],
    "Injection": [
        "14-exploit-arsenal/exploiting-nosql-injection-vulnerabilities",
        "14-exploit-arsenal/exploiting-type-juggling-vulnerabilities",
        "14-exploit-arsenal/exploiting-jwt-algorithm-confusion-attack",
    ],
    "Auth": [
        "05-auth-oauth/oauth-token-replay",
        "05-auth-oauth/oauth-pkce-downgrade",
    ],
    "Post": [
        "18-post-exploit/linux-postexploit",
        "18-post-exploit/windows-postexploit",
        "18-post-exploit/kerberos-attacks",
    ],
    "Cloud": [
        "08-cloud-web/auditing-aws-s3-bucket-permissions",
        "08-cloud-web/detecting-aws-credential-exposure-with-trufflehog",
    ],
    "SAST": [
        "06-automation/cicd-attacks",
        "06-automation/exploit-chain-automation",
    ],
}

# Detected-technology keywords -> (domain, suite skills).
TECH_KEYWORDS = {
    "wordpress": ("Discovery", ["03-exploit/graphql-introspection-abuse"]),
    "nginx": ("Discovery", ["01-recon/httpx-smart-recon"]),
    "apache": ("Discovery", ["01-recon/httpx-smart-recon"]),
    "aws": ("Cloud", ["08-cloud-web/auditing-aws-s3-bucket-permissions"]),
    "s3": ("Cloud", ["08-cloud-web/auditing-aws-s3-bucket-permissions"]),
    "azure": ("Cloud", ["08-cloud-web/detecting-azure-storage-account-misconfigurations"]),
    "gcp": ("Cloud", ["08-cloud-web/auditing-gcp-iam-permissions"]),
    "graphql": ("Discovery", ["03-exploit/graphql-batching-attack", "03-exploit/graphql-introspection-abuse"]),
    "jwt": ("Auth", ["17-attack-core/attack-jwt", "14-exploit-arsenal/exploiting-jwt-algorithm-confusion-attack"]),
    "oauth": ("Auth", ["05-auth-oauth/oauth-token-replay", "12-red-team-web/attacking-oauth-with-device-code-phishing"]),
    "cloudflare": ("Discovery", ["02-waf-bypass/cloudflare-waf-bypass"]),
    "akamai": ("Discovery", ["02-waf-bypass/akamai-waf-bypass"]),
    "waf": ("Discovery", ["02-waf-bypass/cloudflare-waf-bypass"]),
    "php": ("Discovery", ["01-recon/param-miner-advanced"]),
    "react": ("Discovery", ["01-recon/katana-crawler-auto"]),
    "node": ("Discovery", ["01-recon/katana-crawler-auto"]),
    "mysql": ("Injection", ["14-exploit-arsenal/exploiting-sql-injection-vulnerabilities"]),
    "postgres": ("Injection", ["14-exploit-arsenal/exploiting-sql-injection-vulnerabilities"]),
    "mongodb": ("Injection", ["14-exploit-arsenal/exploiting-nosql-injection-vulnerabilities"]),
    "redis": ("Injection", ["14-exploit-arsenal/exploiting-nosql-injection-vulnerabilities"]),
    "docker": ("Post", ["18-post-exploit/linux-postexploit"]),
    "kubernetes": ("Post", ["18-post-exploit/k8s-postexploit"]),
    "kerberos": ("Auth", ["18-post-exploit/kerberos-attacks"]),
    "smb": ("Network", ["11-network-web/analyzing-network-traffic-with-wireshark"]),
    "ssh": ("Network", ["11-network-web/analyzing-network-traffic-for-incidents"]),
    "smtp": ("Network", ["11-network-web/detecting-exfiltration-over-dns-with-zeek"]),
}


def domain_for_service(svc_name, port=None) -> str:
    """Verbatim port of Router._domain_for_service (DB-free)."""
    if svc_name:
        svc_lower = svc_name.lower()
        for key, domain in SERVICE_DOMAIN_MAP.items():
            if key in svc_lower:
                return domain
    if port in WEB_PORTS:
        return "Discovery"
    return "Network"


def category_dir_exists(category: str) -> bool:
    return os.path.isdir(os.path.join(SUITE_ROOT, category))


def skill_dir_exists(skill_path: str) -> bool:
    return os.path.isdir(os.path.join(SUITE_ROOT, skill_path))


def classify(recon_results: Dict) -> Dict[str, List[str]]:
    """Map recon output onto suite categories.

    Reads the recon engine's result shape: services (port/protocol/service)
    plus technologies (name/confidence). Returns {domain: [category paths +
    example skill paths]}.
    """
    routed: Dict[str, List[str]] = {}
    for svc in recon_results.get("services") or []:
        if isinstance(svc, dict):
            svc_name = svc.get("service") or svc.get("name") or ""
            port = svc.get("port")
        else:
            svc_name, port = svc, None
        domain = domain_for_service(svc_name, port)
        entries = routed.setdefault(domain, [])
        for category in DOMAIN_CATEGORIES.get(domain, []):
            if category_dir_exists(category) and category not in entries:
                entries.append(category)
        for example in DOMAIN_EXAMPLE_SKILLS.get(domain, []):
            if example not in entries:
                entries.append(example)

    for tech in recon_results.get("technologies") or []:
        name = (tech.get("name") if isinstance(tech, dict) else str(tech)) or ""
        recommendation = recommend(name)
        if not recommendation:
            continue
        domain, skills = recommendation
        entries = routed.setdefault(domain, [])
        for category in DOMAIN_CATEGORIES.get(domain, []):
            if category_dir_exists(category) and category not in entries:
                entries.append(category)
        for skill in skills:
            if skill_dir_exists(skill) and skill not in entries:
                entries.append(skill)

    return routed


def recommend(tech_name: str):
    """Map a detected technology keyword onto domain + concrete suite skills."""
    lowered = (tech_name or "").lower()
    for keyword, (domain, skills) in TECH_KEYWORDS.items():
        if keyword in lowered:
            live = [s for s in skills if skill_dir_exists(s)]
            return domain, live
    return None


if __name__ == "__main__":
    import json, sys
    sample = {"services": [{"port": 443, "protocol": "tcp", "service": "https"}],
              "technologies": [{"name": "wordpress", "confidence": 0.9}]}
    print(json.dumps(classify(sample), indent=2))
