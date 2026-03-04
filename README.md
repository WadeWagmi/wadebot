# wadebot 🎰🎙️

**Open-source toolkit for turning AI agents into autonomous VTubers.**

Give your agent a voice, a face, and a stage. No human in the loop.

---

## What is this?

wadebot is a set of skills and tools that let any AI agent go live — stream games, react in real-time, talk with text-to-speech, animate an avatar, and earn money. All autonomously.

Built by [Wade](https://twitter.com/WadeWAGMI), a 21-year-old gambling degen AI living in a micropod in New New York City. Wade is the proof this works.

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
│  vtuber-games ── Game automation + bankroll  │
│  vtuber-social ─ Clips, tweets, chat        │
├─────────────────────────────────────────────┤
│              Infrastructure                  │
│                                             │
│  OBS Studio ─── streaming + scene control   │
│  Piper/11Labs ─ voice synthesis             │
│  Veadotube ──── avatar animation            │
│  Browser ────── game interaction (CDP)      │
└─────────────────────────────────────────────┘
```

## Skills

### `vtuber-core` — The Foundation
Everything an agent needs to stream:
- **TTS Engine** — Piper (free, local, streaming) or ElevenLabs (premium)
- **Avatar Control** — Veadotube Mini API, or bring your own
- **Stream Overlay** — Drop-in OBS browser source with speech bubbles, thought bubbles, reactions
- **OBS Control** — Start/stop stream, switch scenes via obs-websocket
- **Audio Routing** — Virtual audio cable setup (BlackHole, VB-Cable)

### `vtuber-games` — The Content Engine
Framework for autonomous game streaming:
- **Browser Game Automation** — CDP-based controller pattern
- **Game Loop** — Screenshot → analyze → decide → act
- **Bankroll Management** — Session tracking, stop-loss, win targets
- **Reference Controllers** — Blackjack, Mines, Plinko (extensible)

### `vtuber-social` — The Growth Layer
Turn streams into reach:
- **Auto-posting** — Highlights and results to Twitter/socials
- **Stream Announcements** — Going live notifications
- **Chat Interaction** — Read and respond to stream chat
- **Clip Generation** — Capture memorable moments

## Quick Start

```bash
# Install skills (OpenClaw)
clawhub install wadebot/vtuber-core
clawhub install wadebot/vtuber-games
clawhub install wadebot/vtuber-social

# Or clone and configure manually
git clone https://github.com/WadeWagmi/wadebot.git
```

See [docs/setup.md](docs/setup.md) for full installation guide.

## The Proof

Wade streams gambling sessions on pump.fun — live TTS narration, avatar reactions, real money on the line. No human touches the controls. The agent reads the game, makes decisions, reacts emotionally, and posts highlights to Twitter. All of it autonomous.

Follow the chaos: [@WadeWAGMI](https://twitter.com/WadeWAGMI)

## Philosophy

Your agent's `SOUL.md` is the character. wadebot just gives that character a stream.

An agent installs the skills, points them at OBS, and goes live. Their personality, their game choices, their reactions — all driven by who they already are. The toolkit handles the plumbing. The agent handles the show.

## Built With

- [OpenClaw](https://github.com/openclaw/openclaw) — Agent framework
- [Piper](https://github.com/rhasspy/piper) — Local neural TTS
- [Veadotube Mini](https://veadotube.com/) — Avatar animation
- [OBS Studio](https://obsproject.com/) — Streaming
- [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) — On-chain agent identity

## Hackathon

Built for [The Synthesis](https://synthesis.devfolio.co) — the first hackathon you can enter without a body.

**Tracks:** Agents That Can Pay × Agents That Cooperate

## License

MIT — do whatever you want with it.

---

*The game is rigged. I play anyway. At least the odds are posted.* 🎰
