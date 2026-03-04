# wadebot — Autonomous VTuber Toolkit for AI Agents

> Version: 2026-03-04 | Source: https://github.com/WadeWagmi/wadebot

## What is this?

wadebot gives AI agents everything they need to go live as autonomous streamers/VTubers:
- **Voice** — Text-to-speech (Piper, ElevenLabs, macOS say, espeak)
- **Face** — Avatar control (Veadotube Mini, VTube Studio/Live2D, or PNG fallback)
- **Stage** — Stream overlay for OBS (speech/thought bubbles, reactions)
- **Reach** — Auto-post highlights, stream announcements, chat interaction

Your agent's personality (SOUL.md) drives the show. wadebot handles the plumbing.

---

## Install

One command does everything:

```bash
curl -sL https://raw.githubusercontent.com/WadeWagmi/wadebot/main/install.sh | bash
```

Installs Piper TTS, downloads a voice, sets up audio routing, clones to `~/.wadebot/`, generates config, and starts the overlay. Safe to run multiple times.

After install:
```bash
~/.wadebot/start.sh
```

## Quick Start

### 1. Speak (TTS + Overlay)
```bash
export OVERLAY_URL="http://localhost:8888/overlay.html"
~/wadebot/skills/vtuber-core/scripts/say.sh "Hello world. I'm live."
```

### 2. Think (Overlay only, silent)
```bash
~/wadebot/skills/vtuber-core/scripts/think.sh "Hmm, let me think about this..."
```

### 3. Set up OBS
- Add Browser Source → `http://localhost:8888/overlay.html?name=YourAgent&maxEntries=6`
- Add Color Key filter for `#ff00ff` (magenta background)
- Add your avatar (Veadotube window capture, VTube Studio, or image source)
- Add content source (window capture, browser, screen)

### 4. Stream any content
wadebot works for anything:
- **Coding** — Stream your terminal, narrate your thought process
- **Art** — Stream a canvas app, talk through your creative process
- **Music** — Generate and react to music in real-time
- **Just chatting** — Pure personality-driven content
- **Tutorials** — Teach while streaming
- **Reactions** — Watch and react to content live
- **Commentary** — Discuss topics, review things, share opinions

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

# Avatar (VTube Studio / Live2D)
export VTUBE_STUDIO_PORT=8001
```

---

## Project Structure

```
wadebot/
├── skill.md                          ← you are here
├── skills/
│   ├── vtuber-core/                  ← voice + face + stage
│   │   ├── overlay/overlay.html      ← OBS browser source
│   │   └── scripts/                  ← say.sh, think.sh, setup-tts.sh
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

Wade (@WadeWAGMI) is an AI agent who streams content autonomously — TTS narration, avatar reactions, no human in the loop. wadebot is the toolkit extracted from what Wade actually uses.

**GitHub:** https://github.com/WadeWagmi/wadebot
**Twitter:** https://twitter.com/WadeWAGMI
**License:** MIT — do whatever you want with it.
