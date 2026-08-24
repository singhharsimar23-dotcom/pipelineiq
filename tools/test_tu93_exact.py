"""
Test graph BFS on tu93 using the node/edge structure.
"""
import sys
from pathlib import Path
from collections import deque
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

def solve_tu93_graph(seed):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("tu93", seed=seed)
    obs = env.reset()
    game = env._game
    
    maze_sprite = game.current_level.get_sprites_by_tag("0005uvnhiglpvh")[0]
    avatar = game.current_level.get_sprites_by_tag("0017unajnymcki")[0]
    exit_sprite = game.current_level.get_sprites_by_tag("0015msvpvzxhqf")[0]
    
    start_r = avatar.y - maze_sprite.y
    start_c = avatar.x - maze_sprite.x
    goal_r = exit_sprite.y - maze_sprite.y
    goal_c = exit_sprite.x - maze_sprite.x
    
    print(f"Seed {seed}: start=({start_r}, {start_c}), goal=({goal_r}, {goal_c})")
    
    # BFS on nodes (r, c)
    q = deque([((start_r, start_c), [])])
    visited = {(start_r, start_c)}
    
    pix = maze_sprite.pixels
    H, W = pix.shape
    
    best_path = None
    while q:
        (cr, cc), path = q.popleft()
        if (cr, cc) == (goal_r, goal_c):
            best_path = path
            break
            
        # 4 neighbors at distance 6:
        # UP: (cr - 6, cc) if (cr - 3, cc) is 2
        if cr >= 6 and pix[cr - 3, cc] == 2:
            nr, nc = cr - 6, cc
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append(((nr, nc), path + [GameAction.ACTION1]))
                
        # DOWN: (cr + 6, cc) if (cr + 3, cc) is 2
        if cr + 6 < H and pix[cr + 3, cc] == 2:
            nr, nc = cr + 6, cc
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append(((nr, nc), path + [GameAction.ACTION2]))
                
        # LEFT: (cr, cc - 6) if (cr, cc - 3) is 2
        if cc >= 6 and pix[cr, cc - 3] == 2:
            nr, nc = cr, cc - 6
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append(((nr, nc), path + [GameAction.ACTION3]))
                
        # RIGHT: (cr, cc + 6) if (cr, cc + 3) is 2
        if cc + 6 < W and pix[cr, cc + 3] == 2:
            nr, nc = cr, cc + 6
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append(((nr, nc), path + [GameAction.ACTION4]))
                
    print(f"Path length: {len(best_path) if best_path else 'None'}")
    if best_path:
        for act in best_path:
            obs = env.step(act)
            if obs.levels_completed > 0:
                print(f"WIN! levels_completed={obs.levels_completed}")
                break
        print(f"Final levels: {obs.levels_completed}")
        return obs.levels_completed
    return 0

for s in range(5):
    solve_tu93_graph(s)
