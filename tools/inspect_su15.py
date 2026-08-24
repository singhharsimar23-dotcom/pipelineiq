"""
Inspect su15 (Navigation / Geodesic Maze).
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
env = arcade.make("su15", seed=0)
obs = env.reset()
game = env._game

f = get_2d_grid(obs)
bg = get_background_color(f)
comps = get_components(f, bg, max_area=600)

print("=== SU15 LEVEL 0 ===")
print("Available actions:", obs.available_actions)
print("Background color:", bg)
print(f"Components ({len(comps)}):")
for c in comps:
    print(f"  cx={c['cx']}, cy={c['cy']}, w={c['w']}, h={c['h']}, area={c['area']}, col={c['col']}")

print("\nSprites:")
for s in game.current_level.get_sprites():
    if s.is_visible:
        print(f"  {s.name}: ({s.x},{s.y}) {s.width}x{s.height} {s.interaction.name} tags={s.tags}")
