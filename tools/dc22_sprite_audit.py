"""
DC22: Full sprite state audit - check what's tangible/intangible initially.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, InteractionMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

def show_sprites():
    for s in game.current_level.get_sprites():
        print(f"  {s.name}: ({s.x},{s.y}) {s.width}x{s.height} {s.interaction.name} tags={s.tags}")
    print(f"  Player: ({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")

print("=== INITIAL STATE ===")
show_sprites()

# Click button a
refgps = next(s for s in game.current_level.get_sprites_by_tag("sys_click") if 'a' in s.tags)
print(f"\n=== AFTER CLICK A ({refgps.x+5},{refgps.y+2}) ===")
env.step(GameAction.ACTION6, {"x": refgps.x + 5, "y": refgps.y + 2})
show_sprites()

# Click button b  
blrmbx = next(s for s in game.current_level.get_sprites_by_tag("sys_click") if 'b' in s.tags)
print(f"\n=== AFTER CLICK B ({blrmbx.x+5},{blrmbx.y+2}) ===")
env.step(GameAction.ACTION6, {"x": blrmbx.x + 5, "y": blrmbx.y + 2})
show_sprites()

# Click A again
print(f"\n=== AFTER CLICK A AGAIN ===")
env.step(GameAction.ACTION6, {"x": refgps.x + 5, "y": refgps.y + 2})
show_sprites()

# After 2 A clicks: try going up
env2 = arcade.make("dc22", seed=0)
obs2 = env2.reset()
g2 = env2._game
refgps2 = next(s for s in g2.current_level.get_sprites_by_tag("sys_click") if 'a' in s.tags)
# Click a twice
env2.step(GameAction.ACTION6, {"x": refgps2.x + 5, "y": refgps2.y + 2})
env2.step(GameAction.ACTION6, {"x": refgps2.x + 5, "y": refgps2.y + 2})
# Move left and up
for act in [GameAction.ACTION3, GameAction.ACTION1, GameAction.ACTION1, GameAction.ACTION1, GameAction.ACTION1]:
    obs2 = env2.step(act)
    print(f"  act={act.name}: player=({g2.qnnpcoyzd.x},{g2.qnnpcoyzd.y}), lvl={obs2.levels_completed}")
