#!/usr/bin/env bash
# restore.sh — Deploy and synchronize omp-bundle-v1 to ~/.omp/agent/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${OMP_AGENT_DIR:-$HOME/.omp/agent}"
PROFILE="default"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    default|pentest)
      PROFILE="$1"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: ./restore.sh [--profile default|pentest]"
      exit 1
      ;;
  esac
done

echo "[*] Restoring omp bundle (profile: $PROFILE) to: $TARGET"

mkdir -p "$TARGET"/{skills,manual-skills,commands,bin,mcp,rules,vendor,profiles,state/chromium-profile,logs}

# 1. Sync skills (52 discovered skills)
echo "[*] Synchronizing skills/..."
rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' "$ROOT/skills/" "$TARGET/skills/"

# 2. Sync manual-skills (15 manual specialists)
echo "[*] Synchronizing manual-skills/..."
rsync -a --delete "$ROOT/manual-skills/" "$TARGET/manual-skills/"

# 3. Sync commands (15 slash command stubs)
echo "[*] Synchronizing commands/..."
rsync -a --delete "$ROOT/commands/" "$TARGET/commands/"

# 4. Sync bin/
echo "[*] Synchronizing bin/..."
rsync -a "$ROOT/bin/" "$TARGET/bin/"

# 4b. Ensure codebase-memory-mcp binary is present and verified
EXPECTED_CBM_SHA="ce11c141431aeadd788506c3a7e6942db8fd438dec369d0707a39ec9fd8c6510"
if [ ! -f "$TARGET/bin/codebase-memory-mcp" ] || [ "$(sha256sum "$TARGET/bin/codebase-memory-mcp" | awk '{print $1}')" != "$EXPECTED_CBM_SHA" ]; then
  echo "[*] Provisioning codebase-memory-mcp..."
  if [ -f "$ROOT/bin/codebase-memory-mcp" ] && [ "$(sha256sum "$ROOT/bin/codebase-memory-mcp" | awk '{print $1}')" = "$EXPECTED_CBM_SHA" ]; then
    cp "$ROOT/bin/codebase-memory-mcp" "$TARGET/bin/codebase-memory-mcp"
  elif [ -f "$HOME/.local/share/opencode-highend/components/codebase-memory/bin/codebase-memory-mcp" ]; then
    cp "$HOME/.local/share/opencode-highend/components/codebase-memory/bin/codebase-memory-mcp" "$TARGET/bin/codebase-memory-mcp"
  elif [ -f "$HOME/.local/share/opencode-highend/cache/downloads/codebase-memory-mcp-linux-amd64-portable.tar.gz" ]; then
    tar -xzf "$HOME/.local/share/opencode-highend/cache/downloads/codebase-memory-mcp-linux-amd64-portable.tar.gz" -C "$TARGET/bin/"
  else
    echo "[*] Downloading codebase-memory-mcp-linux-amd64-portable.tar.gz..."
    CBM_TAR="/tmp/cbm-$$.tar.gz"
    curl -fsSL "https://github.com/DeusData/codebase-memory-mcp/releases/download/v0.11.0/codebase-memory-mcp-linux-amd64-portable.tar.gz" -o "$CBM_TAR"
    tar -xzf "$CBM_TAR" -C "$TARGET/bin/"
    rm -f "$CBM_TAR"
  fi
  ACTUAL_SHA="$(sha256sum "$TARGET/bin/codebase-memory-mcp" 2>/dev/null | awk '{print $1}')"
  if [ "$ACTUAL_SHA" != "$EXPECTED_CBM_SHA" ]; then
    echo "[!] ERROR: codebase-memory-mcp SHA256 mismatch or missing!"
    echo "    Expected: $EXPECTED_CBM_SHA"
    echo "    Actual:   $ACTUAL_SHA"
    exit 1
  fi
  if [ ! -f "$ROOT/bin/codebase-memory-mcp" ]; then
    cp "$TARGET/bin/codebase-memory-mcp" "$ROOT/bin/codebase-memory-mcp"
  fi
fi
chmod +x "$TARGET/bin/"* 2>/dev/null || true
# 5. Sync mcp/
echo "[*] Synchronizing mcp/..."
rsync -a --delete --exclude 'node_modules' "$ROOT/mcp/" "$TARGET/mcp/"
if [ -d "$ROOT/mcp/penulis-ilmiah/node_modules" ]; then
  rsync -a "$ROOT/mcp/penulis-ilmiah/node_modules" "$TARGET/mcp/penulis-ilmiah/"
fi

# 6. Sync rules/
echo "[*] Synchronizing rules/..."
rsync -a --delete "$ROOT/rules/" "$TARGET/rules/"

# 7. Sync vendor/ & profiles/
echo "[*] Synchronizing vendor/ and profiles/..."
rsync -a --delete "$ROOT/vendor/" "$TARGET/vendor/"
rsync -a --delete "$ROOT/profiles/" "$TARGET/profiles/"

# 8. Copy root configurations
echo "[*] Deploying root configurations (profile: $PROFILE)..."
if [ "$PROFILE" = "pentest" ]; then
  cp "$ROOT/profiles/mcp.pentest.json" "$TARGET/mcp.json"
else
  cp "$ROOT/mcp.json" "$TARGET/mcp.json"
fi
cp "$ROOT/config.yml" "$TARGET/config.yml"
cp "$ROOT/models.yml" "$TARGET/models.yml"
cp "$ROOT/AGENTS.md" "$TARGET/AGENTS.md"
echo "[+] Restore complete!"
echo "    Skills installed: $(ls -1 "$TARGET/skills" | wc -l)"
echo "    Manual skills:    $(ls -1 "$TARGET/manual-skills" | wc -l)"
echo "    Commands:         $(ls -1 "$TARGET/commands" | wc -l)"
echo "    Binaries:         $(ls -1 "$TARGET/bin" | wc -l)"
