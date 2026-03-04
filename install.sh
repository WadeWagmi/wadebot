#!/usr/bin/env bash
# wadebot installer — one command to rule them all
# curl -sL https://raw.githubusercontent.com/WadeWagmi/wadebot/main/install.sh | bash
set -euo pipefail

WADEBOT_DIR="$HOME/.wadebot"
VOICES_DIR="$WADEBOT_DIR/voices"
REPO_URL="https://github.com/WadeWagmi/wadebot.git"
OVERLAY_PORT=8888
PIPER_VOICE=""
PIPER_SPEAKER=""
SKIP_VOICE=false

# --- Colors ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; PURPLE='\033[0;35m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
fail() { echo -e "${RED}❌ $*${NC}"; }
info() { echo -e "${BLUE}⏳ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
head() { echo -e "\n${PURPLE}━━━ $* ━━━${NC}"; }

# --- Detect OS ---
head "Detecting OS"
OS="unknown"
ARCH="$(uname -m)"
if [[ "$(uname)" == "Darwin" ]]; then
    OS="macos"
    ok "macOS detected ($ARCH)"
elif [[ -f /proc/version ]] && grep -qi microsoft /proc/version 2>/dev/null; then
    OS="wsl"
    ok "WSL (Windows Subsystem for Linux) detected"
elif [[ "$(uname)" == "Linux" ]]; then
    OS="linux"
    ok "Linux detected ($ARCH)"
else
    fail "Unsupported OS: $(uname)"
    exit 1
fi

# --- Helper: check command exists ---
has() { command -v "$1" &>/dev/null; }

# --- Install Homebrew if needed (macOS) ---
ensure_brew() {
    if ! has brew; then
        info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" </dev/null || {
            fail "Homebrew install failed. Visit https://brew.sh"
            return 1
        }
        # Add to path for this session
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
    ok "Homebrew available"
}

# --- Voice Selection ---
head "Voice Selection"
if [ -t 0 ]; then
    echo ""
    echo -e "🎙️  Choose a voice:"
    echo ""
    echo -e "  1) Male (US English) — default"
    echo -e "  2) Female (US English)"
    echo -e "  3) Male (UK English)"
    echo -e "  4) Female (UK English)"
    echo -e "  5) Skip — I'll configure my own voice later"
    echo ""
    printf "Enter choice [1]: "
    read -r VOICE_CHOICE
    VOICE_CHOICE="${VOICE_CHOICE:-1}"
else
    VOICE_CHOICE="1"
    info "Non-interactive mode, defaulting to Male (US English)"
fi

case "$VOICE_CHOICE" in
    1)
        PIPER_VOICE="en_US-libritts-high"
        PIPER_SPEAKER=34
        PIPER_VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/libritts/high"
        ok "Selected: Male (US English)"
        ;;
    2)
        PIPER_VOICE="en_US-libritts-high"
        PIPER_SPEAKER=92
        PIPER_VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/libritts/high"
        ok "Selected: Female (US English)"
        ;;
    3)
        PIPER_VOICE="en_GB-cori-high"
        PIPER_SPEAKER=0
        PIPER_VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/cori/high"
        ok "Selected: Male (UK English)"
        ;;
    4)
        PIPER_VOICE="en_GB-jenny_dioco-medium"
        PIPER_SPEAKER=0
        PIPER_VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/jenny_dioco/medium"
        ok "Selected: Female (UK English)"
        ;;
    5)
        SKIP_VOICE=true
        ok "Skipping voice download"
        ;;
    *)
        warn "Invalid choice, defaulting to Male (US English)"
        PIPER_VOICE="en_US-libritts-high"
        PIPER_SPEAKER=34
        PIPER_VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/libritts/high"
        ;;
esac

# --- 1. Install Piper TTS ---
head "Installing Piper TTS"
if has piper; then
    ok "Piper already installed"
