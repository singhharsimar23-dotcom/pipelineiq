"""
Inspect move Right at (10, 20) in dc22.
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

btn_a_disp = (48, 19)
btn_b_disp = (48, 36)

# Click button b and button a
env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})
env.step(GameAction.ACTION6, data={"x": btn_a_disp[0], "y": btn_a_disp[1]})

# Walk Up to (10, 20)
for _ in range(5):
    env.step(GameAction.ACTION1)
print(f"Avatar pos: ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y})")

# Try move Right
colls = game.try_move_sprite(game.qnnpcoyzd, 2, 0)
print(f"try_move_sprite(2, 0) colls: {[c.name for c in colls] if colls else []}")
if colls:
    for c in colls:
        print(f"  Collided with: name={c.name}, tags={c.tags}, interaction={c.interaction}")
else:
    w = game.sxnzvaqltp(game.qnnpcoyzd.x, game.qnnpcoyzd.y, game.qnnpcoyzd)
    print(f"Walkable sprite at new pos: {getattr(w, 'name', None)}")
