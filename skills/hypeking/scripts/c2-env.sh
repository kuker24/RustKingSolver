# C2 / red-team tool PATH — source from shell or omp session
#   source ~/.omp/agent/skills/hypeking/scripts/c2-env.sh
export HYPEKING_C2_TOOLS="${HYPEKING_C2_TOOLS:-$HOME/tools}"
export ADAPTIX_ROOT="${ADAPTIX_ROOT:-$HYPEKING_C2_TOOLS/AdaptixC2}"
export CALDERA_ROOT="${CALDERA_ROOT:-$HYPEKING_C2_TOOLS/caldera}"
export SLIVER_TOOLS="${SLIVER_TOOLS:-$HYPEKING_C2_TOOLS/sliver}"
export C2_VENV="${C2_VENV:-$HYPEKING_C2_TOOLS/c2-venv}"
export PATH="$HOME/.local/bin:$SLIVER_TOOLS:$PATH"
# Prefer C2 venv for sliver-py / gophish / ldap3 / requests helpers
if [[ -x "$C2_VENV/bin/python" ]]; then
  export PATH="$C2_VENV/bin:$PATH"
  export VIRTUAL_ENV="$C2_VENV"
fi
# GoPhish binary if present
[[ -x /opt/gophish/gophish ]] && export PATH="/opt/gophish:$PATH"
[[ -x /usr/local/bin/gophish ]] && export PATH="/usr/local/bin:$PATH"
