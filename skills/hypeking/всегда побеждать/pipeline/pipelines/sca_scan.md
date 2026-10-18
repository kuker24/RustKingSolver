# Pipeline: SCA Scan (Dependency & Container Analysis)

| Field | Value |
|-------|-------|
| **Name** | sca_scan |
| **Phase** | vulnerability testing (white-box/gray-box) |
| **Trigger** | Source code, container image, or SBOM available |

## Flow

```
        +----------------+
        | Detect Targets |
        | (source/image/ |
        |  lockfiles)    |
        +-------+--------+
                |
      +---------+---------+
      |         |         |
      v         v         v
+---------+ +--------+ +---------+
| trivy   | | trivy  | | grype   |
| fs      | | config | | dir     |
| (deps)  | | (IaC)  | | (deps)  |
+---------+ +--------+ +---------+
      |         |         |
      v         v         v
+-------------------------------------+
|       Merge SCA Findings            |
|  (python3 merge)                    |
+-------------------------------------+
```

## Steps

```yaml
parameters:
  - name: source_dir
    default: "."
  - name: image_name
    default: "app:latest"
steps:
  - id: trivy_filesystem
    tool: trivy
    command: "trivy fs {source_dir} --scanners vuln,secret --format json -o pipelines/sca/trivy-fs.json"
    output: "pipelines/sca/trivy-fs.json"
    required: true

  - id: trivy_config
    tool: trivy
    command: "trivy config {source_dir} --format json -o pipelines/sca/trivy-config.json"
    parallel: true
    required: false
    notes: "Scans Dockerfile, Terraform, K8s manifests, etc."

  - id: trivy_image
    tool: trivy
    command: "trivy image {image_name} --format json -o pipelines/sca/trivy-image.json"
    condition: "Container image specified in scope"
    parallel: true
    required: false

  - id: grype_scan
    tool: grype
    command: "grype dir:{source_dir} -o json > pipelines/sca/grype.json"
    parallel: true
    required: false

  - id: merge_sca
    tool: python3
    command: |
      python3 -c "
      import json, os, sys
      from glob import glob
      findings = {}
      for f in glob('pipelines/sca/raw/*.json'):
          name = os.path.basename(f)
          with open(f) as fh:
              findings[name] = json.load(fh)
      with open('pipelines/sca/sca-findings.json', 'w') as fh:
          json.dump(findings, fh, indent=2)
      "
    input_from:
      - trivy_filesystem
      - trivy_config
      - trivy_image
      - grype_scan
    output: "pipelines/sca/sca-findings.json"
    required: true
```
