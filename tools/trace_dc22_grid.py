"""
Trace dc22 bridge states and walkable cells.
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

def trace_dc22():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=0)
    obs = env.reset()
    game = env._game

    btn_a = (48, 9)
    btn_b = (48, 26)

    # Click btn_a
    obs = env.step(GameAction.ACTION6, data={"x": btn_a[0], "y": btn_a[1]})
    print(f"After btn_a: avatar at ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y})")
    
    # Try moving avatar around in full 2D BFS:
    from collections import deque
    # We can test valid moves by probing try_move_sprite or checking sxnzvaqltp
    # Let's inspect sxnzvaqltp for all (x, y) on left side (x <= 30)
    walkable = np.zeros((32, 32), dtype=bool)
    for y in range(0, 32, 2):
        for x in range(0, 32, 2):
            w = game.sxnzvaqltp(x, y, game.qnnpcoyzd) is not None
            walkable[y, x] = w
            
    print("Walkable grid after btn_a:")
    for y in range(0, 32, 2):
        print(f"{y:2d}: " + "".join("#" if walkable[y, x] else "." for x in range(0, 32, 2)))

    # Also check with btn_b
    obs = env.step(GameAction.ACTION6, data={"x": btn_b[0], "y": btn_b[1]})
    for y in range(0, 32, 2):
        for x in range(0, 32, 2):
            w = game.sxnzvaqltp(x, y, game.qnnpcoyzd) is not None
            walkable[y, x] = w
            
    print("\nWalkable grid after btn_a + btn_b:")
    for y in range(0, 32, 2):
        print(f"{y:2d}: " + "".join("#" if walkable[y, x] else "." for x in range(0, 32, 2)))

if __name__ == "__main__":
    trace_dc22()
