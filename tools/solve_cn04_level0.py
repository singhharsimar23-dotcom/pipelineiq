"""
Find solution for cn04 Level 0.
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

def solve_cn04_level0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("cn04", seed=0)
    obs = env.reset()
    game = env._game
    
    # Let's inspect camera mapping
    print("Camera scale and padding:")
    print(f"  Camera: scale={game.camera.scale}, x_offset={game.camera.x_offset}, y_offset={game.camera.y_offset}")
    
    # Try selecting sprite 1 and moving it
    # Sprite 1 pos=(3, 3), center in display coords:
    dx, dy = game.camera.grid_to_display(5, 5)
    print(f"Display coords for (5, 5): ({dx}, {dy})")
    
    # Select sprite 1
    obs = env.step(GameAction.ACTION6, data={"x": dx, "y": dy})
    print(f"Selected sprite: {getattr(game.xseexqzst, 'name', None)}")
    
    # Move sprite 1 towards sprite 2
    # Sprite 1 pos=(3, 3), Sprite 2 pos=(12, 9)
    # Let's test moving right (ACTION4) and down (ACTION2)
    for _ in range(8):
        obs = env.step(GameAction.ACTION4)
    for _ in range(6):
        obs = env.step(GameAction.ACTION2)
        
    print(f"After moves: levels_completed={obs.levels_completed}, win_check={game.sjwqloivve()}")

if __name__ == "__main__":
    solve_cn04_level0()
