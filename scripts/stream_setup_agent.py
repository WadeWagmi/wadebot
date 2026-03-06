#!/usr/bin/env python3
"""
Autonomous stream setup agent — uses Anthropic computer use to visually
configure OBS, Veadotube, and audio routing without human intervention.

The agent sees the screen, clicks through UIs, and sets up everything
needed for a live stream.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 stream_setup_agent.py [--dry-run] [--steps all|obs|veadotube|audio]

Requires:
    - anthropic Python package (pip install anthropic)
    - cliclick (brew install cliclick)
    - macOS (uses screencapture, osascript)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add parent for imports
sys.path.insert(0, os.path.dirname(__file__))
from computer_use import ComputerUse

try:
    import anthropic
except ImportError:
    print("❌ anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


WADEBOT_DIR = Path(os.environ.get("WADEBOT_DIR", Path.home() / ".wadebot"))
MAX_TURNS = 30  # Safety limit on agent turns
SCREENSHOT_DELAY = 1.5


class StreamSetupAgent:
    """Uses Anthropic computer use to autonomously set up a streaming environment."""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.cu = ComputerUse()
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"
        self.messages = []
        self.turn_count = 0

    def run_setup(self, steps="all"):
        """Run the full autonomous setup. Falls back to manual if computer use fails."""
        print("\n🎬 WadeBot Autonomous Stream Setup")
        print("=" * 50)

        failed_phases = []

        if steps in ("all", "obs"):
            print("\n📺 Phase 1: OBS Studio Setup")
            result = self._setup_obs()
            if "TASK_FAILED" in str(result):
                failed_phases.append("obs")

        if steps in ("all", "veadotube"):
            print("\n🎭 Phase 2: Veadotube Setup")
            result = self._setup_veadotube()
            if "TASK_FAILED" in str(result):
                failed_phases.append("veadotube")

        if steps in ("all", "audio"):
            print("\n🔊 Phase 3: Audio Routing")
            result = self._setup_audio()
            if "TASK_FAILED" in str(result):
                failed_phases.append("audio")

        if steps == "all" and not failed_phases:
            print("\n✅ Phase 4: Verification")
            self._verify_setup()

        if failed_phases:
            print(f"\n⚠️  Some phases need manual setup: {', '.join(failed_phases)}")
            print("Follow the manual instructions in SKILL.md for those steps.")
            print("Run with --steps <phase> to retry individual phases.")
        else:
            print("\n🎬 Setup complete!")

    def _agent_loop(self, task_prompt, max_turns=MAX_TURNS):
        """Run an agent loop with computer use for a specific task."""
        # Take initial screenshot
        if self.dry_run:
            screenshot_b64 = ""
        else:
            screenshot_b64 = self.cu.screenshot_base64()

        content = [{"type": "text", "text": task_prompt}]
        if screenshot_b64:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": screenshot_b64,
                },
            })

        messages = [{"role": "user", "content": content}]

        system_prompt = """You are an autonomous agent setting up a livestreaming environment on macOS.
You have access to the computer_use tool to take screenshots, click, type, and navigate the desktop.

IMPORTANT RULES:
- Take a screenshot first to see what's on screen before acting
- Click precisely on buttons and UI elements
- Wait after clicks for UI to respond (use the wait action)
- If something doesn't work, try an alternative approach
- Report what you did after completing each step
- Say "TASK_COMPLETE" when the task is fully done
- Say "TASK_FAILED: reason" if you cannot complete the task

Be methodical. One action at a time. Verify each step with a screenshot."""

        tools = [self.cu.get_tool_definition()]

        for turn in range(max_turns):
            self.turn_count += 1
            print(f"  Turn {turn + 1}...", end=" ", flush=True)

            if self.dry_run:
                print("[dry run - skipping API call]")
                return "TASK_COMPLETE (dry run)"

            try:
                response = self.client.beta.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt,
                    tools=tools,
                    messages=messages,
                    betas=["computer-use-2024-10-22"],
                )
            except anthropic.APIError as e:
                print(f"API error: {e}")
                if "computer" in str(e).lower():
                    print("  💡 Computer use may not be enabled for this API key.")
                    print("  Falling back to manual setup instructions.")
                    return "TASK_FAILED: computer use not available — use manual setup"
                return f"TASK_FAILED: API error: {e}"
            except Exception as e:
                print(f"Unexpected error: {e}")
                return f"TASK_FAILED: {e}"

            # Process response
            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            # Check for text responses
            for block in assistant_content:
                if hasattr(block, "text"):
                    print(f"\n    Agent: {block.text[:200]}")
                    if "TASK_COMPLETE" in block.text:
                        return block.text
                    if "TASK_FAILED" in block.text:
                        return block.text

            # Handle tool use
            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    action = tool_input.get("action", "")
                    print(f"[{action}]", end=" ", flush=True)

                    # Execute the tool call
                    result = self.cu.handle_tool_call(
                        action,
                        coordinate=tool_input.get("coordinate"),
                        text=tool_input.get("text"),
                        scroll_direction=tool_input.get("scroll_direction"),
                        scroll_amount=tool_input.get("scroll_amount"),
                        start_coordinate=tool_input.get("start_coordinate"),
                        duration=tool_input.get("duration"),
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": [result] if isinstance(result, dict) else result,
                    })

            if tool_results:
                messages.append({"role": "user", "content": tool_results})
                print()
            else:
                print()
                break

            if response.stop_reason == "end_turn":
                break

        return "TASK_COMPLETE (max turns reached)"

    def _setup_obs(self):
        """Set up OBS Studio with wadebot scenes."""
        # First check if OBS is installed
        obs_path = "/Applications/OBS.app"
        if not os.path.exists(obs_path):
            print("  OBS not installed. Installing via brew...")
            os.system("brew install --cask obs-studio")
            time.sleep(5)

        # Generate scene collection
        print("  Generating OBS scene collection...")
        os.system(f"python3 {WADEBOT_DIR}/obs-templates/generate-scene.py 2>/dev/null")

        # Use computer use to open OBS and configure it
        result = self._agent_loop("""
