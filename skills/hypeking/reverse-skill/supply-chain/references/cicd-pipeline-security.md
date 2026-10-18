# CI/CD Pipeline Security Auditing

## Threat Model (STRIDE)

```text
- Spoofing: Forged builds, fake commits, manipulated provenance
- Tampering: Modified source in transit, altered build artifacts, malicious action steps
- Repudiation: Unaudited pipeline modifications, missing signed commits
- Information Disclosure: Secrets printed to pipeline logs, environment variable leakage
- Denial of Service: Resource exhaustion on runners, infinite test loops
- Elevation of Privilege: Runner breakout, GitHub Actions token permission abuse
```

## Security Checklist

### 1. GitHub Actions Workflow Configuration

- Pin all action dependencies to full 40-character commit SHAs:
  ```yaml
  - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
  ```
- Use minimal explicit permissions:
  ```yaml
  permissions:
    contents: read
  ```
- Avoid untrusted input interpolation into shell scripts:
  ```yaml
  # Dangerous:
  run: echo "${{ github.event.issue.title }}"
  # Safe:
  env:
    TITLE: ${{ github.event.issue.title }}
  run: echo "$TITLE"
  ```
- Avoid `pull_request_target` unless strictly isolated from checking out fork code.

### 2. Secret Management

- Use OpenID Connect (OIDC) with AWS/GCP/Azure instead of long-lived API tokens.
- Restrict secret environment injection to steps that explicitly require them.
- Scan repositories for secrets with `gitleaks detect` and `trufflehog`.

### 3. Build & Artifact Provenance

- Generate build provenance with SLSA generator.
- Sign artifacts using `cosign sign-blob`.
- Verify checksums before installing external binaries in workflow runs.
