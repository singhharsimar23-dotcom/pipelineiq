"""
Test 2D movement of active object in ar25.
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
env = arcade.make("ar25", seed=0)
obs = env.reset()
game = env._game

found = False
for dy in range(-10, 15):
    for dx in range(-10, 15):
        env.reset()
        # dy: ACTION1 (up, dy<0), ACTION2 (down, dy>0)
        # dx: ACTION3 (left, dx<0), ACTION4 (right, dx>0)
        act_y = GameAction.ACTION1 if dy < 0 else GameAction.ACTION2
        for _ in range(abs(dy)):
            env.step(act_y)
        act_x = GameAction.ACTION3 if dx < 0 else GameAction.ACTION4
        for _ in range(abs(dx)):
            obs = env.step(act_x)
        if game.vplrhaovhr() or obs.levels_completed > 0:
            print(f"WIN found with dx={dx}, dy={dy}! levels_completed={obs.levels_completed}")
            found = True
            break
    if found:
        break

if not found:
    print("No simple (dx, dy) win found.")
