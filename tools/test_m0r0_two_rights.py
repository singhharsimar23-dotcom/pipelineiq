"""
Test m0r0 Level 0 with 2x ACTION4 without ACTION6.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_m0r0_two_rights():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    for seed in range(5):
        env = arcade.make("m0r0", seed=seed)
        obs = env.reset()
        print(f"Seed {seed} initial: levels_completed={obs.levels_completed}")
        
        # Action 1: Right
        obs = env.step(GameAction.ACTION4)
        print(f"  After 1st ACTION4: levels_completed={obs.levels_completed}")
        
        # Action 2: Right
        obs = env.step(GameAction.ACTION4)
        print(f"  After 2nd ACTION4: levels_completed={obs.levels_completed}, state={obs.state}")
        scores.append(obs.levels_completed)
        
    print(f"M0R0 Level 0 Results across 5 seeds: {scores}")

if __name__ == "__main__":
    test_m0r0_two_rights()
