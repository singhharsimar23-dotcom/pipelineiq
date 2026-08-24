"""
Trace valve clicks and token shifts in vc33.
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

def trace_vc33():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    game = env._game

    valves = game.current_level.get_sprites_by_tag("0022jvmlspyigc")
    tokens = game.current_level.get_sprites_by_tag("0016uciqlhjlom")

    print(f"Initial token pos: ({tokens[0].x}, {tokens[0].y})")
    
    # Try clicking Valve 1
    v1 = valves[1]
    cx1, cy1 = v1.x + v1.width // 2, v1.y + v1.height // 2
    print(f"\nClicking Valve 1 at ({cx1}, {cy1})...")
    obs = env.step(GameAction.ACTION6, data={"x": cx1, "y": cy1})
    print(f"Token pos: ({tokens[0].x}, {tokens[0].y}), levels_completed={obs.levels_completed}")

    # Try clicking Valve 0
    v0 = valves[0]
    cx0, cy0 = v0.x + v0.width // 2, v0.y + v0.height // 2
    print(f"\nClicking Valve 0 at ({cx0}, {cy0})...")
    obs = env.step(GameAction.ACTION6, data={"x": cx0, "y": cy0})
    print(f"Token pos: ({tokens[0].x}, {tokens[0].y}), levels_completed={obs.levels_completed}")

    # Try 5 clicks on Valve 0
    print("\nClicking Valve 0 multiple times...")
    for step in range(10):
        obs = env.step(GameAction.ACTION6, data={"x": cx0, "y": cy0})
        print(f"Step {step+1}: Token pos=({tokens[0].x}, {tokens[0].y}), levels_completed={obs.levels_completed}")
        if obs.levels_completed > 0:
            print("*** LEVEL CLEARED! ***")
            break

if __name__ == "__main__":
    trace_vc33()
