#!/usr/bin/env python3
"""
Test suite for skills/hypeking/scripts/route.py
Verifies the 8-field router output contract and JSON serialization.
"""

import subprocess
import json
import os
import sys

ROUTE_PY = os.path.join(os.path.dirname(__file__), "..", "skills", "hypeking", "scripts", "route.py")

def test_text_contract_8_fields():
    result = subprocess.run(
        [sys.executable, ROUTE_PY, "--ask", "photo geolocation where was this photo taken"],
        capture_output=True,
        text=True,
        check=True
    )
    lines = result.stdout.strip().split("\n")
    fields = {}
    for line in lines:
        if ": " in line:
            key, val = line.split(": ", 1)
            fields[key.strip()] = val.strip()

    expected_keys = ["ROUTE", "SUITE", "MODE", "NEXT", "MATCHED", "SCORE", "PATH"]
    for k in expected_keys:
        assert k in fields, f"Missing required router field: {k}"

    assert fields["ROUTE"].startswith("skill://hypeking/")
    assert int(fields["SCORE"]) > 0
    assert os.path.isabs(fields["PATH"])
    print("[PASS] test_text_contract_8_fields")

def test_json_output_contract():
    result = subprocess.run(
        [sys.executable, ROUTE_PY, "--ask", "supply chain sbom sca methodology", "--json"],
        capture_output=True,
        text=True,
        check=True
    )
    data = json.loads(result.stdout)
    assert "ask" in data
    assert "routes" in data
    assert len(data["routes"]) > 0

    top_route = data["routes"][0]
    for required in ["route", "suite", "mode", "next", "matched", "score", "path"]:
        assert required in top_route, f"Missing field in json route: {required}"

    assert "supply-chain" in top_route["route"] or "supply-chain" in top_route["suite"]
    print("[PASS] test_json_output_contract")

def test_godmode_routing_to_ai_llm():
    result = subprocess.run(
        [sys.executable, ROUTE_PY, "--ask", "godmode jailbreak prompt"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "pwn-ai-llm/SKILL.md" in result.stdout
    print("[PASS] test_godmode_routing_to_ai_llm")

def test_gap_packs_routing():
    queries = [
        ("photo geolocation exif", "photo-geolocation/SKILL.md"),
        ("game modding universal modder", "game-modding/SKILL.md"),
        ("deepteam red teaming llms", "red-teaming-llms-with-deepteam/SKILL.md"),
        ("supply chain cicd pipeline", "supply-chain-security/SKILL.md")
    ]
    for q, expected_target in queries:
        res = subprocess.run(
            [sys.executable, ROUTE_PY, "--ask", q],
            capture_output=True,
            text=True,
            check=True
        )
        assert expected_target in res.stdout, f"Expected {expected_target} for query '{q}', got:\n{res.stdout}"
    print("[PASS] test_gap_packs_routing")
def test_mcp_profiles():
    root = os.path.dirname(os.path.dirname(__file__))
    default_path = os.path.join(root, "profiles", "mcp.default.json")
    pentest_path = os.path.join(root, "profiles", "mcp.pentest.json")

    with open(default_path) as f:
        d_def = json.load(f)
    with open(pentest_path) as f:
        d_pen = json.load(f)

    assert len(d_def["mcpServers"]) == 17, "Default profile must have 17 servers"
    assert len(d_pen["mcpServers"]) == 17, "Pentest profile must have 17 servers"

    pen_enabled = [k for k, v in d_pen["mcpServers"].items() if v.get("enabled")]
    for expected in ["sliver", "jshook", "ghidra", "rea", "scrapling", "context7", "codebase-memory-mcp"]:
        assert expected in pen_enabled, f"Pentest profile must enable {expected}"

    for disabled in ["shadcn", "penulis-ilmiah", "markitdown", "stitch", "ui-skills", "reticle", "exa"]:
        assert not d_pen["mcpServers"][disabled].get("enabled"), f"{disabled} must be disabled in pentest profile"

    print("[PASS] test_mcp_profiles")

if __name__ == "__main__":
    test_text_contract_8_fields()
    test_json_output_contract()
    test_godmode_routing_to_ai_llm()
    test_gap_packs_routing()
    test_mcp_profiles()
    print("ALL TESTS PASSED.")
