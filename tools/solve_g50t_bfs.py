"""
Solve g50t Level 0 via multi-action BFS state search.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from collections import deque
import numpy as np

def solve_g50t_level0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    
    # State search:
    # Directions: 1 (Up), 2 (Down), 3 (Left), 4 (Right), 5 (Rewind clone)
    # BFS on action sequences up to depth 15
    actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4, GameAction.ACTION5]
    
    q = deque([[]])
    visited_states = set()
    
    while q:
        path = q.popleft()
        if len(path) > 18:
            break
            
        env = arcade.make("g50t", seed=0)
        obs = env.reset()
        game = env._game
        
        valid = True
        for act in path:
            obs = env.step(act)
            if obs.game_over:
                valid = False
                break
                
        if not valid:
            continue
            
        if game.mrzduxdbbk() or obs.levels_completed > 0:
            print(f"*** FOUND G50T WIN PATH! Length: {len(path)} ***")
            print(f"Path: {[a.name for a in path]}")
            return path
            
        # State: (avatar_x, avatar_y, len(clones), buttons_state)
        ax, ay = game.vgwycxsxjz.dzxunlkwxt.x, game.vgwycxsxjz.dzxunlkwxt.y
        state_key = (ax, ay, len(game.vgwycxsxjz.rloltuowth), len(path))
        if state_key in visited_states:
            continue
        visited_states.add(state_key)
        
        for act in [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4, GameAction.ACTION5]:
            q.append(path + [act])

if __name__ == "__main__":
    solve_g50t_level0()
