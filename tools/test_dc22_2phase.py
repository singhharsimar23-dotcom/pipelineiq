"""
Test exact 2-phase moving bridge transport in dc22.
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

def test_dc22_2phase():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=0)
    obs = env.reset()
    game = env._game

    btn_b_disp = (48, 36)

    # Phase 1: Click button b to activate bridge at (8, 24)
    print("Phase 1: Click button b...")
    env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})

    # Phase 2: Walk Up onto bridge at (10, 24) (or 8, 24)
    # Start is (10, 30). Move Up: (10, 28) -> (10, 26) -> (10, 24) -> (8, 24)
    print("Phase 2: Walk onto bridge...")
    env.step(GameAction.ACTION1) # (10, 28)
    env.step(GameAction.ACTION1) # (10, 26)
    env.step(GameAction.ACTION1) # (10, 24)
    print(f"Avatar pos on bridge: ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y})")

    # Phase 3: Click button b to transport bridge to (18, 10)
    print("Phase 3: Click button b to transport...")
    env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})
    print(f"Avatar pos after transport: ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y})")

    # Phase 4: Walk Right from (18, 10) to (24, 10)
    print("Phase 4: Walk to goal...")
    for i in range(4):
        obs = env.step(GameAction.ACTION4)
        print(f"  Step {i+1} Right: pos=({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y}), win_check={game.smxyfelexa()}, levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    test_dc22_2phase()
