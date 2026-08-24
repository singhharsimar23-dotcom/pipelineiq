"""
Test exact transport from (8, 24) to (18, 10) in dc22.
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

def test_dc22_exact_solve():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    
    btn_b_disp = (48, 36)
    
    for seed in range(5):
        env = arcade.make("dc22", seed=seed)
        obs = env.reset()
        game = env._game
        
        # 1. Click button b to activate elevator bridge at (8, 24)
        env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})
        
        # 2. Walk Up to y=24 (3 steps ACTION1)
        env.step(GameAction.ACTION1)
        env.step(GameAction.ACTION1)
        env.step(GameAction.ACTION1)
        
        # 3. Walk Left onto exact elevator anchor (8, 24) (1 step ACTION3)
        env.step(GameAction.ACTION3)
        
        # 4. Click button b to transport elevator and avatar to (18, 10)
        env.step(GameAction.ACTION6, data={"x": btn_b_disp[0], "y": btn_b_disp[1]})
        
        # 5. Walk Right to Goal at (24, 10) (3 steps ACTION4)
        env.step(GameAction.ACTION4)
        env.step(GameAction.ACTION4)
        obs = env.step(GameAction.ACTION4)
        
        print(f"Seed {seed}: avatar at ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y}), win_check={game.smxyfelexa()}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"DC22 EXACT MULTI-SEED SCORES (Seeds 0-4): {scores}")

if __name__ == "__main__":
    test_dc22_exact_solve()
