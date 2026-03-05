#!/bin/bash
# Multi-agent say — TTS + overlay with agent name
# Usage: ./multi-say.sh --agent Wade "Hello world"
#        ./multi-say.sh --agent RoboPat --type thought "Hmm interesting"
#        ./multi-say.sh --agent Wade --no-tts "Silent overlay message"
#
# Environment:
#   WADEBOT_OVERLAY_DIR    — path to overlay directory
#   WADEBOT_TTS_CMD        — TTS command (overrides auto-detect)
#   WADEBOT_PIPER_MODEL    — path to piper .onnx model
#   WADEBOT_PIPER_SPEAKER  — piper speaker id (default: 0)

set -euo pipefail

# ── Parse args ──
AGENT="Agent"
TYPE="speech"
TTS=true

while [[ $# -gt 0 ]]; do
  case $1 in
    --agent) AGENT="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    --no-tts) TTS=false; shift ;;
    --thought) TYPE="thought"; TTS=false; shift ;;
    *) break ;;
  esac
done

TEXT="$*"
if [ -z "$TEXT" ]; then
  echo "Usage: multi-say.sh [--agent NAME] [--type speech|thought] [--no-tts] <text>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OVERLAY_DIR="${WADEBOT_OVERLAY_DIR:-$SCRIPT_DIR/../overlay}"
MESSAGES_FILE="$OVERLAY_DIR/messages.json"

# ── Update multi-agent overlay ──
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")

# Also update legacy thought.json for backward compat
cat > "$OVERLAY_DIR/thought.json" <<EOF
{"text": "$TEXT", "timestamp": $TIMESTAMP, "type": "$TYPE", "agent": "$AGENT"}
EOF

# Append to messages.json (keep last 20 messages)
python3 -c "
import json, os, sys

f = '$MESSAGES_FILE'
msg = {'text': '''$TEXT''', 'timestamp': $TIMESTAMP, 'type': '$TYPE', 'agent': '$AGENT'}

try:
    with open(f) as fh:
        data = json.load(fh)
except:
    data = {'messages': []}

data['messages'].append(msg)
data['messages'] = data['messages'][-20:]  # keep last 20

with open(f, 'w') as fh:
    json.dump(data, fh)
"

echo "[$AGENT] ($TYPE) $TEXT"

# ── TTS ──
if [ "$TTS" = false ]; then
  exit 0
fi

if [ -n "${WADEBOT_TTS_CMD:-}" ]; then
  echo "$TEXT" | eval "$WADEBOT_TTS_CMD"
elif command -v piper &>/dev/null || python3 -m piper --help &>/dev/null 2>&1; then
  VOICE="${WADEBOT_PIPER_MODEL:-}"
  SPEAKER="${WADEBOT_PIPER_SPEAKER:-0}"
  if [ -z "$VOICE" ]; then
    echo "Warning: WADEBOT_PIPER_MODEL not set." >&2
    exit 1
  fi
  PIPER_CMD="piper"
  if ! command -v piper &>/dev/null; then
    PIPER_CMD="python3 -m piper"
  fi
  echo "$TEXT" | $PIPER_CMD -m "$VOICE" -s "$SPEAKER" --output-raw --sentence-silence 0.1 2>/dev/null \
    | play -t raw -r 22050 -e signed -b 16 -c 1 - 2>/dev/null
elif command -v say &>/dev/null; then
  say "$TEXT"
elif command -v espeak &>/dev/null; then
  espeak "$TEXT"
else
  echo "No TTS engine found." >&2
fi
