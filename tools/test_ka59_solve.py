"""
Test solving ka59 Level 0 via Sokoban push planner.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from collections import deque
import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_ka59_solve():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    avatar = game.prkgpeyexo
    block = game.current_level.get_sprites_by_tag("0022vrxelxosfy")[0]
    targets = game.current_level.get_sprites_by_tag("0010xzmuziohuf")
    
    print(f"Avatar: ({avatar.x}, {avatar.y})")
    print(f"Block: ({block.x}, {block.y})")
    for i, t in enumerate(targets):
        print(f"Target {i}: ({t.x}, {t.y})")

if __name__ == "__main__":
    test_ka59_solve()
