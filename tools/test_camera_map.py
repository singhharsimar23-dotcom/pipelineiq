"""
Inspect camera mapping in ka59.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ka59", seed=0)
obs = env.reset()
game = env._game

for dy in range(0, 64, 8):
    for dx in range(0, 64, 8):
        grid_pos = game.camera.display_to_grid(dx, dy)
        if grid_pos:
            s = game.current_level.get_sprite_at(grid_pos[0], grid_pos[1], "0022vrxelxosfy")
            if s:
                print(f"Block at grid {grid_pos} reached by clicking display ({dx}, {dy})")
