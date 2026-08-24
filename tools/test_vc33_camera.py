"""
Check camera transformation and all sprite coordinates in vc33.
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

def test_camera():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    game = env._game

    print(f"Camera: width={game.camera.width}, height={game.camera.height}")
    print(f"Camera display_to_grid(30, 12) = {game.camera.display_to_grid(30, 12)}")
    
    # Try clicking all pixels in a 64x64 grid and find which pixels trigger any state change!
    for y in range(0, 64, 2):
        for x in range(0, 64, 2):
            env.reset()
            obs = env.step(GameAction.ACTION6, data={"x": x, "y": y})
            if game.ielczunthe() or obs.levels_completed > 0:
                print(f"WINNING CLICK FOUND at ({x}, {y})!")
                return (x, y)
    print("No single click win.")

if __name__ == "__main__":
    test_camera()