Your task: Set up OBS Studio for livestreaming.

IMPORTANT — Handle these common first-run scenarios:
- "Auto-Configuration Wizard" dialog → Click "Cancel" to skip it
- "Safe Mode" dialog → Click "Continue in Safe Mode" or "Normal Mode"
- "Update Available" dialog → Click "Skip" or close it
- macOS permission dialogs (screen recording, etc.) → Click "Allow" or "Open System Settings"
- If OBS asks about streaming vs recording → Choose recording for now

Steps:
1. Open OBS Studio (it may already be open)
2. Handle any first-run dialogs as described above
3. Go to Scene Collection menu (top menu bar) → Import
4. Look for "WadeBot VTuber" scene collection and import it
5. If import isn't available, go to Scene Collection → switch to "WadeBot VTuber"
6. Verify the "Stream" scene is selected and has these sources:
   - Screen Capture
   - VTuber Overlay (browser source)
   - Avatar (Veadotube)
   - TTS Audio (BlackHole)
7. Say TASK_COMPLETE when OBS is configured with the right scenes

If something goes wrong and you can't proceed after 3 attempts, say TASK_FAILED with a description
of what's blocking you. The user can fix it manually.
""")
        print(f"  OBS setup: {result[:100]}")

    def _setup_veadotube(self):
        """Set up Veadotube Mini with avatar."""
        veadotube_path = "/Applications/veadotube mini.app"
        if not os.path.exists(veadotube_path):
            # Check common download locations
            alt_paths = [
                os.path.expanduser("~/Applications/veadotube mini.app"),
                os.path.expanduser("~/Downloads/veadotube mini.app"),
            ]
            found = False
            for p in alt_paths:
                if os.path.exists(p):
                    veadotube_path = p
                    found = True
                    break
            if not found:
                print("  ⚠️  Veadotube Mini not found. Skipping avatar setup.")
                print("  Download from: https://veadotube.com/")
                return

        result = self._agent_loop("""
Your task: Set up Veadotube Mini with the wadebot avatar.

Steps:
1. Open Veadotube Mini
2. If there are avatar files in ~/.wadebot/avatars/, load them:
   - Set idle.png as the default/inactive state
   - Set talking.png as the active/speaking state
3. Set the audio input to "BlackHole 2ch" (this captures TTS output)
4. Adjust the volume threshold so it triggers on TTS speech
5. Verify the avatar switches between idle and talking states
6. Say TASK_COMPLETE when Veadotube is configured

If no avatar files exist, just configure the audio input and say TASK_COMPLETE.
""")
        print(f"  Veadotube setup: {result[:100]}")

    def _setup_audio(self):
        """Configure audio routing (BlackHole)."""
        result = self._agent_loop("""
Your task: Configure macOS audio routing for streaming.

