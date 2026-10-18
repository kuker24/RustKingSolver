# Pipeline: SSL/TLS Analysis

| Field | Value |
|-------|-------|
| **Name** | ssl_analysis |
| **Phase** | vulnerability testing |
| **Trigger** | HTTPS endpoints found in recon |

## Flow

```
+----------------+      +------------------+
|  testssl.sh    | ---> | Parse SSL issues |
|  (full scan)   |      | to findings      |
+----------------+      +------------------+
```

## Steps

```yaml
parameters:
  - name: url
    default: "https://example.com"
steps:
  - id: testssl_scan
    tool: testssl.sh
    command: "testssl --jsonfile pipelines/ssl/testssl.json --warnings off {url}"
    output: "pipelines/ssl/testssl.json"
    required: true

  - id: parse_ssl
    tool: python3
    command: |
      cat pipelines/ssl/testssl.json | python3 -c "
      import json, sys
      data = json.load(sys.stdin)
      findings = []
      for entry in data:
          if entry.get('severity', 'OK') in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'WARN'):
              findings.append({
                  'source': 'testssl',
                  'rule_id': entry.get('id', ''),
                  'title': entry.get('finding', ''),
                  'severity': entry.get('severity', '').lower(),
                  'url': entry.get('ip', '') + ':' + str(entry.get('port', '')),
                  'cve': entry.get('cve', '')
              })
      json.dump(findings, sys.stdout, indent=2)
      " > pipelines/ssl/ssl-findings.json
    input_from: testssl_scan
    required: true
```
