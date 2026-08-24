"""
Inspect 0028lydaygyjbu pixels in ka59.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import numpy as np

def inspect_walls():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    for s in game.current_level.get_sprites():
        if "ifoxxfvvvs" in s.tags or "qniapgwsvb" in s.tags:
            print(f"Wall/Gate sprite: name={s.name}, pos=({s.x}, {s.y}), size=({s.width}, {s.height})")
            # Print non-negative pixel locations
            solid_pts = np.argwhere(s.pixels != -1)
            print(f"  Solid pixels count: {len(solid_pts)}")
            # World bounding box of solid pixels:
            min_r = s.y + np.min(solid_pts[:, 0])
            max_r = s.y + np.max(solid_pts[:, 0])
            min_c = s.x + np.min(solid_pts[:, 1])
            max_c = s.x + np.max(solid_pts[:, 1])
            print(f"  World bounds of solid pixels: x in [{min_c}, {max_c}], y in [{min_r}, {max_r}]")

if __name__ == "__main__":
    inspect_walls()
