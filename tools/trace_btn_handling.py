"""
Trace button click handling in dc22.
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

btn_a = (48, 9)
btn_b = (48, 26)

# Test clicking button b directly
ddowbgsdjo = game.camera.display_to_grid(btn_b[0], btn_b[1])
print(f"Display (48, 26) -> grid: {ddowbgsdjo}")
if ddowbgsdjo:
    gx, gy = ddowbgsdjo
    btn = game.xodizggcom(gx, gy, "buezna")
    print(f"Found button buezna: {getattr(btn, 'name', None)}")
    if btn:
        tag = next((t for t in btn.tags if len(t) == 1), None)
        print(f"Button tag: {tag}")
        sprites_affected = game.ilvrmetiiv(tag, btn)
        print(f"Sprites affected: {[s.name for s in sprites_affected]}")
