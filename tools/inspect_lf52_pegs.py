"""
Inspect screen display positions of pegs in lf52 Level 0.
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
env = arcade.make("lf52", seed=0)
obs = env.reset()
game = env._game
world = game.ikhhdzfmarl

# List all peg objects and their absolute screen coordinates
pegs = world.hncnfaqaddg.ndtvadsrqf("fozwvlovdui")
print("=== PEGS IN LF52 ===")
for p in pegs:
    # Get absolute render position
    gx, gy = p.chahdtpdoz
    # world.hncnfaqaddg position
    ox, oy = world.hncnfaqaddg.cdpcbbnfdp
    # Screen coord = (gx * 6 + ox, gy * 6 + oy) or p.x, p.y
    print(f"Peg: name={p.name}, grid=({gx}, {gy}), screen=({p.x}, {p.y})")
