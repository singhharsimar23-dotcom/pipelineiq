"""
Inspect tr87 Level 0 tokens, rules, and solution.
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

def inspect_tr87():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("tr87", seed=0)
    obs = env.reset()
    game = env._game

    print("=== TR87 LEVEL 0 GRAMMAR PUZZLE ===")
    print("Available actions:", getattr(obs, "available_actions", []))
    print(f"Source tokens (zvojhrjxxm): {[s.name for s in game.zvojhrjxxm]}")
    print(f"Editable output tokens (ztgmtnnufb): {[s.name for s in game.ztgmtnnufb]}")
    print("Rules (cifzvbcuwqe):")
    for i, (lhs, rhs) in enumerate(game.cifzvbcuwqe):
        print(f"  Rule {i+1}: {[s.name for s in lhs]} -> {[s.name for s in rhs]}")
        
    print(f"Initial win check: {game.bsqsshqpox()}")

if __name__ == "__main__":
    inspect_tr87()
