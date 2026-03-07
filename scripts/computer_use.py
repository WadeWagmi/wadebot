#!/usr/bin/env python3
"""
macOS computer use tool for wadebot — screenshot + mouse/keyboard control.

Provides the primitives needed for Anthropic's computer use API on macOS:
- Screenshots via screencapture
- Mouse control via cliclick
- Keyboard control via cliclick + osascript
- Window management via osascript

Usage as library:
    from computer_use import ComputerUse
    cu = ComputerUse()
    cu.screenshot("/tmp/screen.png")
    cu.click(100, 200)
    cu.type_text("hello world")

Usage as CLI:
    python3 computer_use.py screenshot
    python3 computer_use.py click 100 200
    python3 computer_use.py type "hello world"
    python3 computer_use.py key "command+space"
"""

import base64
import json
import os
import shutil
import subprocess
import sys
import time
import tempfile
from pathlib import Path


class ComputerUse:
    """macOS computer control for Anthropic computer use API."""

    def __init__(self, display_width=1920, display_height=1080):
        self.width = display_width
        self.height = display_height
        self._verify_tools()

    def _verify_tools(self):
        """Check required tools are available."""
        # screencapture is built into macOS
        if not self._has_command("screencapture"):
            raise RuntimeError("screencapture not found (should be built into macOS)")

        # cliclick for mouse/keyboard
        if not self._has_command("cliclick"):
            print("⚠️  cliclick not found. Install: brew install cliclick")
            print("   Mouse/keyboard control will use osascript fallback (slower)")
            self._use_cliclick = False
        else:
            self._use_cliclick = True

    @staticmethod
    def _has_command(cmd):
        if shutil.which(cmd) is not None:
            return True
        # Fallback: check common macOS paths not always in PATH
        for d in ["/usr/sbin", "/usr/bin", "/usr/local/bin", "/opt/homebrew/bin"]:
            if os.path.isfile(os.path.join(d, cmd)):
                os.environ["PATH"] = os.environ.get("PATH", "") + ":" + d
                return True
        return False

    def _run(self, cmd, **kwargs):
        """Run a shell command."""
        result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
        return result.stdout.strip()

    # ── Screenshots ──

    def screenshot(self, path=None, region=None):
        """Take a screenshot. Returns path to PNG file."""
        if path is None:
            path = os.path.join(tempfile.gettempdir(), f"wadebot_screen_{int(time.time())}.png")

        cmd = ["screencapture", "-x"]  # -x = no sound
        if region:
            # region = (x, y, w, h)
            x, y, w, h = region
            cmd.extend(["-R", f"{x},{y},{w},{h}"])
        cmd.append(path)

        self._run(cmd)
        return path

    def screenshot_base64(self, region=None):
        """Take a screenshot and return as base64-encoded PNG."""
        path = self.screenshot(region=region)
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode()
        os.unlink(path)
        return data

    # ── Mouse Control ──

    def click(self, x, y, button="left"):
        """Click at coordinates."""
        if self._use_cliclick:
            btn = {"left": "c", "right": "rc", "middle": "mc"}[button]
            self._run(["cliclick", f"{btn}:{x},{y}"])
        else:
            self._osascript_click(x, y, button)

    def double_click(self, x, y):
        """Double-click at coordinates."""
        if self._use_cliclick:
            self._run(["cliclick", f"dc:{x},{y}"])
        else:
            self._osascript(f'''
                tell application "System Events"
                    click at {{{x}, {y}}}
                    delay 0.05
                    click at {{{x}, {y}}}
                end tell
            ''')

    def mouse_move(self, x, y):
        """Move mouse to coordinates."""
        if self._use_cliclick:
            self._run(["cliclick", f"m:{x},{y}"])
        else:
            self._osascript(f'''
                do shell script "python3 -c \\"import Quartz; Quartz.CGEventPost(Quartz.kCGHIDEventTap, Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventMouseMoved, ({x}, {y}), 0))\\""
            ''')

    def drag(self, x1, y1, x2, y2):
        """Click and drag from (x1,y1) to (x2,y2)."""
        if self._use_cliclick:
            self._run(["cliclick", f"dd:{x1},{y1}", f"du:{x2},{y2}"])
        else:
            self._osascript(f'''
                do shell script "cliclick dd:{x1},{y1} du:{x2},{y2}"
            ''')

    def scroll(self, x, y, direction="down", amount=3):
        """Scroll at coordinates."""
        self.mouse_move(x, y)
        if self._use_cliclick:
            scroll_amount = amount if direction == "up" else -amount
            # cliclick doesn't have scroll, use osascript
            self._osascript(f'''
                tell application "System Events"
                    scroll {("up" if direction == "up" else "down")} by {amount}
                end tell
            ''')
        else:
            self._osascript(f'''
                tell application "System Events"
                    scroll {("up" if direction == "up" else "down")} by {amount}
                end tell
            ''')

    # ── Keyboard Control ──

    def type_text(self, text):
        """Type text string."""
        if self._use_cliclick:
            self._run(["cliclick", f"t:{text}"])
        else:
            # Escape for osascript
            escaped = text.replace("\\", "\\\\").replace('"', '\\"')
            self._osascript(f'''
                tell application "System Events"
                    keystroke "{escaped}"
                end tell
            ''')

    def key(self, key_combo):
        """Press a key combination (e.g., 'command+space', 'return', 'escape').

        Supported modifiers: command, control, option, shift
        Supported keys: return, escape, tab, delete, space, up, down, left, right,
                       f1-f12, and any single character
        """
        if self._use_cliclick:
            # Convert to cliclick format
            cliclick_key = self._convert_key_for_cliclick(key_combo)
            self._run(["cliclick", f"kp:{cliclick_key}"])
        else:
            self._osascript_key(key_combo)

    def _convert_key_for_cliclick(self, key_combo):
        """Convert key combo string to cliclick format."""
        parts = key_combo.lower().split("+")
        key = parts[-1].strip()
        modifiers = [p.strip() for p in parts[:-1]]

        # cliclick key names
        key_map = {
            "return": "return", "enter": "return",
            "escape": "escape", "esc": "escape",
            "tab": "tab",
            "delete": "delete", "backspace": "delete",
            "space": "space",
            "up": "arrow-up", "down": "arrow-down",
            "left": "arrow-left", "right": "arrow-right",
        }

        cliclick_key = key_map.get(key, key)

        # Build modifier string
        mod_str = ""
        if "command" in modifiers or "cmd" in modifiers:
            mod_str += "cmd,"
        if "control" in modifiers or "ctrl" in modifiers:
            mod_str += "ctrl,"
        if "option" in modifiers or "alt" in modifiers:
            mod_str += "alt,"
        if "shift" in modifiers:
            mod_str += "shift,"

        if mod_str:
            # Use key-down/key-up for modifiers
            return f"{cliclick_key}"  # cliclick handles modifiers differently
        return cliclick_key

    def _osascript_key(self, key_combo):
        """Press key combo via osascript."""
        parts = key_combo.lower().split("+")
        key = parts[-1].strip()
        modifiers = [p.strip() for p in parts[:-1]]

        # Build AppleScript
        mod_clause = ""
        if modifiers:
            mod_list = []
            for m in modifiers:
                if m in ("command", "cmd"):
                    mod_list.append("command down")
                elif m in ("control", "ctrl"):
                    mod_list.append("control down")
                elif m in ("option", "alt"):
                    mod_list.append("option down")
                elif m == "shift":
                    mod_list.append("shift down")
            mod_clause = " using {" + ", ".join(mod_list) + "}"

        # Special keys
        special_keys = {
            "return": 'key code 36', "enter": 'key code 36',
            "escape": 'key code 53', "esc": 'key code 53',
            "tab": 'key code 48',
            "delete": 'key code 51', "backspace": 'key code 51',
            "space": 'key code 49',
            "up": 'key code 126', "down": 'key code 125',
            "left": 'key code 123', "right": 'key code 124',
        }

        if key in special_keys:
            action = f"{special_keys[key]}{mod_clause}"
        else:
            action = f'keystroke "{key}"{mod_clause}'

        self._osascript(f'''
            tell application "System Events"
                {action}
            end tell
        ''')

    # ── Window Management ──

    def open_app(self, app_name):
        """Open an application."""
        self._run(["open", "-a", app_name])
        time.sleep(2)  # Wait for app to launch

    def list_windows(self):
        """List visible windows."""
        script = '''
            tell application "System Events"
                set windowList to {}
                repeat with proc in (every process whose visible is true)
                    repeat with win in (every window of proc)
                        set end of windowList to (name of proc) & ": " & (name of win)
                    end repeat
                end repeat
                return windowList
            end tell
        '''
        result = self._osascript(script)
        return result.split(", ") if result else []

    def focus_window(self, app_name):
        """Bring an application to front."""
        self._osascript(f'''
            tell application "{app_name}" to activate
        ''')
        time.sleep(0.5)

    def get_window_position(self, app_name):
        """Get window position and size."""
        result = self._osascript(f'''
            tell application "System Events"
                tell process "{app_name}"
                    set winPos to position of front window
                    set winSize to size of front window
                    return (item 1 of winPos) & "," & (item 2 of winPos) & "," & (item 1 of winSize) & "," & (item 2 of winSize)
                end tell
            end tell
        ''')
        if result:
            parts = result.split(",")
            return {"x": int(parts[0]), "y": int(parts[1]), "w": int(parts[2]), "h": int(parts[3])}
        return None

    # ── Helpers ──

    def _osascript(self, script):
        """Run AppleScript."""
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def _osascript_click(self, x, y, button="left"):
        """Click via osascript (fallback)."""
        self._osascript(f'''
            do shell script "python3 -c \\"import Quartz; e=Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDown, ({x},{y}), 0); Quartz.CGEventPost(Quartz.kCGHIDEventTap, e); import time; time.sleep(0.05); e=Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseUp, ({x},{y}), 0); Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)\\""
        ''')

    # ── Anthropic API Integration ──

    def get_tool_definition(self):
        """Return the Anthropic computer use tool definition."""
        return {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": self.width,
            "display_height_px": self.height,
            "display_number": 1,
        }

    def handle_tool_call(self, action, **kwargs):
        """Handle a computer use tool call from the Anthropic API.

        Returns a ToolResult dict with base64 screenshot if applicable.
        """
        try:
            if action == "screenshot":
                b64 = self.screenshot_base64()
                return {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}}

            elif action == "cursor_position":
                # Get current cursor position via cliclick
                if self._use_cliclick:
                    result = self._run(["cliclick", "p:"])
                    return {"type": "text", "text": result}
                return {"type": "text", "text": "unknown"}

            elif action == "mouse_move":
                x, y = kwargs.get("coordinate", (0, 0))
                self.mouse_move(x, y)

            elif action == "left_click":
                x, y = kwargs.get("coordinate", (0, 0))
                self.click(x, y, "left")

            elif action == "right_click":
                x, y = kwargs.get("coordinate", (0, 0))
                self.click(x, y, "right")

            elif action == "double_click":
                x, y = kwargs.get("coordinate", (0, 0))
                self.double_click(x, y)

            elif action == "left_click_drag":
                start = kwargs.get("start_coordinate", (0, 0))
                end = kwargs.get("coordinate", (0, 0))
                self.drag(start[0], start[1], end[0], end[1])

            elif action == "type":
                text = kwargs.get("text", "")
                self.type_text(text)

            elif action == "key":
                key = kwargs.get("text", "")
                self.key(key)

            elif action == "scroll":
                x, y = kwargs.get("coordinate", (0, 0))
                direction = kwargs.get("scroll_direction", "down")
                amount = kwargs.get("scroll_amount", 3)
                self.scroll(x, y, direction, amount)

            elif action == "wait":
                duration = kwargs.get("duration", 1)
                time.sleep(duration)

            else:
                return {"type": "text", "text": f"Unknown action: {action}"}

            # Return screenshot after action
            time.sleep(0.5)
            b64 = self.screenshot_base64()
            return {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}}

        except Exception as e:
            return {"type": "text", "text": f"Error: {str(e)}"}


