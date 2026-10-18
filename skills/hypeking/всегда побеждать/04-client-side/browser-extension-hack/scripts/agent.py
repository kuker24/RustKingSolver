#!/usr/bin/env python3
"""
browser-extension-hack/scripts/agent.py
Browser Extension Security Tester — analyze manifests for vulnerabilities.
MITRE ATT&CK: T1190 (Exploit Public-Facing Application), T1203 (Exploitation for Client Execution)
"""
import argparse, json, os, re, signal, sys, tempfile, zipfile, io
from pathlib import Path
try:
    import requests
except ImportError:
    requests = None
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore: RED=GREEN=YELLOW=CYAN=MAGENTA=WHITE=RESET=""
    class Style: BRIGHT=DIM=NORMAL=RESET_ALL=""
    class init: autoreset=lambda: None

active = True
def signal_handler(sig, frame):
    global active
    if active: print(f"\n{Fore.YELLOW}[!] Interrupted{Style.RESET_ALL}")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

CHECKS = {
    "dangerous": ["tabs", "<all_urls>", "webRequest", "debugger", "activeTab", "clipboardRead", "nativeMessaging", "scripting"],
    "csp_high": ["'unsafe-inline'", "'unsafe-eval'"],
}

def load_manifest(path):
    path = Path(path)
    if path.is_dir():
        mf = path / "manifest.json"
        if not mf.exists(): raise FileNotFoundError(f"manifest.json not found in {path}")
        return json.loads(mf.read_text()), path
    raw = path.read_bytes()
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for name in z.namelist():
                if name.endswith("manifest.json"):
                    with z.open(name) as mf: return json.load(mf), path
    except zipfile.BadZipFile: pass
    raise ValueError(f"Could not extract manifest.json from {path}")

def check_permissions(manifest, version):
    findings = []
    perms = manifest.get("permissions", [])
    host_perms = manifest.get("host_permissions", []) if version == 3 else []
    allp = perms + host_perms
    for dp in CHECKS["dangerous"]:
        if dp in allp: findings.append({"severity": "HIGH", "check": "dangerous_permission", "detail": f"Requests '{dp}' — over-privilege risk"})
    for cs in manifest.get("content_scripts", []):
        for m in cs.get("matches", []):
            if m in ("<all_urls>", "http://*/*", "https://*/*", "*://*/*"):
                findings.append({"severity": "MEDIUM", "check": "broad_content_script", "detail": f"Content script matches '{m}' — runs everywhere"})
                break
    return findings

def check_csp(manifest):
    findings = []
    csp = manifest.get("content_security_policy", {})
    csp_str = csp if isinstance(csp, str) else csp.get("extension_pages", "")
    if not csp_str:
        findings.append({"severity": "LOW", "check": "missing_csp", "detail": "No CSP defined"})
        return findings
    for cs in CHECKS["csp_high"]:
        if cs in csp_str: findings.append({"severity": "HIGH", "check": "csp_"+cs.strip("'"), "detail": f"CSP allows {cs} — injection risk"})
    return findings

def check_externally_connectable(manifest):
    findings = []
    ec = manifest.get("externally_connectable", {})
    matches = ec.get("matches", [])
    if "*://*/*" in matches or "*" in str(matches):
        findings.append({"severity": "HIGH", "check": "ec_wildcard", "detail": "externally_connectable allows all origins"})
    return findings

def check_storage_exposure(manifest):
    findings = []
    perms = manifest.get("permissions", [])
    if "storage" in perms: findings.append({"severity": "INFO", "check": "storage_perm", "detail": "Uses storage API — review data hygiene"})
    if "unlimitedStorage" in perms: findings.append({"severity": "MEDIUM", "check": "unlimited_storage", "detail": "unlimitedStorage — data exfil vector"})
    return findings

def check_background_scripts(manifest):
    findings = []
    bg = manifest.get("background", {})
    if manifest.get("manifest_version", 2) == 2:
        if bg.get("scripts") and "persistent" in bg and not bg["persistent"]:
            findings.append({"severity": "MEDIUM", "check": "non_persistent_bg", "detail": "Non-persistent background page may miss critical events"})
    else:
        sw = bg.get("service_worker", "")
        if "eval" in sw.lower(): findings.append({"severity": "HIGH", "check": "sw_eval", "detail": "Service worker suggests dynamic code eval"})
    return findings

def scan_extension(path, quiet=False):
    try: manifest, src = load_manifest(path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e: print(f"{Fore.RED}[!] {e}{Style.RESET_ALL}"); return None
    version = manifest.get("manifest_version", 2)
    name = manifest.get("name", "Unnamed")
    if not quiet:
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} {name} v{manifest.get('version','0')} (MV{version}){Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    checks = [("Permissions",check_permissions(manifest,f"v{version}")),("CSP",check_csp(manifest)),("Connectable",check_externally_connectable(manifest)),("Storage",check_storage_exposure(manifest)),("Background",check_background_scripts(manifest))]
    allf = []
    for cn, cf in checks:
        if not cf: continue
        allf.extend(cf)
        if not quiet:
            print(f"\n{Fore.YELLOW}[{cn}]{Style.RESET_ALL}")
            for f in cf:
                c = {"HIGH":Fore.RED,"MEDIUM":Fore.YELLOW,"LOW":Fore.CYAN,"INFO":Fore.GREEN}.get(f["severity"],Fore.WHITE)
                print(f"  {c}[{f['severity']:>6}]{Style.RESET_ALL} {f['detail']}")
    if not quiet:
        print(f"\n{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        for s in ["HIGH","MEDIUM","LOW","INFO"]:
            n = sum(1 for f in allf if f["severity"]==s)
            if n: print(f"  {Fore.RED if s=='HIGH' else Fore.YELLOW if s=='MEDIUM' else Fore.CYAN}{s}: {n}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    return {"name":name,"version":manifest.get("version","0"),"manifest_version":version,"findings":allf}

def scan_url(url, quiet=False):
    if requests is None: print(f"{Fore.RED}[!] requests required for URL scanning{Style.RESET_ALL}"); return None
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".crx") as t:
            t.write(r.content)
            p = t.name
        result = scan_extension(p, quiet=quiet)
        os.unlink(p)
        return result
    except requests.RequestException as e: print(f"{Fore.RED}[!] Download failed: {e}{Style.RESET_ALL}"); return None

def main():
    parser = argparse.ArgumentParser(description="Browser Extension Security Tester")
    parser.add_argument("path", nargs="?", help="Extension path, .crx, or URL")
    parser.add_argument("-o","--output", help="Output JSON report")
    parser.add_argument("-q","--quiet", action="store_true")
    parser.add_argument("--dump", action="store_true")
    args = parser.parse_args()
    if not args.path: parser.print_help(); sys.exit(1)
    result = scan_url(args.path, quiet=args.quiet) if re.match(r"^https?://", args.path) else scan_extension(args.path, quiet=args.quiet)
    if result is None: sys.exit(1)
    if args.dump: print(json.dumps(result, indent=2))
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f: json.dump(result, f, indent=2)
        print(f"{Fore.GREEN}[+] Written to {args.output}{Style.RESET_ALL}")
    if any(f["severity"]=="HIGH" for f in result["findings"]): sys.exit(2)

if __name__ == "__main__":
    main()
