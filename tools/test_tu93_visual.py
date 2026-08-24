"""
Test pure visual frame extraction of tu93 maze and BFS path.
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
from my_agent import get_2d_grid, get_background_color, get_components

def test_visual_tu93(seed):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("tu93", seed=seed)
    obs = env.reset()
    
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    comps = get_components(f, bg, max_area=1000)
    
    # In visual frame:
    # 1. Maze component has a large bounding box (w >= 30, h >= 30)
    maze_comps = [c for c in comps if c['w'] >= 30 and c['h'] >= 30]
    print(f"Seed {seed}: Found {len(maze_comps)} maze candidates: {[(c['w'], c['h'], c['min_r'], c['min_c']) for c in maze_comps]}")
    
    if not maze_comps:
        return []
    maze_c = maze_comps[0]
    
    # Subgrid of the maze in f:
    # Let's inspect the subgrid:
    min_r, max_r = maze_c['min_r'], maze_c['max_r']
    min_c, max_c = maze_c['min_c'], maze_c['max_c']
    sub = f[min_r:max_r+1, min_c:max_c+1]
    
    # Small square components inside the maze:
    # Avatar is small 3x3 at top-left
    # Goal is small 3x3 at bottom-right
    small = [c for c in comps if c['w'] == 3 and c['h'] == 3 and c != maze_c]
    print(f"Small components: {[(c['cx'], c['cy'], c['col']) for c in small]}")
    
    # In the subgrid, find corridor color (color with bridges)
    # The edges have color 2 in the sprite, which in the frame is rendered as color 2 (or foreground color)
    # Let's check subgrid values:
    print(f"Unique values in maze subgrid: {np.unique(sub)}")
    
    # The start relative pos is (0, 0), goal is (max_r - min_r - 2, max_c - min_c - 2) or relative to small components
    start_r, start_c = 0, 0
    goal_r = (max_r - min_r) // 6 * 6
    goal_c = (max_c - min_c) // 6 * 6
    
    # Look for edge connectivity: check pixels at (r + 3, c) or (r, c + 3)
    # If sub[r + 3, c] != bg and sub[r + 3, c] == edge_col
    # Let's see which color is edge_col:
    edge_cols = [c for c in np.unique(sub) if c != bg and c != 0]
    print(f"Potential edge colors: {edge_cols}")
    
    q = deque([((start_r, start_c), [])])
    visited = {(start_r, start_c)}
    
    best_path = None
    while q:
        (cr, cc), path = q.popleft()
        if (cr, cc) == (goal_r, goal_c):
            best_path = path
            break
            
        # 4 directions with step 6:
        # UP: cr - 6
        if cr >= 6:
            # Check edge at cr - 3, cc
            if sub[cr - 3, cc] in edge_cols:
                nr, nc = cr - 6, cc
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append(((nr, nc), path + [GameAction.ACTION1]))
                    
        # DOWN: cr + 6
        if cr + 6 <= goal_r:
            if sub[cr + 3, cc] in edge_cols:
                nr, nc = cr + 6, cc
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append(((nr, nc), path + [GameAction.ACTION2]))
                    
        # LEFT: cc - 6
        if cc >= 6:
            if sub[cr, cc - 3] in edge_cols:
                nr, nc = cr, cc - 6
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append(((nr, nc), path + [GameAction.ACTION3]))
                    
        # RIGHT: cc + 6
        if cc + 6 <= goal_c:
            if sub[cr, cc + 3] in edge_cols:
                nr, nc = cr, cc + 6
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append(((nr, nc), path + [GameAction.ACTION4]))
                    
    print(f"Visual BFS path: {len(best_path) if best_path else 'None'}")
    if best_path:
        for act in best_path:
            obs = env.step(act)
            if obs.levels_completed > 0:
                print(f"WIN! levels_completed={obs.levels_completed}")
                break
        return obs.levels_completed
    return 0

for s in range(5):
    test_visual_tu93(s)
