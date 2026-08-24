"""
Print exact actions executed in test_wa30_planner.py.
"""
from arcengine import GameAction
from collections import deque

def plan_path(start, target, blocked_cells):
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

actions = []
# 1. Herding Sheep at (16, 28)
path1 = plan_path((32, 48), (20, 28), blocked_cells={(16, 28), (32, 36), (44, 24)})
actions.extend(path1)
actions.append(GameAction.ACTION3)
actions.append(GameAction.ACTION5)
actions.extend([GameAction.ACTION4, GameAction.ACTION4, GameAction.ACTION4])
actions.append(GameAction.ACTION5)

# 2. Herding Sheep at (32, 36)
path2 = plan_path((32, 28), (32, 40), blocked_cells={(28, 28), (32, 36), (44, 24)})
actions.extend(path2)
actions.append(GameAction.ACTION1)
actions.append(GameAction.ACTION5)
actions.extend([GameAction.ACTION1, GameAction.ACTION1])
actions.append(GameAction.ACTION5)

# 3. Herding Sheep at (44, 24)
path3 = plan_path((32, 32), (44, 28), blocked_cells={(28, 28), (32, 28), (44, 24)})
actions.extend(path3)
actions.append(GameAction.ACTION1)
actions.append(GameAction.ACTION5)
actions.extend([GameAction.ACTION3, GameAction.ACTION3, GameAction.ACTION2])
actions.append(GameAction.ACTION5)

print(f"Total actions: {len(actions)}")
print([(a, {}) for a in actions])
