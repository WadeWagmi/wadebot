#!/bin/bash
# Send a message via the wadebot overlay server API
# Usage: ./say-api.sh --agent Wade "Hello world"
#        ./say-api.sh --agent RoboPat --type thought "Interesting..."
#
# Requires the overlay server to be running (python3 server/server.py)
# This replaces file-based messaging with HTTP API calls.
#
# Environment:
#   WADEBOT_API_URL  — server URL (default: http://localhost:8888)

set -euo pipefail

API_URL="${WADEBOT_API_URL:-http://localhost:8888}"
AGENT="Agent"
TYPE="speech"

while [[ $# -gt 0 ]]; do
  case $1 in
    --agent) AGENT="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    --thought) TYPE="thought"; shift ;;
    *) break ;;
  esac
done

TEXT="$*"
if [ -z "$TEXT" ]; then
  echo "Usage: say-api.sh [--agent NAME] [--type speech|thought] <text>" >&2
  exit 1
fi

# Escape text for JSON
ESCAPED_TEXT=$(echo "$TEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

# POST to server
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/say" \
  -H "Content-Type: application/json" \
  -d "{\"agent\": \"$AGENT\", \"text\": $ESCAPED_TEXT, \"type\": \"$TYPE\"}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
  echo "[$AGENT] ($TYPE) $TEXT"
else
  echo "Error ($HTTP_CODE): $BODY" >&2
  exit 1
fi