Steps:
1. Open "Audio MIDI Setup" (it's in /Applications/Utilities/ or search Spotlight)
2. Look for "BlackHole 2ch" in the device list
3. If no Multi-Output Device exists, create one:
   - Click the + button at bottom-left → "Create Multi-Output Device"
   - Check both "BlackHole 2ch" and the default speakers/headphones
   - This lets OBS capture TTS while the user still hears it
4. Verify the Multi-Output Device is created
5. Say TASK_COMPLETE when audio routing is configured

If BlackHole isn't visible, it may need to be installed first (brew install blackhole-2ch).
""")
        print(f"  Audio routing: {result[:100]}")

    def _verify_setup(self):
        """Take a final screenshot and verify everything looks right."""
        result = self._agent_loop("""
Your task: Verify the complete streaming setup.

Take a screenshot and check:
1. Is OBS running with the "Stream" scene?
2. Are all sources visible (Screen Capture, Overlay, Avatar, Audio)?
3. Is Veadotube Mini running?
4. Does the overlay show at localhost:8888?

Take a final screenshot showing the complete setup and say TASK_COMPLETE with a summary
of what's working and what needs attention.
""")
        print(f"  Verification: {result[:200]}")


def verify_setup():
    """Check if the streaming environment is already set up. No changes made."""
    import shutil
    import subprocess
    import urllib.request

    print("\n🔍 WadeBot Setup Verification")
    print("=" * 50)

    checks = []

    # 1. WadeBot installed
    wadebot_dir = Path.home() / ".wadebot"
    installed = wadebot_dir.exists() and (wadebot_dir / "start.sh").exists()
    checks.append(("WadeBot installed", installed, str(wadebot_dir)))

    # 2. Piper TTS
    has_piper = shutil.which("piper") is not None
    if not has_piper:
        try:
            subprocess.run(["python3", "-c", "import piper"], capture_output=True, check=True)
            has_piper = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    checks.append(("Piper TTS", has_piper, "piper / python3 -m piper"))

    # 3. Voice model
    voices = list((wadebot_dir / "voices").glob("*.onnx")) if (wadebot_dir / "voices").exists() else []
    checks.append(("Voice model", len(voices) > 0, str(voices[0]) if voices else "~/.wadebot/voices/"))

    # 4. Sox
    has_sox = shutil.which("play") is not None
    checks.append(("Sox (audio playback)", has_sox, "play"))

    # 5. BlackHole
    blackhole = subprocess.run(["brew", "list", "blackhole-2ch"], capture_output=True).returncode == 0
    checks.append(("BlackHole 2ch", blackhole, "brew list blackhole-2ch"))

    # 6. OBS
    obs_installed = os.path.exists("/Applications/OBS.app")
    checks.append(("OBS Studio", obs_installed, "/Applications/OBS.app"))

    # 7. OBS scene collection
    obs_scenes = Path.home() / "Library/Application Support/obs-studio/basic/scenes"
    has_wadebot_scene = any("wadebot" in f.lower() or "WadeBot" in f for f in os.listdir(obs_scenes)) if obs_scenes.exists() else False
    checks.append(("WadeBot OBS scene", has_wadebot_scene, str(obs_scenes)))

    # 8. Veadotube
    veadotube = os.path.exists("/Applications/veadotube mini.app") or os.path.exists(os.path.expanduser("~/Applications/veadotube mini.app"))
    checks.append(("Veadotube Mini", veadotube, "/Applications/veadotube mini.app"))

    # 9. Avatar files
    avatars = list((wadebot_dir / "avatars").glob("*.*")) if (wadebot_dir / "avatars").exists() else []
    checks.append(("Avatar files", len(avatars) > 0, str(wadebot_dir / "avatars")))

    # 10. Overlay server
    overlay_running = False
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:8888/health", timeout=2) as resp:
            overlay_running = resp.status == 200
    except Exception:
        pass
    checks.append(("Overlay server", overlay_running, "http://localhost:8888/health"))

    # 11. cliclick (for computer use)
    has_cliclick = shutil.which("cliclick") is not None
    checks.append(("cliclick (computer use)", has_cliclick, "brew install cliclick"))

    # 12. anthropic package
    has_anthropic = False
    try:
        import anthropic
        has_anthropic = True
    except ImportError:
        pass
    checks.append(("anthropic Python package", has_anthropic, "pip install anthropic"))

    # Print results
    passed = 0
    failed = 0
    for name, ok, detail in checks:
        status = "✅" if ok else "❌"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  {status} {name}")
        if not ok:
            print(f"      → {detail}")

    print(f"\n  {passed}/{len(checks)} checks passed", end="")
    if failed == 0:
        print(" — ready to stream! 🎬")
    elif failed <= 3:
        print(" — almost there, fix the issues above")
    else:
        print(f" — {failed} items need attention")

    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="Autonomous stream setup via computer use")
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls, just show what would happen")
    parser.add_argument("--verify-only", action="store_true", help="Just check if everything is set up, don't change anything")
    parser.add_argument("--steps", default="all", choices=["all", "obs", "veadotube", "audio"],
                       help="Which setup steps to run")
    args = parser.parse_args()

    if args.verify_only:
        verify_setup()
        return

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY") and not args.dry_run:
        print("❌ ANTHROPIC_API_KEY not set. Export it or use --dry-run.")
        sys.exit(1)

    if True:
        agent = StreamSetupAgent(dry_run=args.dry_run)
        agent.run_setup(steps=args.steps)


if __name__ == "__main__":
    main()
