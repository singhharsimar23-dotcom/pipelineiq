"""
Inspect game level index and sprite states in m0r0.
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
env = arcade.make("m0r0", seed=0)
obs = env.reset()
game = env._game

print(f"Level index before: {game._current_level_index}, levels_completed={obs.levels_completed}")
obs = env.step(GameAction.ACTION4)
print(f"After 1st ACTION4: level_idx={game._current_level_index}, okpvc={game.okpvcjupabr}")
obs = env.step(GameAction.ACTION4)
print(f"After 2nd ACTION4: level_idx={game._current_level_index}, okpvc={game.okpvcjupabr}, levels_completed={obs.levels_completed}, state={obs.state}")

# Check sprites in current level
for s in game.current_level._sprites:
    print(f"Sprite: name={s.name}, pos=(x={s.x}, y={s.y}), interaction={s.interaction}")