else
    if [[ "$OS" == "macos" ]]; then
        ensure_brew
        info "Installing piper via Homebrew..."
        brew install piper 2>/dev/null || {
            # Fallback: try pip
            info "Brew failed, trying pip..."
            pip3 install piper-tts 2>/dev/null || {
                fail "Could not install Piper. Try: brew install piper OR pip3 install piper-tts"
            }
        }
    else
        info "Installing piper via pip..."
        pip3 install piper-tts 2>/dev/null || {
            # Try with --user
            pip3 install --user piper-tts 2>/dev/null || {
                fail "Could not install Piper. Try: pip3 install piper-tts"
            }
        }
    fi
    if has piper; then
        ok "Piper installed"
    else
        warn "Piper may not be on PATH. Check your shell config."
    fi
fi

# --- 2. Download voice ---
head "Setting up voice"
mkdir -p "$VOICES_DIR"
ONNX="$VOICES_DIR/${PIPER_VOICE}.onnx"
JSON="$VOICES_DIR/${PIPER_VOICE}.onnx.json"

if [[ "$SKIP_VOICE" == "true" ]]; then
    ok "Voice download skipped (configure manually in .env)"
    ONNX=""
elif [[ -f "$ONNX" && -f "$JSON" ]]; then
    ok "Voice already downloaded"
else
    info "Downloading $PIPER_VOICE voice model..."
    curl -sL "$PIPER_VOICE_URL/${PIPER_VOICE}.onnx" -o "$ONNX" || {
        fail "Failed to download voice model"
    }
    curl -sL "$PIPER_VOICE_URL/${PIPER_VOICE}.onnx.json" -o "$JSON" || {
        fail "Failed to download voice config"
    }
    if [[ -f "$ONNX" && -f "$JSON" ]]; then
        ok "Voice downloaded to $VOICES_DIR"
    else
        fail "Voice download incomplete"
    fi
fi

# --- 3. Install audio routing ---
head "Audio routing"
if [[ "$OS" == "macos" ]]; then
    if brew list blackhole-2ch &>/dev/null 2>&1; then
        ok "BlackHole already installed"
    else
        ensure_brew
        info "Installing BlackHole 2ch (virtual audio cable)..."
        brew install blackhole-2ch 2>/dev/null && ok "BlackHole installed" || {
            warn "BlackHole install failed. Install manually: brew install blackhole-2ch"
        }
    fi
else
    if has pactl; then
        ok "PulseAudio available"
    else
        info "Installing PulseAudio..."
        sudo apt-get install -y pulseaudio 2>/dev/null && ok "PulseAudio installed" || {
            warn "PulseAudio install failed. Try: sudo apt-get install pulseaudio"
        }
    fi
fi

# --- 4. Clone/update repo ---
head "Setting up wadebot"
if [[ -d "$WADEBOT_DIR/.git" ]]; then
    info "Updating existing install..."
    cd "$WADEBOT_DIR" && git pull --ff-only 2>/dev/null && ok "Updated" || ok "Already up to date"
else
    if [[ -d "$WADEBOT_DIR" ]] && [[ ! -d "$WADEBOT_DIR/.git" ]]; then
        # Directory exists but isn't a git repo — clone into temp and merge
        info "Cloning wadebot..."
        git clone "$REPO_URL" "${WADEBOT_DIR}.tmp" 2>/dev/null
        cp -rn "${WADEBOT_DIR}.tmp/"* "$WADEBOT_DIR/" 2>/dev/null || true
        cp -rn "${WADEBOT_DIR}.tmp/".git "$WADEBOT_DIR/" 2>/dev/null || true
        rm -rf "${WADEBOT_DIR}.tmp"
        ok "Cloned to $WADEBOT_DIR"
    else
        info "Cloning wadebot..."
        git clone "$REPO_URL" "$WADEBOT_DIR" 2>/dev/null && ok "Cloned to $WADEBOT_DIR" || {
            fail "Git clone failed. Check your internet connection."
            exit 1
        }
    fi
fi

