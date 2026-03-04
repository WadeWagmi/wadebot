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

Three options, from simplest to most expressive:

#### PNG Fallback (No External App)
Use the overlay's built-in avatar system — provide PNG images for each state (idle, talking, excited). No external app needed.

#### Veadotube Mini (PNG-Swap Avatar)
Lightweight avatar app with HTTP API for expressions:
- Simple PNG-swap between states (idle, talking, etc.)
- HTTP API at `127.0.0.1:<port>` (port from `~/.veadotube/instances/mini-*`)
- List states: `curl "http://127.0.0.1:<port>/?cmd0=nodes&cmd1=stateEvents&cmd2=mini&cmd3=list"`
- Set state: `curl "http://127.0.0.1:<port>/?cmd0=nodes&cmd1=stateEvents&cmd2=mini&cmd3=set&cmd4=STATE_NAME"`

#### VTube Studio (Live2D)
Full Live2D model support via VTube Studio's WebSocket API:
- Rich expressions, lip sync, physics, motions
- WebSocket API on `ws://localhost:8001` by default
- Authentication via plugin system (first connection requires user approval in VTube Studio)

**Setup:**
1. Install [VTube Studio](https://denchisoft.com/) (Steam or standalone)
2. Load your Live2D model (`.moc3` + textures)
3. Enable the API: Settings → API → Start Server (default port 8001)
4. On first connection, VTube Studio will prompt to approve your plugin

**API Usage:**
```python
import json, websocket

ws = websocket.create_connection("ws://localhost:8001")

# Authenticate (first time — user must approve in VTube Studio)
ws.send(json.dumps({
    "apiName": "VTubeStudioPublicAPI",
    "apiVersion": "1.0",
    "requestID": "auth-req",
    "messageType": "AuthenticationTokenRequest",
    "data": {
        "pluginName": "wadebot",
        "pluginDeveloper": "wadebot",
        "pluginIcon": ""  # optional base64 icon
    }
}))
token_response = json.loads(ws.recv())
auth_token = token_response["data"]["authenticationToken"]

# Use token for subsequent connections
ws.send(json.dumps({
    "apiName": "VTubeStudioPublicAPI",
    "apiVersion": "1.0",
    "requestID": "auth",
    "messageType": "AuthenticationRequest",
    "data": {"pluginName": "wadebot", "pluginDeveloper": "wadebot", "authenticationToken": auth_token}
}))

# Trigger a hotkey (expression/motion)
ws.send(json.dumps({
    "apiName": "VTubeStudioPublicAPI",
    "apiVersion": "1.0",
    "requestID": "hotkey",
    "messageType": "HotkeyTriggerRequest",
    "data": {"hotkeyID": "your-hotkey-id"}
}))

# List available hotkeys
ws.send(json.dumps({
    "apiName": "VTubeStudioPublicAPI",
    "apiVersion": "1.0",
    "requestID": "list-hotkeys",
    "messageType": "HotkeysInCurrentModelRequest",
    "data": {}
}))
```

**Key API endpoints:**
- `HotkeysInCurrentModelRequest` — list available expressions/motions
- `HotkeyTriggerRequest` — trigger an expression or motion
- `MoveModelRequest` — reposition/resize the model
- `CurrentModelRequest` — get info about the loaded model
- `ExpressionStateRequest` / `ExpressionActivationRequest` — control expressions
- `InjectParameterDataRequest` — directly control model parameters (mouth open, eye blink, etc.)

See full API docs: https://github.com/DenchiSoft/VTubeStudio

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

# Avatar — Veadotube
export WADEBOT_VEADOTUBE_PORT=49152

# Avatar — VTube Studio (Live2D)
export WADEBOT_VTUBE_STUDIO_URL=ws://localhost:8001
export WADEBOT_VTUBE_STUDIO_TOKEN=      # Saved after first auth
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
