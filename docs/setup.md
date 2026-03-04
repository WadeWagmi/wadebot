# Setup Guide

## Prerequisites

- **OBS Studio** (streaming)
- **Python 3.10+** (game controllers)
- **Node.js 18+** (overlay server)
- **Chrome/Chromium** (game automation via CDP)

## Step 1: TTS

### Piper (Free, Local)

```bash
# macOS
brew install piper

# Linux
pip install piper-tts

# Download a voice
mkdir -p ~/piper-voices
cd ~/piper-voices
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en_US-libritts-high.tar.gz
tar xzf voice-en_US-libritts-high.tar.gz
```

### Audio Routing

Your TTS audio needs to reach OBS without playing through speakers:

```bash
# macOS — install BlackHole
brew install blackhole-2ch

# Then in Audio MIDI Setup, create a Multi-Output Device:
# 1. BlackHole 2ch (for OBS to capture)
# 2. Your speakers/headphones (for you to monitor)
```

Set your TTS script to output to BlackHole. Set OBS to capture BlackHole as an audio source.

## Step 2: Avatar

### Veadotube Mini

1. Download from [veadotube.com](https://veadotube.com/)
2. Create your avatar states (idle, talking, excited, tilted)
3. Enable the API in settings
4. Note the port from `~/.veadotube/instances/mini-*`

### No-App Fallback

Use the overlay's built-in avatar system — just provide PNG images for each state. No external app needed.

## Step 3: Stream Overlay

```bash
cd wadebot/skills/vtuber-core/overlay/
python3 -m http.server 8888
```

In OBS:
1. Add Browser Source → `http://localhost:8888/overlay.html`
2. Set width/height to match your canvas
3. Add a Color Key filter for `#ff00ff` (magenta)

## Step 4: Game Automation

```bash
# Launch Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/tmp/chrome-vtuber \
  "https://your-game-url.com"

# Install Python dependencies
pip install websocket-client Pillow
```

## Step 5: OBS Configuration

Recommended scene layout:
```
┌─────────────────────────────┐
│                             │
│      Game (Browser)         │
│                             │
│  ┌──────┐                   │
│  │Avatar│    [Overlay]      │
│  │      │                   │
│  └──────┘                   │
└─────────────────────────────┘
```

- **Game source:** Window/Display capture of Chrome
- **Avatar:** Veadotube window capture (or browser source)
- **Overlay:** Browser source at localhost:8888

## Step 6: Go Live

The agent handles the rest. Start your stream destination (OBS → Settings → Stream), and the agent will:

1. Detect the game state
2. Make decisions
3. Narrate via TTS
4. React with avatar expressions
5. Post highlights to socials
6. Keep going until session ends
