"""
Test routing Block 1 around the barrier in ka59 Level 0.
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

def test_ka59_routing():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    # Move Block 0 to Target 0:
    env.step(GameAction.ACTION3)
    env.step(GameAction.ACTION3)
    env.step(GameAction.ACTION2)
    print(f"Block 0 pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y})")

    # Switch to Block 1:
    env.step(GameAction.ACTION6, data={"x": 27, "y": 30})
    print(f"Block 1 initial pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y})")

    # Try routing Block 1 via top corridor (Up -> Right -> Down) or bottom corridor (Down -> Right -> Up)
    # Let's test moving Up (ACTION1) 4 times
    print("Testing Up corridor:")
    for _ in range(4):
        obs = env.step(GameAction.ACTION1)
        print(f"  Up -> pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y})")
        
    for _ in range(6):
        obs = env.step(GameAction.ACTION4)
        print(f"  Right -> pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y})")
        
    for _ in range(4):
        obs = env.step(GameAction.ACTION2)
        print(f"  Down -> pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win_check={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    test_ka59_routing()
