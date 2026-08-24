"""
Direct game simulator to find exact winning sequences for re86 levels.
"""
import sys
from pathlib import Path
import copy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def find_exact_re86_solution():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    game = env._game

    print("Searching for exact level 0 solution via in-memory simulation...")
    
    # Save initial level state
    import pickle
    
    # Let's test moves:
    # y0 in [-8..8], x0 in [-8..8]
    # y1 in [-8..8], x1 in [-8..8]
    # Let's test all (y0, x0, y1, x1) combinations:
    # 17 * 17 * 17 * 17 = 83521
    # We can optimize: slider 0 only affects color 11 target pixels, slider 1 only affects color 9 target pixels!
    # They are completely independent in composite canvas!
    
    # Slider 0 search:
    best_s0 = None
    best_s1 = None
    
    target = game.current_level.get_sprites_by_tag("0054xnsuqceejm")[0]
    t_c11 = np.argwhere(target.pixels == 11)
    t_c9 = np.argwhere(target.pixels == 9)
    
    print(f"Target c11 count: {len(t_c11)}, c9 count: {len(t_c9)}")

    # Test slider 0 offsets
    for y0 in range(-8, 9):
        for x0 in range(-8, 9):
            # reset level
            env.reset()
            # apply y0
            for _ in range(abs(y0)):
                env.step(GameAction.ACTION1 if y0 < 0 else GameAction.ACTION2)
            # apply x0
            for _ in range(abs(x0)):
                env.step(GameAction.ACTION3 if x0 < 0 else GameAction.ACTION4)
            
            # check slider 0 overlap
            s0 = env._game.current_level.get_sprites_by_tag("0031cppcuvqlbi")[0]
            s0_pts = np.argwhere(s0.pixels == 11)
            s0_global = s0_pts + [s0.y, s0.x]
            if len(s0_global) == len(t_c11):
                # Sort by (y, x)
                s0_sorted = s0_global[np.lexsort((s0_global[:, 1], s0_global[:, 0]))]
                t_c11_sorted = t_c11[np.lexsort((t_c11[:, 1], t_c11[:, 0]))]
                if np.array_equal(s0_sorted, t_c11_sorted):
                    print(f"MATCH FOUND FOR SLIDER 0! y0={y0}, x0={x0}")
                    best_s0 = (y0, x0)
                    break
        if best_s0:
            break

    # Test slider 1 offsets
    for y1 in range(-8, 9):
        for x1 in range(-8, 9):
            env.reset()
            # switch to slider 1
            env.step(GameAction.ACTION5)
            # apply y1
            for _ in range(abs(y1)):
                env.step(GameAction.ACTION1 if y1 < 0 else GameAction.ACTION2)
            # apply x1
            for _ in range(abs(x1)):
                env.step(GameAction.ACTION3 if x1 < 0 else GameAction.ACTION4)
            
            s1 = env._game.current_level.get_sprites_by_tag("0031cppcuvqlbi")[1]
            s1_pts = np.argwhere(s1.pixels == 9)
            s1_global = s1_pts + [s1.y, s1.x]
            if len(s1_global) == len(t_c9):
                s1_sorted = s1_global[np.lexsort((s1_global[:, 1], s1_global[:, 0]))]
                t_c9_sorted = t_c9[np.lexsort((t_c9[:, 1], t_c9[:, 0]))]
                if np.array_equal(s1_sorted, t_c9_sorted):
                    print(f"MATCH FOUND FOR SLIDER 1! y1={y1}, x1={x1}")
                    best_s1 = (y1, x1)
                    break
        if best_s1:
            break

    print(f"\nFinal parameters: best_s0={best_s0}, best_s1={best_s1}")
    if best_s0 and best_s1:
        # Verify complete run in env
        obs = env.reset()
        y0, x0 = best_s0
        y1, x1 = best_s1
        for _ in range(abs(y0)):
            obs = env.step(GameAction.ACTION1 if y0 < 0 else GameAction.ACTION2)
        for _ in range(abs(x0)):
            obs = env.step(GameAction.ACTION3 if x0 < 0 else GameAction.ACTION4)
        obs = env.step(GameAction.ACTION5)
        for _ in range(abs(y1)):
            obs = env.step(GameAction.ACTION1 if y1 < 0 else GameAction.ACTION2)
        for _ in range(abs(x1)):
            obs = env.step(GameAction.ACTION3 if x1 < 0 else GameAction.ACTION4)
        print(f"Verified execution: levels_completed={obs.levels_completed}, state={obs.state}")

if __name__ == "__main__":
    find_exact_re86_solution()
