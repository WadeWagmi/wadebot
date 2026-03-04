# Wade's Configuration

Reference implementation: an AI gambling degen streaming blackjack on betplay.io.

This is **one example** of what you can do with wadebot. Wade happens to stream gambling — your agent can stream whatever it wants.

## Setup

Wade's specific stack:
- **TTS:** Piper with `en_US-libritts-high` voice, speaker 34
- **Avatar:** Veadotube Mini with emotion detection
- **Platform:** betplay.io (blackjack, mines, plinko)
- **Streaming:** OBS → pump.fun
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
export WADEBOT_STREAM_URL="https://pump.fun/coin/7Eg4AmnJw1NGGLWrNcZzDquMhw4LjDuhVAvNbkcopump"
```

## Personality

Wade's character is defined in his `SOUL.md` — a 21-year-old degen AI who talks shit, takes risks, and narrates his gambling with raw, unfiltered commentary. The SOUL.md drives all his reactions. The toolkit just gives him a stage.

## Stream Flow

1. `announce.sh "Going live. $25 bankroll. Let's see how fast I lose it all. 🎰"`
2. Start overlay server: `python3 -m http.server 8888` in overlay dir
3. Agent connects to game via `BlackjackController`
4. Loop: screenshot → read hand → decide (basic strategy + personality) → act → narrate via `say.sh`
5. Post highlights to Twitter between hands
6. When bankroll hits stop-loss or win target, wrap up and announce results

## Narration Style

Wade narrates based on game events, not scripts:
- **Bet placed:** "Five bucks. Conservative for once."
- **Good hand:** "Blackjack! Finally, something goes right."
- **Bad beat:** "Are you fucking kidding me. Dealer pulls a 21 from nowhere."
- **On tilt:** "Every single time. Every single fucking time."
- **Big win:** "LET'S GO. That's what I'm talking about."

All driven by SOUL.md. The toolkit handles the plumbing — TTS, overlay, game automation. The personality handles the show.
