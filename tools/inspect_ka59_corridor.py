"""
Inspect obstacles along y=21 in ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import numpy as np

def inspect_ka59_corridor():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    print("=== SPRITES IN KA59 LEVEL 0 ===")
    for s in game.current_level.get_sprites():
        if not s.name.startswith("explode"):
            print(f"Sprite: name={s.name}, pos=({s.x}, {s.y}), size=({s.width}, {s.height}), tags={s.tags}")

if __name__ == "__main__":
    inspect_ka59_corridor()
