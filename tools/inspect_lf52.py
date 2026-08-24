"""
Diagnostic probe for lf52 Level 0 entities and mechanics.
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

def inspect_lf52():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("lf52", seed=0)
    obs = env.reset()
    game = env._game
    world = game.ikhhdzfmarl

    print("=== LF52 LEVEL 0 ENTITIES ===")
    print("Available actions:", getattr(obs, "available_actions", []))
    print(f"World state attributes: {dir(world)}")
    print(f"iajuzrgttrv (win flag): {world.iajuzrgttrv}")
    
    # Render frame
    f = np.array(obs.frame[0])
    print(f"Frame shape: {f.shape}, unique colors: {np.unique(f)}")

if __name__ == "__main__":
    inspect_lf52()
