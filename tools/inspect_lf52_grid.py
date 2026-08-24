"""
Inspect lf52 Level 0 grid, avatar, boxes, and goals.
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

def inspect_lf52_grid():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("lf52", seed=0)
    obs = env.reset()
    game = env._game
    world = game.ikhhdzfmarl

    print(f"Level index: {world.whtqurkphir}")
    print(f"Entities in world:")
    for entity in world.hncnfaqaddg.all_sprites():
        print(f"  Entity: name={entity.name}, pos=({entity.x}, {entity.y})")

    # Let's test a simple action sequence
    # Avatar is at some position, try moving around
    for act in [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]:
        env = arcade.make("lf52", seed=0)
        obs = env.reset()
        obs = env.step(act)
        print(f"Action {act.name} -> levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    inspect_lf52_grid()
