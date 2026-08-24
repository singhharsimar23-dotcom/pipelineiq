"""
Find exact multi-level move plans for all levels of re86.
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

def solve_re86_all_levels_perfect():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    game = env._game

    level = 0
    total_steps = 0
    while True:
        lvl = game.current_level
        print(f"\n================ SOLVING LEVEL {level} ================")
        target = lvl.get_sprites_by_tag("0054xnsuqceejm")[0]
        sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")
        
        # Determine active slider
        active_idx = 0
        for i, s in enumerate(sliders):
            if s.pixels[s.height // 2, s.width // 2] == 0:
                active_idx = i
                break
                
        print(f"Level {level}: {len(sliders)} sliders, active slider={active_idx}")
        exec_order = [(active_idx + k) % len(sliders) for k in range(len(sliders))]
        
        level_actions = []
        for step_num, s_idx in enumerate(exec_order):
            if step_num > 0:
                level_actions.append(GameAction.ACTION5)
                
            s = sliders[s_idx]
            color = s.pixels[(s.pixels != -1) & (s.pixels != 0)][0]
            t_pts = np.argwhere(target.pixels == color)
            
            # When sprite moves by (dy, dx) steps of 3:
            # new s.y = s.y + dy * 3
            # new s.x = s.x + dx * 3
            # cross line in global coords:
            # horizontal line is at global Y = s.y + dy * 3 + (s.height // 2)
            # vertical line is at global X = s.x + dx * 3 + (s.width // 2)
            
            best_steps = (0, 0)
            best_covered = -1
            
            for dy in range(-15, 16):
                for dx in range(-15, 16):
                    gy = s.y + dy * 3 + (s.height // 2)
                    gx = s.x + dx * 3 + (s.width // 2)
                    
                    # Check coverage of t_pts:
                    # A target point (tr, tc) is covered if:
                    # tr == gy and (s.x + dx*3) <= tc < (s.x + dx*3 + s.width)
                    # OR tc == gx and (s.y + dy*3) <= tr < (s.y + dy*3 + s.height)
                    covered = 0
                    for tr, tc in t_pts:
                        on_horiz = (tr == gy) and (s.x + dx * 3 <= tc < s.x + dx * 3 + s.width)
                        on_vert = (tc == gx) and (s.y + dy * 3 <= tr < s.y + dy * 3 + s.height)
                        if on_horiz or on_vert:
                            covered += 1
                            
                    if covered > best_covered:
                        best_covered = covered
                        best_steps = (dy, dx)
                        if covered == len(t_pts):
                            break
                if best_covered == len(t_pts):
                    break
                    
            print(f"  Slider {s_idx} (color {color}): target points={len(t_pts)}, covered={best_covered}/{len(t_pts)}, steps={best_steps}")
            sy, sx = best_steps
            if sy < 0:
                level_actions.extend([GameAction.ACTION1] * abs(sy))
            elif sy > 0:
                level_actions.extend([GameAction.ACTION2] * sy)
            if sx < 0:
                level_actions.extend([GameAction.ACTION3] * abs(sx))
            elif sx > 0:
                level_actions.extend([GameAction.ACTION4] * sx)

        print(f"Executing {len(level_actions)} actions...")
        advanced = False
        for a in level_actions:
            obs = env.step(a)
            total_steps += 1
            if obs.levels_completed > level:
                print(f"*** ADVANCED: Level {level} -> Level {obs.levels_completed} (total steps: {total_steps}) ***")
                level = obs.levels_completed
                advanced = True
                break
                
        if not advanced:
            print(f"Level {level} failed to advance. Final state: {obs.state}")
            break
            
        if obs.state in (GameState.WIN, GameState.GAME_OVER):
            break

    print(f"\n================ FINAL SCORE ================")
    print(f"Total levels cleared: {obs.levels_completed}")
    print(f"Total steps: {total_steps}")
    print(f"Game state: {obs.state}")
    return obs.levels_completed

if __name__ == "__main__":
    solve_re86_all_levels_perfect()