# ── CLI Interface ──

def main():
    if len(sys.argv) < 2:
        print("Usage: computer_use.py <action> [args...]")
        print("Actions: screenshot, click, double_click, type, key, move, open, windows, focus")
        sys.exit(1)

    cu = ComputerUse()
    action = sys.argv[1]

    if action == "screenshot":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        result = cu.screenshot(path)
        print(f"Screenshot saved: {result}")

    elif action == "click":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        button = sys.argv[4] if len(sys.argv) > 4 else "left"
        cu.click(x, y, button)
        print(f"Clicked ({x}, {y})")

    elif action == "double_click":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        cu.double_click(x, y)
        print(f"Double-clicked ({x}, {y})")

    elif action == "type":
        text = " ".join(sys.argv[2:])
        cu.type_text(text)
        print(f"Typed: {text}")

    elif action == "key":
        combo = sys.argv[2]
        cu.key(combo)
        print(f"Pressed: {combo}")

    elif action == "move":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        cu.mouse_move(x, y)
        print(f"Moved to ({x}, {y})")

    elif action == "open":
        app = " ".join(sys.argv[2:])
        cu.open_app(app)
        print(f"Opened: {app}")

    elif action == "windows":
        windows = cu.list_windows()
        for w in windows:
            print(f"  {w}")

    elif action == "focus":
        app = " ".join(sys.argv[2:])
        cu.focus_window(app)
        print(f"Focused: {app}")

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
