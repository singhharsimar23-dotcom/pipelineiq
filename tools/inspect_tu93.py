"""
Inspect tu93 Sokoban mechanics and test BFS.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from my_agent import get_2d_grid, get_background_color, get_components

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("tu93", seed=0)
obs = env.reset()
game = env._game

print("=== TU93 LEVEL 0 ===")
print("Available actions:", obs.available_actions)
f = get_2d_grid(obs)
bg = get_background_color(f)
print("Background:", bg)

print("Sprites:")
for s in game.current_level.get_sprites():
    if s.is_visible:
        print(f"  {s.name}: ({s.x},{s.y}) {s.width}x{s.height} tags={s.tags}")

# Test movement step size
print("\nTesting movement:")
for act, name in [(GameAction.ACTION1, "UP"), (GameAction.ACTION2, "DOWN"), (GameAction.ACTION3, "LEFT"), (GameAction.ACTION4, "RIGHT")]:
    env.reset()
    obs1 = env.step(act)
    print(f"  {name}: levels={obs1.levels_completed}")
