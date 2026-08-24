"""
Test actions on ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ka59", seed=0)
obs = env.reset()
game = env._game

print(f"Initial: avatar pos=({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win={game.dbmlcqbquh()}")

# Try moving right (ACTION4)
for i in range(5):
    obs = env.step(GameAction.ACTION4)
    print(f"Step {i+1} (ACTION4): avatar pos=({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")
