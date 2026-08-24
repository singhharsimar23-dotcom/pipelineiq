"""
Pure visual Peg Solitaire solver from raw frame f.
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
from agent.my_agent import get_components, get_background_color
from arcengine import GameAction

def solve_peg_solitaire_from_frame(f: np.ndarray, bg: int):
    # 1. Extract non-bg components
    comps = get_components(f, bg, max_area=50)
    
    # Filter peg candidates (area 4..25, roughly square)
    pegs = [c for c in comps if 4 <= c['area'] <= 25 and abs(c['w'] - c['h']) <= 2]
    if len(pegs) < 3:
        return None
        
    print(f"Peg candidates count: {len(pegs)}")
    for p in pegs:
        print(f"  Peg at ({p['cx']}, {p['cy']}) area={p['area']} color={f[p['cy'], p['cx']]}")
        
    # Group pegs by color
    colors = [int(f[p['cy'], p['cx']]) for p in pegs]
    dominant_peg_col = max(set(colors), key=colors.count)
    active_pegs = [p for p in pegs if f[p['cy'], p['cx']] == dominant_peg_col]
    print(f"Dominant peg color: {dominant_peg_col}, count: {len(active_pegs)}")
    
    # 2. Extract grid step size from differences
    xs = sorted(list(set(p['cx'] for p in active_pegs)))
    dxs = [xs[i+1] - xs[i] for i in range(len(xs)-1) if xs[i+1] - xs[i] > 2]
    step_x = min(dxs) if dxs else 6
    print(f"Detected lattice step: {step_x}")
    
    # Build grid coords
    min_x = min(p['cx'] for p in active_pegs)
    min_y = min(p['cy'] for p in active_pegs)
    
    peg_grid = set()
    for p in active_pegs:
        gx = round((p['cx'] - min_x) / step_x) + 1
        gy = round((p['cy'] - min_y) / step_x) + 2
        peg_grid.add((gx, gy))
        
    print(f"Normalized Peg Grid: {peg_grid}")
    
    # Holes: standard cross or board layout around the pegs
    # Holes exist wherever board background is non-padding
    holes = set()
    for gy in range(8):
        for gx in range(8):
            px = min_x + (gx - 1) * step_x
            py = min_y + (gy - 2) * step_x
            if 0 <= px < 64 and 0 <= py < 64:
                # Check if inside playable board
                if f[py, px] != bg:
                    holes.add((gx, gy))
                    
    print(f"Extracted board holes ({len(holes)}): {holes}")
    
    # Run BFS
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    q = deque([(frozenset(peg_grid), [])])
    visited = {frozenset(peg_grid)}
    
    while q:
        curr_pegs, path = q.popleft()
        if len(curr_pegs) == 1:
            print(f"*** SOLVED FROM PURE VISION! Jumps: {len(path)} ***")
            actions = []
            for (fgx, fgy), (tgx, tgy) in path:
                fcx = min_x + (fgx - 1) * step_x
                fcy = min_y + (fgy - 2) * step_x
                tcx = min_x + (tgx - 1) * step_x
                tcy = min_y + (tgy - 2) * step_x
                actions.append((GameAction.ACTION6, {"x": fcx, "y": fcy}))
                actions.append((GameAction.ACTION6, {"x": tcx, "y": tcy}))
            return actions
            
        for px, py in curr_pegs:
            for dx, dy in dirs:
                mid_x, mid_y = px + dx, py + dy
                dest_x, dest_y = px + 2*dx, py + 2*dy
                if (mid_x, mid_y) in curr_pegs and (dest_x, dest_y) in holes and (dest_x, dest_y) not in curr_pegs:
                    next_pegs = (curr_pegs - {(px, py), (mid_x, mid_y)}) | {(dest_x, dest_y)}
                    if next_pegs not in visited:
                        visited.add(next_pegs)
                        q.append((next_pegs, path + [((px, py), (dest_x, dest_y))]))
    return None

def test_visual_solver():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("lf52", seed=0)
    obs = env.reset()
    f = np.array(obs.frame[0])
    bg = get_background_color(f)
    
    plan = solve_peg_solitaire_from_frame(f, bg)
    print(f"Generated plan length: {len(plan)}")
    
    for act, data in plan:
        obs = env.step(act, data=data)
    print(f"Result: levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    test_visual_solver()
