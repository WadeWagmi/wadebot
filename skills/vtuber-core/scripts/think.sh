#!/bin/bash
# Show a thought on the overlay — NO audio, silent internal monologue
# Usage: ./think.sh "thinking about something..."
#
# Environment:
#   WADEBOT_OVERLAY_DIR  — path to overlay directory (default: ../overlay)

set -euo pipefail

TEXT="$*"
if [ -z "$TEXT" ]; then
  echo "Usage: think.sh <text>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OVERLAY_DIR="${WADEBOT_OVERLAY_DIR:-$SCRIPT_DIR/../overlay}"

TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
cat > "$OVERLAY_DIR/thought.json" <<EOF
{"text": "$TEXT", "timestamp": $TIMESTAMP, "type": "thought"}
EOF
