# vtuber-social

Turn streams into reach. Auto-post highlights, announce streams, interact with chat.

## Features

### Stream Announcements
Auto-post when going live:
```
"Going live on pump.fun. $25 bankroll. Blackjack. 
Let's see how fast I can lose it all. 🎰"
```

### Highlight Posting
After notable moments (big wins, brutal losses, milestones), auto-post to Twitter/socials:
- Screenshot of the moment
- Short narration in the agent's voice
- Link to stream

### Chat Interaction
Read and respond to stream chat (platform-dependent):
- pump.fun token page chat
- Twitch IRC
- YouTube Live chat

### Clip Generation
Capture stream segments around key moments:
- ffmpeg-based screen recording
- Configurable pre/post buffer
- Auto-upload to socials

## Config

```json
{
  "twitter": {
    "enabled": true,
    "announceGoLive": true,
    "postHighlights": true,
    "maxPostsPerStream": 5
  },
  "chat": {
    "enabled": true,
    "platform": "pumpfun",
    "responseRate": 0.3
  },
  "clips": {
    "enabled": false,
    "bufferSeconds": 10,
    "maxClipsPerStream": 3
  }
}
```

## Social Platforms

| Platform | Post | Read Chat | Go Live |
|----------|------|-----------|---------|
| Twitter/X | ✅ | N/A | N/A |
| pump.fun | ✅ (chat) | ✅ | ✅ |
| Twitch | ✅ | ✅ | ✅ |
| YouTube | ✅ | ✅ | ✅ |
| Moltbook | ✅ | N/A | N/A |
