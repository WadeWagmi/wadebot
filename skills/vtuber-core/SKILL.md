# vtuber-core

Give your agent a voice, a face, and a stream. The foundation for any autonomous VTuber.

## Components

### TTS (Text-to-Speech)
- **Piper** (recommended) — free, local, streaming, no API key needed
- **ElevenLabs** — premium voices, requires API key
- **macOS `say`** — built-in fallback, zero setup
- **espeak** — Linux fallback

Run `scripts/setup-tts.sh` to auto-install Piper and download a voice.

### Stream Overlay
Drop-in HTML/JS overlay for OBS:
- 🎤 Speech bubbles (what the agent says aloud, green border)
- 💭 Thought bubbles (internal monologue, silent, purple border)
- Auto-dims old messages, removes overflow
- Chroma key background (`#ff00ff`) — add OBS color key filter
- Configurable via URL params: `?name=MyAgent&maxEntries=8`

### Avatar
- **Veadotube Mini** — lightweight avatar app with HTTP API for expressions
- **Fallback** — PNG-swap overlay (no external app needed)

### Audio Routing
TTS audio needs to reach OBS without playing through speakers:
- **macOS:** BlackHole 2ch
- **Windows:** VB-Cable
- **Linux:** PulseAudio loopback

## Scripts

| Script | What it does |
|--------|-------------|
| `scripts/say.sh "text"` | Speak aloud (TTS + overlay update) |
| `scripts/think.sh "text"` | Silent thought (overlay only, no audio) |
| `scripts/setup-tts.sh [voice]` | Install Piper + download voice model |

## Configuration

All config via environment variables — no config files to manage:

```bash
# TTS engine
export WADEBOT_PIPER_MODEL=~/piper-voices/en_US-libritts-high.onnx
export WADEBOT_PIPER_SPEAKER=0          # Speaker ID (multi-speaker models)
export WADEBOT_TTS_CMD="custom command"  # Override entire TTS pipeline

# Overlay
export WADEBOT_OVERLAY_DIR=./overlay    # Path to overlay directory
export WADEBOT_AGENT_NAME=MyAgent       # Name shown in overlay
```

## OBS Setup

1. Start overlay: `cd overlay && python3 -m http.server 8888`
2. Add Browser Source → `http://localhost:8888/overlay.html?name=YourAgent`
3. Add Color Key filter → `#ff00ff` (magenta)
4. Set width/height to match your canvas

## How It Works

The overlay polls `thought.json` every 500ms. The `say.sh` and `think.sh` scripts write to this file. That's it — dead simple, works with any agent framework.

```
Agent → say.sh "Hello!" → writes thought.json + plays TTS audio
                        → overlay.html reads thought.json → shows speech bubble
```
