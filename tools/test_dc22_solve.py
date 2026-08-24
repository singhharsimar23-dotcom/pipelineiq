"""
DC22 - navigate player to goal using BFS over 4-directional movement + click actions.
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

def bfs_path(sx, sy, gx, gy, step=2):
    """BFS 4-directional path from (sx,sy) to (gx,gy) in grid coords."""
    q = deque([((sx, sy), [])])
    vis = {(sx, sy)}
    dirs = [(0, -step, GameAction.ACTION1), (0, step, GameAction.ACTION2),
            (-step, 0, GameAction.ACTION3), (step, 0, GameAction.ACTION4)]
    while q:
        (cx, cy), path = q.popleft()
        if cx == gx and cy == gy:
            return path
        for dx, dy, act in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < 64 and 0 <= ny < 64 and (nx, ny) not in vis:
                vis.add((nx, ny))
                q.append(((nx, ny), path + [act]))
    return []

def test_dc22():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []

    for seed in range(5):
        env = arcade.make("dc22", seed=seed)
        obs = env.reset()
        game = env._game

        px, py = game.qnnpcoyzd.x, game.qnnpcoyzd.y
        gx, gy = game.hfuqkxulm.x, game.hfuqkxulm.y
        print(f"\nSeed {seed}: player=({px},{py}), goal=({gx},{gy})")

        # There are clickable sprites that may open paths — check click buttons first
        buezna_sprites = game.current_level.get_sprites_by_tag("sys_click")
        for bs in buezna_sprites:
            obs = env.step(GameAction.ACTION6, {"x": bs.x + bs.width // 2, "y": bs.y + bs.height // 2})
            print(f"  Clicked {bs.name} at ({bs.x},{bs.y}): player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y}), win={game.smxyfelexa()}")

        # Now BFS navigate to goal
        px, py = game.qnnpcoyzd.x, game.qnnpcoyzd.y
        gx, gy = game.hfuqkxulm.x, game.hfuqkxulm.y
        path = bfs_path(px, py, gx, gy, step=2)
        print(f"  BFS path length: {len(path)}")
        for act in path:
            obs = env.step(act)
            if game.smxyfelexa() or obs.levels_completed > 0:
                print(f"  WIN: levels={obs.levels_completed}, pos=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
                break
        scores.append(obs.levels_completed)
        print(f"  Final: levels={obs.levels_completed}")

    print(f"\nDC22 SCORES: {scores}")

if __name__ == "__main__":
    test_dc22()
