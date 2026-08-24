"""
Inspect re86 Level 1 sprites and mechanics.
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

def inspect_level1():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    
    # Solve Level 0
    # 7 UP, 4 RIGHT on S1, ACTION5, 6 UP, 2 LEFT on S0
    for _ in range(7):
        obs = env.step(GameAction.ACTION1)
    for _ in range(4):
        obs = env.step(GameAction.ACTION4)
    obs = env.step(GameAction.ACTION5)
    for _ in range(6):
        obs = env.step(GameAction.ACTION1)
    for _ in range(2):
        obs = env.step(GameAction.ACTION3)
    
    print(f"Reached Level 1: levels_completed={obs.levels_completed}")
    f = np.array(obs.frame[0])
    print(f"Level 1 frame unique colors: {np.unique(f)}")

    lvl = env._game.current_level
    print(f"Level 1 name: {lvl.name}")
    
    targets = lvl.get_sprites_by_tag("0054xnsuqceejm")
    sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")
    wells = lvl.get_sprites_by_tag("0007dtbisvazhv")

    print(f"Target count: {len(targets)}")
    for i, t in enumerate(targets):
        valid = t.pixels[(t.pixels != -1) & (t.pixels != 4)]
        print(f"  Target {i}: non-empty={len(valid)}, colors={np.unique(valid)}")
        pts = np.argwhere((t.pixels != -1) & (t.pixels != 4))
        for r, c in pts:
            print(f"    ({r}, {c}) -> {t.pixels[r, c]}")

    print(f"Sliders count: {len(sliders)}")
    for i, s in enumerate(sliders):
        valid = s.pixels[s.pixels != -1]
        print(f"  Slider {i}: pos=({s.x},{s.y}) size={s.pixels.shape} colors={np.unique(valid)}")

    print(f"Wells count: {len(wells)}")
    for i, w in enumerate(wells):
        valid = w.pixels[w.pixels != -1]
        print(f"  Well {i}: pos=({w.x},{w.y}) size={w.pixels.shape} colors={np.unique(valid)}")

if __name__ == "__main__":
    inspect_level1()
