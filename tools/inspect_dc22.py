"""
Inspect dc22 Level 0 sprites and win condition.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

print("=== DC22 LEVEL 0 ===")
print(f"Available actions: {obs.available_actions}")
for s in game.current_level.get_sprites():
    print(f"Sprite: name={s.name}, pos=({s.x},{s.y}), size=({s.width}x{s.height}), tags={s.tags}")

print(f"\nPlayer sprite: ({game.qnnpcoyzd.x}, {game.qnnpcoyzd.y})")
print(f"Goal sprite: ({game.hfuqkxulm.x}, {game.hfuqkxulm.y})")
print(f"Win check: {game.smxyfelexa()}")

# Test movement
print("\n--- Testing moves ---")
for act_name, act in [("Up", GameAction.ACTION1), ("Down", GameAction.ACTION2), ("Left", GameAction.ACTION3), ("Right", GameAction.ACTION4)]:
    obs2 = env.step(act)
    print(f"{act_name}: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y}), win={game.smxyfelexa()}, levels={obs2.levels_completed}")
    env.step(GameAction.RESET)
    obs2 = env.reset()
