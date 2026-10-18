# Pipeline: SAST Scan (Static Analysis)

| Field | Value |
|-------|-------|
| **Name** | sast_scan |
| **Phase** | vulnerability testing (white-box) |
| **Trigger** | Source code access provided |

## Flow

```
                    +----------------+
                    | Detect Language |
                    +-------+--------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
        +-----------+ +-----------+ +-----------+
        |  semgrep  | |  bandit   | |  semgrep  |
        |  (auto)   | | (python)  | | (secrets) |
        +-----------+ +-----------+ +-----------+
              |             |             |
              v             v             v
        +-------------------------------------+
        |     Merge SAST Findings             |
        | (python3 merge)                     |
        +-------------------------------------+
```

## Steps

```yaml
parameters:
  - name: source_dir
    default: "."
steps:
  - id: detect_language
    tool: bash
    command: |
      find {source_dir} -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10 \
        > pipelines/sast/languages.txt
    output: "pipelines/sast/languages.txt"
    required: true

  - id: semgrep_auto
    tool: semgrep
    command: "semgrep --config auto {source_dir} --json -o pipelines/sast/semgrep-auto.json"
    input_from: detect_language
    output: "pipelines/sast/semgrep-auto.json"
    required: true

  - id: semgrep_secrets
    tool: semgrep
    command: "semgrep --config 'p/secrets' {source_dir} --json -o pipelines/sast/semgrep-secrets.json"
    parallel: true
    required: false

  - id: semgrep_owasp
    tool: semgrep
    command: "semgrep --config 'p/owasp-top-ten' {source_dir} --json -o pipelines/sast/semgrep-owasp.json"
    parallel: true
    required: false

  - id: semgrep_custom
    tool: semgrep
    command: "semgrep --config ${PROJECT_DIR}/rules/semgrep {source_dir} --json -o pipelines/sast/semgrep-custom.json"
    input_from: detect_language
    output: "pipelines/sast/semgrep-custom.json"
    parallel: true
    required: false

  - id: bandit_scan
    tool: bandit
    command: "bandit -r {source_dir} -ll -f json -o pipelines/sast/bandit.json"
    condition: "Python files detected"
    parallel: true
    required: false

  - id: merge_sast
    tool: python3
    command: |
      python3 -c "
      import json, os, sys
      from glob import glob
      findings = []
      for f in glob('pipelines/sast/raw/*.json'):
          with open(f) as fh:
              findings.append(json.load(fh))
      with open('pipelines/sast/sast-findings.json', 'w') as fh:
          json.dump(findings, fh, indent=2)
      "
    input_from:
      - semgrep_auto
      - semgrep_secrets
      - semgrep_owasp
      - semgrep_custom
      - bandit_scan
    output: "pipelines/sast/sast-findings.json"
    required: true
```
