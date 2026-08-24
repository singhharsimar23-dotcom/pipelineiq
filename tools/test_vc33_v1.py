"""
Test clicking both valves in vc33.
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

def test_both_valves():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    game = env._game

    valves = game.current_level.get_sprites_by_tag("0022jvmlspyigc")
    tokens = game.current_level.get_sprites_by_tag("0016uciqlhjlom")

    print(f"Testing Valve 1 at ({valves[1].x + 1}, {valves[1].y + 1})...")
    cx1, cy1 = valves[1].x + 1, valves[1].y + 1
    for i in range(1, 10):
        obs = env.step(GameAction.ACTION6, data={"x": cx1, "y": cy1})
        print(f"Valve 1 Click {i}: Token at ({tokens[0].x}, {tokens[0].y}), win={game.ielczunthe()}, levels_completed={obs.levels_completed}")
        if obs.levels_completed > 0:
            print(f"*** LEVEL CLEARED AT CLICK {i}! ***")
            break

if __name__ == "__main__":
    test_both_valves()
