"""
Trace pixel movements in re86 sliders.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

def trace_slider():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    game = env._game

    s0 = game.current_level.get_sprites_by_tag("0031cppcuvqlbi")[0]
    print(f"Initial s0: pos=({s0.x}, {s0.y}), shape={s0.pixels.shape}")
    pts = np.argwhere(s0.pixels == 11)
    print(f"Initial non-empty points in s0:\n{pts}")
    
    # Try ACTION1
    print("\nExecuting ACTION1 (UP)...")
    env.step(GameAction.ACTION1)
    pts1 = np.argwhere(s0.pixels == 11)
    print(f"Points after ACTION1:\n{pts1}")

    # Try ACTION1 again
    print("\nExecuting ACTION1 (UP) again...")
    env.step(GameAction.ACTION1)
    pts2 = np.argwhere(s0.pixels == 11)
    print(f"Points after 2nd ACTION1:\n{pts2}")

    # Try ACTION3 (LEFT)
    print("\nExecuting ACTION3 (LEFT)...")
    env.step(GameAction.ACTION3)
    pts3 = np.argwhere(s0.pixels == 11)
    print(f"Points after ACTION3:\n{pts3}")

if __name__ == "__main__":
    trace_slider()
