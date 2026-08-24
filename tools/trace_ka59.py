"""
Trace ka59 Level 0 solution.
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

def trace_ka59():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    # Initial state:
    # Block 0 is at (9, 21), active block is Block 0
    # Block 1 is at (18, 21)
    # Target 0 is at (2, 23) -> matching pos: (3, 24)
    # Target 1 is at (35, 17) -> matching pos: (36, 18)
    
    print("Moving Block 0 to Target 0...")
    # Move Block 0 Left twice, Down once:
    env.step(GameAction.ACTION3)
    env.step(GameAction.ACTION3)
    obs = env.step(GameAction.ACTION2)
    print(f"Block 0 pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win_check={game.dbmlcqbquh()}")

    # Now switch to Block 1:
    # Block 1 is at (18, 21), display coord = (18+9, 21+9) = (27, 30)
    print("Switching to Block 1...")
    obs = env.step(GameAction.ACTION6, data={"x": 27, "y": 30})
    print(f"Active block pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y})")
    
    # Try moving Block 1 Right towards (36, 18)
    # Let's test moving Right (ACTION4)
    for step in range(8):
        obs = env.step(GameAction.ACTION4)
        print(f"Step {step+1} Right -> pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win_check={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")
        
    # Move Up (ACTION1)
    obs = env.step(GameAction.ACTION1)
    print(f"Step Up -> pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win_check={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    trace_ka59()
