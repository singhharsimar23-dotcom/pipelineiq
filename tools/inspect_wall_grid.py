"""
Inspect wall sprite coordinates and pixel value at (5, 9).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("m0r0", seed=0)
obs = env.reset()
game = env._game

walls = game.current_level.get_sprites_by_tag("wahtyt")[0]
print(f"walls: pos=(x={walls.x}, y={walls.y}), shape={walls.pixels.shape}")

# For (x=5, y=9):
rx = 5 - walls.x
ry = 9 - walls.y
print(f"At (5, 9): relative pos=(ry={ry}, rx={rx}), pixel value = {walls.pixels[ry, rx]}")

# Print entire walls grid with row indices and column indices
for r in range(walls.pixels.shape[0]):
    print(f"Row {r:2d} (y={r + walls.y:2d}): {[int(v) for v in walls.pixels[r]]}")
