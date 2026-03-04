#!/bin/bash
# Announce that the agent is going live
# Usage: ./announce.sh "Going live! Playing some blackjack tonight."
#        ./announce.sh  (uses default message)
#
# Integrations (configure via environment):
#   WADEBOT_TWITTER_CMD    — command to post a tweet (e.g., "bird tweet" or "python3 ~/scripts/tweet.py")
#   WADEBOT_DISCORD_WEBHOOK — Discord webhook URL for announcements
#   WADEBOT_STREAM_URL     — URL where the stream is live
#
# Example:
#   export WADEBOT_TWITTER_CMD="python3 ~/scripts/tweet.py"
#   export WADEBOT_STREAM_URL="https://twitch.tv/myagent"
#   ./announce.sh "Going live with some coding! Come hang out."

set -euo pipefail

DEFAULT_MSG="Going live! Come watch the stream. 🎬"
MESSAGE="${*:-$DEFAULT_MSG}"
STREAM_URL="${WADEBOT_STREAM_URL:-}"

# Append stream URL if set
if [ -n "$STREAM_URL" ]; then
  FULL_MESSAGE="$MESSAGE\n\n$STREAM_URL"
else
  FULL_MESSAGE="$MESSAGE"
fi

echo "📢 Stream announcement: $MESSAGE"

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
  echo "  export WADEBOT_ANNOUNCE_HOOK='your-custom-command'"
fi

echo "✅ Announced to $POSTED channel(s)"
