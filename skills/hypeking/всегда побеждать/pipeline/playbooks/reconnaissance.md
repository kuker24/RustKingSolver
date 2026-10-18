---
name: Reconnaissance Playbook
description: Attack surface mapping and target discovery — mandatory execution for all phases
mode: agent
max_phases: 3
mandatory_tools:
  - subfinder
  - amass
  - dnsx
  - httpx
  - nmap
  - masscan
  - smap
  - katana
  - gau
  - waybackurls
  - crt.sh
  - whatweb
  - ffuf
  - gobuster
  - feroxbuster
  - dirsearch
  - arjun
  - paramspider
  - kiterunner
  - nuclei
  - nikto
preflight_checks:
  - Verify every tool in mandatory_tools is installed and accessible via PATH
  - Verify target domain resolves and is scoped in the authorization letter
  - Verify output directories exist: recon/{passive,active,correlation}/
  - Verify rate-limit and timeout configs match target scope agreement
---

## Phase 1: Passive Reconnaissance

**Objective**: Gather intelligence without touching the target infrastructure. Every tool listed below MUST be run against the target.

### 0.5 Preflight (MANDATORY — before ANY tool runs)

```bash
# Install every missing required tool and log the doctor preflight PASS row
bash db/doctor.sh --install                      # network; refuses with PENTEST_NO_NETWORK=1
bash db/doctor.sh --preflight-log                # offline: audit + log PASS/FAIL row
bash db/findings.sh gate --phase recon           # exit 0 ONLY after PASS row + recon evidence
```

NOTE: Every discovered-but-unexplored surface (subdomain, vhost, endpoint, port,
credential, header, param, CVE) MUST be recorded with `findings.sh lead add ...`
DURING recon — even if you intend to test it later. The gate blocks "done" while
any lead stays open; `findings.sh push` resurfaces abandoned leads every run.

### 1.1 Subdomain Enumeration

- **subfinder** — Run `subfinder -d TARGET -all -recursive -o recon/passive/subfinder.txt` (all sources, recursive).
- **amass (passive)** — Run `amass enum -passive -d TARGET -config amass_config.ini -o recon/passive/amass_passive.txt`.
- **crt.sh** — Run `curl -s "https://crt.sh/?q=%25.TARGET&output=json" | jq -r '.[].name_value' | sort -u > recon/passive/crtsh.txt`.
- **Merge** — Run `cat recon/passive/subfinder.txt recon/passive/amass_passive.txt recon/passive/crtsh.txt | sort -u > recon/passive/all_subdomains.txt`.

### 1.2 DNS Resolution

- **dnsx** — Run `dnsx -l recon/passive/all_subdomains.txt -a -aaaa -cname -mx -txt -ns -resp -o recon/passive/dns_records.txt`.
- **dnsx (resolved-only)** — Run `dnsx -l recon/passive/all_subdomains.txt -a -silent -o recon/passive/resolved_ips.txt`.

### 1.3 HTTP Probing

- **httpx** — Run `httpx -l recon/passive/resolved_ips.txt -title -tech-detect -status-code -content-length -webserver -ip -ports 80,443,8080,8443,9000 -o recon/passive/httpx_probed.txt`.

### 1.4 Web Crawling & Historical Discovery

- **katana (passive)** — Run `katana -list recon/passive/httpx_probed.txt -passive -known-files all -silent -o recon/passive/katana_passive.txt`.
- **gau**: Run `target="example.com"; gau "$target" --subs | python3 engine/scope_guard.py --filter --scope "$target" | sort -u > recon/passive/gau_urls.txt`.
- **waybackurls** — Run `waybackurls TARGET | sort -u > recon/passive/wayback_urls.txt`.
- **Merge URLs** — Run `cat recon/passive/katana_passive.txt recon/passive/gau_urls.txt recon/passive/wayback_urls.txt | sort -u > recon/passive/all_urls.txt`.

### 1.5 Technology Detection

- **whatweb** — Run `whatweb -i recon/passive/httpx_probed.txt --aggression 3 -v > recon/passive/whatweb_scan.txt`.
- **httpx (tech-detect)** — Already captured in 1.3 httpx output via `-tech-detect` flag.

### 1.6 WHOIS Lookups

- **whois** — Run `whois TARGET > recon/passive/whois.txt`.
- **whois (all subdomains)** — Run `xargs -a recon/passive/all_subdomains.txt -P10 -I{} sh -c 'whois {} 2>/dev/null | head -20' > recon/passive/whois_subdomains.txt`.

