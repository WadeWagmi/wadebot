#!/usr/bin/env python3
"""
Base Game Controller for browser-based game automation via Chrome DevTools Protocol (CDP).

This is the foundation for all wadebot game controllers. It handles:
- CDP WebSocket connection to Chrome
- JavaScript evaluation in page or iframe contexts
- Mouse/keyboard input dispatch
- Screenshots
- Element discovery

Subclass this and implement your game-specific logic.

Setup:
  1. Launch Chrome with remote debugging:
     google-chrome --remote-debugging-port=9222 --remote-allow-origins=* \
       --user-data-dir=/tmp/chrome-wadebot "https://your-game-url.com"
  
  2. pip install websocket-client requests Pillow

Usage:
  from base import GameController

  class MyGameController(GameController):
      def deal(self): self._click(565, 320)
      def hit(self): self._click_button('hit')
      ...
"""

import json
import time
import base64
from abc import ABC, abstractmethod

import requests
import websocket


class GameController(ABC):
    """Abstract base for CDP-based browser game automation.

    Subclasses should:
    - Set `GAME_URL_MATCH` to a string that appears in the target page/iframe URL
    - Implement game-specific action methods (deal, bet, hit, etc.)
    - Optionally override `_find_target()` for custom iframe discovery
    """

    CDP_PORT = 9222
    GAME_URL_MATCH: str = ""  # Override in subclass — substring to match in page URL

    def __init__(self, port=None):
        if port:
            self.CDP_PORT = port
        self.ws = None
        self.page_ws_url = None
        self._msg_id = 0
        self._connect()

    # ── Connection ──────────────────────────────────────────────

    def _connect(self):
        """Find the game page/iframe and connect via CDP WebSocket."""
        pages = requests.get(f"http://127.0.0.1:{self.CDP_PORT}/json", timeout=5).json()

        target = self._find_target(pages)
        if not target:
            raise RuntimeError(
                f"Game page not found. Looking for URL containing '{self.GAME_URL_MATCH}'.\n"
                f"Available pages: {[p.get('url','')[:80] for p in pages]}"
            )

        self.page_ws_url = target["webSocketDebuggerUrl"]
        self.ws = websocket.create_connection(self.page_ws_url, timeout=15)
        print(f"Connected: {target['url'][:80]}")

    def _find_target(self, pages):
        """Find the CDP target matching our game. Override for custom logic."""
        for p in pages:
            if self.GAME_URL_MATCH and self.GAME_URL_MATCH in p.get("url", ""):
                return p
        return None

    def reconnect(self):
        """Reconnect to the game (e.g., after page reload)."""
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        self._msg_id = 0
        self._connect()

    # ── CDP Primitives ──────────────────────────────────────────

    def _send(self, method, params=None):
        """Send a CDP command and return the response."""
        self._msg_id += 1
        msg = {"id": self._msg_id, "method": method}
        if params:
            msg["params"] = params
        self.ws.send(json.dumps(msg))

        # Read until we get our response (skip events)
        for _ in range(200):
            try:
                resp = json.loads(self.ws.recv())
                if resp.get("id") == self._msg_id:
                    return resp
            except websocket.WebSocketTimeoutException:
                return None
        return None

    def _eval(self, expression, await_promise=False):
        """Evaluate JavaScript in the connected page/iframe."""
        params = {"expression": expression, "returnByValue": True}
        if await_promise:
            params["awaitPromise"] = True
        result = self._send("Runtime.evaluate", params)
        if not result:
            return None
        return result.get("result", {}).get("result", {}).get("value")

    # ── Shadow DOM Support ──────────────────────────────────────
    # Many modern web games use Shadow DOM (web components).
    # These helpers let you evaluate JS inside a shadow root.

    def _shadow_eval(self, js, host_selector="blink-launcher"):
        """Evaluate JS inside a shadow root. `sr` is available as the shadow root."""
        wrapped = f"""(() => {{
            let host = document.querySelector("{host_selector}");
            if (!host || !host.shadowRoot) return "ERROR: no shadow root for {host_selector}";
            let sr = host.shadowRoot;
            {js}
        }})()"""
        return self._eval(wrapped)

    def _shadow_click_by_text(self, tag, text, host_selector="blink-launcher"):
        """Click an element inside shadow DOM by its text content."""
        return self._shadow_eval(
            f'let els = sr.querySelectorAll("{tag}");'
            f'for (let el of els) {{'
            f'  if (el.textContent.trim() === "{text}") {{ el.click(); return "clicked: {text}"; }}'
            f'}}'
            f'return "ERROR: not found: {text}";',
            host_selector,
        )

    # ── Input ───────────────────────────────────────────────────

    def _click(self, x, y):
        """Click at coordinates using JS event dispatch (works in iframes)."""
        self._eval(f"""
            (function() {{
                var el = document.elementFromPoint({x}, {y});
                if (el) {{
                    el.dispatchEvent(new PointerEvent('pointerdown', {{clientX: {x}, clientY: {y}, bubbles: true}}));
                    el.dispatchEvent(new PointerEvent('pointerup', {{clientX: {x}, clientY: {y}, bubbles: true}}));
                    el.dispatchEvent(new MouseEvent('click', {{clientX: {x}, clientY: {y}, bubbles: true}}));
                }}
            }})()
        """)

    def _cdp_click(self, x, y):
        """Click at coordinates using CDP Input events (works for React/canvas)."""
        self._send("Input.dispatchMouseEvent", {
            "type": "mousePressed", "x": x, "y": y,
            "button": "left", "clickCount": 1,
        })
        self._send("Input.dispatchMouseEvent", {
            "type": "mouseReleased", "x": x, "y": y,
            "button": "left", "clickCount": 1,
        })

    def _click_button(self, name):
        """Find and click a button by its text label (case-insensitive)."""
        buttons = self._find_buttons()
        if name.lower() in buttons:
            pos = buttons[name.lower()]
            self._click(pos["x"], pos["y"])
            return True
        return False

    def _find_buttons(self):
        """Find all visible buttons and their center coordinates."""
        result = self._eval("""
            JSON.stringify(
                Array.from(document.querySelectorAll('button')).reduce((btns, el) => {
                    const rect = el.getBoundingClientRect();
                    const text = (el.textContent || '').trim().toLowerCase();
                    if (rect.width > 0 && text) {
                        btns[text] = {
                            x: Math.round(rect.x + rect.width / 2),
                            y: Math.round(rect.y + rect.height / 2)
                        };
                    }
                    return btns;
                }, {})
            )
        """)
        return json.loads(result) if result else {}

    def _set_input(self, selector, value):
        """Set an input field's value (React-compatible)."""
        return self._eval(f"""
            (() => {{
                let input = document.querySelector('{selector}');
                if (!input) return 'ERROR: not found';
                let setter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                setter.call(input, '{value}');
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return 'set';
            }})()
        """)

    # ── Screenshot ──────────────────────────────────────────────

    def screenshot(self, path="/tmp/game.png"):
        """Take a screenshot. Returns the file path."""
        result = self._send("Page.captureScreenshot", {"format": "png"})
        if result and "result" in result:
            with open(path, "wb") as f:
                f.write(base64.b64decode(result["result"]["data"]))
            return path
        return None

    # ── State ───────────────────────────────────────────────────

    def get_buttons(self):
        """Get dict of currently visible button labels → positions."""
        return self._find_buttons()

    @abstractmethod
    def get_state(self):
        """Return the current game state as a dict. Subclasses must implement."""
        ...

    # ── Lifecycle ───────────────────────────────────────────────

    def close(self):
        """Close the CDP WebSocket connection."""
        if self.ws:
            self.ws.close()
            print("Connection closed")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()
