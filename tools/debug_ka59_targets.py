"""
Debug ka59 exact block and target match.
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

print(f"Initial: t0=({t0.x}, {t0.y}), t1=({t1.x}, {t1.y}), b0=({b_list[0].x}, {b_list[0].y}), b1=({b_list[1].x}, {b_list[1].y})")

# Move Block 0
env.step(GameAction.ACTION3)
env.step(GameAction.ACTION3)
env.step(GameAction.ACTION2)
print(f"After b0 moves: b0=({b_list[0].x}, {b_list[0].y}), matches t0={b_list[0].x == t0.x + 1 and b_list[0].y == t0.y + 1}")

# Switch to b1
env.step(GameAction.ACTION6, data={"x": 27, "y": 30})
print(f"After switch: active block is at ({game.prkgpeyexo.x}, {game.prkgpeyexo.y})")

for _ in range(5):
    env.step(GameAction.ACTION4)
env.step(GameAction.ACTION1)
obs = env.step(GameAction.ACTION4)

print(f"After b1 moves: b1=({b_list[1].x}, {b_list[1].y}), matches t1={b_list[1].x == t1.x + 1 and b_list[1].y == t1.y + 1}")
print(f"Target 0 check: {b_list[0].x == t0.x + 1, b_list[0].y == t0.y + 1, t0.x, t0.y, b_list[0].x, b_list[0].y}")
print(f"Target 1 check: {b_list[1].x == t1.x + 1, b_list[1].y == t1.y + 1, t1.x, t1.y, b_list[1].x, b_list[1].y}")
print(f"Final game.dbmlcqbquh() = {game.dbmlcqbquh()}")
