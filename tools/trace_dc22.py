"""
DC22 deeper investigation: trace player movement step by step.
Player starts at (10,30), goal at (24,10).
Check if buttons change the bridge/map before trying to navigate.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

px0, py0 = game.qnnpcoyzd.x, game.qnnpcoyzd.y
gx, gy = game.hfuqkxulm.x, game.hfuqkxulm.y
print(f"Player=({px0},{py0}), Goal=({gx},{gy})")

# Click each button and observe changes
sys_clicks = game.current_level.get_sprites_by_tag("sys_click")
print(f"Available sys_click sprites: {[(s.name, s.tags, s.x, s.y) for s in sys_clicks]}")

# Try clicking button 'a' (top)
button_a = [s for s in sys_clicks if 'a' in s.tags and 'b' not in s.tags][0]
button_b = [s for s in sys_clicks if 'b' in s.tags and 'a' not in s.tags][0]

cx_a = button_a.x + button_a.width // 2
cy_a = button_a.y + button_a.height // 2

cx_b = button_b.x + button_b.width // 2
cy_b = button_b.y + button_b.height // 2

# Try pressing button A (opens row a)
print(f"\nClicking button A at ({cx_a},{cy_a})")
obs = env.step(GameAction.ACTION6, {"x": cx_a, "y": cy_a})
print(f"After A: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y}), win={game.smxyfelexa()}")

# Now try moving toward goal (up 10, right 7)
moves_up = [(0, -2, GameAction.ACTION1)] * 10
moves_right = [(2, 0, GameAction.ACTION4)] * 7

for dx, dy, act in moves_up + moves_right:
    obs = env.step(act)
    print(f"  Move ({dx},{dy}): player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y}), win={game.smxyfelexa()}, lvl={obs.levels_completed}")
    if game.smxyfelexa() or obs.levels_completed > 0:
        print("WIN!")
        break
