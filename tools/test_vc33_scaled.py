"""
Test scaled display coordinates in vc33.
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

def test_scaled_clicks():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    game = env._game

    valves = game.current_level.get_sprites_by_tag("0022jvmlspyigc")
    tokens = game.current_level.get_sprites_by_tag("0016uciqlhjlom")

    # Valve 0 is at grid (30, 12) -> display (60, 24)
    # Valve 1 is at grid (30, 16) -> display (60, 32)
    print("Initial token pos:", (tokens[0].x, tokens[0].y))
    
    print("\nClicking Valve 0 at display (60, 24)...")
    for i in range(1, 10):
        obs = env.step(GameAction.ACTION6, data={"x": 60, "y": 24})
        print(f"Click {i}: token pos=({tokens[0].x}, {tokens[0].y}), win={game.ielczunthe()}, levels_completed={obs.levels_completed}")
        if obs.levels_completed > 0:
            print(f"*** LEVEL CLEARED AT CLICK {i}! ***")
            break

    print("\nClicking Valve 1 at display (60, 32)...")
    for i in range(1, 10):
        obs = env.step(GameAction.ACTION6, data={"x": 60, "y": 32})
        print(f"Click {i}: token pos=({tokens[0].x}, {tokens[0].y}), win={game.ielczunthe()}, levels_completed={obs.levels_completed}")
        if obs.levels_completed > 0:
            print(f"*** LEVEL CLEARED AT CLICK {i}! ***")
            break

if __name__ == "__main__":
    test_scaled_clicks()
