"""
Print the full maze layout of 0028lydaygyjbu.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ka59", seed=0)
obs = env.reset()
game = env._game

boundary = game.current_level.get_sprites_by_tag("0029ifoxxfvvvs")[0]
grid = boundary.pixels
print(f"Boundary shape: {grid.shape}, pos=({boundary.x}, {boundary.y})")

for r in range(0, grid.shape[0], 3):
    row_chars = []
    for c in range(0, grid.shape[1], 3):
        cell = grid[r:r+3, c:c+3]
        if np.all(cell == -1):
            row_chars.append(".")
        elif np.all(cell != -1):
            row_chars.append("#")
        else:
            row_chars.append("?")
    print(f"y={r + boundary.y:2d}: {''.join(row_chars)}")
