# SBOM + SCA Methodology

## SBOM Standards

| Standard | Formats | Ecosystem | Focus |
|---|---|---|---|
| CycloneDX | JSON, XML | OWASP, Kubernetes | Security analysis, vulnerability tracking |
| SPDX | JSON, YAML, tag-value | Linux Foundation, ISO/IEC 5962 | License compliance, provenance |
| SWID | XML | ISO/IEC 19770-2 | Enterprise IT software asset management |

## Toolchain

- **CycloneDX generator (`cdxgen`)**:
  ```bash
  cdxgen -o bom.json -t cyclonedx
  ```
- **Syft**:
  ```bash
  syft dir:. -o spdx-json > sbom.spdx.json
  syft <image> -o cyclonedx-json > sbom.cdx.json
  ```
- **OSV-Scanner**:
  ```bash
  osv-scanner scan --sbom bom.json
  ```
- **Trivy**:
  ```bash
  trivy fs --severity HIGH,CRITICAL .
  ```

## Triage & Reachability Heuristics

1. **Direct vs Transitive**: Transitive dependencies without exposed entrypoints have lower reachability risk.
2. **Execution Context**: Test-only or build-time dependencies (`devDependencies`) rarely affect runtime attack surface.
3. **AST Symbol Call Path**: Verify if vulnerable method is imported and called along any execution flow from public APIs or network endpoints.
