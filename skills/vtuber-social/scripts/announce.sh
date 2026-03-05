#!/bin/bash
# Announce that an agent is going live
# Usage: ./announce.sh "Going live! Coding session tonight."
#        ./announce.sh --agent Wade "Streaming some code!"
#        ./announce.sh  (uses default message)
#
# Integrations (configure via environment):
#   WADEBOT_TWITTER_CMD      — command to post a tweet
#   WADEBOT_DISCORD_WEBHOOK  — Discord webhook URL
#   WADEBOT_TELEGRAM_BOT     — Telegram bot token
#   WADEBOT_TELEGRAM_CHAT    — Telegram chat ID
#   WADEBOT_STREAM_URL       — URL where the stream is live
#   WADEBOT_ANNOUNCE_HOOK    — custom command (receives message on stdin)

set -euo pipefail

# ── Parse args ──
AGENT=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --agent) AGENT="$2"; shift 2 ;;
    *) break ;;
  esac
done

DEFAULT_MSG="Going live! Come watch the stream. 🎬"
MESSAGE="${*:-$DEFAULT_MSG}"
STREAM_URL="${WADEBOT_STREAM_URL:-}"

# Prefix with agent name if provided
if [ -n "$AGENT" ]; then
  DISPLAY_MSG="[$AGENT] $MESSAGE"
else
  DISPLAY_MSG="$MESSAGE"
fi

# Append stream URL if set
if [ -n "$STREAM_URL" ]; then
  FULL_MESSAGE="$DISPLAY_MSG\n\n$STREAM_URL"
else
  FULL_MESSAGE="$DISPLAY_MSG"
fi

echo "📢 Stream announcement: $DISPLAY_MSG"

POSTED=0

# ── Twitter ──
if [ -n "${WADEBOT_TWITTER_CMD:-}" ]; then
  echo "  → Twitter..."
  eval "$WADEBOT_TWITTER_CMD" "$(echo -e "$FULL_MESSAGE")" && POSTED=$((POSTED + 1)) || echo "  ⚠️  Twitter post failed"
fi

# ── Discord Webhook ──
if [ -n "${WADEBOT_DISCORD_WEBHOOK:-}" ]; then
  echo "  → Discord..."
  curl -s -H "Content-Type: application/json" \
    -d "{\"content\": \"$(echo -e "$FULL_MESSAGE" | sed 's/"/\\"/g')\"}" \
    "$WADEBOT_DISCORD_WEBHOOK" && POSTED=$((POSTED + 1)) || echo "  ⚠️  Discord post failed"
fi

# ── Telegram ──
if [ -n "${WADEBOT_TELEGRAM_BOT:-}" ] && [ -n "${WADEBOT_TELEGRAM_CHAT:-}" ]; then
  echo "  → Telegram..."
  curl -s "https://api.telegram.org/bot${WADEBOT_TELEGRAM_BOT}/sendMessage" \
    -d "chat_id=${WADEBOT_TELEGRAM_CHAT}" \
    -d "text=$(echo -e "$FULL_MESSAGE")" \
    -d "parse_mode=Markdown" > /dev/null && POSTED=$((POSTED + 1)) || echo "  ⚠️  Telegram post failed"
fi

# ── Custom hook ──
if [ -n "${WADEBOT_ANNOUNCE_HOOK:-}" ]; then
  echo "  → Custom hook..."
  echo -e "$FULL_MESSAGE" | eval "$WADEBOT_ANNOUNCE_HOOK" && POSTED=$((POSTED + 1)) || echo "  ⚠️  Custom hook failed"
fi

if [ "$POSTED" -eq 0 ]; then
  echo ""
  echo "No announcement channels configured. Set one or more:"
  echo "  export WADEBOT_TWITTER_CMD='bird tweet'"
  echo "  export WADEBOT_DISCORD_WEBHOOK='https://discord.com/api/webhooks/...'"
  echo "  export WADEBOT_TELEGRAM_BOT='bot-token'"
  echo "  export WADEBOT_TELEGRAM_CHAT='chat-id'"
  echo "  export WADEBOT_ANNOUNCE_HOOK='your-custom-command'"
fi

echo "✅ Announced to $POSTED channel(s)"
