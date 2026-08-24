"""
Test path around obstacle for Block 1 in ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ka59", seed=0)
obs = env.reset()
game = env._game

t0 = game.current_level.get_sprites_by_tag("0010xzmuziohuf")[0]
t1 = game.current_level.get_sprites_by_tag("0010xzmuziohuf")[1]
b_list = game.current_level.get_sprites_by_tag("0022vrxelxosfy")

# 1. Place Block 0 onto Target 0 at (3, 24)
env.step(GameAction.ACTION3)
env.step(GameAction.ACTION3)
env.step(GameAction.ACTION2)

# 2. Switch to Block 1 at (18, 21)
env.step(GameAction.ACTION6, data={"x": 27, "y": 30})

# 3. Move Block 1 around wall:
# Up x4: (18, 21) -> (18, 9)
for _ in range(4):
    env.step(GameAction.ACTION1)
print(f"After moving Up: b1=({b_list[1].x}, {b_list[1].y})")

# Right x6: (18, 9) -> (36, 9)
for _ in range(6):
    env.step(GameAction.ACTION4)
print(f"After moving Right: b1=({b_list[1].x}, {b_list[1].y})")

# Down x3: (36, 9) -> (36, 18) [Target 1 at (35, 17) -> needs (36, 18)]
for _ in range(3):
    obs = env.step(GameAction.ACTION2)
print(f"After moving Down: b1=({b_list[1].x}, {b_list[1].y}), win={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")
