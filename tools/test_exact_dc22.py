"""
Test clicking buttons with exact display coords in dc22.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
import numpy as np

def test_exact_dc22():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=0)
    obs = env.reset()
    game = env._game

    # Click btn_b and btn_a
    env.step(GameAction.ACTION6, data={"x": 48, "y": 36})
    env.step(GameAction.ACTION6, data={"x": 48, "y": 19})

    # Check walkable cells
    grid = np.zeros((32, 32), dtype=bool)
    for y in range(0, 32, 2):
        for x in range(0, 32, 2):
            grid[y, x] = (game.sxnzvaqltp(x, y, game.qnnpcoyzd) is not None)

    print("Walkable grid after exact clicks:")
    for y in range(0, 32, 2):
        print(f"{y:2d}: " + "".join("#" if grid[y, x] else "." for x in range(0, 32, 2)))

    # BFS from (10, 30) to (24, 10)
    from collections import deque
    q = deque([(10, 30, [])])
    visited = {(10, 30)}
    dirs = [(0, -2, GameAction.ACTION1), (0, 2, GameAction.ACTION2), (-2, 0, GameAction.ACTION3), (2, 0, GameAction.ACTION4)]

    while q:
        cx, cy, path = q.popleft()
        if (cx, cy) == (24, 10):
            print(f"*** FOUND BFS PATH TO GOAL! Length: {len(path)} ***")
            for act in path:
                obs = env.step(act)
            print(f"Final avatar pos: ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y}), win_check={game.smxyfelexa()}, levels_completed={obs.levels_completed}")
            break
        for dx, dy, act in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < 32 and 0 <= ny < 32 and grid[ny, nx] and (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny, path + [act]))

if __name__ == "__main__":
    test_exact_dc22()
