"""
Test exact bfs termination.
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

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ls20", seed=0)
obs = env.reset()
f = np.array(obs.frame[0])
bg = get_background_color(f)

sy, sx = 45, 31
step = 5

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
        if abs(cy - gy) <= 2 and abs(cx - gx) <= 2:
            return path
        if len(path) >= 50:
            continue
        for act, dy, dx in dir_map:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < 64 and 0 <= nx < 64 and (ny, nx) not in vis:
                if (f[ny, nx] == bg) or (abs(ny - gy) <= 2 and abs(nx - gx) <= 2):
                    vis.add((ny, nx))
                    q.append((ny, nx, path + [act]))
    return []

# Modifier is at (y=30, x=19) -> (31, 20)
p1 = bfs(45, 34, 30, 19)
print(f"Path to modifier (30, 19): {len(p1)} actions: {[a.name for a in p1]}")

p2 = bfs(30, 19, 10, 34)
print(f"Path from modifier to door (10, 34): {len(p2)} actions: {[a.name for a in p2]}")
