"""
Probe movements of b1 after moving LEFT.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

arcade = Arcade(operation_mode=OperationMode.OFFLINE)

for name, act in [("UP", GameAction.ACTION1), ("DOWN", GameAction.ACTION2)]:
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game
    b_list = game.current_level.get_sprites_by_tag("0022vrxelxosfy")
    env.step(GameAction.ACTION6, data={"x": 27, "y": 30})
    env.step(GameAction.ACTION3) # Move Left to (15, 21)
    env.step(act)
    print(f"Action {name} from (15, 21): b1 pos = ({b_list[1].x}, {b_list[1].y})")
