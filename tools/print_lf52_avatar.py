"""
Print avatar location and all entity names in lf52 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("lf52", seed=0)
obs = env.reset()
game = env._game
world = game.ikhhdzfmarl

print("All items on grid:")
for y in range(world.hncnfaqaddg.grid_size[1]):
    for x in range(world.hncnfaqaddg.grid_size[0]):
        items = [i.name for i in world.hncnfaqaddg.ijpoqzvnjt(x, y)]
        if items:
            print(f"  Cell ({x}, {y}): {items}")
