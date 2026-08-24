"""
In-memory fast BFS solver for m0r0 Level 0.
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

def solve_m0r0_fast():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("m0r0", seed=0)
    obs = env.reset()
    game = env._game

    # Level 0 has 11x11 grid
    # Wall grid
    wall_sprite = game.current_level.get_sprites_by_tag("wahtyt")[0]
    walls = (wall_sprite.pixels != -1)
    
    # Starting avatar positions:
    # Avatar 1 (Left): moves (dx, dy)
    # Avatar 2 (Right): moves (-dx, dy)
    s1 = game.current_level.get_sprites_by_name("pikgci-toljda-leklkn")[0]
    s2 = game.current_level.get_sprites_by_name("pikgci-toljda-rivmdg")[0]
    start_pos1 = (s1.x, s1.y)
    start_pos2 = (s2.x, s2.y)
    
    print(f"Start pos1: {start_pos1}, start pos2: {start_pos2}")
    
    actions = [
        (GameAction.ACTION1, 0, -1), # Up: dy=-1
        (GameAction.ACTION2, 0, 1),  # Down: dy=+1
        (GameAction.ACTION3, -1, 0), # Left: dx=-1
        (GameAction.ACTION4, 1, 0),  # Right: dx=+1
    ]
    
    q = deque([(start_pos1, start_pos2, [])])
    visited = {(start_pos1, start_pos2)}
    
    while q:
        (x1, y1), (x2, y2), path = q.popleft()
        
        # Check collision / win
        if (x1, y1) == (x2, y2):
            print(f"*** FOUND M0R0 SOLUTION! Path length: {len(path)} ***")
            print(f"Action sequence: {[a.name for a in path]}")
            
            # Execute on real environment
            for a in path:
                obs = env.step(a)
                if obs.levels_completed > 0:
                    print(f"*** M0R0 LEVEL 0 CLEARED AT STEP {len(path)}! ***")
                    return path
            return path
            
        for act, dx, dy in actions:
            # Avatar 1 moves (dx, dy)
            nx1, ny1 = x1 + dx, y1 + dy
            if not (0 <= nx1 < 11 and 0 <= ny1 < 11) or walls[ny1, nx1]:
                nx1, ny1 = x1, y1 # blocked by wall
                
            # Avatar 2 moves (-dx, dy) (mirrored X)
            nx2, ny2 = x2 - dx, y2 + dy
            if not (0 <= nx2 < 11 and 0 <= ny2 < 11) or walls[ny2, nx2]:
                nx2, ny2 = x2, y2 # blocked by wall
                
            state = ((nx1, ny1), (nx2, ny2))
            if state not in visited:
                visited.add(state)
                q.append(((nx1, ny1), (nx2, ny2), path + [act]))

    print("No solution found in state graph.")
    return None

if __name__ == "__main__":
    solve_m0r0_fast()
