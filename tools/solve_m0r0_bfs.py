"""
Solve m0r0 Level 0 via Mirror Sokoban BFS state search.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from collections import deque
import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def solve_m0r0_level0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("m0r0", seed=0)
    obs = env.reset()
    game = env._game

    # Let's run a BFS exploration on env actions [1, 2, 3, 4]
    # We can clone env or simulate mirror physics
    # Let's simulate:
    s1 = game.current_level.get_sprites_by_name("pikgci-toljda-leklkn")[0]
    s2 = game.current_level.get_sprites_by_name("pikgci-toljda-rivmdg")[0]
    
    # Let's search over action sequences of length 1..10
    q = deque([[]])
    visited = set()
    
    actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
    
    while q:
        seq = q.popleft()
        if len(seq) > 12:
            continue
            
        # Re-play sequence from fresh env
        env = arcade.make("m0r0", seed=0)
        obs = env.reset()
        
        for a in seq:
            obs = env.step(a)
            if obs.levels_completed > 0:
                print(f"*** M0R0 LEVEL 0 SOLVED! Sequence: {[act.name for act in seq]} (length: {len(seq)}) ***")
                return seq
                
        # State signature
        game = env._game
        s1 = game.current_level.get_sprites_by_name("pikgci-toljda-leklkn")[0]
        s2 = game.current_level.get_sprites_by_name("pikgci-toljda-rivmdg")[0]
        state = ((s1.x, s1.y), (s2.x, s2.y))
        
        if state not in visited:
            visited.add(state)
            for act in actions:
                q.append(seq + [act])
                
    print("BFS exhausted without win.")
    return None

if __name__ == "__main__":
    solve_m0r0_level0()
