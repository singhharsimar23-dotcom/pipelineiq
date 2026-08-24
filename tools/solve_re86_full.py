"""
Multi-Level Dynamic Solver for re86 with proper level transition.
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

def solve_re86_level_from_frame(f):
    vals, counts = np.unique(f, return_counts=True)
    bg = vals[np.argmax(counts)]
    
    candidate_colors = [c for c in vals if c not in (bg, 0, 4, 15, 1)]
    print(f"Colors detected: {candidate_colors}")
    
    black_pts = np.argwhere(f == 0)
    plans = []
    for color in candidate_colors:
        pts = np.argwhere(f == color)
        if len(pts) < 4:
            continue
        
        rows, r_counts = np.unique(pts[:, 0], return_counts=True)
        cols, c_counts = np.unique(pts[:, 1], return_counts=True)
        
        cross_y = rows[np.argmax(r_counts)]
        cross_x = cols[np.argmax(c_counts)]
        
        # Diamond points
        diamond_pts = []
        for p in pts:
            if (p[0] != cross_y or len(pts[pts[:, 0] == cross_y]) < 5) and (p[1] != cross_x or len(pts[pts[:, 1] == cross_x]) < 5):
                diamond_pts.append(p)
        
        if len(diamond_pts) == 0:
            diamond_pts = pts

        diamond_pts = np.array(diamond_pts)
        
        r_vals, r_cnts = np.unique(diamond_pts[:, 0], return_counts=True)
        c_vals, c_cnts = np.unique(diamond_pts[:, 1], return_counts=True)
        
        target_y = r_vals[np.argmax(r_cnts)] if len(r_vals) > 0 else cross_y
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
    
    actions = []
    for idx, plan in enumerate(plans):
        if idx > 0:
            actions.append(GameAction.ACTION5)
        sy = plan["steps_y"]
        sx = plan["steps_x"]
        if sy < 0:
            actions.extend([GameAction.ACTION1] * abs(sy))
        elif sy > 0:
            actions.extend([GameAction.ACTION2] * sy)
        if sx < 0:
            actions.extend([GameAction.ACTION3] * abs(sx))
        elif sx > 0:
            actions.extend([GameAction.ACTION4] * sx)
            
    return actions

def solve_re86_all(env):
    obs = env.reset()
    level = 0
    total_steps = 0
    
    while True:
        f = np.array(obs.frame[0])
        print(f"\n================ SOLVING LEVEL {level} ================")
        actions = solve_re86_level_from_frame(f)
        print(f"Generated {len(actions)} actions for Level {level}.")
        
        for i, a in enumerate(actions):
            obs = env.step(a)
            total_steps += 1
            if obs.levels_completed > level:
                print(f"*** ADVANCED: Level {level} -> Level {obs.levels_completed} (total steps: {total_steps}) ***")
                level = obs.levels_completed
                # Frame after advance is now updated on the next iteration
                break

        if obs.levels_completed == level and len(actions) == 0:
            print(f"Level {level}: No more actions found.")
            break
            
        if obs.state in (GameState.WIN, GameState.GAME_OVER):
            break

    print(f"\n================ SUMMARY ================")
    print(f"Final levels cleared: {obs.levels_completed}")
    print(f"Final game state: {obs.state}")
    print(f"Total steps used: {total_steps}")
    return obs.levels_completed

if __name__ == "__main__":
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    for seed in range(5):
        print(f"\n################ SEED {seed} ################")
        env = arcade.make("re86", seed=seed)
        solve_re86_all(env)
