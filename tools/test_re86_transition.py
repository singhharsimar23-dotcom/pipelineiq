"""
Inspect frame transition after level clear in re86.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

def test_transition():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    
    # Solve Level 0: 7 UP, 4 RIGHT on S1, ACTION5, 6 UP, 2 LEFT on S0
    for _ in range(7):
        obs = env.step(GameAction.ACTION1)
    for _ in range(4):
        obs = env.step(GameAction.ACTION4)
    obs = env.step(GameAction.ACTION5)
    for _ in range(6):
        obs = env.step(GameAction.ACTION1)
    for _ in range(2):
        obs = env.step(GameAction.ACTION3)
    
    print(f"Step 20 (win step): levels_completed={obs.levels_completed}")
    f0 = np.array(obs.frame[0])
    print(f"Frame immediately after clear: unique colors = {np.unique(f0)}")
    
    # Next step (e.g. dummy action or first move of level 1)
    obs1 = env.step(GameAction.ACTION5) # harmless switch
    f1 = np.array(obs1.frame[0])
    print(f"Frame after 1 step in level 1: unique colors = {np.unique(f1)}")

if __name__ == "__main__":
    test_transition()
