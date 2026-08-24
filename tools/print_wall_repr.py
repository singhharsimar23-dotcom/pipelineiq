"""
Print non-negative pixels of 0028lydaygyjbu.
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
env = arcade.make("ka59", seed=0)
obs = env.reset()
game = env._game

s = [sp for sp in game.current_level.get_sprites() if sp.name == "0028lydaygyjbu"][0]
print(f"Wall pos: ({s.x}, {s.y}), shape: {s.pixels.shape}")
solid = (s.pixels != -1)
print(f"Solid count: {np.sum(solid)}")

# Print 2D representation
for r in range(s.pixels.shape[0]):
    row = "".join("#" if s.pixels[r, c] != -1 else "." for c in range(s.pixels.shape[1]))
    print(f"{r-3:2d}: {row}")
