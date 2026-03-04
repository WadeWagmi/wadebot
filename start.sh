#!/usr/bin/env bash
# wadebot start — launch all components
set -euo pipefail

WADEBOT_DIR="$HOME/.wadebot"
ENV_FILE="$WADEBOT_DIR/.env"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
fail() { echo -e "${RED}❌ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }

echo -e "${BLUE}🎬 Starting wadebot...${NC}\n"

# Source config
if [[ -f "$ENV_FILE" ]]; then
    set -a; source "$ENV_FILE"; set +a
    ok "Config loaded from $ENV_FILE"
else
    fail "No .env found. Run install.sh first."
    exit 1
fi

OVERLAY_PORT="${OVERLAY_PORT:-8888}"

# Start overlay server if not running
if lsof -i ":$OVERLAY_PORT" &>/dev/null; then
    ok "Overlay server running on port $OVERLAY_PORT"
else
    cd "$WADEBOT_DIR/skills/vtuber-core/overlay"
    nohup python3 -m http.server "$OVERLAY_PORT" &>/dev/null &
    sleep 1
    if lsof -i ":$OVERLAY_PORT" &>/dev/null; then
        ok "Overlay server started on port $OVERLAY_PORT"
    else
        fail "Could not start overlay server"
    fi
fi

# Status check
echo ""
echo -e "${BLUE}Component Status:${NC}"
command -v piper &>/dev/null && ok "Piper TTS" || warn "Piper TTS not found"
[[ -f "${PIPER_MODEL:-}" ]] && ok "Voice model: $(basename "${PIPER_MODEL}")" || warn "Voice model not found"
lsof -i ":$OVERLAY_PORT" &>/dev/null && ok "Overlay: http://localhost:$OVERLAY_PORT/overlay.html" || fail "Overlay not running"

echo ""
echo -e "${GREEN}🎬 wadebot is ready to stream!${NC}"
echo -e "  say.sh:   $WADEBOT_DIR/skills/vtuber-core/scripts/say.sh \"Hello!\""
echo -e "  think.sh: $WADEBOT_DIR/skills/vtuber-core/scripts/think.sh \"Hmm...\""
echo ""
