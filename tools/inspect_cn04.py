"""
Inspect cn04 Level 0 sprites, positions, connectors, and solution.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
import numpy as np

def inspect_cn04():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("cn04", seed=0)
    obs = env.reset()
    game = env._game
    
    print(f"Grid size: {game.current_level.grid_size}")
    print(f"Sprites in cn04 Level 0:")
    for s in game.current_level.get_sprites():
        print(f"  Sprite: name={s.name}, pos=({s.x}, {s.y}), size=({s.width}, {s.height}), visible={s.is_visible}, rotation={s.rotation}")
        # Find connectors 8 and 13
        p = s.pixels
        conns_8 = np.argwhere(p == 8)
        conns_13 = np.argwhere(p == 13)
        print(f"    Connectors 8 at: {conns_8.tolist()}, Connectors 13 at: {conns_13.tolist()}")

if __name__ == "__main__":
    inspect_cn04()
