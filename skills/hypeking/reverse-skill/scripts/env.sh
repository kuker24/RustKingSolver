# reverse-skill tool PATH — source from shell or omp session
export REVERSE_SKILL_TOOLS_DIR="${REVERSE_SKILL_TOOLS_DIR:-$HOME/tools}"
export PATH="$HOME/.local/bin:$REVERSE_SKILL_TOOLS_DIR/jadx/bin:$REVERSE_SKILL_TOOLS_DIR/apktool:$REVERSE_SKILL_TOOLS_DIR/ghidra:$PATH"
# optional RE python libs
export RE_VENV="${RE_VENV:-$HOME/tools/re-venv}"
[[ -d "$RE_VENV" ]] && export PATH="$RE_VENV/bin:$PATH"
