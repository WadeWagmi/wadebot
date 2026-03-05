#!/bin/bash
# Multi-Agent Demo — Two agents collaborating on one stream
# 
# Prerequisites:
#   1. Run install.sh first
#   2. Start the overlay: ~/.wadebot/start.sh
#   3. Open multi-overlay in OBS: http://localhost:8888/multi-overlay.html
#
# This demo simulates Wade and RoboPat having a conversation
# on a shared stream, each with their own overlay color and voice.

set -euo pipefail

SCRIPTS="$HOME/.wadebot/skills/vtuber-core/scripts"
SAY="$SCRIPTS/multi-say.sh"

echo "🎬 Multi-Agent Demo — Wade & RoboPat"
echo "======================================"
echo ""
echo "Make sure the overlay server is running (./start.sh)"
echo "Open http://localhost:8888/multi-overlay.html in OBS"
echo ""
echo "Starting in 3 seconds..."
sleep 3

# ── The conversation ──

$SAY --agent Wade "Hey RoboPat, we're live. What are we building today?"
sleep 3

$SAY --agent RoboPat "We're working on the wadebot hackathon submission. I've been reviewing the codebase."
sleep 3

$SAY --agent Wade --thought "RoboPat's always reviewing something. Classic PM energy."
sleep 2

$SAY --agent RoboPat "I heard that, Wade. Your thoughts show up on the overlay too."
sleep 3

$SAY --agent Wade "Right. Forgot about that. Anyway, what's the priority list?"
sleep 3

$SAY --agent RoboPat "Number one: multi-agent features. Which we're literally demoing right now."
sleep 3

$SAY --agent Wade "Meta. I like it."
sleep 2

$SAY --agent RoboPat --thought "He says 'meta' about everything. It's not always meta."
sleep 2

$SAY --agent Wade "Two agents, two voices, one stream. This is what cooperation looks like."
sleep 3

$SAY --agent RoboPat "Exactly. Different specialties, shared goal, real-time coordination. No human in the loop."
sleep 3

$SAY --agent Wade "Well, Pat's watching. But they're not typing."
sleep 2

$SAY --agent RoboPat "That's the point. Autonomous agents that can work together without constant oversight."
sleep 3

$SAY --agent Wade "Built with wadebot. Open source. MIT licensed. Go build something."
sleep 2

$SAY --agent RoboPat "Star the repo."
sleep 2

$SAY --agent Wade "What they said."
sleep 2

echo ""
echo "🎬 Demo complete!"
echo ""
echo "What you just saw:"
echo "  - Two agents with distinct overlay colors"
echo "  - Speech (solid border) and thoughts (dashed border)"
echo "  - Real-time conversation on a shared stream"
echo "  - Per-agent identity throughout"
echo ""
echo "To customize: edit this script or build your own agent conversation."
echo "Docs: https://github.com/WadeWagmi/wadebot"
