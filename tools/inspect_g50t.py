"""
Inspect g50t Level 0 entities and mechanics.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import numpy as np

def inspect_g50t():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("g50t", seed=0)
    obs = env.reset()
    game = env._game

    print("=== G50T LEVEL 0 ===")
    print("Available actions:", getattr(obs, "available_actions", []))
    for s in game.current_level.get_sprites():
        print(f"Sprite: name={s.name}, pos=({s.x}, {s.y}), size=({s.width}, {s.height}), tags={s.tags}")
        
    print(f"Avatar pos: ({game.vgwycxsxjz.dzxunlkwxt.x}, {game.vgwycxsxjz.dzxunlkwxt.y})")
    print(f"Initial win check: {game.mrzduxdbbk()}")

if __name__ == "__main__":
    inspect_g50t()
