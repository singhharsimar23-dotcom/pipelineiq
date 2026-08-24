"""
Test Level 1 solution in re86.
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

def test_level1():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    
    # Solve Level 0:
    for _ in range(7): obs = env.step(GameAction.ACTION1)
    for _ in range(4): obs = env.step(GameAction.ACTION4)
    obs = env.step(GameAction.ACTION5)
    for _ in range(6): obs = env.step(GameAction.ACTION1)
    for _ in range(2): obs = env.step(GameAction.ACTION3)
    
    print(f"Level 0 cleared, state: levels_completed={obs.levels_completed}")
    
    # Level 1 execution:
    # Active slider is Slider 0 (color 12)
    # Slider 0: dy = +30 (+10 DOWN: ACTION2), dx = -18 (-6 LEFT: ACTION3)
    print("Executing Slider 0 (color 12)...")
    for _ in range(10): obs = env.step(GameAction.ACTION2)
    for _ in range(6): obs = env.step(GameAction.ACTION3)
    
    # Switch to Slider 1 (color 13)
    print("Switching to Slider 1 (color 13)...")
    obs = env.step(GameAction.ACTION5)
    # Slider 1: dy = -21 (-7 UP: ACTION1), dx = -18 (-6 LEFT: ACTION3)
    for _ in range(7): obs = env.step(GameAction.ACTION1)
    for _ in range(6): obs = env.step(GameAction.ACTION3)

    # Switch to Slider 2 (color 9)
    print("Switching to Slider 2 (color 9)...")
    obs = env.step(GameAction.ACTION5)
    # Slider 2: dy = +6 (+2 DOWN: ACTION2), dx = -21 (-7 LEFT: ACTION3)
    for _ in range(2): obs = env.step(GameAction.ACTION2)
    for _ in range(7):
        obs = env.step(GameAction.ACTION3)
        if obs.levels_completed > 1:
            print(f"*** LEVEL 1 CLEARED! levels_completed={obs.levels_completed} ***")
            break

    print(f"Final state: levels_completed={obs.levels_completed}, state={obs.state}")
    print(f"Game win condition: {env._game.jeiavrvavi()}")

if __name__ == "__main__":
    test_level1()
