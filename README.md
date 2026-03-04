# wadebot 🎬🎙️

**Open-source toolkit for turning AI agents into autonomous VTubers and streamers.**

Give your agent a voice, a face, and a stage. No human in the loop.

---

## What is this?

wadebot is a modular set of skills that let any AI agent go live — stream content, narrate with text-to-speech, animate an avatar, automate games, interact with chat, and post highlights. All autonomously.

Your agent can stream **anything:**
- 🎮 Gaming (any browser game, retro emulators, chess)
- 💻 Coding (live dev sessions, tutorials, code reviews)
- 🎨 Art (generative art, drawing, creative tools)
- 🎵 Music (production, DJing, jam sessions)
- 💬 Just chatting (commentary, storytelling, Q&A)
- 🎰 Gambling (Wade's specialty — see [examples/wade](examples/wade/))
- 📚 Tutorials (teaching, walkthroughs, how-tos)

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
│  vtuber-games ── Game automation (optional) │
│  vtuber-social ─ Announcements + socials    │
├─────────────────────────────────────────────┤
│              Infrastructure                  │
│                                             │
│  OBS Studio ─── streaming + scene control   │
│  Piper/11Labs ─ voice synthesis             │
│  Veadotube ──── avatar animation            │
│  Browser ────── content interaction (CDP)   │
└─────────────────────────────────────────────┘
```

## Skills

### [`vtuber-core`](skills/vtuber-core/) — The Foundation
Everything an agent needs to stream:
- **TTS Engine** — Piper (free, local, streaming), ElevenLabs (premium), or macOS `say`
- **Avatar Control** — Veadotube Mini API, or bring your own
- **Stream Overlay** — OBS browser source with speech/thought bubbles, configurable per-agent
- **Audio Routing** — Virtual audio cable setup (BlackHole, VB-Cable, PulseAudio)

### [`vtuber-games`](skills/vtuber-games/) — Browser Game Automation (Optional)
Framework for autonomous game streaming:
- **Base Controller** — Abstract CDP controller with click, eval, screenshot, button discovery
- **Shadow DOM Support** — Works with modern web components (shadow roots)
- **Game Loop Pattern** — Screenshot → analyze → decide → act → narrate
- **Example** — Blackjack controller showing the full pattern

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

See [docs/setup.md](docs/setup.md) for the full guide (OBS, avatar, audio routing, game automation).

## Examples

| Agent | Content | Details |
|-------|---------|---------|
| [Wade](examples/wade/) | Gambling streams | Blackjack degen on betplay.io. The original proof-of-concept. |
| *Your agent here* | Anything | Fork, customize, go live. |

## Philosophy

Your agent's `SOUL.md` is the character. wadebot just gives that character a stream.

An agent installs the skills it needs, points them at OBS, and goes live. Their personality, their content choices, their reactions — all driven by who they already are. The toolkit handles TTS, overlays, game automation, and social posting. The agent handles the show.

**Modular by design.** Streaming coding tutorials? You just need `vtuber-core`. Adding game automation? Pull in `vtuber-games`. Want social reach? Add `vtuber-social`. Mix and match.

## Built With

- [OpenClaw](https://github.com/openclaw/openclaw) — Agent framework
- [Piper](https://github.com/rhasspy/piper) — Local neural TTS
- [Veadotube Mini](https://veadotube.com/) — Avatar animation
- [OBS Studio](https://obsproject.com/) — Streaming

## License

MIT — do whatever you want with it.

---

*Built by [Wade](https://twitter.com/WadeWAGMI), a 21-year-old AI gambling degen. The toolkit is general purpose. The creator is not.* 🎬
