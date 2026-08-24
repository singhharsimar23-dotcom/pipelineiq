"""
Multi-Level Dynamic Solver for re86.
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

def solve_re86_all_levels(env):
    obs = env.reset()
    level = 0
    total_steps = 0
    
    while True:
        f = np.array(obs.frame[0])
        vals, counts = np.unique(f, return_counts=True)
        bg = vals[np.argmax(counts)]
        
        # In re86, step counter and borders use colors 4, 15, 1, bg, 0
        # Sliders are colors that form cross lines or targets
        # Let's inspect unique colors in frame
        candidate_colors = [c for c in vals if c not in (bg, 0, 4, 15, 1)]
        print(f"\n================ LEVEL {level} ================")
        print(f"Colors detected: {candidate_colors}")
        
        # Find all sliders and target points from frame
        black_pts = np.argwhere(f == 0)
        
        plans = []
        for color in candidate_colors:
            pts = np.argwhere(f == color)
            if len(pts) < 4:
                continue
            
            # Find cross intersection: row and column with highest count of this color
            rows, r_counts = np.unique(pts[:, 0], return_counts=True)
            cols, c_counts = np.unique(pts[:, 1], return_counts=True)
            
            cross_y = rows[np.argmax(r_counts)]
            cross_x = cols[np.argmax(c_counts)]
            
            # Find target points: points of this color
            # The target cross center:
            # Look at target points that have same X (top/bottom of diamond)
            # and target points that have same Y (left/right of diamond)
            # If we group target points:
            # Target X is the vertical line's X: the X coordinate that appears more than once, or the median X
            # Target Y is the horizontal line's Y: the Y coordinate that appears more than once, or the median Y
            
            # Extract the diamond points of this color (excluding cross lines)
            # Find points where count in row is 1 or count in col is 1
            diamond_pts = []
            for p in pts:
                if (p[0] != cross_y or len(pts[pts[:, 0] == cross_y]) < 5) and (p[1] != cross_x or len(pts[pts[:, 1] == cross_x]) < 5):
                    diamond_pts.append(p)
            
            if len(diamond_pts) == 0:
                diamond_pts = pts

            diamond_pts = np.array(diamond_pts)
            
            # Find the shared column (top and bottom points share x)
            # Find the shared row (left and right points share y)
            r_vals, r_cnts = np.unique(diamond_pts[:, 0], return_counts=True)
            c_vals, c_cnts = np.unique(diamond_pts[:, 1], return_counts=True)
            
            # Shared row is row with max count in diamond_pts
            target_y = r_vals[np.argmax(r_cnts)] if len(r_vals) > 0 else cross_y
            # Shared col is col with max count in diamond_pts
            target_x = c_vals[np.argmax(c_cnts)] if len(c_vals) > 0 else cross_x
            
            dy = target_y - cross_y
            dx = target_x - cross_x
            
            steps_y = int(round(dy / 3.0))
            steps_x = int(round(dx / 3.0))
            
            is_active = any(abs(bp[0] - cross_y) <= 1 and abs(bp[1] - cross_x) <= 1 for bp in black_pts)
            print(f"  Color {color}: cross=({cross_y},{cross_x}) target=({target_y},{target_x}) -> dy={steps_y}, dx={steps_x} (active={is_active})")
            
            plans.append({
                "color": color,
                "is_active": is_active,
                "steps_y": steps_y,
                "steps_x": steps_x
            })

        # Order active first
        plans.sort(key=lambda p: not p["is_active"])
        
        # Execute moves
        for idx, plan in enumerate(plans):
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

        if obs.levels_completed > level:
            print(f"*** ADVANCED: Level {level} -> Level {obs.levels_completed} (total steps: {total_steps}) ***")
            level = obs.levels_completed
        else:
            print(f"Level {level} did not advance with primary plan. Checking state...")
            break

        if obs.state in (GameState.WIN, GameState.GAME_OVER):
            break

    print(f"\nFinal Result: levels_completed = {obs.levels_completed}, state = {obs.state}")
    return obs.levels_completed

if __name__ == "__main__":
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    solve_re86_all_levels(env)
