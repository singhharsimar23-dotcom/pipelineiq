"""
Solver search for re86.
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

def solve_re86_level():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()

    # Let's test sequences of actions on level 0
    print("Testing BFS on re86 action space...")
    # State space: slider 0 shift (dx, dy) in [-4..4], slider 1 shift (dx, dy) in [-4..4]
    # Let's perform a simple BFS over sequences of actions up to depth 12
    from collections import deque
    
    # We can clone/simulate by running steps in env with reset
    # Or measure is_win:
    def test_seq(seq):
        obs = env.reset()
        for act in seq:
            obs = env.step(act)
            if obs.levels_completed > 0 or obs.state == GameState.WIN:
                return True, obs
        return False, obs

    # Test small combinations of actions
    # Actions: [1=UP, 2=DOWN, 3=LEFT, 4=RIGHT, 5=CYCLE]
    # For slider 0: try up to 3 moves in each direction
    # Then ACTION5 (switch to slider 1)
    # For slider 1: try up to 3 moves in each direction
    moves = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
    
    s0_sequences = [[]]
    for m in moves:
        s0_sequences.append([m])
        for m2 in moves:
            s0_sequences.append([m, m2])
            for m3 in moves:
                s0_sequences.append([m, m2, m3])

    s1_sequences = [[]]
    for m in moves:
        s1_sequences.append([m])
        for m2 in moves:
            s1_sequences.append([m, m2])
            for m3 in moves:
                s1_sequences.append([m, m2, m3])

    print(f"Total candidate combinations: {len(s0_sequences) * len(s1_sequences)}")
    attempts = 0
    for s0 in s0_sequences:
        for s1 in s1_sequences:
            attempts += 1
            full_seq = s0 + [GameAction.ACTION5] + s1
            win, obs = test_seq(full_seq)
            if win:
                print(f"WIN FOUND! Attempt {attempts}: seq={[a.name for a in full_seq]}")
                print(f"Levels completed: {obs.levels_completed}")
                return full_seq
    
    print("No win found in depth-3 grid search.")
    return None

if __name__ == "__main__":
    solve_re86_level()
