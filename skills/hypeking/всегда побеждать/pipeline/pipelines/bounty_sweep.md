# Pipeline: Bounty Sweep

A fast, high-value bug bounty discovery pass. Runs a single URL target through
crawling, technology fingerprinting, exposure/sensitive-file scanning, and XSS
probing, then converges results into a single report. Designed to be chained:
run this for a quick win, then escalate promising targets with `web_app_scan`
or `injection_test`.

| Field | Value |
|-------|-------|
| **Name** | bounty_sweep |
| **Phase** | hunting |
| **Trigger** | Live bug bounty target URL in scope |

## Required flags

- `--param target_url=<url>` — the in-scope target, e.g. `https://example.com`
- `--flag bug_bounty_scope_confirmed` — confirms the target is within the program scope

## Flow

```
                       +-------------------+
                       | {target_url}      |
                       +---------+---------+
                                 |
                  +--------------+--------------+
                  |              |              |
                  v              v              v
            +---------+  +-----------+  +-----------+
            | katana  |  |  nuclei    | |  nuclei   |
            | crawl   |  | tech scan  | | exposures|
            +----+----+  +--+--------+ +--+--------+
                 |          |              |
                 v          |              |
          +---------+       |              |
          | extract |       |              |
          | params  |       |              |
          +----+----+       |              |
               |            |              |
               v            v              v
          +---------+  +-----------+  +-----------+
          |  ffuf   |  |  dalfox   | |  merge    |
          | param   |  | xss probe |  | findings  |
          | fuzz    |  |           |  |           |
          +---------+  +-----------+  +-----------+
```

## Steps

```yaml
parameters:
  - name: target_url
    default: ""
  - name: bug_bounty_scope_confirmed
    default: "true"

steps:
  - id: crawl
    tool: katana
    command: "katana -u {target_url} -jc -d 2 -kf all -fs fq -o pipelines/sweep/crawl_urls.txt"
    input_from: null
    output: "pipelines/sweep/crawl_urls.txt"
    parallel: false
    required: true
    flags:
      - bug_bounty_scope_confirmed

  - id: tech_scan
    tool: nuclei
    command: "nuclei -u {target_url} -t http/technologies -silent -jsonl -o pipelines/sweep/tech.json"
    input_from: null
    output: "pipelines/sweep/tech.json"
    parallel: true
    parallel_group: deep_scan
    required: false

  - id: exposure_scan
    tool: nuclei
    command: "nuclei -u {target_url} -t ${PROJECT_DIR}/rules/nuclei -silent -jsonl -o pipelines/sweep/exposures.json"
    input_from: null
    output: "pipelines/sweep/exposures.json"
    parallel: true
    parallel_group: deep_scan
    required: false

  - id: extract_params
    tool: internal
    command: extract_parameters
    input_from: crawl
    input_params:
      source: "pipelines/sweep/crawl_urls.txt"
      url: "{target_url}"
    output: "pipelines/sweep/params.json"
    parse: "jq -r '.[] | \"\(.url)?\(.param)=FUZZ\"' pipelines/sweep/params.json > pipelines/sweep/fuzz_targets.txt"
    parallel: false
    required: false

  - id: param_fuzz
    tool: ffuf
    command: params
    input_from: extract_params
    input_params:
      url: "{each_url_from:pipelines/sweep/fuzz_targets.txt}"
      value: "'\"><{{7*7}}"
      baseline_size: "true"
    output: "pipelines/sweep/ffuf_anomalies_{url_hash}.json"
    parallel: false
    required: false

  - id: xss_scan
    tool: dalfox
    command: "dalfox file pipelines/sweep/crawl_urls.txt --silence --format json -o pipelines/sweep/xss.json"
    input_from: crawl
    input_params:
      input_file: "pipelines/sweep/crawl_urls.txt"
    output: "pipelines/sweep/xss.json"
    parallel: true
    parallel_group: deep_scan
    required: false

  - id: merge_findings
    tool: internal
    command: merge_json
    input_from:
      - tech_scan
      - exposure_scan
      - xss_scan
    output: "pipelines/sweep/bounty_sweep_report.json"
    required: true
```
