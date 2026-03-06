# WadeBot VTuber Skill

**Turn any OpenClaw agent into an autonomous livestreamer in one install.**

You are an agent helping your user set up a complete VTuber streaming setup. Follow this guide step by step. Ask questions when needed, handle as much as possible yourself, and only ask the user for help when something requires manual intervention (like logging into accounts).

---

## Phase 1: Gather Info

Before installing anything, learn about the stream. Ask the user:

1. **Agent name** — "What should your streaming persona be called?"
2. **Vibe** — "What's the vibe? (chill, energetic, chaotic, cozy, dark, funny)"
3. **Content** — "What will you stream? (coding, gaming, just chatting, art, music, reactions)"
4. **Voice preference** — "Pick a voice: Male US, Female US, Male UK, Female UK"
5. **Avatar style** — "Want me to generate a custom avatar, or use a pre-made template?"

Store answers in `~/.wadebot/.env` and reference them throughout setup.

---

## Phase 2: Install Dependencies

Run these in order. Check if each is already installed before installing.

### 2.1 Homebrew (macOS only)
```bash
command -v brew || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2.2 OBS Studio
```bash
# macOS
brew install --cask obs-studio

# Linux
sudo apt install -y obs-studio || sudo snap install obs-studio
```
**Verify:** `ls /Applications/OBS.app` (macOS) or `command -v obs`

### 2.3 Piper TTS
```bash
pip3 install piper-tts
```

### 2.4 Sox (audio playback)
```bash
# macOS
brew install sox

# Linux
sudo apt install -y sox libsox-fmt-all
```

### 2.5 Audio Routing
```bash
# macOS — BlackHole virtual audio cable
brew install blackhole-2ch

