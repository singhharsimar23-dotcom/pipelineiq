"""
Inspect goals and BFS segments in detail.
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

def inspect_segments():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ls20", seed=0)
    obs = env.reset()
    f = np.array(obs.frame[0])
    bg = get_background_color(f)
    
    # Avatar pos after ACTION3: (y=45, x=31)
    sy, sx = 45, 31
    step = 5
    
    comps = get_components(f, bg, max_area=300)
    goals = [(c['cy'], c['cx']) for c in comps
             if 1 <= c['area'] <= 60
             and 5 <= c['cy'] <= 54 and 5 <= c['cx'] <= 58
             and abs(c['cy'] - sy) + abs(c['cx'] - sx) >= 4]
    
    print(f"Goals found: {goals}")
    
    dir_map = [
        (GameAction.ACTION3, 0, -step),  # Left
        (GameAction.ACTION1, -step, 0),  # Up
        (GameAction.ACTION4, 0, step),   # Right
        (GameAction.ACTION2, step, 0),   # Down
    ]

    def bfs(sy, sx, gy, gx):
        q = deque([(sy, sx, [])])
        vis = {(sy, sx)}
        while q:
            cy, cx, path = q.popleft()
            if abs(cy - gy) <= step and abs(cx - gx) <= step:
                return path
            if len(path) >= 50:
                continue
            for act, dy, dx in dir_map:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < 64 and 0 <= nx < 64 and (ny, nx) not in vis:
                    if (f[ny, nx] == bg) or (abs(ny - gy) <= step and abs(nx - gx) <= step):
                        vis.add((ny, nx))
                        q.append((ny, nx, path + [act]))
        return []

    for gy, gx in goals:
        p = bfs(sy, sx, gy, gx)
        print(f"Path to ({gy}, {gx}): len={len(p)}, {[a.name for a in p]}")

if __name__ == "__main__":
    inspect_segments()
