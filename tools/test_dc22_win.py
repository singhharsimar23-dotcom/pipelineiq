"""
Test dc22 Level 0 complete solution.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from collections import deque
import numpy as np

def test_dc22_win():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    
    # Buttons:
    # Button a: (48, 9), Button b: (48, 26)
    for seed in range(5):
        env = arcade.make("dc22", seed=seed)
        obs = env.reset()
        game = env._game
        
        # Click button b and button a
        env.step(GameAction.ACTION6, data={"x": 48, "y": 26})
        env.step(GameAction.ACTION6, data={"x": 48, "y": 9})
        
        # Walk from (10, 30) to (24, 10):
        # Step 1: Up from 30 to 20: 5 steps Up (ACTION1)
        for _ in range(5):
            env.step(GameAction.ACTION1)
        # Step 2: Right from 10 to 18: 4 steps Right (ACTION4)
        for _ in range(4):
            env.step(GameAction.ACTION4)
        # Step 3: Up from 20 to 10: 5 steps Up (ACTION1)
        for _ in range(5):
            env.step(GameAction.ACTION1)
        # Step 4: Right from 18 to 24: 3 steps Right (ACTION4)
        for _ in range(3):
            obs = env.step(GameAction.ACTION4)
            
        print(f"Seed {seed}: avatar at ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y}), win_check={game.smxyfelexa()}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"DC22 MULTI-SEED SCORES (Seeds 0-4): {scores}")

if __name__ == "__main__":
    test_dc22_win()
