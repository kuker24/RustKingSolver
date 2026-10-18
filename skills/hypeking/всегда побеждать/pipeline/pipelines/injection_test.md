# Pipeline: Injection Testing

| Field | Value |
|-------|-------|
| **Name** | injection_test |
| **Phase** | exploitation |
| **Trigger** | Parameters or forms discovered on target |

## Flow

```
              +-----------------+
              | extract params  |
              | (from crawl)    |
              +--------+--------+
                       |
                       v
              +-----------------+
              |  ffuf fuzz      |
              |  (find injects) |
              +--------+--------+
                       |
                       v
              +-----------------+
              |    sqlmap       |
              |  (confirm SQLi) |
              +--------+--------+
                       |
                       v
              +-----------------+
              |  verify PoC     |
              | (safe confirm)  |
              +-----------------+
```

## Steps

```yaml
parameters:
  - name: target_url
    default: "https://example.com"
  - name: crawl_results
    default: ""
  - name: auto_calibrate
    default: "true"
  - name: anomaly_urls
    default: "pipelines/injection/ffuf_anomalies_*.json"
steps:
  - id: extract_params
    tool: internal
    command: extract_parameters
    input_from: null
    input_params:
      source: "{crawl_results}"
      url: "{target_url}"
    output: "pipelines/injection/params.json"
    parse: "jq -r '.[] | \"\\(.url)?\\(.param)=FUZZ\"' pipelines/injection/params.json > pipelines/injection/fuzz_targets.txt"
    parallel: false
    required: true

  - id: fuzz_params
    tool: ffuf
    command: params
    input_from: extract_params
    input_params:
      url: "{each_url_from:pipelines/injection/fuzz_targets.txt}"
      value: "'\"><{{7*7}}"
      baseline_size: "{auto_calibrate}"
    output: "pipelines/injection/ffuf_anomalies_{url_hash}.json"
    parse: "jq -r '.results[] | \"\\(.url) -> \\(.status) [\\(.length)]\"' pipelines/injection/ffuf_anomalies_*.json"
    parallel: false
    required: true

  - id: sqli_test
    tool: sqlmap
    command: crawl
    input_from: fuzz_params
    input_params:
      url: "{anomaly_urls}"
    output: "pipelines/injection/sqlmap_results/"
    parse: "grep -rE '(injectable|payload|Type:)' pipelines/injection/sqlmap_results/*/log"
    parallel: false
    required: true
    flags:
      - "scope_confirmed"
      - "injection_testing_authorized"

  - id: verify_poc
    tool: internal
    command: verify_injection
    input_from: sqli_test
    input_params:
      findings: "pipelines/injection/sqlmap_results/"
    output: "pipelines/injection/verified_findings.json"
    parse: "jq '.[] | select(.verified == true) | {url: .url, type: .type, payload: .payload, evidence: .evidence}' pipelines/injection/verified_findings.json"
    parallel: false
    required: true
    flags:
      - "safe_verification_only"
```
