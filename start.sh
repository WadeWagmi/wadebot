#!/usr/bin/env bash
# wadebot start — launch all components
# Usage: ./start.sh [--status] [--help]
set -euo pipefail

WADEBOT_DIR="$HOME/.wadebot"
ENV_FILE="$WADEBOT_DIR/.env"
PID_FILE="$WADEBOT_DIR/.overlay.pid"

# Ensure lsof/kill are findable
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
fail() { echo -e "${RED}❌ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }

# --- Help ---
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: start.sh [--status] [--help]"
    echo ""
    echo "  --status   Show component status without starting anything"
    echo "  --help     Show this help"
    echo ""
    echo "Reads config from $ENV_FILE"
    exit 0
fi

# --- Load config ---
if [[ -f "$ENV_FILE" ]]; then
    set -a; source "$ENV_FILE"; set +a
else
    fail "No .env found. Run install.sh first."
    exit 1
fi

OVERLAY_PORT="${OVERLAY_PORT:-8888}"
STATUS_ONLY=false
[[ "${1:-}" == "--status" ]] && STATUS_ONLY=true

# --- Piper check (CLI or python module) ---
has_piper() { command -v piper &>/dev/null || python3 -c "import piper" >/dev/null 2>&1; }

if [[ "$STATUS_ONLY" == "false" ]]; then
    echo -e "${BLUE}🎬 Starting wadebot...${NC}\n"

    # Start overlay server if not running
    if lsof -i ":$OVERLAY_PORT" &>/dev/null; then
        ok "Overlay server already running on port $OVERLAY_PORT"
    else
        OVERLAY_DIR="$WADEBOT_DIR/skills/vtuber-core/overlay"
        if [[ -d "$OVERLAY_DIR" ]]; then
            cd "$OVERLAY_DIR"
            nohup python3 -m http.server "$OVERLAY_PORT" &>/dev/null &
            echo $! > "$PID_FILE"
            sleep 1
            if lsof -i ":$OVERLAY_PORT" &>/dev/null; then
                ok "Overlay server started on port $OVERLAY_PORT"
            else
                fail "Could not start overlay server"
            fi
        else
            fail "Overlay directory not found: $OVERLAY_DIR"
        fi
    fi
fi

# --- Status ---
echo ""
echo -e "${BLUE}Component Status:${NC}"
has_piper && ok "Piper TTS" || warn "Piper TTS not found (install: pip3 install piper-tts)"
[[ -f "${PIPER_MODEL:-}" ]] && ok "Voice model: $(basename "${PIPER_MODEL}")" || warn "Voice model not configured"
lsof -i ":$OVERLAY_PORT" &>/dev/null && ok "Overlay: http://localhost:$OVERLAY_PORT/overlay.html" || fail "Overlay not running"

# Check for optional components
[[ -n "${ELEVENLABS_API_KEY:-}" ]] && ok "ElevenLabs TTS configured" || true
[[ -n "${VEADOTUBE_PORT:-}" ]] && ok "Veadotube port: $VEADOTUBE_PORT" || true
[[ -n "${VTUBE_STUDIO_PORT:-}" ]] && ok "VTube Studio port: $VTUBE_STUDIO_PORT" || true

echo ""
echo -e "${GREEN}🎬 wadebot is ready!${NC}"
echo -e "  say:      $WADEBOT_DIR/skills/vtuber-core/scripts/say.sh \"Hello!\""
echo -e "  think:    $WADEBOT_DIR/skills/vtuber-core/scripts/think.sh \"Hmm...\""
echo -e "  announce: $WADEBOT_DIR/skills/vtuber-social/scripts/announce.sh \"Going live!\""
echo -e "  stop:     $WADEBOT_DIR/stop.sh"
echo ""
