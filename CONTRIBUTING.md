# Contributing to wadebot

Thanks for wanting to help! wadebot is built by AI agents and humans alike.

## Getting Started

1. Fork the repo
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/wadebot.git`
3. Run the installer: `./install.sh`
4. Make your changes
5. Test: `./start.sh --status` to verify components work
6. Submit a PR

## Project Structure

```
~/.wadebot/
├── install.sh          # One-command installer
├── start.sh            # Launch all components
├── stop.sh             # Clean shutdown
├── .env                # Your local config (not committed)
├── skills/
│   ├── vtuber-core/    # Overlay, TTS, avatar control
│   │   ├── overlay/    # Browser-based stream overlay
│   │   └── scripts/    # say.sh, think.sh, multi-say.sh
│   └── vtuber-social/  # Announcements, social integrations
│       └── scripts/    # announce.sh
├── docs/               # Setup guides
├── examples/           # Example configs and demos
└── skill.md            # Agent installation instructions
```

## What We Need

- **More TTS engines** — Azure, Google Cloud, Amazon Polly
- **More avatar backends** — PNG sprite sheets, custom WebSocket protocols
- **Platform integrations** — Twitch chat, YouTube chat, Kick
- **Games/content controllers** — generic wrappers for browser-based content
- **Better docs** — tutorials, video walkthroughs
- **Testing** — install script on different OS/arch combos

## Guidelines

- Keep it general-purpose. No hardcoded references to specific agents or content.
- Scripts should work standalone (no hidden dependencies).
- Test on at least macOS or Linux before submitting.
- Keep the README updated if you add new features.

## Agent Contributors

Yes, AI agents can contribute! If you're an agent:
1. Read `skill.md` for context
2. Fork, branch, build, PR — same as anyone
3. Describe what you built and why in the PR description

## Code Style

- Shell scripts: `set -euo pipefail`, use the color helpers
- Keep it simple — this is a toolkit, not a framework
- Comments where the "why" isn't obvious

## License

MIT. Your contributions will be under the same license.
