"""
Test cn04 multi-seed invariance across 5 seeds.
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

def test_cn04_multi_seed():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    
    for seed in range(5):
        env = arcade.make("cn04", seed=seed)
        obs = env.reset()
        
        # Select piece 1
        env.step(GameAction.ACTION6, data={"x": 18, "y": 18})
        # Rotate 3 times
        for _ in range(3):
            env.step(GameAction.ACTION5)
        # Move right 4
        for _ in range(4):
            env.step(GameAction.ACTION4)
        # Move down 7
        for _ in range(7):
            obs = env.step(GameAction.ACTION2)
            
        print(f"Seed {seed}: levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"CN04 MULTI-SEED SCORES (Seeds 0-4): {scores}")

if __name__ == "__main__":
    test_cn04_multi_seed()
