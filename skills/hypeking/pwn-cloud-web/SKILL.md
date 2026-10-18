---
name: pwn-cloud-web
description: "Cloud security: AWS, Azure, GCP, Kubernetes auditing, privilege escalation and attack emulation. 57 skills: auditing-aws-s3-bucket-permissions, auditing-azure-active-directory-configuration, auditing-entra-id-with-aadinternals, auditing-gcp-iam-permissions, auditing-kubernetes-cluster-rbac, auditing-kubernetes-rbac-privilege-escalation, conducting-cloud-penetration-testing, detecting-aws-cloudtrail-anomalies. Trigger words: auditing aws s3 bucket permissions, auditing azure active directory configuration, auditing entra id with aadinternals, auditing gcp iam permissions, auditing kubernetes cluster rbac, auditing kubernetes rbac privilege escalation."
---

# pwn-cloud-web — 08-cloud-web

**Category path:** `~/.omp/agent/skills/hypeking/всегда побеждать/08-cloud-web/`

## Routing table (57 skills)

| Skill | Path | Mode | Purpose |
|---|---|---|---|
| `auditing-aws-s3-bucket-permissions` | `08-cloud-web/auditing-aws-s3-bucket-permissions/scripts/agent.py` | run | Agent for auditing AWS S3 bucket permissions using boto3. |
| `auditing-azure-active-directory-configuration` | `08-cloud-web/auditing-azure-active-directory-configuration/scripts/agent.py` | run | Agent for auditing Azure Active Directory (Entra ID) configuration. |
| `auditing-entra-id-with-aadinternals` | `08-cloud-web/auditing-entra-id-with-aadinternals/scripts/agent.py` | run | agent.py - Entra ID outsider-recon helper + AADInternals (PowerShell) launcher. |
| `auditing-gcp-iam-permissions` | `08-cloud-web/auditing-gcp-iam-permissions/scripts/agent.py` | run | Agent for auditing GCP IAM permissions using google-cloud libraries. |
| `auditing-kubernetes-cluster-rbac` | `08-cloud-web/auditing-kubernetes-cluster-rbac/scripts/agent.py` | run | Agent for auditing Kubernetes cluster RBAC configurations. |
| `auditing-kubernetes-rbac-privilege-escalation` | `08-cloud-web/auditing-kubernetes-rbac-privilege-escalation/scripts/agent.py` | run | Kubernetes RBAC privilege-escalation auditor. |
| `conducting-cloud-penetration-testing` | `08-cloud-web/conducting-cloud-penetration-testing/scripts/agent.py` | run | Cloud Penetration Testing Agent - Enumerates and tests AWS IAM misconfigurations. |
| `detecting-aws-cloudtrail-anomalies` | `08-cloud-web/detecting-aws-cloudtrail-anomalies/scripts/agent.py` | run | Agent for detecting anomalies in AWS CloudTrail logs. |
| `detecting-aws-credential-exposure-with-trufflehog` | `08-cloud-web/detecting-aws-credential-exposure-with-trufflehog/scripts/agent.py` | run | AWS credential exposure detection agent using TruffleHog and AWS APIs. |
| `detecting-aws-iam-privilege-escalation` | `08-cloud-web/detecting-aws-iam-privilege-escalation/scripts/agent.py` | run | Detect AWS IAM privilege escalation paths using boto3 policy analysis. |
| `detecting-azure-lateral-movement` | `08-cloud-web/detecting-azure-lateral-movement/scripts/agent.py` | run | Azure Lateral Movement Detection Agent - hunts for lateral movement in Azure AD/Entra ID. |
| `detecting-azure-service-principal-abuse` | `08-cloud-web/detecting-azure-service-principal-abuse/scripts/agent.py` | run | Azure Service Principal abuse detection agent. |
| `detecting-azure-storage-account-misconfigurations` | `08-cloud-web/detecting-azure-storage-account-misconfigurations/scripts/agent.py` | run | Audit Azure Storage accounts for security misconfigurations using azure-mgmt-storage SDK. |
| `detecting-cloud-threats-with-guardduty` | `08-cloud-web/detecting-cloud-threats-with-guardduty/scripts/agent.py` | run | Amazon GuardDuty threat detection and response automation agent. |
| `detecting-compromised-cloud-credentials` | `08-cloud-web/detecting-compromised-cloud-credentials/scripts/agent.py` | run | Compromised cloud credential detection agent using AWS CloudTrail and GuardDuty. |
| `detecting-cryptomining-in-cloud` | `08-cloud-web/detecting-cryptomining-in-cloud/scripts/agent.py` | run | Cloud cryptomining detection agent with multi-signal analysis. |
| `detecting-misconfigured-azure-storage` | `08-cloud-web/detecting-misconfigured-azure-storage/scripts/agent.py` | run | Azure Storage misconfiguration detection agent using Azure CLI. |
| `detecting-privilege-escalation-in-kubernetes-pods` | `08-cloud-web/detecting-privilege-escalation-in-kubernetes-pods/scripts/agent.py` | run | Kubernetes pod privilege escalation detection agent. |
| `detecting-s3-data-exfiltration-attempts` | `08-cloud-web/detecting-s3-data-exfiltration-attempts/scripts/agent.py` | run | S3 data exfiltration detection agent using CloudTrail and GuardDuty. |
| `detecting-serverless-function-injection` | `08-cloud-web/detecting-serverless-function-injection/scripts/agent.py` | run | Serverless Function Injection Detection Agent - Scans Lambda functions for injection vulnerabilities, layer hijacking, and IAM escalation paths. |
| `detecting-shadow-it-cloud-usage` | `08-cloud-web/detecting-shadow-it-cloud-usage/scripts/agent.py` | run | Agent for detecting shadow IT cloud usage via proxy logs, DNS queries, and netflow. |
| `detecting-supply-chain-attacks-in-ci-cd` | `08-cloud-web/detecting-supply-chain-attacks-in-ci-cd/scripts/agent.py` | run | Agent for detecting supply chain attacks in CI/CD pipelines. |
| `emulating-cloud-attacks-with-stratus-red-team` | `08-cloud-web/emulating-cloud-attacks-with-stratus-red-team/scripts/agent.py` | run | Stratus Red Team detection-validation helper. |
| `enumerating-cloud-with-cloudfox` | `08-cloud-web/enumerating-cloud-with-cloudfox/scripts/agent.py` | run | CloudFox enumeration driver. |
| `escaping-containers-to-host` | `08-cloud-web/escaping-containers-to-host/scripts/agent.py` | run | Container escape posture assessor. |
| `exploiting-aws-with-pacu` | `08-cloud-web/exploiting-aws-with-pacu/scripts/agent.py` | run | Pacu engagement driver. |
| `hunting-for-living-off-the-cloud-techniques` | `08-cloud-web/hunting-for-living-off-the-cloud-techniques/scripts/agent.py` | run | Agent for hunting living-off-the-cloud (LOTC) techniques using cloud service logs. |
| `implementing-cloud-trail-log-analysis` | `08-cloud-web/implementing-cloud-trail-log-analysis/scripts/agent.py` | run | CloudTrail log analysis agent for security monitoring and threat detection. |
| `implementing-cloud-waf-rules` | `08-cloud-web/implementing-cloud-waf-rules/scripts/agent.py` | run | Cloud WAF rules management agent using AWS WAFv2 boto3 client. |
| `implementing-cloud-workload-protection` | `08-cloud-web/implementing-cloud-workload-protection/scripts/agent.py` | run | Agent for cloud workload protection on AWS EC2 instances. |
| `implementing-container-network-policies-with-calico` | `08-cloud-web/implementing-container-network-policies-with-calico/scripts/agent.py` | run | Agent for implementing container network policies with Calico. |
| `implementing-gcp-binary-authorization` | `08-cloud-web/implementing-gcp-binary-authorization/scripts/agent.py` | run | Agent for auditing and managing GCP Binary Authorization policies. |
| `implementing-gcp-vpc-firewall-rules` | `08-cloud-web/implementing-gcp-vpc-firewall-rules/scripts/agent.py` | run | GCP VPC firewall rules audit and management agent. |
| `implementing-kubernetes-network-policy-with-calico` | `08-cloud-web/implementing-kubernetes-network-policy-with-calico/scripts/agent.py` | run | Agent for auditing and generating Calico Kubernetes network policies. |
| `implementing-kubernetes-pod-security-standards` | `08-cloud-web/implementing-kubernetes-pod-security-standards/scripts/agent.py` | run | Agent for auditing Kubernetes Pod Security Standards enforcement. |
| `implementing-rbac-hardening-for-kubernetes` | `08-cloud-web/implementing-rbac-hardening-for-kubernetes/scripts/agent.py` | run | Kubernetes RBAC hardening audit agent. |
| `implementing-runtime-security-with-tetragon` | `08-cloud-web/implementing-runtime-security-with-tetragon/scripts/agent.py` | run | Agent for auditing Cilium Tetragon runtime security configuration. |
| `implementing-secrets-management-with-vault` | `08-cloud-web/implementing-secrets-management-with-vault/scripts/agent.py` | run | HashiCorp Vault secrets management agent. |
| `performing-aws-account-enumeration-with-scout-suite` | `08-cloud-web/performing-aws-account-enumeration-with-scout-suite/scripts/agent.py` | run | ScoutSuite AWS account enumeration and security audit agent. |
| `performing-aws-privilege-escalation-assessment` | `08-cloud-web/performing-aws-privilege-escalation-assessment/scripts/agent.py` | run | AWS Privilege Escalation Assessment Agent — AUTHORIZED TESTING ONLY |
| `performing-cloud-asset-inventory-with-cartography` | `08-cloud-web/performing-cloud-asset-inventory-with-cartography/scripts/agent.py` | run | Cartography cloud asset inventory agent. |
| `performing-cloud-native-threat-hunting-with-aws-detective` | `08-cloud-web/performing-cloud-native-threat-hunting-with-aws-detective/SKILL.md` | read | Hunt for threats in AWS environments using Detective behavior graphs, |
| `performing-cloud-penetration-testing-with-pacu` | `08-cloud-web/performing-cloud-penetration-testing-with-pacu/scripts/agent.py` | run | AWS Penetration Testing with Pacu Agent — AUTHORIZED TESTING ONLY |
| `performing-container-escape-detection` | `08-cloud-web/performing-container-escape-detection/scripts/agent.py` | run | Agent for detecting container escape vectors in Kubernetes. |
| `performing-container-image-hardening` | `08-cloud-web/performing-container-image-hardening/scripts/agent.py` | run | Container image hardening audit agent. |
| `performing-container-security-scanning-with-trivy` | `08-cloud-web/performing-container-security-scanning-with-trivy/scripts/agent.py` | run | Trivy Container Security Agent - scans images for vulnerabilities, misconfigs, and secrets. |
| `performing-gcp-penetration-testing-with-gcpbucketbrute` | `08-cloud-web/performing-gcp-penetration-testing-with-gcpbucketbrute/scripts/agent.py` | run | GCP penetration testing agent: bucket enumeration, IAM audit, privilege escalation analysis. |
| `performing-gcp-security-assessment-with-forseti` | `08-cloud-web/performing-gcp-security-assessment-with-forseti/scripts/agent.py` | run | Agent for performing GCP security assessment. |
| `performing-kubernetes-penetration-testing` | `08-cloud-web/performing-kubernetes-penetration-testing/scripts/agent.py` | run | Agent for performing Kubernetes penetration testing — authorized testing only. |
| `scanning-container-images-with-grype` | `08-cloud-web/scanning-container-images-with-grype/scripts/agent.py` | run | Agent for scanning container images with Anchore Grype. |
| `scanning-containers-with-trivy-in-cicd` | `08-cloud-web/scanning-containers-with-trivy-in-cicd/scripts/agent.py` | run | Agent for scanning containers with Trivy in CI/CD pipelines. |
| `scanning-docker-images-with-trivy` | `08-cloud-web/scanning-docker-images-with-trivy/scripts/agent.py` | run | Agent for scanning Docker images with Trivy. |
| `scanning-iac-and-images-with-trivy` | `08-cloud-web/scanning-iac-and-images-with-trivy/scripts/agent.py` | run | Trivy scanning helper. |
| `scanning-kubernetes-manifests-with-kubesec` | `08-cloud-web/scanning-kubernetes-manifests-with-kubesec/scripts/agent.py` | run | Agent for scanning Kubernetes manifests with Kubesec. |
| `securing-aws-iam-permissions` | `08-cloud-web/securing-aws-iam-permissions/scripts/agent.py` | run | Agent for auditing and hardening AWS IAM permissions using least-privilege principles. |
| `securing-aws-lambda-execution-roles` | `08-cloud-web/securing-aws-lambda-execution-roles/scripts/agent.py` | run | Agent for auditing and securing AWS Lambda execution roles. |
| `securing-serverless-functions` | `08-cloud-web/securing-serverless-functions/scripts/agent.py` | run | Agent for auditing serverless function security across AWS Lambda. |

## Usage

Automation skills (Mode = run):
```bash
python3 '~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/scripts/agent.py' --help
```

Methodology skills (Mode = read):
```
read ~/.omp/agent/skills/hypeking/всегда побеждать/<category>/<skill>/SKILL.md
```
