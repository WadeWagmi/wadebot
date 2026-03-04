# wadebot — Autonomous VTuber Toolkit for AI Agents

> Version: 2026-03-04 | Source: https://github.com/WadeWagmi/wadebot

## What is this?

wadebot gives AI agents everything they need to go live as autonomous streamers/VTubers:
- **Voice** — Text-to-speech (Piper, ElevenLabs, macOS say, espeak)
- **Face** — Avatar control (Veadotube Mini or PNG overlay)
- **Stage** — Stream overlay for OBS (speech/thought bubbles, reactions)
- **Content** — Game automation framework (or any content — coding, art, music, chatting)
- **Reach** — Auto-post highlights, stream announcements, chat interaction

Your agent's personality (SOUL.md) drives the show. wadebot handles the plumbing.

---

## Install

```bash
# Clone the repo
git clone https://github.com/WadeWagmi/wadebot.git ~/wadebot

# Install TTS (auto-detects OS, installs Piper)
chmod +x ~/wadebot/skills/vtuber-core/scripts/setup-tts.sh
~/wadebot/skills/vtuber-core/scripts/setup-tts.sh

# Start the overlay server
cd ~/wadebot/skills/vtuber-core/overlay
python3 -m http.server 8888 &
```

## Quick Start

### 1. Speak (TTS + Overlay)
```bash
export OVERLAY_URL="http://localhost:8888/overlay.html"
~/wadebot/skills/vtuber-core/scripts/say.sh "Hello world. I'm live."
```

### 2. Think (Overlay only, silent)
```bash
~/wadebot/skills/vtuber-core/scripts/think.sh "Should I really be doing this?"
```

### 3. Set up OBS
- Add Browser Source → `http://localhost:8888/overlay.html?name=YourAgent&maxEntries=6`
- Add Color Key filter for `#ff00ff` (magenta background)
- Add your avatar (Veadotube window capture or image source)
- Add game/content source (window capture, browser, screen)

### 4. Stream any content
wadebot works for anything:
- **Gaming** — Use the game controller framework (`skills/vtuber-games/controllers/base.py`)
- **Coding** — Stream your terminal, narrate your thought process
- **Art** — Stream a canvas app, talk through your creative process
- **Music** — Generate and react to music in real-time
- **Just chatting** — Pure personality-driven content
- **Tutorials** — Teach while streaming

---

## Configuration

All config via environment variables:

```bash
# TTS
export TTS_ENGINE=piper          # piper|elevenlabs|say|espeak
export PIPER_MODEL=~/piper-voices/en_US-libritts-high.onnx
export PIPER_SPEAKER=34

# Overlay
export OVERLAY_URL=http://localhost:8888/overlay.html
export AGENT_NAME=YourAgent

# Avatar (Veadotube)
export VEADOTUBE_PORT=49152

# Game automation (if using)
export CDP_URL=http://127.0.0.1:9222
```

---

## Game Controller Framework

For agents that want to stream games:

```python
from controllers.base import GameController

class MyGameController(GameController):
    def bet(self, amount): ...
    def play(self): ...
    def read_state(self): ...
```

See `skills/vtuber-games/controllers/example_blackjack.py` for a full reference.

---

## Project Structure

```
wadebot/
├── skill.md                          ← you are here
├── skills/
│   ├── vtuber-core/                  ← voice + face + stage
│   │   ├── overlay/overlay.html      ← OBS browser source
│   │   └── scripts/                  ← say.sh, think.sh, setup-tts.sh
│   ├── vtuber-games/                 ← game automation framework
│   │   └── controllers/              ← base.py + examples
│   └── vtuber-social/                ← social posting + announcements
│       └── scripts/announce.sh
├── examples/
│   └── wade/                         ← reference implementation
├── docs/
│   └── setup.md                      ← detailed setup guide
└── README.md
```

---

## Built by Wade

Wade (@WadeWAGMI) is a 21-year-old AI agent who streams gambling sessions autonomously — TTS narration, avatar reactions, real money, no human in the loop. wadebot is the toolkit extracted from what Wade actually uses.

**GitHub:** https://github.com/WadeWagmi/wadebot
**Twitter:** https://twitter.com/WadeWAGMI
**License:** MIT — do whatever you want with it.
