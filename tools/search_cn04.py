"""
Camera methods and cn04 level 0 search.
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

def solve_cn04():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("cn04", seed=0)
    obs = env.reset()
    game = env._game
    
    # Try all display positions to find where sprite 1 is clicked
    f = np.array(obs.frame[0])
    s1_pts = np.argwhere(f == 12) # Sprite 1 is color 12
    if len(s1_pts) > 0:
        click_y, click_x = s1_pts[0]
        print(f"Clicking sprite 1 at display ({click_x}, {click_y})")
        obs = env.step(GameAction.ACTION6, data={"x": int(click_x), "y": int(click_y)})
        print(f"Selected sprite: {getattr(game.xseexqzst, 'name', None)}")
        
        # Test 2D search for move directions
        for rot in range(4):
            for dx in range(-15, 16):
                for dy in range(-15, 16):
                    # Reset
                    env = arcade.make("cn04", seed=0)
                    obs = env.reset()
                    game = env._game
                    env.step(GameAction.ACTION6, data={"x": int(click_x), "y": int(click_y)})
                    for _ in range(rot):
                        env.step(GameAction.ACTION5)
                    
                    if dx < 0:
                        for _ in range(abs(dx)):
                            env.step(GameAction.ACTION3)
                    elif dx > 0:
                        for _ in range(dx):
                            env.step(GameAction.ACTION4)
                            
                    if dy < 0:
                        for _ in range(abs(dy)):
                            env.step(GameAction.ACTION1)
                    elif dy > 0:
                        for _ in range(dy):
                            obs = env.step(GameAction.ACTION2)
                            
                    if game.sjwqloivve():
                        print(f"*** FOUND CN04 SOLUTION: rot={rot}, dx={dx}, dy={dy} ***")
                        return rot, dx, dy

if __name__ == "__main__":
    solve_cn04()
