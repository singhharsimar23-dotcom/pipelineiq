"""
Test moving b1 from (3, 12) up to y=6 then right to x=36.
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
env = arcade.make("ka59", seed=0)
obs = env.reset()
game = env._game

b_list = game.current_level.get_sprites_by_tag("0022vrxelxosfy")

# 1. Place Block 0 onto Target 0 at (3, 24)
env.step(GameAction.ACTION3)
env.step(GameAction.ACTION3)
env.step(GameAction.ACTION2)

# 2. Switch to Block 1 at (18, 21)
env.step(GameAction.ACTION6, data={"x": 27, "y": 30})

# 3. Path to (3, 12):
for act in [GameAction.ACTION3, GameAction.ACTION3, GameAction.ACTION1, GameAction.ACTION1, GameAction.ACTION1, GameAction.ACTION3, GameAction.ACTION3, GameAction.ACTION3]:
    env.step(act)
print(f"Reached pos: ({b_list[1].x}, {b_list[1].y})")

# Move UP from (3, 12):
for _ in range(4):
    env.step(GameAction.ACTION1)
print(f"After moving UP: ({b_list[1].x}, {b_list[1].y})")

# Move RIGHT from top corridor:
for _ in range(12):
    env.step(GameAction.ACTION4)
print(f"After moving RIGHT: ({b_list[1].x}, {b_list[1].y})")

# Move DOWN to Target 1 at (35, 17) -> needs (36, 18):
for _ in range(6):
    obs = env.step(GameAction.ACTION2)
print(f"After moving DOWN: ({b_list[1].x}, {b_list[1].y}), win={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")
