"""
Debug collision check on 2nd ACTION4 in m0r0.
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
env = arcade.make("m0r0", seed=0)
obs = env.reset()
game = env._game

s1 = game.current_level.get_sprites_by_name("pikgci-toljda-leklkn")[0]
s2 = game.current_level.get_sprites_by_name("pikgci-toljda-rivmdg")[0]
walls = game.current_level.get_sprites_by_tag("wahtyt")[0]

print(f"Initial: s1=({s1.x}, {s1.y}), s2=({s2.x}, {s2.y})")

# Step 1: ACTION4
obs = env.step(GameAction.ACTION4)
print(f"Step 1: s1=({s1.x}, {s1.y}), s2=({s2.x}, {s2.y})")

# Check manual move to (5, 9)
s1.move(1, 0)
print(f"Manual move s1 to (5, 9): collides with walls = {s1.collides_with(walls)}")
s1.move(-1, 0) # revert

s2.move(-1, 0)
print(f"Manual move s2 to (5, 9): collides with walls = {s2.collides_with(walls)}")
s2.move(1, 0) # revert
