"""
Print maze_sprite pixels in tu93.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("tu93", seed=0)
obs = env.reset()
game = env._game

maze = game.current_level.get_sprites_by_tag("0005uvnhiglpvh")[0]
print("Maze shape:", maze.pixels.shape)
for r in range(0, maze.pixels.shape[0], 3):
    row_str = "".join([f"{maze.pixels[r, c]:2d} " for c in range(0, maze.pixels.shape[1], 3)])
    print(f"r={r:2d}: {row_str}")
