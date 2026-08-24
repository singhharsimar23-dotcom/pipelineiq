"""
Test navigating g50t Level 0 to goal.
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

def test_g50t():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("g50t", seed=0)
    obs = env.reset()
    game = env._game

    # Avatar starts at (13, 7). Goal at (43, 49).
    # Try all 4 directions step-by-step
    print(f"Start pos: ({game.vgwycxsxjz.dzxunlkwxt.x}, {game.vgwycxsxjz.dzxunlkwxt.y})")
    
    # Try moving Right:
    for i in range(5):
        obs = env.step(GameAction.ACTION4)
        print(f"Move Right {i+1}: pos=({game.vgwycxsxjz.dzxunlkwxt.x}, {game.vgwycxsxjz.dzxunlkwxt.y}), win={game.mrzduxdbbk()}")

    # Try moving Down:
    for i in range(7):
        obs = env.step(GameAction.ACTION2)
        print(f"Move Down {i+1}: pos=({game.vgwycxsxjz.dzxunlkwxt.x}, {game.vgwycxsxjz.dzxunlkwxt.y}), win={game.mrzduxdbbk()}, levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    test_g50t()
