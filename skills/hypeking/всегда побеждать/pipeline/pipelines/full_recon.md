# Pipeline: Full Recon

| Field | Value |
|-------|-------|
| **Name** | full_recon |
| **Phase** | reconnaissance |
| **Trigger** | New engagement, domain scope provided |

## Flow

```
                         +------------+
                         | subfinder  |
                         | (subs)     |
                         +-----+------+
                               |
                               v
                         +------------+
                         |   dnsx     |
                         | (resolve)  |
                         +-----+------+
                               |
                               v
                         +------------+
                         |   httpx    |
                         | (probe)    |
                         +-----+------+
                               |
                   +-----------+-----------+
                   |           |           |
                   v           v           v
             +----------+ +--------+ +----------+
             |   nmap   | |  ffuf  | |  nuclei  |
             |  (ports) | | (dirs) | |  (scan)  |
             +----+-----+ +---+----+ +----+-----+
                  |            |           |
                  +------------+-----------+
                               |
                               v
                       +---------------+
                       |   aggregate   |
                       | (merge JSON)  |
                       +---------------+
```

## Steps

```yaml
parameters:
  - name: target_domain
    default: "example.com"
steps:
  - id: enumerate_subs
    tool: subfinder
    command: all_sources
    input_from: null
    input_params:
      domain: "{target_domain}"
    output: "pipelines/recon/subdomains.txt"
    parse: "sort -u"
    parallel: false
    required: true

  - id: resolve_dns
    tool: dnsx
    command: json
    input_from: enumerate_subs
    input_params:
      input_file: "pipelines/recon/subdomains.txt"
    output: "pipelines/recon/dns_resolved.json"
    parse: "jq -r '.host' pipelines/recon/dns_resolved.json | sort -u > pipelines/recon/resolved_hosts.txt"
    parallel: false
    required: true

  - id: probe_http
    tool: httpx
    command: full
    input_from: resolve_dns
    input_params:
      input_file: "pipelines/recon/resolved_hosts.txt"
    output: "pipelines/recon/httpx_results.json"
    parse: "jq -r '.url' pipelines/recon/httpx_results.json | sort -u > pipelines/recon/live_urls.txt"
    parallel: false
    required: true

  - id: scan_ports
    tool: nmap
    command: quick
    input_from: resolve_dns
    input_params:
      target: "pipelines/recon/resolved_hosts.txt"
    output: "pipelines/recon/nmap_scan"
    parse: "python3 -c \"import xml.etree.ElementTree as ET; tree=ET.parse('pipelines/recon/nmap_scan.xml'); [print(f'{h.get(\\\"addr\\\")}:{p.get(\\\"portid\\\")} {s.get(\\\"name\\\",\\\"?\\\")} {s.get(\\\"product\\\",\\\"?\\\")}') for h in tree.findall('.//host') for p in h.findall('.//port[state[@state=\\\"open\\\"]]') for s in p.findall('service')]\""
    parallel: true
    parallel_group: "deep_recon"
    required: false

  - id: fuzz_dirs
    tool: ffuf
    command: dirs
    input_from: probe_http
    input_params:
      url: "{each_url_from:pipelines/recon/live_urls.txt}"
    output: "pipelines/recon/ffuf_dirs_{url_hash}.json"
    parse: "jq -r '.results[] | \"\\(.status) \\(.url)\"' pipelines/recon/ffuf_dirs_*.json"
    parallel: true
    parallel_group: "deep_recon"
    required: false

  - id: vuln_scan
    tool: nuclei
    command: full
    input_from: probe_http
    input_params:
      input_file: "pipelines/recon/live_urls.txt"
    output: "pipelines/recon/nuclei_results.json"
    parse: "jq '{template: .\"template-id\", severity: .info.severity, matched: .\"matched-at\"}' pipelines/recon/nuclei_results.json"
    parallel: true
    parallel_group: "deep_recon"
    required: false

  - id: aggregate
    tool: internal
    command: merge_json
    input_from:
      - scan_ports
      - fuzz_dirs
      - vuln_scan
    output: "pipelines/recon/full_recon_report.json"
    parse: "jq '.' pipelines/recon/full_recon_report.json"
    parallel: false
    required: true
```

## Downstream Findings

Each step that produces findings should publish them:
```bash
# Example: after aggregate completes
findings.sh add host <ip> --hostname <hostname> --os <os>
findings.sh add service <ip> <port> --service <name> --banner <banner>
findings.sh add vuln "<title>" --severity <severity> --cve <cve> --tool <tool>
```
