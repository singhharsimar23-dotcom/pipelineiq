"""
Test complete continuous walking path in dc22 Level 0.
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

def test_dc22_walk_win():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    
    btn_a_disp = (48, 19)
    btn_b_disp = (48, 36)
    
    for seed in range(5):
        env = arcade.make("dc22", seed=seed)
        obs = env.reset()
        game = env._game
        
        # 1. Click button b and button a
        env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})
        env.step(GameAction.ACTION6, data={"x": btn_a_disp[0], "y": btn_a_disp[1]})
        
        # 2. Walk path:
        # Up from (10, 30) to (10, 20) -> 5 steps Up (ACTION1)
        for _ in range(5):
            env.step(GameAction.ACTION1)
            
        # Right to (14, 20) -> 2 steps Right (ACTION4)
        for _ in range(2):
            env.step(GameAction.ACTION4)
            
        # Up to (14, 14) -> 3 steps Up (ACTION1)
        for _ in range(3):
            env.step(GameAction.ACTION1)
            
        # Right to (20, 14) -> 3 steps Right (ACTION4)
        for _ in range(3):
            env.step(GameAction.ACTION4)
            
        # Up to (20, 10) -> 2 steps Up (ACTION1)
        for _ in range(2):
            env.step(GameAction.ACTION1)
            
        # Right to (24, 10) -> 2 steps Right (ACTION4)
        for _ in range(2):
            obs = env.step(GameAction.ACTION4)
            
        print(f"Seed {seed}: avatar at ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y}), win_check={game.smxyfelexa()}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"DC22 MULTI-SEED SCORES (Seeds 0-4): {scores}")

if __name__ == "__main__":
    test_dc22_walk_win()
