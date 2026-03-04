# vtuber-games

Framework for autonomous game streaming via browser automation. Your agent plays, reacts, and narrates — viewers watch.

**Optional skill.** Only needed if your agent streams browser-based games. Coding streams, art streams, just-chatting — those only need `vtuber-core`.

## Game Loop Pattern

Every game controller follows the same cycle:

```
1. Screenshot the game state
2. Analyze (image → structured data, or DOM reading)
3. Decide (strategy + agent personality)
4. Act (click/input via CDP)
5. Narrate (TTS + overlay via vtuber-core)
6. Repeat
```

## Base Controller

`controllers/base.py` provides the CDP foundation:

```python
from base import GameController

class MyGameController(GameController):
    GAME_URL_MATCH = "my-game"  # Substring in the game's URL
    
    def deal(self):
        self._click(565, 320)
    
    def hit(self):
        self._click_button("hit")  # Finds button by text label
    
    def get_state(self):
        hand = self._eval("document.querySelector('.score').textContent")
        buttons = self.get_buttons()
        return {"score": hand, "actions": list(buttons.keys())}
```

### What the base gives you:
- CDP WebSocket connection management
- `_click(x, y)` — JS event dispatch (works in iframes)
- `_cdp_click(x, y)` — CDP Input events (works for React/canvas)
- `_click_button("text")` — Find and click buttons by label
- `_eval(js)` — Run JavaScript in the game page
- `_shadow_eval(js)` — Run JS inside shadow DOM (web components)
- `_set_input(selector, value)` — React-compatible input setting
- `_find_buttons()` — Discover all visible buttons + positions
- `screenshot(path)` — Capture the game state
- Context manager support (`with MyController() as game:`)

## Example: Blackjack

See `controllers/example_blackjack.py` for a complete implementation:
- Chip selection + bet placement
- Deal, hit, stand, double down
- DOM-based hand value reading
- Basic strategy helper
- Full game loop example

## Adding a New Game

1. **Subclass `GameController`** — set `GAME_URL_MATCH`
2. **Map coordinates** — screenshot the game, note button/element positions
3. **Implement actions** — `_click()` for simple, `_click_button()` for dynamic
4. **Read game state** — `_eval()` to query the DOM, or screenshot + image analysis
5. **Wire up narration** — call `say.sh`/`think.sh` from your agent's game loop

## Setup

```bash
# Launch Chrome with remote debugging
google-chrome --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/tmp/chrome-wadebot \
  "https://your-game-url.com"

# Install Python deps
pip install websocket-client requests Pillow
```

## Narration

Game narration comes from the agent's personality (SOUL.md), not from the toolkit. The controller tells the agent what happened; the agent decides how to react.

```
state = game.get_state()
# Agent sees: player=20, dealer=6, actions=[hit, stand]
# Agent decides: stand (basic strategy)
# Agent narrates: "Twenty. Standing. Don't get greedy." (personality-driven)
```