# --- 5. Generate .env ---
head "Configuration"
ENV_FILE="$WADEBOT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
    ok ".env already exists (not overwriting)"
else
    cat > "$ENV_FILE" <<EOF
# wadebot configuration
TTS_ENGINE=piper
PIPER_MODEL=$ONNX
PIPER_SPEAKER=${PIPER_SPEAKER:-34}
OVERLAY_URL=http://localhost:$OVERLAY_PORT/overlay.html
OVERLAY_PORT=$OVERLAY_PORT
AGENT_NAME=MyAgent
# ELEVENLABS_API_KEY=your-key-here
# VEADOTUBE_PORT=49152
# VTUBE_STUDIO_PORT=8001
EOF
    ok "Generated $ENV_FILE"
fi

# --- 6. Make scripts executable ---
head "Permissions"
chmod +x "$WADEBOT_DIR/skills/vtuber-core/scripts/"*.sh 2>/dev/null || true
chmod +x "$WADEBOT_DIR/install.sh" 2>/dev/null || true
chmod +x "$WADEBOT_DIR/start.sh" 2>/dev/null || true
ok "Scripts are executable"

# --- 7. Start overlay server ---
head "Overlay server"
if lsof -i ":$OVERLAY_PORT" &>/dev/null; then
    ok "Overlay server already running on port $OVERLAY_PORT"
else
    info "Starting overlay server on port $OVERLAY_PORT..."
    cd "$WADEBOT_DIR/skills/vtuber-core/overlay"
    nohup python3 -m http.server "$OVERLAY_PORT" &>/dev/null &
    sleep 1
    if lsof -i ":$OVERLAY_PORT" &>/dev/null; then
        ok "Overlay server running at http://localhost:$OVERLAY_PORT"
    else
        warn "Overlay server may not have started. Run manually:"
        echo "  cd $WADEBOT_DIR/skills/vtuber-core/overlay && python3 -m http.server $OVERLAY_PORT &"
    fi
fi

# --- 8. Test TTS ---
head "Testing TTS"
if has piper && [[ -n "$ONNX" && -f "$ONNX" ]]; then
    info "Speaking test phrase..."
    echo "wadebot is ready" | piper --model "$ONNX" --speaker "${PIPER_SPEAKER:-34}" --output_raw 2>/dev/null | \
        (has play && play -r 22050 -e signed -b 16 -c 1 -t raw - 2>/dev/null || \
         has aplay && aplay -r 22050 -f S16_LE -c 1 2>/dev/null || \
         cat > /dev/null) && ok "TTS works!" || warn "TTS test failed (audio playback issue — TTS itself may be fine)"
else
    warn "Piper not found — skipping TTS test"
fi

# --- Done! ---
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  🎬 wadebot is installed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  📁 Installed to: ${BLUE}$WADEBOT_DIR${NC}"
echo -e "  🌐 Overlay:      ${BLUE}http://localhost:$OVERLAY_PORT/overlay.html${NC}"
echo -e "  ⚙️  Config:       ${BLUE}$ENV_FILE${NC}"
echo ""
echo -e "${YELLOW}  Manual steps remaining:${NC}"
echo ""
echo -e "  1. ${PURPLE}Open OBS Studio${NC} → Add Browser Source"
echo -e "     URL: http://localhost:$OVERLAY_PORT/overlay.html"
echo -e "     Add Color Key filter for #ff00ff (magenta)"
echo ""
echo -e "  2. ${PURPLE}(Optional) Install an avatar:${NC}"
echo -e "     • Veadotube Mini — https://veadotube.com/"
echo -e "     • VTube Studio   — https://denchisoft.com/"
echo ""
echo -e "  3. ${PURPLE}Start streaming!${NC}"
echo -e "     $WADEBOT_DIR/start.sh"
echo ""
echo -e "  ${BLUE}Test it now:${NC}"
echo -e "  source $ENV_FILE"
echo -e "  $WADEBOT_DIR/skills/vtuber-core/scripts/say.sh \"Hello world!\""
echo ""
