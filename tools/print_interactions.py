"""
Print all intangible sprites after button clicks in dc22.
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

# Click button a and button b
env.step(GameAction.ACTION6, data={"x": btn_a_disp[0], "y": btn_a_disp[1]})
env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})

print("=== INTANGIBLE SPRITES AFTER A + B ===")
for s in game.current_level.get_sprites():
    print(f"Sprite: name={s.name}, pos=({s.x}, {s.y}), size=({s.width}, {s.height}), interaction={s.interaction}")
