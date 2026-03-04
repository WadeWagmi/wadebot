#!/bin/bash
# Install and configure Piper TTS for wadebot
# Usage: ./setup-tts.sh [voice-name]
#
# Default voice: en_US-libritts-high (multi-speaker, good quality)
# Browse voices: https://rhasspy.github.io/piper-samples/

set -euo pipefail

VOICE="${1:-en_US-libritts-high}"
VOICE_DIR="${WADEBOT_VOICE_DIR:-$HOME/piper-voices}"

echo "🎙️  wadebot TTS Setup"
echo "===================="
echo "Voice: $VOICE"
echo "Directory: $VOICE_DIR"
echo ""

# ── Install Piper ──
if command -v piper &>/dev/null; then
  echo "✅ Piper already installed: $(which piper)"
else
  echo "📦 Installing Piper..."
  OS="$(uname -s)"
  case "$OS" in
    Darwin)
      if command -v brew &>/dev/null; then
        brew install piper
      else
        echo "Install Homebrew first: https://brew.sh" >&2
        exit 1
      fi
      ;;
    Linux)
      if command -v pip3 &>/dev/null; then
        pip3 install piper-tts
      elif command -v pip &>/dev/null; then
        pip install piper-tts
      else
        echo "Install pip first: sudo apt install python3-pip" >&2
        exit 1
      fi
      ;;
    *)
      echo "Unsupported OS: $OS. Install Piper manually: https://github.com/rhasspy/piper" >&2
      exit 1
      ;;
  esac
  echo "✅ Piper installed"
fi

# ── Install sox (for play command) ──
if command -v play &>/dev/null; then
  echo "✅ sox already installed"
else
  echo "📦 Installing sox (for audio playback)..."
  OS="$(uname -s)"
  case "$OS" in
    Darwin) brew install sox ;;
    Linux) sudo apt-get install -y sox ;;
  esac
  echo "✅ sox installed"
fi

# ── Download voice model ──
mkdir -p "$VOICE_DIR"
MODEL_FILE="$VOICE_DIR/${VOICE}.onnx"
CONFIG_FILE="$VOICE_DIR/${VOICE}.onnx.json"

if [ -f "$MODEL_FILE" ]; then
  echo "✅ Voice model already downloaded: $MODEL_FILE"
else
  echo "📥 Downloading voice: $VOICE ..."
  BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"
  # Voice path structure: language/region/name/quality/
  LANG=$(echo "$VOICE" | cut -d'-' -f1-2)     # e.g., en_US
  NAME=$(echo "$VOICE" | cut -d'-' -f3-)       # e.g., libritts-high
  LANG_UNDER=$(echo "$LANG" | tr '_' '/')      # e.g., en/US (wrong)
  # Actually piper voices use: en/en_US/libritts/high/
  LANG_SHORT=$(echo "$LANG" | cut -d'_' -f1)
  QUALITY=$(echo "$NAME" | rev | cut -d'-' -f1 | rev)
  MODEL_NAME=$(echo "$NAME" | sed "s/-${QUALITY}$//")

  VOICE_URL="${BASE_URL}/${LANG_SHORT}/${LANG}/${MODEL_NAME}/${QUALITY}/${VOICE}.onnx"
  CONFIG_URL="${VOICE_URL}.json"

  curl -L -o "$MODEL_FILE" "$VOICE_URL" || {
    echo "❌ Failed to download voice model. Try manually:" >&2
    echo "   Browse: https://rhasspy.github.io/piper-samples/" >&2
    exit 1
  }
  curl -L -o "$CONFIG_FILE" "$CONFIG_URL" 2>/dev/null || true
  echo "✅ Voice downloaded: $MODEL_FILE"
fi

# ── Test it ──
echo ""
echo "🧪 Testing TTS..."
echo "Hello! I am your streaming agent." | piper -m "$MODEL_FILE" --output-raw --sentence-silence 0.1 2>/dev/null \
  | play -t raw -r 22050 -e signed -b 16 -c 1 - 2>/dev/null && echo "✅ TTS working!" || echo "⚠️  TTS test failed (audio device issue?)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setup complete! Add to your environment:"
echo ""
echo "  export WADEBOT_PIPER_MODEL=\"$MODEL_FILE\""
echo "  export WADEBOT_PIPER_SPEAKER=0"
echo ""
echo "Then use: ./say.sh \"Hello world!\""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
