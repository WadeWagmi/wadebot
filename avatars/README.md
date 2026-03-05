# Avatar Templates

During install, the agent can generate a custom avatar or use a pre-made template.

## Custom Generation
The agent uses image generation to create avatar states based on the user's personality:
- `idle.png` — neutral expression, default pose
- `talking.png` — mouth open, animated pose
- `excited.png` — energetic pose (optional, for reactions)

## Pre-made Templates
Place template sets in `templates/<name>/` with at least `idle.png` and `talking.png`.

## Veadotube Mini Setup
1. Open Veadotube Mini
2. Click + to add a new avatar
3. Set `idle.png` as the default state
4. Set `talking.png` as the speaking state
5. Set audio input to BlackHole 2ch (captures TTS output)
6. Adjust volume threshold until mouth moves with TTS
