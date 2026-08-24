"""
Complete trace and solver for re86.
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

def solve_re86():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    game = env._game

    target = game.current_level.get_sprites_by_tag("0054xnsuqceejm")[0]
    print("Target non-(-1) and non-4 pixels:")
    t_mask = (target.pixels != -1) & (target.pixels != 4)
    t_pts = np.argwhere(t_mask)
    for r, c in t_pts:
        print(f"  ({r}, {c}) -> color {target.pixels[r, c]}")

    # Let's test a simple grid search over action sequences:
    # First move Slider 1 (which is active):
    # Try moves in [ACTION1..ACTION4]
    # Then ACTION5 (switch to Slider 0)
    # Try moves in [ACTION1..ACTION4]
    
    # Let's check win condition after each move
    actions_1to4 = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
    
    # Generate single direction counts: up to 10 in Y, up to 10 in X
    s1_moves = []
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            seq = []
            if dy < 0:
                seq.extend([GameAction.ACTION1] * abs(dy))
            elif dy > 0:
                seq.extend([GameAction.ACTION2] * dy)
            if dx < 0:
                seq.extend([GameAction.ACTION3] * abs(dx))
            elif dx > 0:
                seq.extend([GameAction.ACTION4] * dx)
            s1_moves.append((dy, dx, seq))

    s0_moves = []
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            seq = []
            if dy < 0:
                seq.extend([GameAction.ACTION1] * abs(dy))
            elif dy > 0:
                seq.extend([GameAction.ACTION2] * dy)
            if dx < 0:
                seq.extend([GameAction.ACTION3] * abs(dx))
            elif dx > 0:
                seq.extend([GameAction.ACTION4] * dx)
            s0_moves.append((dy, dx, seq))

    print(f"Testing {len(s1_moves) * len(s0_moves)} combinations...")
    count = 0
    for dy1, dx1, seq1 in s1_moves:
        for dy0, dx0, seq0 in s0_moves:
            count += 1
            env.reset()
            # Execute seq1 on Slider 1
            for a in seq1:
                env.step(a)
            # Switch to Slider 0
            env.step(GameAction.ACTION5)
            # Execute seq0 on Slider 0
            for a in seq0:
                env.step(a)
            
            if game.jeiavrvavi():
                print(f"\n*** WIN DETECTED! ***")
                print(f"Slider 1: dy={dy1}, dx={dx1} (seq={[a.name for a in seq1]})")
                print(f"Slider 0: dy={dy0}, dx={dx0} (seq={[a.name for a in seq0]})")
                
                # Execute in env to confirm level progression
                obs_final = env.step(GameAction.ACTION1) # any step triggers check or next_level
                print(f"Final levels completed: {obs_final.levels_completed}")
                return (seq1, seq0)

    print("Search completed without win.")

if __name__ == "__main__":
    solve_re86()
