"""
Test solving su15 Level 0 with click sequences.
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
env = arcade.make("su15", seed=0)
obs = env.reset()
game = env._game

print("Goal target:", game.dsqlbvwaj)
print("Initial win check:", game.cbdhpcilgb())

# Try clicking in the launcher / bucket area
for y in range(5, 55, 5):
    for x in range(5, 55, 5):
        env.reset()
        for _ in range(5):
            obs = env.step(GameAction.ACTION6, {"x": x, "y": y})
            if game.cbdhpcilgb() or obs.levels_completed > 0:
                print(f"WIN found with click at ({x}, {y})! levels_completed={obs.levels_completed}")
                break
        if obs.levels_completed > 0:
            break
    if obs.levels_completed > 0:
        break
