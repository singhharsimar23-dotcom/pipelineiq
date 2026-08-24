"""
Test solving tr87 Level 0 via exact grammar alignment.
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

def test_tr87_solve():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    
    # Target sequence: [B3, B2, B6, B5, B1]
    for seed in range(5):
        env = arcade.make("tr87", seed=seed)
        obs = env.reset()
        game = env._game
        
        # Token 0: B1 -> B3: 2x ACTION2
        env.step(GameAction.ACTION2)
        env.step(GameAction.ACTION2)
        
        # Move cursor to Token 1: 1x ACTION4
        env.step(GameAction.ACTION4)
        # Token 1: B7 -> B2: 2x ACTION2
        env.step(GameAction.ACTION2)
        env.step(GameAction.ACTION2)
        
        # Move cursor to Token 2: 1x ACTION4
        env.step(GameAction.ACTION4)
        # Token 2: B2 -> B6: 3x ACTION1 (since kjgicbtgrt = 7: 2 - 1 = 1, 1 - 1 = 7, 7 - 1 = 6)
        env.step(GameAction.ACTION1)
        env.step(GameAction.ACTION1)
        env.step(GameAction.ACTION1)
        
        # Move cursor to Token 3: 1x ACTION4
        env.step(GameAction.ACTION4)
        # Token 3: B4 -> B5: 1x ACTION2
        env.step(GameAction.ACTION2)
        
        # Move cursor to Token 4: 1x ACTION4
        env.step(GameAction.ACTION4)
        # Token 4: B6 -> B1: 2x ACTION2 (6 + 1 = 7, 7 + 1 = 1)
        env.step(GameAction.ACTION2)
        obs = env.step(GameAction.ACTION2)
        
        print(f"Seed {seed}: output tokens={[s.name for s in game.ztgmtnnufb]}, win_check={game.bsqsshqpox()}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"TR87 MULTI-SEED SCORES (Seeds 0-4): {scores}")

if __name__ == "__main__":
    test_tr87_solve()
