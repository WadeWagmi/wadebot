#!/usr/bin/env bash
# Start the chat bridge for Twitch or YouTube
# Usage:
#   start-chat.sh --channel <twitch_channel>
#   start-chat.sh --youtube <youtube_url>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WADEBOT_DIR="${WADEBOT_DIR:-$HOME/.wadebot}"

# Load .env if available
[ -f "$WADEBOT_DIR/.env" ] && source "$WADEBOT_DIR/.env"

SERVER="${WADEBOT_SERVER:-http://localhost:${OVERLAY_PORT:-8888}}"

exec python3 "$SCRIPT_DIR/chat-bridge.py" --server "$SERVER" "$@"
