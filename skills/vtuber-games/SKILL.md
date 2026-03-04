# vtuber-games

Framework for autonomous game streaming. Your agent plays, reacts, and narrates — you watch.

## Game Loop

Every game controller follows the same pattern:

```
1. Screenshot the game state
2. Analyze (image → structured data)
3. Decide (strategy + personality)
4. Act (click/input via CDP)
5. Narrate (TTS + overlay reaction)
6. Repeat
```

## Controller Pattern

```python
class GameController:
    """Base class for browser game automation via CDP."""
    
    def __init__(self, cdp_url, game_iframe_url=None):
        self.ws = connect_cdp(cdp_url)
        self.game_frame = find_frame(game_iframe_url)
    
    def screenshot(self) -> str:
        """Capture current game state as base64 PNG."""
        
    def click(self, x, y):
        """Click at coordinates in the game frame."""
        
    def find_element(self, selector):
        """Find element in game iframe."""

class BlackjackController(GameController):
    """Example: betplay.io blackjack automation."""
    
    def deal(self): ...
    def hit(self): ...
    def stand(self): ...
    def double_down(self): ...
    def set_bet(self, amount_usd): ...
    def read_hand(self) -> dict: ...
```

## Bankroll Management

```json
{
  "session": {
    "startingBalance": 25.00,
    "stopLoss": 10.00,
    "winTarget": 50.00,
    "maxHands": 100,
    "currency": "USD"
  }
}
```

The agent tracks:
- Session P&L
- Win/loss streaks
- Bet sizing history
- Time played

## Reference Controllers

| Game | File | Platform |
|------|------|----------|
| Blackjack | `controllers/blackjack.py` | betplay.io |
| Mines | `controllers/mines.py` | betplay.io |
| Plinko | `controllers/plinko.py` | betplay.io |

## Adding a New Game

1. Subclass `GameController`
2. Implement game-specific actions (deal, bet, etc.)
3. Add screenshot analysis prompts
4. Define a basic strategy (or let the agent wing it)
5. Wire up narration hooks

## Narration Flow

The agent narrates naturally based on game events:

```
bet_placed    → "Putting $5 on it. Let's see."
cards_dealt   → "King-seven. Seventeen. Dealer showing a six."
decision      → "Standing. Don't be greedy."
win           → "Thank fuck."
loss          → "Are you fucking kidding me."
streak_loss   → "Every single time. Every single fucking time."
```

Reactions come from the agent's SOUL.md / IDENTITY.md — not hardcoded. The personality drives the stream.
