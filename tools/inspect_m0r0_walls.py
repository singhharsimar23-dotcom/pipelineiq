"""
Inspect m0r0 Level 0 wall grid.
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
env = arcade.make("m0r0", seed=0)
obs = env.reset()
game = env._game

walls = game.current_level.get_sprites_by_tag("wahtyt")[0]
grid = np.array(walls.pixels)
print("=== WALL GRID (0=wall, -1=empty) ===")
for r in range(grid.shape[0]):
    row_str = "".join(["#" if c != -1 else "." for c in grid[r]])
    print(f"Row {r:2d}: {row_str}")

# Also check other obstacles (like mosdlc placed block, gayktr, etc.)
for tag in ["xbso", "spswjz"]:
    items = game.current_level.get_sprites_by_tag(tag)
    print(f"Tag {tag}: {[(s.name, s.x, s.y) for s in items]}")
