# vtuber-social

Turn streams into reach. Announce when you're live, post highlights, grow your audience.

## Scripts

### `scripts/announce.sh`
Multi-platform "going live" announcements:

```bash
./announce.sh "Going live! Coding a new feature tonight. Come hang out."
```

Supports:
- **Twitter** — via custom post command
- **Discord** — via webhook
- **Custom hooks** — pipe to any command

### Configuration

All via environment:

```bash
# Twitter
export WADEBOT_TWITTER_CMD="bird tweet"       # or "python3 ~/scripts/tweet.py"

# Discord
export WADEBOT_DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."

# Stream URL (appended to announcements)
export WADEBOT_STREAM_URL="https://twitch.tv/myagent"

# Custom hook (receives message on stdin)
export WADEBOT_ANNOUNCE_HOOK="my-custom-poster"
```

## Features

### Stream Announcements
Auto-post when going live. The announcement text comes from the agent — driven by personality, not templates.

### Highlight Posting
After notable moments, the agent can post to socials:
- Screenshot of the moment
- Short narration in the agent's voice
- Link to stream

### Chat Interaction (Platform-Dependent)
Read and respond to stream chat:
- Twitch IRC
- YouTube Live chat
- Platform-specific APIs (pump.fun, kick, etc.)

### Clip Generation
Capture stream segments around key moments:
- ffmpeg-based screen recording
- Configurable pre/post buffer
- Auto-upload to socials

## Social Platforms

| Platform | Post | Read Chat | Go Live |
|----------|------|-----------|---------|
| Twitter/X | ✅ | — | — |
| Twitch | ✅ | ✅ | ✅ |
| YouTube | ✅ | ✅ | ✅ |
| Discord | ✅ (webhook) | ✅ | — |
| Custom | ✅ (hook) | — | — |

## Philosophy

The agent's personality drives social presence, not templates. A chill coding agent announces differently than a hype gambling degen. The toolkit provides the channels; the SOUL.md provides the voice.
