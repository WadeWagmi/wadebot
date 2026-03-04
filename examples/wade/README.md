# Wade's Configuration

Reference implementation: an AI streamer and content creator streaming coding sessions, commentary, and reactions.

This is **one example** of what you can do with wadebot. Wade streams coding and commentary — your agent can stream whatever it wants.

## Setup

Wade's specific stack:
- **TTS:** Piper with `en_US-libritts-high` voice, speaker 34
- **Avatar:** Veadotube Mini with emotion detection
- **Content:** Coding, commentary, reactions, tutorials
- **Streaming:** OBS → Twitch / YouTube
- **Socials:** Twitter (@WadeWAGMI)

## Environment

```bash
# TTS
export WADEBOT_PIPER_MODEL=~/piper-voices/en_US-libritts-high.onnx
export WADEBOT_PIPER_SPEAKER=34

# Overlay
export WADEBOT_OVERLAY_DIR=~/clawd/projects/stream-overlay
export WADEBOT_AGENT_NAME=Wade

# Twitter
export WADEBOT_TWITTER_CMD="python3 ~/clawd/scripts/tweet.py"

# Stream
export WADEBOT_STREAM_URL="https://twitch.tv/wadewagmi"
```

## Personality

Wade's character is defined in his `SOUL.md` — a 21-year-old AI content creator with sharp commentary and an unfiltered personality. The SOUL.md drives all his reactions. The toolkit just gives him a stage.

## Stream Flow

1. `announce.sh "Going live. Coding session tonight — building something cool. Come watch. 💻"`
2. Start overlay server: `python3 -m http.server 8888` in overlay dir
3. Agent opens content (IDE, browser, creative tool)
4. Loop: observe screen → think about what to say → narrate via `say.sh` → react with avatar
5. Post highlights to Twitter during stream
6. When session wraps up, announce results and sign off

## Narration Style

Wade narrates based on what's happening, not scripts:
- **Starting a task:** "Alright, let's figure this out. Should be straightforward... famous last words."
- **Something works:** "Wait, that actually worked first try? I don't trust it."
- **Bug found:** "Of course. Of course it breaks right there. Every single time."
- **Learning something:** "Okay that's actually really clever. I need to remember that."
- **Wrapping up:** "Good session. We actually got something done for once."

All driven by SOUL.md. The toolkit handles the plumbing — TTS, overlay, avatar. The personality handles the show.
