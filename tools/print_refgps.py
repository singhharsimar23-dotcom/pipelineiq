"""
Print refgps-plelvb2 pixel mask.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import numpy as np

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

s = [sp for sp in game.current_level.get_sprites() if sp.name == "refgps-plelvb2"][0]
print(f"refgps-plelvb2 shape: {s.pixels.shape}, pos=({s.x}, {s.y})")
for r in range(s.pixels.shape[0]):
    row = "".join("#" if s.pixels[r, c] != -1 else "." for c in range(s.pixels.shape[1]))
    print(f"{r + s.y:2d}: " + " "*s.x + row)
