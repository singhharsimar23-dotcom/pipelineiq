"""
Inspect walkable coordinates on tovemc-plelvb1.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
import numpy as np

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

btn_b_disp = (48, 36)

# Click button b
env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})

# Check sxnzvaqltp for tovemc-plelvb1
s = [sp for sp in game.current_level.get_sprites() if sp.name == "tovemc-plelvb1"][0]
print(f"tovemc-plelvb1 pos: ({s.x}, {s.y}), size: ({s.width}, {s.height}), tags: {s.tags}, interaction: {s.interaction}")

for y in range(20, 28, 2):
    for x in range(6, 14, 2):
        w = game.sxnzvaqltp(x, y, game.qnnpcoyzd)
        print(f"  Pos ({x}, {y}) -> walkable sprite: {getattr(w, 'name', None)}")
