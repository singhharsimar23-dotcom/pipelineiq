"""
Test active slider mechanics in re86.
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

def test_active_slider():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    game = env._game

    sliders = game.current_level.get_sprites_by_tag("0031cppcuvqlbi")
    for i, s in enumerate(sliders):
        center_val = s.pixels[s.height // 2, s.width // 2]
        print(f"Slider {i}: name={s.name}, center_pixel={center_val}")

    print("\nMoving active slider (Slider 1) UP with ACTION1...")
    env.step(GameAction.ACTION1)
    for i, s in enumerate(sliders):
        center_val = s.pixels[s.height // 2, s.width // 2]
        print(f"Slider {i}: name={s.name}, center_pixel={center_val}")
    
    # Check non-empty pixels of slider 1
    s1 = sliders[1]
    pts = np.argwhere(s1.pixels == 9)
    print(f"Slider 1 color 9 points after ACTION1:\n{pts}")

if __name__ == "__main__":
    test_active_slider()
