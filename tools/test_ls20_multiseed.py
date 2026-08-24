"""
Test ls20 multi-seed pathfinding across 5 seeds.
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

def test_ls20_multiseed():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    for seed in range(5):
        env = arcade.make("ls20", seed=seed)
        obs = env.reset()
        game = env._game
        
        avatar = game.gudziatsk
        rot_mod = game.current_level.get_sprites_by_tag("rhsxkxzdjz")[0]
        door = game.plrpelhym[0]
        walls = game.current_level.get_sprites_by_tag("ihdgageizm")
        
        path1 = bfs_path((avatar.x, avatar.y), (rot_mod.x, rot_mod.y), walls)
        path2 = bfs_path((rot_mod.x, rot_mod.y), (door.x, door.y), walls)
        
        total_path = (path1 or []) + (path2 or [])
        for a in total_path:
            obs = env.step(a)
            if obs.levels_completed > 0:
                break
        print(f"Seed {seed}: levels_completed={obs.levels_completed}, steps={len(total_path)}")
        scores.append(obs.levels_completed)
    print(f"LS20 Multi-Seed Scores: {scores}")

if __name__ == "__main__":
    test_ls20_multiseed()
