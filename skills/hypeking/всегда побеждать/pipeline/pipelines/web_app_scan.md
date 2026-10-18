# Pipeline: Web App Scan

| Field | Value |
|-------|-------|
| **Name** | web_app_scan |
| **Phase** | scanning |
| **Trigger** | Live web application URL identified |

## Flow

```
                      +------------+
                      | ZAP spider |
                      +-----+------+
                            |
                            v
                      +-------------+
                      | ZAP active  |
                      |   scan      |
                      +-----+-------+
                            |
                  +---------+---------+
                  |                   |
                  v                   v
           +----------+        +----------+
           |  nuclei  |        |  dalfox  |
           | (tech)   |        |  (xss)   |
           +----+-----+        +----+-----+
                |                    |
                +----------+---------+
                           |
                           v
                    +-----------+
                    |   merge   |
                    | findings  |
                    +-----------+
```

## Steps

```yaml
parameters:
  - name: target_url
    default: "http://127.0.0.1:8090"
  - name: zap_api_key
    default: "changeme"
steps:
  - id: zap_start
    tool: zap-cli
    command: start_daemon
    input_from: null
    input_params:
      zap_port: "8090"
      zap_api_key: "{zap_api_key}"
    output: "none"
    parse: "curl -s http://127.0.0.1:8090/JSON/core/view/version/"
    parallel: false
    required: true

  - id: zap_spider
    tool: zap-cli
    command: spider
    input_from: zap_start
    input_params:
      url: "{target_url}"
      zap_port: "8090"
      zap_api_key: "{zap_api_key}"
    output: "pipelines/webapp/zap_spider_urls.txt"
    parse: "curl -s 'http://127.0.0.1:8090/JSON/spider/view/results/?apikey={zap_api_key}' | jq -r '.results[]' > pipelines/webapp/zap_spider_urls.txt"
    parallel: false
    required: true

  - id: zap_active
    tool: zap-cli
    command: active_scan
    input_from: zap_spider
    input_params:
      url: "{target_url}"
      zap_port: "8090"
      zap_api_key: "{zap_api_key}"
    output: "pipelines/webapp/zap_alerts.json"
    parse: "curl -s 'http://127.0.0.1:8090/JSON/core/view/alerts/?apikey={zap_api_key}&baseurl={target_url}' | jq '.alerts[]' > pipelines/webapp/zap_alerts.json"
    parallel: false
    required: true

  - id: nuclei_tech
    tool: nuclei
    command: auto
    input_from: zap_spider
    input_params:
      url: "{target_url}"
    output: "pipelines/webapp/nuclei_results.json"
    parse: "jq '{template: .\"template-id\", severity: .info.severity, matched: .\"matched-at\"}' pipelines/webapp/nuclei_results.json"
    parallel: true
    parallel_group: "deep_scan"
    required: false

  - id: exposure_scan
    tool: nuclei
    command: "nuclei -u {target_url} -t ${PROJECT_DIR}/rules/nuclei -silent -jsonl -o pipelines/webapp/exposures.json"
    output: "pipelines/webapp/exposures.json"
    parallel: true
    parallel_group: "deep_scan"
    required: false

  - id: xss_scan
    tool: dalfox
    command: pipe
    input_from: zap_spider
    input_params:
      input_file: "pipelines/webapp/zap_spider_urls.txt"
    output: "pipelines/webapp/dalfox_results.json"
    parse: "jq '{type: .type, poc: .poc, param: .param}' pipelines/webapp/dalfox_results.json"
    parallel: true
    parallel_group: "deep_scan"
    required: false

  - id: merge_findings
    tool: internal
    command: merge_json
    input_from:
      - zap_active
      - nuclei_tech
      - exposure_scan
      - xss_scan
    output: "pipelines/webapp/webapp_scan_report.json"
    parse: "jq '.' pipelines/webapp/webapp_scan_report.json"
    parallel: false
    required: true
```
