"""
Inspect click coordinate transformation and sprite hit in vc33.
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

def check_hit():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    game = env._game

    valves = game.current_level.get_sprites_by_tag("0022jvmlspyigc")
    for i, v in enumerate(valves):
        print(f"Valve {i}: pos=({v.x}, {v.y}), size=({v.width}, {v.height})")
        for r in range(v.height):
            for c in range(v.width):
                gx = v.x + c
                gy = v.y + r
                hit = game.current_level.get_sprite_at(gx, gy)
                print(f"  Pixel ({gx}, {gy}): sprite={hit.name if hit else None}, tags={hit.tags if hit else None}")

    # Check display_to_grid
    for x in range(v.x, v.x + v.width + 1):
        for y in range(v.y, v.y + v.height + 1):
            disp = game.camera.grid_to_display(x, y)
            grid = game.camera.display_to_grid(x, y)
            print(f"Grid ({x}, {y}) -> Display {disp} -> Grid {grid}")

if __name__ == "__main__":
    check_hit()