### 1.7 Search Engine Dorking

- **Google dorks** — Run search queries against Google for:
  - `site:TARGET intitle:"index of"` → save to `recon/passive/dorks_google.txt`
  - `site:TARGET ext:log | ext:sql | ext:env | ext:bak` → append to dork file
  - `site:TARGET inurl:admin | inurl:config | inurl:backup` → append
  - `site:TARGET intitle:"dashboard" | intitle:"login"` → append
- **Bing dorks** — Run:
  - `site:TARGET ip:port` → `recon/passive/dorks_bing.txt`
  - `site:TARGET "db_password" | "connection string"` → append
- **Shodan/smap** — Run `smap -p 1-65535 TARGET_IP -oN recon/passive/shodan_smap.txt` (requires Smap/Shodan API).

### 1.8 DNS Zone Transfers (Passive Check)

- **dnsx (axfr)** — Run `dnsx -l recon/passive/all_subdomains.txt -axfr -o recon/passive/axfr_results.txt`.

---

## Phase 2: Active Reconnaissance

**Objective**: Directly probe the target to map attack surface. Every tool listed below MUST be run against the target.

### 2.0 Anti-Bot / Challenge-Wall Precheck (MANDATORY before any active probe)

Classify every target vhost BEFORE running nmap/ffuf/katana against it — a
challenge wall wastes budget and pollutes results with boilerplate responses.

```bash
export PENTEST_ENGAGEMENT=<engagement>
bash db/webchallenge.sh fetch "https://TARGET" --json      # exit 0 = clean
bash db/webchallenge.sh fetch "https://TARGET"             # human-readable
```

When `kind != clean`: log a note (`findings.sh log recon webchallenge ...`),
skip brute-force/crawling on that vhost, and pivot to alternate origins
(staging vhosts, IP-based access, other subdomains) before treating it as dead.

### 2.1 Port Scanning

- **nmap (quick top-1000)** — Run `nmap -sS -sV -T4 --top-ports 1000 -iL recon/passive/resolved_ips.txt -oN recon/active/nmap_quick.txt -oX recon/active/nmap_quick.xml`.
- **nmap (full all-ports)** — Run `nmap -sS -sV -T4 -p- -iL recon/passive/resolved_ips.txt -oN recon/active/nmap_full.txt -oX recon/active/nmap_full.xml`.
- **nmap (UDP)** — Run `nmap -sU -T4 --top-ports 100 -iL recon/passive/resolved_ips.txt -oN recon/active/nmap_udp.txt`.
- **nmap (stealth)** — Run `nmap -sS -sV -T2 --top-ports 1000 -iL recon/passive/resolved_ips.txt -oN recon/active/nmap_stealth.txt`.
- **nmap (OS-detection)** — Run `nmap -O -iL recon/passive/resolved_ips.txt -oN recon/active/nmap_os.txt`.
- **nmap (vuln-scripts)** — Run `nmap -sV --script vuln -iL recon/passive/resolved_ips.txt -oN recon/active/nmap_vuln.txt`.
- **nmap (service-enumeration)** — Run `nmap -sV -sC -iL recon/passive/resolved_ips.txt -oN recon/active/nmap_service_enum.txt`.
- **masscan** — Run `masscan -p1-65535 --rate=10000 -iL recon/passive/resolved_ips.txt -oJ recon/active/masscan.json && masscan -p1-65535 --rate=10000 -iL recon/passive/resolved_ips.txt -oG recon/active/masscan.gnmap`.
- **smap (Shodan enrich)** — Run `smap -iL recon/passive/resolved_ips.txt -oN recon/active/smap_enrich.txt`.

### 2.2 Directory & File Brute-Force

- **ffuf (quick)** — Run `ffuf -w /usr/share/wordlists/dirb/common.txt -u TARGET_URL/FUZZ -t 50 -o recon/active/ffuf_quick.json` for every live web service.
- **ffuf (common-extensions)** — Run `ffuf -w /usr/share/wordlists/dirb/common.txt -e .php,.asp,.aspx,.jsp,.py,.txt,.bak,.old,.inc,.config -u TARGET_URL/FUZZ -t 50 -o recon/active/ffuf_extended.json`.
- **ffuf (recursive)** — Run `ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -u TARGET_URL/FUZZ -recursion -recursion-depth 3 -t 30 -o recon/active/ffuf_recursive.json`.
- **gobuster (dir)** — Run `gobuster dir -u TARGET_URL -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 50 -o recon/active/gobuster_dir.txt`.
- **gobuster (dns)** — Run `gobuster dns -d TARGET -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 30 -o recon/active/gobuster_dns.txt`.
- **gobuster (vhost)** — Run `gobuster vhost -u TARGET_URL -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 30 -o recon/active/gobuster_vhost.txt`.
- **gobuster (s3)** — Run `gobuster s3 -d TARGET -w /usr/share/wordlists/seclists/Discovery/Web-Content/bucket-names.txt -t 30 -o recon/active/gobuster_s3.txt`.
- **feroxbuster (recursive auto-tuning)** — Run `feroxbuster -u TARGET_URL -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt -t 50 --auto-tune -d 3 -o recon/active/feroxbuster.txt`.
- **dirsearch** — Run `dirsearch -u TARGET_URL -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -t 50 --recursive --random-agent -o recon/active/dirsearch.txt`.

