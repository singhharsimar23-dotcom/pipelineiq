"""
Test ACTION6 + ACTION4, ACTION4 on m0r0 Level 0 across 5 seeds.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_m0r0_clear():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    for seed in range(5):
        env = arcade.make("m0r0", seed=seed)
        obs = env.reset()
        
        # Start mirror movement mode
        obs = env.step(GameAction.ACTION6)
        
        # Move right twice to merge
        obs = env.step(GameAction.ACTION4)
        obs = env.step(GameAction.ACTION4)
        
        print(f"Seed {seed}: levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
    print(f"M0R0 Scores: {scores}")

if __name__ == "__main__":
    test_m0r0_clear()
