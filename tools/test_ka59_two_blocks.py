"""
Test moving block 0 onto target 0 in ka59 Level 0.
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

print("Target 0:", (game.current_level.get_sprites_by_tag("0010xzmuziohuf")[0].x, game.current_level.get_sprites_by_tag("0010xzmuziohuf")[0].y))
print("Target 1:", (game.current_level.get_sprites_by_tag("0010xzmuziohuf")[1].x, game.current_level.get_sprites_by_tag("0010xzmuziohuf")[1].y))

# Move Left twice from (9, 21) -> (3, 21)
env.step(GameAction.ACTION3)
env.step(GameAction.ACTION3)

# Move Down once: (3, 21) -> (3, 24)
obs = env.step(GameAction.ACTION2)
print(f"After move down: pos=({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win={game.dbmlcqbquh()}")

# Now switch to Block 1 at (18, 21)
# Grid (18, 21) in display coords:
display_pos = game.camera.grid_to_display(18, 21)
print(f"Block 1 display pos: {display_pos}")
obs = env.step(GameAction.ACTION6, data={"x": display_pos[0], "y": display_pos[1]})
print(f"After switch active block: pos=({game.prkgpeyexo.x}, {game.prkgpeyexo.y})")

# Move Block 1 towards Target 1 at (35, 17)
# (18, 21) -> Right x5 -> (33, 21) -> Up x1 -> (33, 18)
for _ in range(5):
    env.step(GameAction.ACTION4)
obs = env.step(GameAction.ACTION1)
print(f"After move to Target 1: pos=({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")