### 2.3 Parameter Discovery

- **arjun (all methods)** — Run `arjun -u TARGET_URL -m GET,POST,JSON --get --headers -oJ recon/active/arjun_params.json`.
- **paramspider (all levels)** — Run `paramspider -d TARGET --level high --subs True --exclude jpg,jpeg,gif,css,png,js,ico,svg,woff,ttf -o recon/active/paramspider.txt`.

### 2.4 API Endpoint Discovery

- **kiterunner (routes)** — Run `kr scan TARGET_URL -w /usr/share/wordlists/seclists/Discovery/Web-Content/api/api-endpoints-res.txt -j recon/active/kiterunner.json`.
- **katana (active crawling)** — Run `katana -list recon/passive/httpx_probed.txt -d 5 -js-crawl -kf all -silent -o recon/active/katana_active.txt`.

### 2.5 Subdomain Brute-Force (Active)

- **gobuster dns** — Already run in 2.2 (gobuster dns).
- **amass (active)** — Run `amass enum -active -d TARGET -config amass_config.ini -o recon/active/amass_active.txt`.
- **puredns** — Run `puredns bruteforce /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt TARGET -r /usr/share/wordlists/resolvers.txt -o recon/active/puredns_brute.txt`.

### 2.6 Vulnerability Scanning

- **nuclei (tech)** — Run `nuclei -l recon/passive/httpx_probed.txt -tags tech -o recon/active/nuclei_tech.txt`.
- **nuclei (exposure)** — Run `nuclei -l recon/passive/httpx_probed.txt -tags exposure -o recon/active/nuclei_exposure.txt`.
- **nuclei (misconfig)** — Run `nuclei -l recon/passive/httpx_probed.txt -tags misconfig -o recon/active/nuclei_misconfig.txt`.
- **nuclei (takeovers)** — Run `nuclei -l recon/passive/httpx_probed.txt -tags takeover -o recon/active/nuclei_takeovers.txt`.
- **nuclei (cves)** — Run `nuclei -l recon/passive/httpx_probed.txt -tags cve -severity critical,high,medium -o recon/active/nuclei_cves.txt`.
- **nuclei (all templates)** — Run `nuclei -l recon/passive/httpx_probed.txt -t ~/nuclei-templates/ -o recon/active/nuclei_all.txt`.
- **nikto (full)** — Run `nikto -h TARGET_URL -ssl -Format txt -o recon/active/nikto_full.txt`.
- **nikto (evasion)** — Run `nikto -h TARGET_URL -ssl -evasion 12345678 -Format txt -o recon/active/nikto_evasion.txt`.
- **nikto (all hosts)** — Run `xargs -a recon/passive/httpx_probed.txt -P5 -I{} nikto -h {} -ssl -Format txt -o recon/active/nikto_all.txt`.

### 2.7 Service Enumeration (NSE Scripts)

