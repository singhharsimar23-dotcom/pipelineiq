"""
Inspect re86 frame regions, target template, and slider movements.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def analyze_re86():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    f = np.array(obs.frame[0])

    lvl = env._game.current_level
    target = lvl.get_sprites_by_tag("0054xnsuqceejm")[0]
    sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")

    print(f"Target sprite shape: {target.pixels.shape}")
    t_mask = (target.pixels != -1) & (target.pixels != 4)
    print(f"Target non-4 non-(-1) pixels: {np.sum(t_mask)}")
    print(f"Target bounding box: y=[{np.min(np.where(t_mask)[0])}, {np.max(np.where(t_mask)[0])}], x=[{np.min(np.where(t_mask)[1])}, {np.max(np.where(t_mask)[1])}]")
    
    # Check if target is visible in f directly
    for y in range(0, 64 - 10):
        for x in range(0, 64 - 10):
            # check small patch matching
            pass

    # Print where target pixels are located
    t_coords = np.argwhere(t_mask)
    print(f"Target coordinates and colors (first 10):")
    for r, c in t_coords[:10]:
        print(f"  ({r}, {c}) -> color {target.pixels[r, c]}")

    # Let's inspect slider movement steps
    print("\n--- Testing Slider Positions vs Movements ---")
    for s_idx in range(len(sliders)):
        print(f"\nTesting slider {s_idx}:")
        env.reset()
        # cycle to slider s_idx
        for _ in range(s_idx):
            env.step(GameAction.ACTION5)
        
        for move_act in [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]:
            env.reset()
            for _ in range(s_idx):
                env.step(GameAction.ACTION5)
            s_before = (sliders[s_idx].x, sliders[s_idx].y)
            env.step(move_act)
            s_after = (sliders[s_idx].x, sliders[s_idx].y)
            print(f"  {move_act.name}: pos {s_before} -> {s_after}")

if __name__ == "__main__":
    analyze_re86()
