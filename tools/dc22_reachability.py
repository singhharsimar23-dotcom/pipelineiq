"""
DC22 - try to get player to align with tovemc position (8,24) using various routes.
Also check if the player needs to be at a specific offset within the tovemc.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

# Player at (10,30), tovemc-plelvb1 at (8,24), size 4x4.
# Try from BELOW: move player left to x=8, then up
# But tovemc is at y=24 occupying rows 24-27.
# Player moving from y=28 up 1 step (2 pixels) goes to y=26.
# That would overlap with tovemc rows 24-27. So collision at y=28-2=26.
# Player can only reach y=26 when approaching from below (y=28).
# This means player CANNOT stand on tovemc from the bottom (collision).

# Check if player can reach tovemc from the RIGHT side: player at (12,24) -> left to (10,24) -> left to (8,24)?
# From right: need y=24. Player at (10,30) - go up to y=24 via RIGHT side.

def test_path(seed, actions):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=seed)
    obs = env.reset()
    game = env._game
    
    positions = [(game.qnnpcoyzd.x, game.qnnpcoyzd.y)]
    for act in actions:
        obs = env.step(act)
        positions.append((game.qnnpcoyzd.x, game.qnnpcoyzd.y))
    return positions, obs.levels_completed

U = GameAction.ACTION1
D = GameAction.ACTION2
L = GameAction.ACTION3
R = GameAction.ACTION4
C6 = GameAction.ACTION6

paths = [
    # Try going RIGHT first to get past x=8 wall, then UP, then LEFT
    ("R3-U3-L3", [R,R,R, U,U,U, L,L,L]),
    # Try going DOWN then around
    ("D3-R3-U6-L3", [D,D,D, R,R,R, U,U,U,U,U,U, L,L,L]),
    # From right side approach at row 24
    ("R-U3-L3-U3", [R, U,U,U, L,L,L, U,U,U]),
    # try up then right
    ("U1-R3-U2", [U, R,R,R, U,U]),
]

for label, moves in paths:
    positions, lvl = test_path(0, moves)
    pos_str = " -> ".join([f"({p[0]},{p[1]})" for p in positions])
    print(f"[{label}] {pos_str} | final_lvl={lvl}")

# Also check: what positions can the player reach at all?
print("\n--- Reachability scan ---")
arcade2 = Arcade(operation_mode=OperationMode.OFFLINE)
env2 = arcade2.make("dc22", seed=0)
obs2 = env2.reset()
game2 = env2._game

from collections import deque

start = (game2.qnnpcoyzd.x, game2.qnnpcoyzd.y)
visited = {start}
q = deque([(start, [])])
reachable = [start]

while q:
    (px, py), path = q.popleft()
    if len(path) > 20:
        continue
    for act in [U, D, L, R]:
        env3 = arcade2.make("dc22", seed=0)
        obs3 = env3.reset()
        g3 = env3._game
        for pa in path:
            env3.step(pa)
        env3.step(act)
        npos = (g3.qnnpcoyzd.x, g3.qnnpcoyzd.y)
        if npos not in visited:
            visited.add(npos)
            reachable.append(npos)
            q.append((npos, path + [act]))

print(f"All reachable positions: {sorted(reachable)}")