- **nmap SMB** — Run `nmap -p445 --script smb-os-discovery,smb-enum-shares,smb-enum-users,smb-vuln* -iL recon/passive/resolved_ips.txt -oN recon/active/nse_smb.txt`.
- **nmap SMTP** — Run `nmap -p25,465,587 --script smtp-commands,smtp-enum-users,smtp-vuln* -iL recon/passive/resolved_ips.txt -oN recon/active/nse_smtp.txt`.
- **nmap SSH** — Run `nmap -p22 --script ssh2-enum-algos,ssh-hostkey,ssh-auth-methods -iL recon/passive/resolved_ips.txt -oN recon/active/nse_ssh.txt`.
- **nmap FTP** — Run `nmap -p21 --script ftp-anon,ftp-bounce,ftp-vuln* -iL recon/passive/resolved_ips.txt -oN recon/active/nse_ftp.txt`.
- **nmap DNS** — Run `nmap -p53 --script dns-zone-transfer,dns-brute,dns-srv-enum,dns-nsid -iL recon/passive/resolved_ips.txt -oN recon/active/nse_dns.txt`.
- **nmap HTTP** — Run `nmap -p80,443,8080,8443 --script http-enum,http-title,http-headers,http-methods,http-webdav-scan,http-config-backup -iL recon/passive/resolved_ips.txt -oN recon/active/nse_http.txt`.
- **nmap LDAP** — Run `nmap -p389,636 --script ldap-rootdse,ldap-search -iL recon/passive/resolved_ips.txt -oN recon/active/nse_ldap.txt`.
- **nmap MySQL** — Run `nmap -p3306 --script mysql-empty-password,mysql-users,mysql-variables,mysql-vuln* -iL recon/passive/resolved_ips.txt -oN recon/active/nse_mysql.txt`.
- **nmap MSSQL** — Run `nmap -p1433 --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell -iL recon/passive/resolved_ips.txt -oN recon/active/nse_mssql.txt`.
- **nmap Redis** — Run `nmap -p6379 --script redis-info -iL recon/passive/resolved_ips.txt -oN recon/active/nse_redis.txt`.
- **nmap MongoDB** — Run `nmap -p27017 --script mongodb-info,mongodb-databases -iL recon/passive/resolved_ips.txt -oN recon/active/nse_mongodb.txt`.

---

## Phase 3: Correlate

**Objective**: Merge all recon outputs into an actionable attack surface model.

- **surface-analyzer** — Run `surface-analyzer merge --input-dir recon/ --output recon/correlation/surface.json`.
- **Attack surface report** — Run `surface-analyzer report --input recon/correlation/surface.json --format html --output recon/correlation/attack_surface_report.html`.
- **Findings graph (ShadowGraph)** — Run `shadowgraph build --input recon/correlation/surface.json --output recon/correlation/shadowgraph.gml`.
- **Target ranking** — Run `surface-analyzer rank --input recon/correlation/surface.json --output recon/correlation/target_ranking.txt`.
- **Default credential check** — Run `surface-analyzer default-creds --input recon/correlation/surface.json --output recon/correlation/default_creds_found.txt`.

---

## Mandatory Tools Checklist

| Tool | Phase | Minimum Command Variant |
|------|-------|-------------------------|
| subfinder | 1 | `subfinder -d TARGET -all -recursive` |
| amass | 1, 2 | `amass enum -passive -d TARGET` / `amass enum -active -d TARGET` |
| dnsx | 1 | `dnsx -l domains.txt -a -aaaa -cname -mx -txt -ns` |
| httpx | 1 | `httpx -l hosts.txt -title -tech-detect -status-code -content-length -webserver -ip` |
| nmap | 2 | `nmap -sS -sV -T4 -p- -iL hosts.txt` |
| masscan | 2 | `masscan -p1-65535 --rate=10000 -iL hosts.txt` |
| smap | 1, 2 | `smap -iL hosts.txt -oN smap.txt` |
| katana | 1, 2 | `katana -list urls.txt -passive -known-files all` / `katana -list urls.txt -d 5 -js-crawl` |
| gau | 1 | `gau TARGET --subs | python3 engine/scope_guard.py --filter --scope TARGET | sort -u` |
| waybackurls | 1 | `waybackurls TARGET` |
| crt.sh | 1 | `curl crt.sh?q=%25.TARGET&output=json` |
| whatweb | 1 | `whatweb -i hosts.txt --aggression 3` |
| ffuf | 2 | `ffuf -w wordlist -u URL/FUZZ -t 50` |
| gobuster | 2 | `gobuster dir -u URL -w wordlist -t 50` |
| feroxbuster | 2 | `feroxbuster -u URL -w wordlist -t 50 --auto-tune -d 3` |
| dirsearch | 2 | `dirsearch -u URL -w wordlist -t 50 --recursive` |
| arjun | 2 | `arjun -u URL -m GET,POST,JSON --get --headers` |
| paramspider | 2 | `paramspider -d TARGET --level high --subs True` |
| kiterunner | 2 | `kr scan URL -w api-endpoints-res.txt` |
| nuclei | 2 | `nuclei -l hosts.txt -t ~/nuclei-templates/` |
| nikto | 2 | `nikto -h URL -ssl -Format txt` |
| surface-analyzer | 3 | `surface-analyzer merge --input-dir recon/` |
| shadowgraph | 3 | `shadowgraph build --input surface.json` |
