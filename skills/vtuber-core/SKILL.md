# vtuber-core

Give your agent a voice, a face, and a stream.

## Components

### TTS (Text-to-Speech)
- **Piper** (recommended) — free, local, streaming, no API key
- **ElevenLabs** — premium voices, requires API key

Setup: `scripts/setup-tts.sh` detects your OS and installs Piper with a default voice.

### Avatar
- **Veadotube Mini** — lightweight avatar app with HTTP API
- **Fallback** — PNG-swap overlay (no external app needed)

Control states (expressions) via the Veadotube API:
```bash
# List available states
curl "http://127.0.0.1:${PORT}/?cmd0=nodes&cmd1=stateEvents&cmd2=mini&cmd3=list"

# Set state
curl "http://127.0.0.1:${PORT}/?cmd0=nodes&cmd1=stateEvents&cmd2=mini&cmd3=set&cmd4=STATE_NAME"
```

### Stream Overlay
HTML/JS overlay for OBS browser source:
- Speech bubbles (what the agent says aloud)
- Thought bubbles (internal monologue, silent)
- Reaction effects
- Auto-fade old messages
- Chroma key background (#ff00ff)

### OBS Control
Via obs-websocket (v5):
- Start/stop streaming
- Switch scenes
- Toggle sources
- Set stream key

### Audio Routing
Virtual audio cable setup for routing TTS to OBS:
- **macOS:** BlackHole 2ch
- **Windows:** VB-Cable
- **Linux:** PulseAudio loopback

## Scripts

| Script | Description |
|--------|-------------|
| `say.sh "text"` | TTS + overlay (speech) |
| `think.sh "text"` | Overlay only (thought, silent) |
| `setup-tts.sh` | Install and configure TTS engine |
| `setup-audio.sh` | Configure virtual audio routing |

## Config

```json
{
  "tts": {
    "engine": "piper",
    "voice": "en_US-libritts-high",
    "speaker": 34
  },
  "avatar": {
    "engine": "veadotube",
    "port": 49152
  },
  "overlay": {
    "port": 8888,
    "maxEntries": 6,
    "chromaKey": "#ff00ff"
  },
  "obs": {
    "host": "localhost",
    "port": 4455,
    "password": ""
  }
}
```
