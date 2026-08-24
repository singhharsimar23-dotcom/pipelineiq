"""
Test elevator / moving bridge transportation mechanic in dc22 Level 0.
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

def test_bridge_transport():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=0)
    obs = env.reset()
    game = env._game

    btn_a_disp = (48, 19)
    btn_b_disp = (48, 36)

    # Initial state: avatar at (10, 30)
    # Move Up to (10, 24) onto bridge tile:
    for _ in range(3):
        env.step(GameAction.ACTION1)
    print(f"Avatar pos before click b: ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y})")

    # Click button b while standing on bridge tile:
    env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})
    print(f"Avatar pos after click b: ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y})")

    # Now avatar is transported to (18, 10)!
    # Move Right from 18 to 24 (Goal is at 24, 10):
    for i in range(3):
        obs = env.step(GameAction.ACTION4)
        print(f"Move Right {i+1} -> pos: ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y}), levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    test_bridge_transport()
