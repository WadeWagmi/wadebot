#!/usr/bin/env bash
# wadebot stop — stop all wadebot components
set -euo pipefail

WADEBOT_DIR="$HOME/.wadebot"
ENV_FILE="$WADEBOT_DIR/.env"
PID_FILE="$WADEBOT_DIR/.overlay.pid"

export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }

# Load config for port
if [[ -f "$ENV_FILE" ]]; then
    set -a; source "$ENV_FILE"; set +a
fi
OVERLAY_PORT="${OVERLAY_PORT:-8888}"

echo "🛑 Stopping wadebot..."

# Kill overlay server
KILLED=false
if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null && ok "Overlay server stopped (pid $PID)" || warn "Could not stop overlay (pid $PID)"
        KILLED=true
    fi
    rm -f "$PID_FILE"
fi

# Fallback: kill by port
if [[ "$KILLED" == "false" ]]; then
    PIDS=$(lsof -ti ":$OVERLAY_PORT" 2>/dev/null || true)
    if [[ -n "$PIDS" ]]; then
        echo "$PIDS" | xargs kill 2>/dev/null && ok "Overlay server stopped (port $OVERLAY_PORT)" || warn "Could not stop overlay on port $OVERLAY_PORT"
    else
        ok "Overlay server not running"
    fi
fi

echo ""
echo "Done. Run start.sh to restart."
