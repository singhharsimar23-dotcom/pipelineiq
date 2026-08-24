"""
Find walkable corridor graph for b1 in ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from collections import deque
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ka59", seed=0)
obs = env.reset()
game = env._game

# We can run a BFS exploration directly on the env:
# Available actions for current active block: [ACTION1 (Up), ACTION2 (Down), ACTION3 (Left), ACTION4 (Right)]
q = deque([( (18, 21), [] )])
visited = {(18, 21)}

while q:
    (bx, by), path = q.popleft()
    for act, name, dx, dy in [(GameAction.ACTION1, 'UP', 0, -3), (GameAction.ACTION2, 'DOWN', 0, 3), (GameAction.ACTION3, 'LEFT', -3, 0), (GameAction.ACTION4, 'RIGHT', 3, 0)]:
        # Test if act is valid from (bx, by)
        # Re-play path + act
        env = arcade.make("ka59", seed=0)
        obs = env.reset()
        env.step(GameAction.ACTION6, data={"x": 27, "y": 30})
        for a in path + [act]:
            obs = env.step(a)
        
        game = env._game
        s = game.prkgpeyexo
        npos = (s.x, s.y)
        if npos != (bx, by) and npos not in visited:
            visited.add(npos)
            print(f"Discovered reachable position: {npos} via path length {len(path)+1}")
            q.append((npos, path + [act]))

print(f"Total reachable positions for b1: {len(visited)}")
