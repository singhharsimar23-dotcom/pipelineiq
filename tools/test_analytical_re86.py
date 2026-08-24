"""
Analytical solver for re86 by matching sprite centroid to target centroid.
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

def test_analytical_re86():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    
    lvl = env._game.current_level
    target = lvl.get_sprites_by_tag("0054xnsuqceejm")[0]
    sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")

    # Let's inspect each slider's current centroid on the global canvas
    # and match it to the target's cluster centroid of that color!
    for s_idx, slider in enumerate(sliders):
        s_colors = np.unique(slider.pixels[slider.pixels != -1])
        print(f"Slider {s_idx} colors: {s_colors}")
        # Find corresponding target points of this color
        for c in s_colors:
            if c == 0:
                continue
            t_pts = np.argwhere((target.pixels == c))
            s_pts = np.argwhere((slider.pixels == c))
            
            t_center = np.mean(t_pts, axis=0) # (y, x)
            s_local_center = np.mean(s_pts, axis=0)
            s_global_center = (slider.y + s_local_center[0], slider.x + s_local_center[1])
            
            dy = t_center[0] - s_global_center[0]
            dx = t_center[1] - s_global_center[1]
            print(f"  Color {c}: Target center={t_center}, Slider global center={s_global_center}, delta=(dy={dy}, dx={dx})")
            
            # Step size in re86 is 3 pixels per action
            steps_y = int(round(dy / 3.0))
            steps_x = int(round(dx / 3.0))
            print(f"  Required moves: Y={steps_y} steps, X={steps_x} steps")

    # Let's test this exact move sequence in env!
    print("\n--- Executing Move Sequence ---")
    obs = env.reset()
    # Slider 0:
    # moves Y
    steps_y0 = -5  # dy = -15 -> 5 steps UP
    steps_x0 = -2  # dx = -6  -> 2 steps LEFT
    for _ in range(abs(steps_y0)):
        obs = env.step(GameAction.ACTION1 if steps_y0 < 0 else GameAction.ACTION2)
        print(f"Slider 0 Y-step -> levels_completed={obs.levels_completed}")
    for _ in range(abs(steps_x0)):
        obs = env.step(GameAction.ACTION3 if steps_x0 < 0 else GameAction.ACTION4)
        print(f"Slider 0 X-step -> levels_completed={obs.levels_completed}")

    # Switch to Slider 1
    obs = env.step(GameAction.ACTION5)
    print(f"Switched to Slider 1 -> levels_completed={obs.levels_completed}")

    # Slider 1:
    # dy = -20.25 -> 6/7 steps UP, dx = 11.25 -> 4 steps RIGHT
    steps_y1 = -6
    steps_x1 = 4
    for _ in range(abs(steps_y1)):
        obs = env.step(GameAction.ACTION1 if steps_y1 < 0 else GameAction.ACTION2)
        print(f"Slider 1 Y-step -> levels_completed={obs.levels_completed}")
    for _ in range(abs(steps_x1)):
        obs = env.step(GameAction.ACTION3 if steps_x1 < 0 else GameAction.ACTION4)
        print(f"Slider 1 X-step -> levels_completed={obs.levels_completed}")
    
    print(f"Final state: {obs.state}, levels_completed: {obs.levels_completed}")
    print(f"Game win check: {env._game.jeiavrvavi()}")

if __name__ == "__main__":
    test_analytical_re86()
