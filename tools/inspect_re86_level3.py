"""
Inspect Level 3 of re86 (Color Wells mechanic).
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

def inspect_level3():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    
    # Solve Level 0:
    for _ in range(7): env.step(GameAction.ACTION1)
    for _ in range(4): env.step(GameAction.ACTION4)
    env.step(GameAction.ACTION5)
    for _ in range(6): env.step(GameAction.ACTION1)
    for _ in range(2): env.step(GameAction.ACTION3)

    # Solve Level 1:
    for _ in range(10): env.step(GameAction.ACTION2)
    for _ in range(3): env.step(GameAction.ACTION3)
    env.step(GameAction.ACTION5)
    for _ in range(7): env.step(GameAction.ACTION1)
    for _ in range(7): env.step(GameAction.ACTION3)
    env.step(GameAction.ACTION5)
    for _ in range(2): env.step(GameAction.ACTION2)
    for _ in range(7): env.step(GameAction.ACTION3)

    # Solve Level 2:
    for _ in range(13): env.step(GameAction.ACTION1)
    for _ in range(2): env.step(GameAction.ACTION3)
    env.step(GameAction.ACTION5)
    for _ in range(8): env.step(GameAction.ACTION1)
    for _ in range(8): env.step(GameAction.ACTION4)
    env.step(GameAction.ACTION5)
    for _ in range(6): env.step(GameAction.ACTION1)
    for _ in range(9): obs = env.step(GameAction.ACTION3)

    print(f"Reached Level 3: levels_completed={obs.levels_completed}")
    lvl = env._game.current_level
    targets = lvl.get_sprites_by_tag("0054xnsuqceejm")[0]
    sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")
    wells = lvl.get_sprites_by_tag("0007dtbisvazhv")

    print(f"\nTarget non-empty pixels:")
    t_mask = (targets.pixels != -1) & (targets.pixels != 4)
    t_colors = np.unique(targets.pixels[t_mask])
    print(f"Target colors: {t_colors}")
    for c in t_colors:
        pts = np.argwhere(targets.pixels == c)
        print(f"  Color {c} points ({len(pts)}): {pts.tolist()}")

    print(f"\nSliders in Level 3 ({len(sliders)}):")
    for i, s in enumerate(sliders):
        pts = np.argwhere((s.pixels != -1) & (s.pixels != 0))
        color = s.pixels[pts[0][0], pts[0][1]]
        print(f"  Slider {i}: pos=({s.x},{s.y}) size={s.pixels.shape} color={color}")

    print(f"\nWells in Level 3 ({len(wells)}):")
    for i, w in enumerate(wells):
        pts = np.argwhere(w.pixels != -1)
        color = w.pixels[pts[0][0], pts[0][1]]
        print(f"  Well {i}: pos=({w.x},{w.y}) size={w.pixels.shape} color={color}")

if __name__ == "__main__":
    inspect_level3()
