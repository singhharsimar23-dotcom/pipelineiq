"""
Print all reachable positions and paths for b1 in ka59.
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

q = deque([( (18, 21), [] )])
visited = {(18, 21): []}

while q:
    (bx, by), path = q.popleft()
    for act in [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]:
        # Test if act is valid from (bx, by)
        env = arcade.make("ka59", seed=0)
        obs = env.reset()
        env.step(GameAction.ACTION6, data={"x": 27, "y": 30})
        for a in path + [act]:
            obs = env.step(a)
        
        game = env._game
        s = game.prkgpeyexo
        npos = (s.x, s.y)
        if npos != (bx, by) and npos not in visited:
            visited[npos] = path + [act]
            print(f"Reachable: {npos} via {[a.name for a in visited[npos]]}")
            q.append((npos, visited[npos]))

print(f"\nAll reachable positions ({len(visited)}):")
for pos, p in visited.items():
    if abs(pos[0] - 36) <= 3 and abs(pos[1] - 18) <= 3:
        print(f"  NEAR TARGET 1 (36, 18): pos={pos}, path len={len(p)}")
