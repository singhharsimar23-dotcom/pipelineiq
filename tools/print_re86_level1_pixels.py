"""
Print exact pixel maps of sliders in Level 1 of re86.
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

def print_slider_pixels():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    
    # Solve Level 0:
    for _ in range(7): env.step(GameAction.ACTION1)
    for _ in range(4): env.step(GameAction.ACTION4)
    env.step(GameAction.ACTION5)
    for _ in range(6): env.step(GameAction.ACTION1)
    for _ in range(2): env.step(GameAction.ACTION3)
    
    lvl = env._game.current_level
    sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")
    
    for i, s in enumerate(sliders):
        print(f"\n--- Slider {i} (shape {s.pixels.shape}) ---")
        for r in range(s.height):
            row_str = "".join([f"{val:2d}" if val != -1 else " ." for val in s.pixels[r]])
            if any(val != -1 for val in s.pixels[r]):
                print(f"Row {r:2d}: {row_str}")

if __name__ == "__main__":
    print_slider_pixels()
