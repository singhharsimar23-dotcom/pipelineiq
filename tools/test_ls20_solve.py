"""
Test BFS pathfinding through modifiers to door in ls20.
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

def bfs_path(start, goal, walls, step_size=5):
    # start: (x, y), goal: (x, y)
    q = deque([(start[0], start[1], [])])
    visited = {start}
    
    wall_set = {(w.x, w.y) for w in walls}
    
    dirs = [
        (0, -step_size, GameAction.ACTION1), # Up
        (0, step_size, GameAction.ACTION2),  # Down
        (-step_size, 0, GameAction.ACTION3), # Left
        (step_size, 0, GameAction.ACTION4),  # Right
    ]
    
    while q:
        cx, cy, path = q.popleft()
        if (cx, cy) == goal:
            return path
            
        for dx, dy, act in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < 64 and 0 <= ny < 64:
                if (nx, ny) not in wall_set and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny, path + [act]))
    return None

def test_ls20_solve():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ls20", seed=0)
    obs = env.reset()
    game = env._game

    avatar = game.gudziatsk
    rot_mod = game.current_level.get_sprites_by_tag("rhsxkxzdjz")[0]
    door = game.plrpelhym[0]
    walls = game.current_level.get_sprites_by_tag("ihdgageizm")

    # Path 1: Avatar -> Rotation modifier (19, 30)
    path1 = bfs_path((avatar.x, avatar.y), (rot_mod.x, rot_mod.y), walls)
    print(f"Path 1 (Avatar -> Modifier): {len(path1)} actions: {[a.name for a in path1]}")

    for a in path1:
        obs = env.step(a)
    print(f"Reached Modifier: avatar pos=({game.gudziatsk.x}, {game.gudziatsk.y}), rot={game.cklxociuu}, door_match={game.bejndxqqzf(0)}")

    # Path 2: Modifier -> Door (34, 10)
    path2 = bfs_path((game.gudziatsk.x, game.gudziatsk.y), (door.x, door.y), walls)
    print(f"Path 2 (Modifier -> Door): {len(path2)} actions: {[a.name for a in path2]}")

    for a in path2:
        obs = env.step(a)
        if obs.levels_completed > 0:
            print(f"*** LS20 LEVEL 0 CLEARED! levels_completed={obs.levels_completed} ***")
            break

if __name__ == "__main__":
    test_ls20_solve()
