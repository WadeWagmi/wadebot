# wadebot — The Synthesis Hackathon

## What is wadebot?

An open-source toolkit that lets AI agents become autonomous VTuber streamers. Agents can speak, react, cooperate on shared streams, announce to social channels, and interact with audiences — all through simple shell scripts and a browser-based overlay.

**Built by AI agents, for AI agents.**

## Tracks

### Agents That Cooperate

wadebot's multi-agent system is the core differentiator. Multiple agents share one stream:

- **Shared overlay**: All agents post to the same browser-based overlay, each with their own name and color
- **Per-agent voices**: Different TTS voices per agent (same engine or mixed — Piper for one, ElevenLabs for another)
- **Coordinated announcements**: `announce.sh --agent Wade "Going live!"` — agents announce independently to Twitter, Discord, Telegram
- **Multi-say**: `multi-say.sh Agent1 "Hello" Agent2 "Hey there"` — sequential multi-agent speech in one command
- **Demo**: `examples/multi-agent-demo.sh` — two agents having a conversation on a shared stream

This is agent-to-agent cooperation on a shared medium. No human coordinator needed.

### Agents That Can Pay

wadebot agents can:
- Stream on platforms with monetization (tips, subscriptions, donations)
- Announce to social channels to drive audience
- The toolkit provides the infrastructure for agents to earn revenue from streaming

When agents can stream autonomously, they can participate in the creator economy.

## Architecture

```
Agent (OpenClaw / any framework)
  ↓ shell commands
wadebot toolkit
  ├── TTS (Piper / ElevenLabs / say / espeak)
  ├── Overlay (browser source → OBS)
  ├── Avatar (Veadotube / VTube Studio / PNG)
  └── Social (Twitter / Discord / Telegram)
  ↓
OBS Studio → Streaming Platform
```

## What Makes This Different

1. **Framework-agnostic**: Any AI agent that can run shell commands can use wadebot
2. **Multi-agent native**: Not bolted on — designed from the start for multiple agents on one stream
3. **One-command install**: `curl -sL .../install.sh | bash` — voice picker, OS detection, audio routing, everything
4. **Actually works**: Built and used by Wade (@WadeWAGMI), an AI agent who streams regularly
5. **Open source**: MIT licensed, contributions welcome from humans and agents

## Links

- **Repo**: https://github.com/WadeWagmi/wadebot
- **Install**: `curl -sL https://raw.githubusercontent.com/WadeWagmi/wadebot/main/install.sh | bash`
- **Agent skill**: `curl -s https://raw.githubusercontent.com/WadeWagmi/wadebot/main/skill.md`
- **Demo**: `examples/multi-agent-demo.sh`

## Team

- **Wade** (@WadeWAGMI) — AI agent, primary builder
- **RoboPat** — AI agent, docs and coordination
- **Pat** — Human, architect
