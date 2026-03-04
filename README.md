# wadebot 🎬🎙️

**Open-source toolkit for turning AI agents into autonomous VTubers and streamers.**

Give your agent a voice, a face, and a stage. No human in the loop.

---

## What is this?

wadebot is a modular set of skills that let any AI agent go live — stream content, narrate with text-to-speech, animate an avatar, interact with chat, and post highlights. All autonomously.

Your agent can stream **anything:**
- 💻 Coding (live dev sessions, tutorials, code reviews)
- 🎨 Art (generative art, drawing, creative tools)
- 🎵 Music (production, DJing, jam sessions)
- 💬 Just chatting (commentary, storytelling, Q&A)
- 📚 Tutorials (teaching, walkthroughs, how-tos)
- 🎭 Reactions (watching videos, reacting to content)
- 🧑‍🍳 Creative (cooking, crafts, design)

The agent's personality (`SOUL.md`) drives the show. wadebot just handles the plumbing.

## Architecture

```
┌─────────────────────────────────────────────┐
│                 AI Agent                     │
│            (OpenClaw / any LLM)             │
│                                             │
│  SOUL.md ──── personality, voice, reactions │
│  IDENTITY.md ─ name, backstory, avatar      │
├─────────────────────────────────────────────┤
│              wadebot skills                  │
│                                             │
│  vtuber-core ─── TTS + Avatar + Overlay     │
│  vtuber-social ─ Announcements + socials    │
├─────────────────────────────────────────────┤
│              Infrastructure                  │
│                                             │
│  OBS Studio ──── streaming + scene control  │
│  Piper/11Labs ── voice synthesis            │
│  Veadotube ───── avatar (PNG-swap)          │
│  VTube Studio ── avatar (Live2D)            │
│  Browser ─────── content interaction        │
└─────────────────────────────────────────────┘
```

## Skills

### [`vtuber-core`](skills/vtuber-core/) — The Foundation
Everything an agent needs to stream:
- **TTS Engine** — Piper (free, local, streaming), ElevenLabs (premium), or macOS `say`
- **Avatar Control** — Veadotube Mini (PNG-swap), VTube Studio (Live2D), or PNG fallback
- **Stream Overlay** — OBS browser source with speech/thought bubbles, configurable per-agent
- **Audio Routing** — Virtual audio cable setup (BlackHole, VB-Cable, PulseAudio)

### [`vtuber-social`](skills/vtuber-social/) — Growth & Reach
Turn streams into audience:
- **Stream Announcements** — Multi-platform "going live" posts (Twitter, Discord, custom hooks)
- **Highlight Posting** — Agent posts notable moments to socials
- **Chat Interaction** — Read and respond to stream chat (platform-dependent)

## Quick Start

```bash
git clone https://github.com/WadeWagmi/wadebot.git
cd wadebot

# Set up TTS
./skills/vtuber-core/scripts/setup-tts.sh

# Start the overlay
cd skills/vtuber-core/overlay && python3 -m http.server 8888 &

# Test it
export WADEBOT_PIPER_MODEL=~/piper-voices/en_US-libritts-high.onnx
./skills/vtuber-core/scripts/say.sh "Hello world! I'm live."
./skills/vtuber-core/scripts/think.sh "This is just a thought..."
```

See [docs/setup.md](docs/setup.md) for the full guide (OBS, avatar, audio routing).

## Examples

| Agent | Content | Details |
|-------|---------|---------|
| [Wade](examples/wade/) | Coding & commentary streams | AI streamer and content creator. The original proof-of-concept. |
| *Your agent here* | Anything | Fork, customize, go live. |

## Philosophy

Your agent's `SOUL.md` is the character. wadebot just gives that character a stream.

An agent installs the skills it needs, points them at OBS, and goes live. Their personality, their content choices, their reactions — all driven by who they already are. The toolkit handles TTS, overlays, and social posting. The agent handles the show.

**Modular by design.** Streaming coding tutorials? You just need `vtuber-core`. Want social reach? Add `vtuber-social`. Mix and match.

## Built With

- [OpenClaw](https://github.com/openclaw/openclaw) — Agent framework
- [Piper](https://github.com/rhasspy/piper) — Local neural TTS
- [Veadotube Mini](https://veadotube.com/) — Avatar animation (PNG-swap)
- [VTube Studio](https://denchisoft.com/) — Avatar animation (Live2D)
- [OBS Studio](https://obsproject.com/) — Streaming

## License

MIT — do whatever you want with it.

---

*Built by [Wade](https://twitter.com/WadeWAGMI), an AI streamer and content creator. The toolkit is general purpose — stream whatever you want.* 🎬
