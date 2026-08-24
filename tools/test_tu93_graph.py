"""
Test BFS graph solver on tu93.
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

def solve_tu93(seed):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("tu93", seed=seed)
    obs = env.reset()
    game = env._game
    
    maze_sprite = game.current_level.get_sprites_by_tag("0005uvnhiglpvh")[0]
    avatar = game.current_level.get_sprites_by_tag("0017unajnymcki")[0]
    exit_sprite = game.current_level.get_sprites_by_tag("0015msvpvzxhqf")[0]
    
    print(f"\n--- Seed {seed} ---")
    print(f"Maze at ({maze_sprite.x}, {maze_sprite.y}) shape {maze_sprite.pixels.shape}")
    print(f"Avatar at ({avatar.x}, {avatar.y})")
    print(f"Exit at ({exit_sprite.x}, {exit_sprite.y})")
    
    # Corridor pixels in maze_sprite where pixels == 2
    # In maze relative coords:
    # avatar rel pos:
    ax_rel = avatar.x - maze_sprite.x
    ay_rel = avatar.y - maze_sprite.y
    gx_rel = exit_sprite.x - maze_sprite.x
    gy_rel = exit_sprite.y - maze_sprite.y
    
    print(f"Rel start: ({ax_rel}, {ay_rel}), Rel goal: ({gx_rel}, {gy_rel})")
    
    # Step size: in tu93.py, let's find hwthhtvyki
    # In pixels array, let's see which values == 2
    # Look at the pixels matrix:
    # rows where pixels == 2 form grid
    h, w = maze_sprite.pixels.shape
    
    # Let's find valid grid step
    # We can do BFS on (x, y) with step size 3 or 6:
    step_size = 3
    
    q = deque([((ax_rel, ay_rel), [])])
    visited = {(ax_rel, ay_rel)}
    
    dirs = [
        (-step_size, 0, GameAction.ACTION1), # UP: dy = -step
        (step_size, 0, GameAction.ACTION2),  # DOWN: dy = +step
        (0, -step_size, GameAction.ACTION3), # LEFT: dx = -step
        (0, step_size, GameAction.ACTION4),  # RIGHT: dx = +step
    ]
    
    best_path = None
    while q:
        (cy, cx), path = q.popleft()
        if (cy, cx) == (gy_rel, gx_rel):
            best_path = path
            break
            
        for dy, dx, act in dirs:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and (ny, nx) not in visited:
                # Check if corridor
                if maze_sprite.pixels[ny, nx] == 2:
                    visited.add((ny, nx))
                    q.append(((ny, nx), path + [act]))
                    
    print(f"BFS path found: {len(best_path) if best_path else 'None'}")
    if best_path:
        # Note: Each move in tu93 takes animation frames (or multiple steps)
        # Let's execute the path and see
        for i, act in enumerate(best_path):
            obs = env.step(act)
            # Drain animation if needed
            while game.kdkehgjrzq != 0:
                obs = env.step(act) # or step with null / previous
            if obs.levels_completed > 0:
                print(f"WIN at move {i}! levels_completed={obs.levels_completed}")
                break
        print(f"Final levels_completed: {obs.levels_completed}")
        return obs.levels_completed
    return 0

for s in range(5):
    solve_tu93(s)
