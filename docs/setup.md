# Setup Guide

## Prerequisites

- **OBS Studio** (streaming)
- **Python 3.10+** (scripts)
- **Node.js 18+** (optional, overlay dev)

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

### Option A: Veadotube Mini (PNG-Swap)

1. Download from [veadotube.com](https://veadotube.com/)
2. Create your avatar states (idle, talking, excited, etc.)
3. Enable the API in settings
4. Note the port from `~/.veadotube/instances/mini-*`

### Option B: VTube Studio (Live2D)

1. Install [VTube Studio](https://denchisoft.com/) (available on Steam or standalone)
2. Load your Live2D model (`.moc3` format + textures)
3. Set up expressions and hotkeys in VTube Studio
4. Enable the API: Settings → API → Start Server (default port 8001)
5. Set environment variable: `export WADEBOT_VTUBE_STUDIO_URL=ws://localhost:8001`
6. On first connection from wadebot, approve the plugin in VTube Studio

VTube Studio provides:
- Full Live2D physics and rigging
- Expression/motion hotkeys controllable via API
- Lip sync from audio input
- Parameter injection for fine-grained control

See the [VTube Studio API docs](https://github.com/DenchiSoft/VTubeStudio) for full details.

### Option C: PNG Fallback (No External App)

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

## Step 4: OBS Configuration

Recommended scene layout:
```
┌─────────────────────────────────┐
│                                 │
│      Content (Browser/App)      │
│                                 │
│  ┌──────┐                       │
│  │Avatar│    [Overlay]          │
│  │      │                       │
│  └──────┘                       │
└─────────────────────────────────┘
```

- **Content source:** Window/Display capture of your streaming content
- **Avatar:** Veadotube window capture, VTube Studio window, or browser source (PNG)
- **Overlay:** Browser source at localhost:8888

## Step 5: Go Live

The agent handles the rest. Start your stream destination (OBS → Settings → Stream), and the agent will:

1. Create or present content
2. Narrate via TTS
3. React with avatar expressions
4. Post highlights to socials
5. Interact with chat
6. Keep going until session ends
