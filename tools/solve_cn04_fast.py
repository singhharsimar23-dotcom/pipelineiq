"""
Find analytical alignment for cn04 Level 0.
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

def solve_cn04_fast():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("cn04", seed=0)
    obs = env.reset()
    game = env._game
    
    # Sprite 1 initial grid pos: (3, 3), rotation: 90
    # Sprite 2 initial grid pos: (12, 9), rotation: 0
    # Connector 8 of Sprite 2 is at grid (12, 11) and (12, 13)
    # Let's test rotating Sprite 1 and moving it
    
    for target_rot in [0, 90, 180, 270]:
        for tx in range(0, 20):
            for ty in range(0, 20):
                # Reset simulation
                s1 = game.current_level.get_sprites()[0]
                s2 = game.current_level.get_sprites()[1]
                
                # Check connector overlap
                # Base s1 pixels has 8 at (1, 5) and (3, 5)
                # If s1 is at (tx, ty) with target_rot:
                # compute rotated coords
                rot_steps = ((target_rot - 90) % 360) // 90
                
                # Let's test in-game directly with RESET:
                env.step(GameAction.RESET)
                env.step(GameAction.ACTION6, data={"x": 18, "y": 18}) # select s1
                for _ in range(rot_steps):
                    env.step(GameAction.ACTION5)
                
                # Current s1 pos is (3, 3)
                dx = tx - 3
                dy = ty - 3
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
                    print(f"*** FOUND WIN! target_rot={target_rot}, rot_steps={rot_steps}, tx={tx}, ty={ty}, dx={dx}, dy={dy} ***")
                    print(f"levels_completed={obs.levels_completed}")
                    return rot_steps, dx, dy

if __name__ == "__main__":
    solve_cn04_fast()
