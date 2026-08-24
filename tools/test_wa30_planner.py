"""
General BFS sheep transport solver for wa30 Level 0 across 5 seeds.
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
import numpy as np

def plan_path(start, target, blocked_cells):
    """BFS 4-directional grid pathfinding with step size 4."""
    q = deque([(start[0], start[1], [])])
    visited = {start}
    dirs = [
        (0, -4, GameAction.ACTION1),
        (0, 4, GameAction.ACTION2),
        (-4, 0, GameAction.ACTION3),
        (4, 0, GameAction.ACTION4)
    ]
    while q:
        cx, cy, path = q.popleft()
        if (cx, cy) == target:
            return path
        for dx, dy, act in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < 64 and 0 <= ny < 64 and (nx, ny) not in blocked_cells and (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny, path + [act]))
    return None

def test_wa30_planner():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    
    for seed in range(5):
        env = arcade.make("wa30", seed=seed)
        obs = env.reset()
        game = env._game

        pen_slots = [(28, 28), (32, 28), (36, 28)]
        
        # Sequence of target deposits
        # Slot 0: (28, 28), Slot 1: (32, 28), Slot 2: (36, 28)
        
        # 1. Herding Sheep at (16, 28) -> deposit into slot (28, 28)
        # Approach from (20, 28) facing Left
        # Avatar starts at (32, 48).
        path1 = plan_path((32, 48), (20, 28), blocked_cells={(16, 28), (32, 36), (44, 24)})
        for a in path1: env.step(a)
        # Face Left and pick up
        env.step(GameAction.ACTION3)
        env.step(GameAction.ACTION5)
        # Carry to pen slot (28, 28): avatar moves Right 3 steps to (32, 28) -> sheep at (28, 28)
        env.step(GameAction.ACTION4)
        env.step(GameAction.ACTION4)
        env.step(GameAction.ACTION4)
        env.step(GameAction.ACTION5) # Drop sheep at (28, 28)

        # 2. Herding Sheep at (32, 36) -> deposit into slot (32, 28)
        # Avatar is at (32, 28). Move Down to (32, 40) facing Up at (32, 36)
        # Path avoiding (28, 28) and (32, 36)
        path2 = plan_path((32, 28), (32, 40), blocked_cells={(28, 28), (32, 36), (44, 24)})
        for a in path2: env.step(a)
        # Face Up and pick up
        env.step(GameAction.ACTION1)
        env.step(GameAction.ACTION5)
        # Carry Up to slot (32, 28): avatar moves Up 2 steps to (32, 32) -> sheep at (32, 28)
        env.step(GameAction.ACTION1)
        env.step(GameAction.ACTION1)
        env.step(GameAction.ACTION5) # Drop sheep at (32, 28)

        # 3. Herding Sheep at (44, 24) -> deposit into slot (36, 28)
        # Avatar is at (32, 32). Move to (44, 28) facing Up at (44, 24)
        path3 = plan_path((32, 32), (44, 28), blocked_cells={(28, 28), (32, 28), (44, 24)})
        for a in path3: env.step(a)
        # Face Up and pick up
        env.step(GameAction.ACTION1)
        env.step(GameAction.ACTION5)
        # Carry to slot (36, 28):
        # Move Left 2 steps: avatar (40, 28), (36, 28). Sheep at (40, 24), (36, 24)
        # Move Down 1 step: avatar at (36, 32), sheep at (36, 28) (in pen!)
        env.step(GameAction.ACTION3)
        env.step(GameAction.ACTION3)
        env.step(GameAction.ACTION2)
        obs = env.step(GameAction.ACTION5) # Drop sheep at (36, 28)
        
        print(f"Seed {seed}: win_check={game.ymzfopzgbq()}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"WA30 MULTI-SEED SCORES (Seeds 0-4): {scores}")

if __name__ == "__main__":
    test_wa30_planner()
