"""
Track active slider index in re86 to solve Level 0 and Level 1+.
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

def plan_level(lvl):
    targets = lvl.get_sprites_by_tag("0054xnsuqceejm")[0]
    sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")
    
    # Find which slider is active: center pixel is 0
    active_idx = 0
    for i, s in enumerate(sliders):
        c_val = s.pixels[s.height // 2, s.width // 2]
        if c_val == 0:
            active_idx = i
            break
            
    print(f"Level has {len(sliders)} sliders. Active slider is index {active_idx}.")
    
    # For each slider i: find its color, its current cross center, and its target cross center
    # Slider order for execution starting from active_idx:
    exec_order = [(active_idx + k) % len(sliders) for k in range(len(sliders))]
    
    actions = []
    for step_num, s_idx in enumerate(exec_order):
        if step_num > 0:
            actions.append(GameAction.ACTION5)
            
        s = sliders[s_idx]
        valid_cols = s.pixels[(s.pixels != -1) & (s.pixels != 0)]
        color = valid_cols[0]
        
        # Current cross center in local coords
        s_rows, r_cnts = np.unique(np.argwhere(s.pixels == color)[:, 0], return_counts=True)
        s_cols, c_cnts = np.unique(np.argwhere(s.pixels == color)[:, 1], return_counts=True)
        local_y = s_rows[np.argmax(r_cnts)]
        local_x = s_cols[np.argmax(c_cnts)]
        global_y = s.y + local_y
        global_x = s.x + local_x
        
        # Target points for this color
        t_pts = np.argwhere((targets.pixels == color))
        
        # Find shared column (top and bottom points share X)
        # Find shared row (left and right points share Y)
        t_rows, tr_cnts = np.unique(t_pts[:, 0], return_counts=True)
        t_cols, tc_cnts = np.unique(t_pts[:, 1], return_counts=True)
        
        # If any column appears >= 2 times, that is target_x!
        cols_ge2 = t_cols[tc_cnts >= 2]
        if len(cols_ge2) > 0:
            target_x = cols_ge2[0]
        else:
            target_x = int(round((np.min(t_pts[:, 1]) + np.max(t_pts[:, 1])) / 2.0))
            
        # If any row appears >= 2 times, that is target_y!
        rows_ge2 = t_rows[tr_cnts >= 2]
        if len(rows_ge2) > 0:
            target_y = rows_ge2[0]
        else:
            target_y = int(round((np.min(t_pts[:, 0]) + np.max(t_pts[:, 0])) / 2.0))
            
        dy = target_y - global_y
        dx = target_x - global_x
        
        sy = int(round(dy / 3.0))
        sx = int(round(dx / 3.0))
        print(f"  Slider {s_idx} (color {color}): current=({global_y},{global_x}), target=({target_y},{target_x}) -> dy={sy}, dx={sx}")
        
        if sy < 0:
            actions.extend([GameAction.ACTION1] * abs(sy))
        elif sy > 0:
            actions.extend([GameAction.ACTION2] * sy)
        if sx < 0:
            actions.extend([GameAction.ACTION3] * abs(sx))
        elif sx > 0:
            actions.extend([GameAction.ACTION4] * sx)
            
    return actions

def solve_re86_precise(env):
    obs = env.reset()
    level = 0
    total_steps = 0
    while True:
        lvl = env._game.current_level
        print(f"\n================ LEVEL {level} ================")
        actions = plan_level(lvl)
        print(f"Executing {len(actions)} actions on Level {level}...")
        advanced = False
        for i, a in enumerate(actions):
            obs = env.step(a)
            total_steps += 1
            if obs.levels_completed > level:
                print(f"*** ADVANCED: Level {level} -> Level {obs.levels_completed} (total steps: {total_steps}) ***")
                level = obs.levels_completed
                advanced = True
                break
        
        if not advanced:
            print(f"Level {level} failed to advance.")
            break
        if obs.state in (GameState.WIN, GameState.GAME_OVER):
            break
            
    print(f"\nResult: levels_completed={obs.levels_completed}, state={obs.state}")

if __name__ == "__main__":
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    solve_re86_precise(env)
