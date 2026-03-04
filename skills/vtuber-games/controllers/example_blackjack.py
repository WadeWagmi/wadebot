#!/usr/bin/env python3
"""
Example: Blackjack Controller

Demonstrates how to subclass GameController for a specific browser-based card game.
This example targets betplay.io's blackjack, but the pattern works for any game:

1. Define coordinate maps for UI elements (chips, buttons, bet areas)
2. Implement game actions (deal, hit, stand, double)
3. Implement state reading (hand values, available actions)
4. Wire up a game loop

Adapt this for your game by changing the URL match, coordinates, and actions.

Usage:
    from example_blackjack import BlackjackController
    
    with BlackjackController() as bj:
        bj.select_chip(1)      # $1 chip
        bj.place_bet()         # click bet area
        bj.deal()              # start hand
        
        state = bj.get_state()
        print(f"Player: {state['player']}, Dealer: {state['dealer']}")
        
        bj.hit()   # or bj.stand(), bj.double_down()
"""

import json
import time
from base import GameController


class BlackjackController(GameController):
    """CDP controller for a browser-based blackjack game.
    
    This example uses betplay.io's blackjack which runs in a nested iframe.
    The key pattern: find the game iframe by URL substring, connect to it,
    then use coordinate-based clicks + DOM queries for game state.
    """

    GAME_URL_MATCH = "fg-blackjack"  # Substring in the game iframe URL

    # ── UI Coordinates (empirically determined) ─────────────────
    # These are specific to betplay.io's blackjack layout.
    # For your game: take screenshots, note coordinates, update these.

    CHIPS = {
        0.1: (388, 580),
        1:   (476, 580),
        2:   (565, 580),
        5:   (653, 580),
        10:  (741, 580),
    }

    BET_AREA = (565, 380)
    DEAL_BUTTON = (565, 320)

    # ── Betting ─────────────────────────────────────────────────

    def select_chip(self, value):
        """Select a chip denomination."""
        if value not in self.CHIPS:
            raise ValueError(f"Invalid chip. Choose from: {list(self.CHIPS.keys())}")
        self._click(*self.CHIPS[value])
        time.sleep(0.2)

    def place_bet(self, clicks=1):
        """Click the betting area. Multiple clicks = higher bet."""
        for _ in range(clicks):
            self._click(*self.BET_AREA)
            time.sleep(0.15)

    def new_bet(self):
        """Start new betting round (after a hand ends)."""
        self._click_button("new bet")
        time.sleep(0.5)

    def rebet(self):
        """Repeat last bet and auto-deal."""
        self._click_button("rebet")
        time.sleep(0.5)

    # ── Game Actions ────────────────────────────────────────────

    def deal(self):
        """Deal the cards."""
        self._click_button("deal") or self._click(*self.DEAL_BUTTON)
        time.sleep(1)

    def hit(self):
        """Request another card."""
        self._click_button("hit")
        time.sleep(0.5)

    def stand(self):
        """Keep current hand."""
        self._click_button("stand")
        time.sleep(0.5)

    def double_down(self):
        """Double the bet and take exactly one more card."""
        self._click_button("double")
        time.sleep(0.5)

    # ── State Reading ───────────────────────────────────────────

    def read_hand(self):
        """Read player and dealer totals from the DOM.
        
        Returns: {'player': int|None, 'dealer': int|None}
        
        This works by finding small numeric elements positioned in the
        dealer area (top) vs player area (bottom) of the game canvas.
        """
        result = self._eval("""
            JSON.stringify(
                Array.from(document.querySelectorAll('*')).filter(el => {
                    const text = (el.innerText || '').trim();
                    if (text && text.length <= 2 && !isNaN(text)) {
                        const val = parseInt(text);
                        if (val >= 4 && val <= 21) {
                            const rect = el.getBoundingClientRect();
                            return rect.width > 0 && rect.x > 400 && rect.x < 700
                                   && rect.y > 100 && rect.y < 400;
                        }
                    }
                    return false;
                }).map(el => {
                    const rect = el.getBoundingClientRect();
                    return {
                        val: parseInt((el.innerText || '').trim()),
                        y: Math.round(rect.y)
                    };
                })
            )
        """)

        hand = {"player": None, "dealer": None}
        if result:
            data = json.loads(result)
            dealer_totals = [t["val"] for t in data if t["y"] < 200]
            player_totals = [t["val"] for t in data if t["y"] > 200]
            if dealer_totals:
                hand["dealer"] = dealer_totals[0]
            if player_totals:
                hand["player"] = max(player_totals)
        return hand

    def get_state(self):
        """Get full game state: hand values + available actions."""
        hand = self.read_hand()
        buttons = self._find_buttons()
        return {
            "player": hand["player"],
            "dealer": hand["dealer"],
            "actions": list(buttons.keys()),
        }

    # ── Basic Strategy (optional helper) ────────────────────────

    @staticmethod
    def basic_strategy(player, dealer):
        """Simple blackjack basic strategy. Returns 'hit', 'stand', or 'double'.
        
        This is a simplified version. A real agent would use its SOUL.md personality
        to decide whether to follow strategy strictly or go with gut feeling.
        """
        if player is None or dealer is None:
            return "stand"
        if player >= 17:
            return "stand"
        if player == 11:
            return "double"
        if player == 10 and dealer <= 9:
            return "double"
        if player <= 11:
            return "hit"
        if player <= 16 and dealer >= 7:
            return "hit"
        return "stand"


# ── Example game loop ───────────────────────────────────────────

def play_one_hand(bet=1):
    """Play a single hand using basic strategy. Demonstrates the pattern."""
    with BlackjackController() as bj:
        # Bet
        bj.select_chip(bet)
        bj.place_bet()
        bj.deal()

        # Play
        while True:
            state = bj.get_state()
            print(f"Player: {state['player']} | Dealer: {state['dealer']} | Actions: {state['actions']}")

            if "hit" not in state["actions"] and "stand" not in state["actions"]:
                print("Hand over.")
                break

            action = bj.basic_strategy(state["player"], state["dealer"])
            print(f"→ {action}")

            if action == "hit":
                bj.hit()
            elif action == "double" and "double" in state["actions"]:
                bj.double_down()
            else:
                bj.stand()
                break

        bj.screenshot("/tmp/blackjack-result.png")
        print("Done. Screenshot saved.")


if __name__ == "__main__":
    play_one_hand()
