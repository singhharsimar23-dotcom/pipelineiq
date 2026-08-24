"""
Generalized dynamic visual solver for re86 across all levels and seeds.
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

def solve_re86_dynamic(env, max_levels=8):
    obs = env.reset()
    level = 0
    total_steps = 0
    
    while level < max_levels:
        f = np.array(obs.frame[0])
        # Background color
        vals, counts = np.unique(f, return_counts=True)
        bg = vals[np.argmax(counts)]
        
        # Colors present (excluding bg, border, and black dot)
        slider_colors = [c for c in vals if c not in (bg, 0, 4, 15)]
        print(f"\n[Level {level}] Slider colors found: {slider_colors}")
        
        # For each slider color:
        # 1. Target diamond points: points of this color that are isolated (not part of the continuous cross line)
        # Or simply: the cross line is a continuous segment.
        # Let's find cross line:
        # Cross horizontal line has many adjacent horizontal pixels of this color
        # Cross vertical line has many adjacent vertical pixels of this color
        
        # Let's determine the active slider:
        # The slider with a center black pixel (0) at its intersection
        # Find which color has black pixel (0) at its cross intersection:
        black_pts = np.argwhere(f == 0)
        
        # Plan moves for each slider
        slider_plans = []
        for color in slider_colors:
            pts = np.argwhere(f == color)
            # Row counts and Col counts of this color
            rows, r_counts = np.unique(pts[:, 0], return_counts=True)
            cols, c_counts = np.unique(pts[:, 1], return_counts=True)
            
            # The cross line row has the maximum count of this color
            cross_y = rows[np.argmax(r_counts)]
            cross_x = cols[np.argmax(c_counts)]
            
            # The target points are the 4 diamond points
            # They are at min_y, max_y on cross_x, and min_x, max_x on cross_y?
            # No, the target diamond points are points of this color NOT on the current cross line!
            target_pts = pts[(pts[:, 0] != cross_y) & (pts[:, 1] != cross_x)]
            if len(target_pts) == 0:
                # Target diamond might share row/col or be the endpoints of the diamond
                # The diamond bounding box:
                # Top, bottom points have same X
                # Left, right points have same Y
                # Let's find all points of this color outside the cross bounding box or with small counts:
                target_pts = pts[pts[:, 0] != cross_y]
            
            # If target points are isolated:
            # Diamond center is mean of target_pts
            if len(target_pts) > 0:
                target_y = int(round(np.mean(target_pts[:, 0])))
                target_x = int(round(np.mean(target_pts[:, 1])))
            else:
                target_y, target_x = cross_y, cross_x
            
            dy = target_y - cross_y
            dx = target_x - cross_x
            
            steps_y = int(round(dy / 3.0))
            steps_x = int(round(dx / 3.0))
            print(f"  Color {color}: cross at ({cross_y}, {cross_x}), target at ({target_y}, {target_x}) -> dy={steps_y} steps, dx={steps_x} steps")
            
            # Check if this slider is currently active (has a black dot at (cross_y, cross_x))
            is_active = any(abs(bp[0] - cross_y) <= 1 and abs(bp[1] - cross_x) <= 1 for bp in black_pts)
            slider_plans.append({
                "color": color,
                "is_active": is_active,
                "steps_y": steps_y,
                "steps_x": steps_x
            })

        # Order sliders: active slider first!
        slider_plans.sort(key=lambda sp: not sp["is_active"])
        
        # Execute plans with ACTION5 between sliders
        for idx, plan in enumerate(slider_plans):
            if idx > 0:
                obs = env.step(GameAction.ACTION5)
                total_steps += 1
            
            sy = plan["steps_y"]
            sx = plan["steps_x"]
            for _ in range(abs(sy)):
                obs = env.step(GameAction.ACTION1 if sy < 0 else GameAction.ACTION2)
                total_steps += 1
            for _ in range(abs(sx)):
                obs = env.step(GameAction.ACTION3 if sx < 0 else GameAction.ACTION4)
                total_steps += 1
        
        print(f"Level {level} execution finished: levels_completed={obs.levels_completed}")
        if obs.levels_completed > level:
            level = obs.levels_completed
            print(f"*** ADVANCED TO LEVEL {level} (total steps: {total_steps}) ***")
        else:
            print(f"Level {level} failed to advance.")
            break
            
        if obs.state == GameState.WIN or obs.state == GameState.GAME_OVER:
            break

    print(f"\nFinal result: levels cleared = {obs.levels_completed}, total steps = {total_steps}")
    return obs.levels_completed

def verify_multi_seeds():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    for seed in range(5):
        print(f"\n================ SEED {seed} ================")
        env = arcade.make("re86", seed=seed)
        cleared = solve_re86_dynamic(env)
        print(f"Seed {seed} result: {cleared} levels cleared.")

if __name__ == "__main__":
    verify_multi_seeds()
