"""
Solve cn04 Level 0 via translation search.
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

def test_cn04_solve():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    for rot in range(4):
        for dx in range(-12, 13):
            for dy in range(-12, 13):
                env = arcade.make("cn04", seed=0)
                obs = env.reset()
                game = env._game
                
                # Select Piece 1 at (18, 18)
                env.step(GameAction.ACTION6, data={"x": 18, "y": 18})
                
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
                    print(f"*** FOUND CN04 LEVEL 0 WIN! rot={rot}, dx={dx}, dy={dy}, levels_completed={obs.levels_completed} ***")
                    return rot, dx, dy

if __name__ == "__main__":
    test_cn04_solve()
