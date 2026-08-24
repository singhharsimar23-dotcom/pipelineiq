"""
Test 3 valve clicks on vc33 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_vc33_solve():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    game = env._game

    print("Initial state: win=", game.ielczunthe())
    
    # Click valve 0 at (31, 13) 3 times:
    for i in range(1, 10):
        obs = env.step(GameAction.ACTION6, data={"x": 31, "y": 13})
        print(f"Click {i}: win={game.ielczunthe()}, levels_completed={obs.levels_completed}")
        if obs.levels_completed > 0:
            print(f"*** LEVEL 0 CLEARED AT CLICK {i}! ***")
            break

if __name__ == "__main__":
    test_vc33_solve()
