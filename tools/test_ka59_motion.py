"""
Test moving blocks in ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_ka59_motion():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    print("Initial active block pos:", (game.prkgpeyexo.x, game.prkgpeyexo.y))
    
    # Try moving left (ACTION3)
    for _ in range(3):
        obs = env.step(GameAction.ACTION3)
        print(f"Move Left: pos=({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win={game.dbmlcqbquh()}")

if __name__ == "__main__":
    test_ka59_motion()
