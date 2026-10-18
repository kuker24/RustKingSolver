#!/usr/bin/env python3
"""
Test suite for bin/omp (profile-aware launcher).

The launcher is exercised with a temporary OMP_AGENT_DIR and a stub
OMP_REAL_BIN that records its argv, so the real oh-my-pi binary is never
launched. This verifies:

  * the correct MCP profile file is selected per argument shape
  * the launcher is not recursive (stub receives the pass-through args)
  * bare `omp` and unknown args reset to the default profile
  * `omp status` / `omp <profile> status` print status without launching omp
  * a missing profiles/ dir fails loudly and points at restore.sh
  * OMP_NO_PROFILE=1 bypasses all profile management
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCHER = os.path.join(ROOT, "bin", "omp")
DEFAULT_PROFILE = os.path.join(ROOT, "profiles", "mcp.default.json")
PENTEST_PROFILE = os.path.join(ROOT, "profiles", "mcp.pentest.json")


def _read_json(path):
    with open(path) as fh:
        return json.load(fh)


def _enabled(profile_path):
    return sorted(k for k, v in _read_json(profile_path)["mcpServers"].items() if v.get("enabled"))


def _make_stub(tmp):
    """Create a stub binary that records its argv to $ARGV_LOG."""
    stub = os.path.join(tmp, "fake-omp")
    with open(stub, "w") as fh:
        fh.write(
            '#!/usr/bin/env bash\n'
            ': > "${ARGV_LOG}"\n'
            'for a in "$@"; do printf \'%s\\n\' "$a" >> "${ARGV_LOG}"; done\n'
            'exit 0\n'
        )
    os.chmod(stub, 0o755)
    return stub


def _make_env(agent_dir, stub, argv_log, extra=None):
    env = dict(os.environ)
    env["OMP_AGENT_DIR"] = agent_dir
    env["OMP_REAL_BIN"] = stub
    env["ARGV_LOG"] = argv_log
    env.pop("OMP_NO_PROFILE", None)
    if extra:
        env.update(extra)
    return env


def _setup(tmp, with_profiles=True):
    agent_dir = os.path.join(tmp, "agent")
    os.makedirs(agent_dir, exist_ok=True)
    if with_profiles:
        os.makedirs(os.path.join(agent_dir, "profiles"), exist_ok=True)
        shutil.copy(DEFAULT_PROFILE, os.path.join(agent_dir, "profiles", "mcp.default.json"))
        shutil.copy(PENTEST_PROFILE, os.path.join(agent_dir, "profiles", "mcp.pentest.json"))
        # restore.sh always deploys an initial mcp.json; mirror that state.
        shutil.copy(DEFAULT_PROFILE, os.path.join(agent_dir, "mcp.json"))
    stub = _make_stub(tmp)
    argv_log = os.path.join(tmp, "argv.log")
    return agent_dir, stub, argv_log


def _run(args, env):
    if os.path.exists(env["ARGV_LOG"]):
        os.remove(env["ARGV_LOG"])
    return subprocess.run([LAUNCHER, *args], capture_output=True, text=True, env=env)


def _read_argv(env):
    path = env["ARGV_LOG"]
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        data = fh.read()
    return data.split("\n")[:-1] if data else []


def test_pentest_selects_pentest_profile():
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp)
        env = _make_env(agent_dir, stub, argv_log)
        res = _run(["pentest", "--help"], env)
        assert res.returncode == 0, res.stderr
        assert _enabled(os.path.join(agent_dir, "mcp.json")) == _enabled(PENTEST_PROFILE)
        assert _read_argv(env) == ["--help"], _read_argv(env)
        assert "[+] pentest profile active" in res.stderr
        assert "[+] pentest profile active" not in res.stdout
        print("[PASS] test_pentest_selects_pentest_profile")


def test_bare_omp_resets_to_default():
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp)
        env = _make_env(agent_dir, stub, argv_log)
        # Pre-set pentest, then a bare call must reset to default.
        shutil.copy(PENTEST_PROFILE, os.path.join(agent_dir, "mcp.json"))
        res = _run([], env)
        assert res.returncode == 0, res.stderr
        assert _enabled(os.path.join(agent_dir, "mcp.json")) == _enabled(DEFAULT_PROFILE)
        # Bare launch is silent on stderr.
        assert res.stderr.strip() == "", res.stderr
        assert _read_argv(env) == [], _read_argv(env)
        print("[PASS] test_bare_omp_resets_to_default")


def test_unknown_arg_passthrough_with_default():
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp)
        env = _make_env(agent_dir, stub, argv_log)
        res = _run(["--help"], env)
        assert res.returncode == 0, res.stderr
        assert _enabled(os.path.join(agent_dir, "mcp.json")) == _enabled(DEFAULT_PROFILE)
        assert _read_argv(env) == ["--help"], _read_argv(env)
        print("[PASS] test_unknown_arg_passthrough_with_default")


def test_status_shortcut_no_launch():
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp)
        env = _make_env(agent_dir, stub, argv_log)
        res = _run(["status"], env)
        assert res.returncode == 0, res.stderr
        # No omp launch => stub never wrote the argv log.
        assert _read_argv(env) is None, _read_argv(env)
        assert "ENABLED" in res.stdout, res.stdout
        print("[PASS] test_status_shortcut_no_launch")


def test_profile_status_switches_then_prints():
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp)
        env = _make_env(agent_dir, stub, argv_log)
        res = _run(["pentest", "status"], env)
        assert res.returncode == 0, res.stderr
        assert _read_argv(env) is None, "omp must not launch for '<profile> status'"
        assert _enabled(os.path.join(agent_dir, "mcp.json")) == _enabled(PENTEST_PROFILE)
        for server in ("sliver", "jshook", "ghidra", "rea", "scrapling", "context7", "codebase-memory-mcp"):
            assert server in res.stdout, f"{server} missing from status output"
        print("[PASS] test_profile_status_switches_then_prints")


def test_idempotent_double_invoke():
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp)
        env = _make_env(agent_dir, stub, argv_log)
        first = _run(["pentest", "--help"], env)
        second = _run(["pentest", "--help"], env)
        assert first.returncode == 0 and second.returncode == 0
        assert _enabled(os.path.join(agent_dir, "mcp.json")) == _enabled(PENTEST_PROFILE)
        assert "active" in second.stderr  # still reports, but file is stable
        print("[PASS] test_idempotent_double_invoke")


def test_missing_bundle_fails_loudly():
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp, with_profiles=False)
        env = _make_env(agent_dir, stub, argv_log)
        res = _run(["pentest"], env)
        assert res.returncode != 0, "missing bundle must fail"
        assert "restore.sh" in res.stderr, res.stderr
        assert _read_argv(env) is None, "omp must not launch when profile is missing"
        print("[PASS] test_missing_bundle_fails_loudly")


def test_no_profile_escape_hatch():
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp)
        env = _make_env(agent_dir, stub, argv_log, extra={"OMP_NO_PROFILE": "1"})
        res = _run(["pentest", "--help"], env)
        assert res.returncode == 0, res.stderr
        # Bypass: profile untouched and the `pentest` token is not intercepted.
        with open(os.path.join(agent_dir, "mcp.json")) as fh:
            active = json.load(fh)
        assert active == _read_json(DEFAULT_PROFILE)
        assert _read_argv(env) == ["pentest", "--help"], _read_argv(env)
        print("[PASS] test_no_profile_escape_hatch")


def test_not_recursive_when_first_on_path():
    """Wrapper first on PATH must still find the real binary, not itself."""
    with tempfile.TemporaryDirectory() as tmp:
        agent_dir, stub, argv_log = _setup(tmp)
        bindir = os.path.join(tmp, "pathbin")
        os.makedirs(bindir, exist_ok=True)
        shutil.copy(LAUNCHER, os.path.join(bindir, "omp"))
        os.chmod(os.path.join(bindir, "omp"), 0o755)
        env = _make_env(agent_dir, stub, argv_log)
        env["PATH"] = bindir + os.pathsep + env["PATH"]
        res = subprocess.run([os.path.join(bindir, "omp"), "--help"], capture_output=True, text=True, env=env)
        assert res.returncode != 127, res.stderr
        assert _read_argv(env) == ["--help"], _read_argv(env)
        print("[PASS] test_not_recursive_when_first_on_path")


if __name__ == "__main__":
    test_pentest_selects_pentest_profile()
    test_bare_omp_resets_to_default()
    test_unknown_arg_passthrough_with_default()
    test_status_shortcut_no_launch()
    test_profile_status_switches_then_prints()
    test_idempotent_double_invoke()
    test_missing_bundle_fails_loudly()
    test_no_profile_escape_hatch()
    test_not_recursive_when_first_on_path()
    print("ALL LAUNCHER TESTS PASSED.")