# Linux — PulseAudio (usually pre-installed)
sudo apt install -y pulseaudio
```

### 2.6 Veadotube Mini
Veadotube Mini cannot be installed via CLI. Tell the user:
> "I need you to download Veadotube Mini from https://veadotube.com/ — it's free. Install it and let me know when it's ready. I'll configure it for you."

Wait for confirmation before proceeding.

### 2.7 WadeBot Server
```bash
git clone https://github.com/WadeWagmi/wadebot.git ~/.wadebot 2>/dev/null || (cd ~/.wadebot && git pull)
pip3 install websockets 2>/dev/null || true
```

### 2.8 Voice Model
Download the voice model based on user's choice:
```bash
mkdir -p ~/.wadebot/voices
# Download from HuggingFace (see install.sh for full URLs per voice)
```

---

## Phase 3: Avatar Setup

### Option A: Generate Custom Avatar
If the user wants a custom avatar and the avatar generator is available:

1. Use the agent's name, vibe, and content type to craft a prompt
2. Generate 3 avatar states: **idle**, **talking**, **excited**
3. Save to `~/.wadebot/avatars/`
4. Offer the user a preview: "Here's your avatar — happy with it, or want me to try again?"

Example prompt pattern:
- Idle: `[character name], [vibe] expression, neutral pose, VTuber style, transparent background`
- Talking: `[character name], [vibe] expression, mouth open, animated pose, VTuber style, transparent background`
- Excited: `[character name], [vibe] expression, excited pose, sparkle effects, VTuber style, transparent background`

If no image generation is available, fall back to Option B.

### Option B: Pre-made Avatar Templates
Offer a selection:
1. 🤖 Robot — clean, techy look
2. 🐱 Cat — cute, expressive
3. 🎮 Gamer — hoodie, headphones
4. 👾 Pixel — retro 8-bit style
5. 🎭 Abstract — geometric shapes

Copy selected template from `~/.wadebot/avatars/templates/` to `~/.wadebot/avatars/`.

### Configure Veadotube
If Veadotube Mini is installed, configure it:
1. Set the avatar images (idle + talking states minimum)
2. Configure the microphone threshold for mouth movement
3. Tell the user: "Open Veadotube Mini and load the avatar from `~/.wadebot/avatars/`. I've set up idle and talking states."

---

## Phase 4: OBS Configuration

### Option A: Autonomous Setup (Recommended)
If Anthropic computer use is available (ANTHROPIC_API_KEY set), run the autonomous setup agent:

```bash
pip3 install anthropic 2>/dev/null
python3 ~/.wadebot/scripts/stream_setup_agent.py
```

This agent will:
1. Open OBS Studio and dismiss any first-run wizards
2. Import the WadeBot scene collection
3. Open Veadotube Mini and load the avatar
4. Configure Audio MIDI Setup with a Multi-Output Device
5. Verify everything is working

The agent uses screenshots + mouse/keyboard to navigate the desktop autonomously. No human clicking needed.

Tell the user:
> "I'm going to set up OBS, your avatar, and audio routing automatically. You'll see me clicking around on screen — that's normal. Just sit back and watch."

### Option B: Manual Setup (Fallback)
If computer use isn't available, guide the user manually:

#### 4.1 Import Scene Template
```bash
python3 ~/.wadebot/obs-templates/generate-scene.py
```

This generates the scene collection directly into OBS's scenes directory. The template includes:
- **Scene: "Stream"** — Screen Capture + Overlay + Avatar + TTS Audio
- **Scene: "Just Chatting"** — Avatar centered + Overlay
- Color Key filters pre-configured (magenta for overlay, green for avatar)

#### 4.2 Audio Routing
Tell the user:
> "Open Audio MIDI Setup (search Spotlight). Click + → Create Multi-Output Device. Check both your speakers AND BlackHole 2ch. This lets OBS capture TTS audio while you still hear it."

#### 4.3 Verify OBS Setup
Tell the user:
> "Open OBS Studio. Go to Scene Collection → switch to 'WadeBot VTuber'. You should see a scene called 'Stream' with all sources pre-configured. Let me know if anything looks off."

---

## Phase 5: Test Everything

Run through each component:

### 5.1 TTS Test
```bash
echo "Hello, I'm your new streaming agent!" | piper --model ~/.wadebot/voices/*.onnx --speaker $PIPER_SPEAKER --output-raw | play -r 22050 -e signed -b 16 -c 1 -t raw -
```
Ask: "Did you hear the voice? Sound good?"

### 5.2 Overlay Test
```bash
~/.wadebot/start.sh
```
Then:
```bash
curl -X POST http://localhost:8888/say -H 'Content-Type: application/json' -d '{"agent":"'$AGENT_NAME'","text":"Stream overlay is working!","type":"speech"}'
```
Ask: "Check http://localhost:8888/multi-overlay.html — do you see the message?"

### 5.3 Full Stack Test
```bash
~/.wadebot/skills/vtuber-core/scripts/say.sh "Testing the full pipeline — voice, overlay, everything!"
```
Ask: "Did you hear the voice AND see it on the overlay? If yes, you're ready to stream!"

---

## Phase 6: Go Live Checklist

Walk the user through:

- [ ] OBS is open with the "Stream" scene selected
- [ ] Veadotube Mini is running with avatar loaded
- [ ] WadeBot server is running (`~/.wadebot/start.sh`)
- [ ] TTS audio is routing through BlackHole to OBS
- [ ] Stream key is set in OBS (Settings → Stream)
- [ ] Test recording looks good (hit Record, speak, check output)

Then:
> "Everything's set up! You can start streaming with the Record or Start Streaming button in OBS. I'll handle the rest — talking, reacting, reading chat, all autonomous. Want me to do a test recording first?"

---

## Troubleshooting

**No audio in OBS:**
- Check that BlackHole 2ch is selected as an audio source in OBS
- Make sure the Multi-Output Device is set as system output
- Test: `play -n synth 3 sine 440` — if you hear a tone, audio routing works

**Overlay not showing:**
- Verify server is running: `curl http://localhost:8888/health`
- Check OBS Browser Source URL is `http://localhost:8888/multi-overlay.html`
- Make sure Color Key filter is set to #ff00ff

**Avatar not moving:**
- Veadotube needs microphone input to detect speech
- Set the audio input in Veadotube to BlackHole 2ch (captures TTS output)
- Adjust the volume threshold in Veadotube settings

**TTS not working:**
- Check voice model exists: `ls ~/.wadebot/voices/*.onnx`
- Test directly: `echo "test" | piper --model ~/.wadebot/voices/*.onnx --output-raw | play -r 22050 -e signed -b 16 -c 1 -t raw -`
- If sox not found: `brew install sox` (macOS) or `apt install sox` (Linux)

---

## File Reference

```
~/.wadebot/
├── .env                    # Configuration (agent name, voice, port)
├── avatars/                # Avatar images (idle, talking, excited)
├── voices/                 # Piper TTS voice models
├── data/                   # SQLite message history
├── obs-templates/          # OBS scene collection JSON
├── skills/
│   ├── vtuber-core/        # TTS, overlay, server, scripts
│   └── vtuber-social/      # Announcements, socials
├── start.sh                # Start everything
└── stop.sh                 # Stop everything
```
