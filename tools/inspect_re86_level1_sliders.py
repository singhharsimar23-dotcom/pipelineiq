"""
Inspect Slider 0 in Level 1 of re86.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

def inspect_level1_sliders():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    
    # Clear Level 0
    for _ in range(7): env.step(GameAction.ACTION1)
    for _ in range(4): env.step(GameAction.ACTION4)
    env.step(GameAction.ACTION5)
    for _ in range(6): env.step(GameAction.ACTION1)
    for _ in range(2): env.step(GameAction.ACTION3)
    
    lvl = env._game.current_level
    sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")
    targets = lvl.get_sprites_by_tag("0054xnsuqceejm")[0]

    print(f"Level 1 has {len(sliders)} sliders:")
    for i, s in enumerate(sliders):
        pts = np.argwhere((s.pixels != -1) & (s.pixels != 0))
        color = s.pixels[pts[0][0], pts[0][1]]
        print(f"\nSlider {i}: pos=(x={s.x}, y={s.y}), size={s.pixels.shape}, color={color}")
        print(f"Non-empty points count: {len(pts)}")
        # Print shape of points
        r_vals, r_cnts = np.unique(pts[:, 0], return_counts=True)
        c_vals, c_cnts = np.unique(pts[:, 1], return_counts=True)
        print(f"Rows with counts >= 2: {r_vals[r_cnts >= 2]}")
        print(f"Cols with counts >= 2: {c_vals[c_cnts >= 2]}")
        center_y = s.height // 2
        center_x = s.width // 2
        print(f"Geometric center: ({center_y}, {center_x}) -> global: (y={s.y + center_y}, x={s.x + center_x})")

    print("\nTarget Points per color in Level 1:")
    for c in [9, 12, 13]:
        t_pts = np.argwhere(targets.pixels == c)
        print(f"Color {c}: points={t_pts.tolist()}")

if __name__ == "__main__":
    inspect_level1_sliders()
