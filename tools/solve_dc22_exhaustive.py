"""
DC22 - systematic exploration of every click sequence + nav to find win.
Uses the actual env to test paths (not BFS re-instantiation).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

def try_path(seed, clicks, nav_actions):
    """Apply clicks then nav actions, return (levels_completed, player_pos)."""
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=seed)
    obs = env.reset()
    game = env._game
    
    sys_clicks = game.current_level.get_sprites_by_tag("sys_click")
    # Sort by tag name
    button_a = next(s for s in sys_clicks if 'a' in s.tags)
    button_b = next(s for s in sys_clicks if 'b' in s.tags)
    buttons = {'a': button_a, 'b': button_b}
    
    for c in clicks:
        btn = buttons[c]
        obs = env.step(GameAction.ACTION6, {"x": btn.x + 5, "y": btn.y + 2})
    
    for act in nav_actions:
        obs = env.step(act)
        if game.smxyfelexa() or obs.levels_completed > 0:
            return obs.levels_completed, (game.qnnpcoyzd.x, game.qnnpcoyzd.y)
    
    return obs.levels_completed, (game.qnnpcoyzd.x, game.qnnpcoyzd.y)

# Try: 0,1,2 button a presses, then different nav sequences
from itertools import product

U = GameAction.ACTION1
D = GameAction.ACTION2
L = GameAction.ACTION3
R = GameAction.ACTION4

# Goal: player at (10,30) needs to reach goal at (24,10)
# dx = +14, dy = -20 from start, moving in steps of 2

# Candidate nav sequences
candidates = [
    # No clicks: direct path
    ([U]*10 + [R]*7, "0clicks"),
    ([R]*7 + [U]*10, "0clicks-R-first"),
    # After click a: try paths
    ([U]*10 + [R]*7, "1click-a"),
    ([R]*7 + [U]*10, "1click-a-R-first"),
    ([U]*2 + [R]*2 + [U]*2 + [R]*2 + [U]*2 + [R]*2 + [U]*2 + [R]*1, "1click-a-zigzag"),
    # After click b  
    ([U]*10 + [R]*7, "1click-b"),
    ([R]*7 + [U]*10, "1click-b-R-first"),
    ([U]*5 + [R]*5 + [U]*5 + [R]*2, "1click-b-zigzag"),
    # After click a then b
    ([U]*10 + [R]*7, "2clicks-ab"),
    ([R]*7 + [U]*10, "2clicks-ab-R-first"),
    # After b then a
    ([U]*10 + [R]*7, "2clicks-ba"),
    ([R]*7 + [U]*10, "2clicks-ba-R-first"),
    # After 2x a  
    ([U]*10 + [R]*7, "2clicks-aa"),
    ([U]*5 + [R]*3 + [U]*5 + [R]*4, "2clicks-aa-mid"),
]

click_combos = {
    "0clicks": [],
    "1click-a": ['a'],
    "1click-a-R-first": ['a'],
    "1click-b": ['b'],
    "1click-b-R-first": ['b'],
    "1click-b-zigzag": ['b'],
    "2clicks-ab": ['a','b'],
    "2clicks-ab-R-first": ['a','b'],
    "2clicks-ba": ['b','a'],
    "2clicks-ba-R-first": ['b','a'],
    "2clicks-aa": ['a','a'],
    "2clicks-aa-mid": ['a','a'],
    "1click-a-zigzag": ['a'],
}

print("Testing dc22 seed 0 click+nav combos:")
for nav, label in candidates:
    clicks = click_combos.get(label, [])
    lvl, pos = try_path(0, clicks, nav)
    print(f"  [{label}] clicks={clicks}, nav_len={len(nav)}: pos={pos}, lvl={lvl}")
    if lvl > 0:
        print(f"  *** SOLUTION FOUND: [{label}] ***")
        break
