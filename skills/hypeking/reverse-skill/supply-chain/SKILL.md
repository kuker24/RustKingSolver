---
name: supply-chain-security
description: Use for software supply-chain security assessment covering SBOM, SCA, CI/CD pipelines, container images, build integrity, dependency provenance, and vulnerability reachability.
---
# Supply Chain Security Testing

## ACTION REQUIRED

1. `NOW`: Check assessment scope and authorization boundaries
2. `NOW`: Identify target build artifacts, manifests, and CI/CD pipelines
3. `NEXT`: Audit SBOM, dependencies, and container images
4. `ACT`: Enter workflow steps below

> SBOM / SCA / CI/CD Pipeline / Dependency Provenance / SLSA Governance

## Scope

- Software supply chain risk assessment
- Open source dependency vulnerability scanning & reachability analysis
- CI/CD pipeline security auditing (GitHub Actions, GitLab CI)
- Container image analysis (base images, secrets, multi-layer vulnerabilities)
- Third-party component license and provenance compliance
- Build artifact signing and integrity verification (Cosign, SLSA)

## Six-Layer Governance Framework

```text
Layer 1: Source Trust Evaluation → Upstream repository, maintainer activity, commit history
Layer 2: Build Pipeline Integration → CI/CD security gates, action pinning, secret isolation
Layer 3: Artifact Distribution Integrity → Cosign signatures, checksums, SBOM attachments
Layer 4: Runtime Protection → Container image scanning, admission control (OPA/Kyverno)
Layer 5: Continuous Monitoring → CVE tracking, vulnerability reachability analysis
Layer 6: Incident Response → Dependency tampering rollback, revoke compromised credentials
```

## Workflow

### 1. SBOM Generation & Audit

```text
Generate SBOM:
- CycloneDX format: cdxgen -o bom.json
- SPDX format: sbom-tool generate -b ./build -bc ./src -pn MyApp -pv 1.0
- Syft: syft <image|dir> -o spdx-json

Audit Checklist:
- Unknown or unauthorized dependencies
- Deprecated or abandoned packages (no commits > 1 year)
- License incompatibilities / copyleft risks
- Direct vs transitive dependency tree depth
- Component release timeline and maintainer verification
```

### 2. Software Composition Analysis (SCA)

```bash
# OSV-Scanner (Google OSV database)
osv-scanner scan -r . --format json

# Trivy (filesystem + containers + IaC)
trivy fs .
trivy image <image_tag>
trivy config .

# OWASP Dependency-Check / Dependency-Track
# Snyk CLI
snyk test --all-projects
```

### 3. Vulnerability Reachability Verification

```text
SCA alert != exploitable risk. Typically < 20% of reported vulnerabilities are reachable.

Verification Steps:
1. Extract CVE list from SCA scanner (filter CVSS >= 7.0)
2. Identify symbols/functions called in codebase using AST / call graph
3. Verify whether vulnerable methods are reachable from exposed interfaces
4. Isolate exploit test in sandbox environment
5. Rank remediation priority based on reachability and impact
```

### 4. CI/CD Pipeline Security

```text
Pipeline Checklist:
- Code commits: pre-commit secret scanning (gitleaks)
- PR validation: SCA scan before merge
- Build phase: Artifact signing (cosign) + SLSA provenance
- Secrets management: GitHub Actions secrets, OIDC for cloud auth (no long-lived tokens)
- Action pinning: Pin third-party GitHub Actions to immutable full commit SHAs, not mutable tags
- Permissions: Minimum required permissions (e.g., permissions: contents: read)
```

### 5. Container Image Security

```bash
# Dockerfile static linting
hadolint Dockerfile

# Multi-layer image scanning
trivy image --severity HIGH,CRITICAL <image>:latest

# Cosign image signature verification
cosign verify --key cosign.pub <image>:latest
```

## References

- `references/sbom-sca-methodology.md` — SBOM & SCA methodologies
- `references/cicd-pipeline-security.md` — CI/CD pipeline auditing
