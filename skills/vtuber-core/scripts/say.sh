#!/bin/bash
# Say something out loud — TTS + overlay update
# Usage: ./say.sh "text to say"
#
# Environment:
#   WADEBOT_OVERLAY_DIR  — path to overlay directory (default: ../overlay)
#   WADEBOT_TTS_CMD      — TTS command (default: piper-based, see below)
#   WADEBOT_AGENT_NAME   — agent name for overlay (default: Agent)
#
# TTS engines (set WADEBOT_TTS_CMD):
#   Piper:      echo "$TEXT" | piper -m /path/to/model.onnx --output-raw | play -t raw -r 22050 -e signed -b 16 -c 1 -
#   ElevenLabs: Use the sag CLI or curl the API
#   macOS:      say -v "Alex" "$TEXT"
#   espeak:     espeak "$TEXT"

set -euo pipefail

TEXT="$*"
if [ -z "$TEXT" ]; then
  echo "Usage: say.sh <text>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OVERLAY_DIR="${WADEBOT_OVERLAY_DIR:-$SCRIPT_DIR/../overlay}"

# ── Update overlay ──
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
cat > "$OVERLAY_DIR/thought.json" <<EOF
{"text": "$TEXT", "timestamp": $TIMESTAMP, "type": "speech"}
EOF

# ── Speak via TTS ──
if [ -n "${WADEBOT_TTS_CMD:-}" ]; then
  # Custom TTS command — pipe text to it
  echo "$TEXT" | eval "$WADEBOT_TTS_CMD"
elif command -v piper &>/dev/null; then
  # Default: Piper local TTS
  VOICE="${WADEBOT_PIPER_MODEL:-}"
  SPEAKER="${WADEBOT_PIPER_SPEAKER:-0}"
  if [ -z "$VOICE" ]; then
    echo "Warning: WADEBOT_PIPER_MODEL not set. Set it to your .onnx model path." >&2
    echo "Example: export WADEBOT_PIPER_MODEL=~/piper-voices/en_US-libritts-high.onnx" >&2
    exit 1
  fi
  echo "$TEXT" | piper -m "$VOICE" -s "$SPEAKER" --output-raw --sentence-silence 0.1 2>/dev/null \
    | play -t raw -r 22050 -e signed -b 16 -c 1 - 2>/dev/null
elif command -v say &>/dev/null; then
  # Fallback: macOS built-in TTS
  say "$TEXT"
elif command -v espeak &>/dev/null; then
  # Fallback: espeak
  espeak "$TEXT"
else
  echo "No TTS engine found. Install piper, or set WADEBOT_TTS_CMD." >&2
  echo "(Overlay was still updated)" >&2
fi
