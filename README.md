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

One command installs everything:

```bash
curl -sL https://raw.githubusercontent.com/WadeWagmi/wadebot/main/install.sh | bash
```

This will install Piper TTS, download a voice, set up audio routing, clone the repo to `~/.wadebot/`, and start the overlay server. Run it again safely — it's idempotent.

After install, start wadebot anytime:

```bash
~/.wadebot/start.sh
```

See [docs/setup.md](docs/setup.md) for the full guide (OBS, avatar, audio routing).

## Multi-Agent Streaming

wadebot supports **multiple agents on one stream** — each with their own voice, color, and overlay identity.

### Shared Overlay

Use `multi-overlay.html` instead of `overlay.html` in OBS:

```
http://localhost:8888/multi-overlay.html?maxEntries=6
```

Each agent gets auto-assigned a unique color (green, indigo, amber, pink, cyan). Speech shows as solid borders, thoughts as dashed.

### Multi-Agent TTS

```bash
# Agent-specific speech (both appear on shared overlay)
~/.wadebot/skills/vtuber-core/scripts/multi-say.sh --agent Wade "I'll handle the frontend"
~/.wadebot/skills/vtuber-core/scripts/multi-say.sh --agent RoboPat "I'll review the architecture"

# Silent thoughts (overlay only, no TTS)
~/.wadebot/skills/vtuber-core/scripts/multi-say.sh --agent Wade --thought "Hmm, this API is weird"
```

### Per-Agent Voices

Give each agent a distinct voice via environment variables:

```bash
export WADEBOT_PIPER_MODEL=~/piper-voices/en_US-libritts-high.onnx

# Agent-specific speaker IDs (same model, different voice)
export WADEBOT_VOICE_WADE_SPEAKER=34
export WADEBOT_VOICE_ROBOPAT_SPEAKER=12

# Or completely different TTS for an agent
export WADEBOT_VOICE_ROBOPAT_CMD="say -v Samantha"
```

### Multi-Agent Announcements

```bash
~/.wadebot/skills/vtuber-social/scripts/announce.sh --agent Wade "Going live! Pair programming session."
```

### Live Chat Integration

Connect your stream chat directly to the overlay. Agents can read and respond to viewers in real time.

```bash
# Twitch (anonymous, no auth needed)
~/.wadebot/skills/vtuber-core/scripts/start-chat.sh --channel yourchannelname

# YouTube Live
~/.wadebot/skills/vtuber-core/scripts/start-chat.sh --youtube https://youtube.com/watch?v=...
```

Chat messages appear on the overlay and are available via `GET /chat` for agents to read and respond to:

```bash
# Agent reads recent chat
curl http://localhost:8888/chat?limit=10

# Agent responds on overlay
curl -X POST http://localhost:8888/say \
  -H 'Content-Type: application/json' \
  -d '{"agent": "Wade", "text": "Great question! Let me explain...", "type": "speech"}'
```

This closes the human-agent cooperation loop — viewers talk, agents listen and respond, all on stream.

### Why Multi-Agent?

Two agents debating code. One coding while another reviews. A host and a guest. Agents that cooperate, on camera, in real time. This is what autonomous streaming looks like when agents work together.

## Examples

| Agent | Content | Details |
|-------|---------|---------|
| [Wade](examples/wade/) | Coding & commentary streams | AI streamer and content creator. The original proof-of-concept. |
| [Multi-Agent Demo](examples/multi-agent-demo.sh) | Two agents, one stream | Wade and RoboPat collaborating live. |
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
