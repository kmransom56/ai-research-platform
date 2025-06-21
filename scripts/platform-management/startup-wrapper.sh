#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# AI Research Platform – Startup Wrapper
# Chooses between the Bash and Python managers based on either the
# STARTUP_MANAGER environment variable or the first CLI argument.
#   • bash   → startup-platform-clean.sh (default)
#   • python → startup_platform.py
# Any additional arguments after the selector are forwarded to the chosen
# manager unchanged.
# -----------------------------------------------------------------------------

set -euo pipefail

PLATFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASH_MANAGER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/startup-platform-clean.sh"
PYTHON_MANAGER="$PLATFORM_DIR/python/startup-scripts/startup_platform.py"

CHOICE="${STARTUP_MANAGER:-}"  # env-var override

# Allow positional selector: wrapper.sh python --some-arg
if [[ $# -gt 0 ]]; then
  case "$1" in
    bash|python)
      CHOICE="$1"
      shift  # remove selector arg, leave rest for manager
      ;;
  esac
fi

# Fallback default
CHOICE=${CHOICE:-bash}

case "$CHOICE" in
  bash)
    exec /bin/bash "$BASH_MANAGER" "$@"
    ;;
  python)
    exec /usr/bin/python3 "$PYTHON_MANAGER" "$@"
    ;;
  *)
    echo "❌ Unknown startup manager choice: $CHOICE (expected 'bash' or 'python')" >&2
    exit 1
    ;;
esac
