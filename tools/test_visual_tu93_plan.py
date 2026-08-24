"""
Pure visual graph BFS solver for tu93.
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

def build_tu93_plan(f, bg):
    comps = get_components(f, bg, max_area=50)
    
    # Nodes are 3x3 components on a 6-pixel grid
    # Avatar is small 3x3 component (or area 8-9) with color 9 / top-left
    # Exit is small 3x3 component with color 14 / bottom-right
    # Edge components have color 2
    
    nodes = [c for c in comps if c['w'] == 3 and c['h'] == 3 and c['col'] in (0, 9, 14)]
    edges = [c for c in comps if c['w'] == 3 and c['h'] == 3 and c['col'] == 2]
    
    if len(nodes) < 10 or len(edges) < 5:
        return []
        
    start_nodes = [c for c in nodes if c['col'] == 9 or (c['cx'] < 20 and c['cy'] < 20)]
    exit_nodes = [c for c in nodes if c['col'] == 14 or (c['cx'] > 40 and c['cy'] > 40)]
    
    if not start_nodes or not exit_nodes:
        return []
        
    start = (start_nodes[0]['cx'], start_nodes[0]['cy'])
    goal = (exit_nodes[0]['cx'], exit_nodes[0]['cy'])
    
    edge_set = {(e['cx'], e['cy']) for e in edges}
    
    # BFS on nodes:
    q = deque([(start, [])])
    visited = {start}
    
    while q:
        (cx, cy), path = q.popleft()
        if (cx, cy) == goal:
            return path
            
        # UP: cy - 6, edge at (cx, cy - 3)
        if (cx, cy - 3) in edge_set:
            nxt = (cx, cy - 6)
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, path + [(GameAction.ACTION1, {})]))
                
        # DOWN: cy + 6, edge at (cx, cy + 3)
        if (cx, cy + 3) in edge_set:
            nxt = (cx, cy + 6)
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, path + [(GameAction.ACTION2, {})]))
                
        # LEFT: cx - 6, edge at (cx - 3, cy)
        if (cx - 3, cy) in edge_set:
            nxt = (cx - 6, cy)
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, path + [(GameAction.ACTION3, {})]))
                
        # RIGHT: cx + 6, edge at (cx + 3, cy)
        if (cx + 3, cy) in edge_set:
            nxt = (cx + 6, cy)
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, path + [(GameAction.ACTION4, {})]))
                
    return []

for seed in range(5):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("tu93", seed=seed)
    obs = env.reset()
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    plan = build_tu93_plan(f, bg)
    print(f"Seed {seed}: plan len = {len(plan)}")
    for act, data in plan:
        obs = env.step(act)
        if obs.levels_completed > 0:
            print(f"  WIN! levels_completed={obs.levels_completed}")
            break
    print(f"  Final: levels={obs.levels_completed}")
