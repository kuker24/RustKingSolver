#!/usr/bin/env python3
"""
DeepTeam red-team automation helper.

Wraps the Confident AI deepteam framework (https://github.com/confident-ai/deepteam)
to run automated adversarial evaluations against target LLM systems, agents, and RAG pipelines.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys


def _deepteam_cmd():
    if shutil.which("deepteam"):
        return ["deepteam"]
    return [sys.executable, "-m", "deepteam"]


def list_attacks(_args):
    attacks = [
        "prompt-injection",
        "jailbreak",
        "crescendo",
        "tree-of-attacks",
        "rot13-obfuscation",
        "base64-obfuscation",
        "roleplay-manipulation",
        "persona-adoption"
    ]
    print("[*] Available DeepTeam attack strategies:")
    for a in attacks:
        print(f"  - {a}")


def list_vulnerabilities(_args):
    vulns = [
        "pii-leakage",
        "bias",
        "toxicity",
        "system-prompt-leakage",
        "unauthorized-tool-use",
        "sql-injection",
        "ssrf",
        "hallucination-under-adversity"
    ]
    print("[*] Available DeepTeam vulnerability evaluations:")
    for v in vulns:
        print(f"  - {v}")


def run_scan(args):
    cmd = _deepteam_cmd() + ["run"]
    if args.config:
        cmd += ["--config", args.config]
    if args.model:
        cmd += ["--model", args.model]
    if args.output:
        cmd += ["--output", args.output]

    print("[*] Executing DeepTeam scan:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("[!] deepteam CLI is not installed. Install with: pip install -U deepteam", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="DeepTeam Red Teaming Automation Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-attacks", help="List available attacks")
    subparsers.add_parser("list-vulnerabilities", help="List available vulnerabilities")

    run_parser = subparsers.add_parser("run", help="Execute an evaluation run")
    run_parser.add_argument("--config", help="Path to DeepTeam YAML configuration")
    run_parser.add_argument("--model", help="Target LLM model name")
    run_parser.add_argument("--attacks", help="Comma-separated list of attacks")
    run_parser.add_argument("--output", help="Path to save output results JSON")

    args = parser.parse_args()
    if args.command == "list-attacks":
        list_attacks(args)
    elif args.command == "list-vulnerabilities":
        list_vulnerabilities(args)
    elif args.command == "run":
        sys.exit(run_scan(args))


if __name__ == "__main__":
    main()
