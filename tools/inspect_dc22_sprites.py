"""
Inspect buttons and crane in dc22 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import numpy as np

def inspect_dc22_sprites():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=0)
    obs = env.reset()
    game = env._game

    for s in game.current_level.get_sprites():
        print(f"Sprite: name={s.name}, pos=({s.x}, {s.y}), size=({s.width}, {s.height}), tags={s.tags}")

if __name__ == "__main__":
    inspect_dc22_sprites()
