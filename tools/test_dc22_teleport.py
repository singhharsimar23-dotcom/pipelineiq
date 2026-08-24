"""
DC22 - Test the teleport hypothesis:
1. Walk player onto tovemc-plelvb1 (at 8,24)
2. Click buezna-blrmbx (b) to teleport to tovemc-plelvb2 (18,10)
3. Walk to goal at (24,10)
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

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

print(f"Start: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y}), goal=({game.hfuqkxulm.x},{game.hfuqkxulm.y})")
print(f"tovemc1=({game.jrxnntmty[0].x},{game.jrxnntmty[0].y}), tovemc2=({game.jrxnntmty[1].x},{game.jrxnntmty[1].y})")

# Player at (10,30). tovemc-plelvb1 at (8,24). Need to walk Left 1 step and Up 3 steps.
# Step size is 2 per action
# Left from (10,30) -> (8,30), Up from (8,30) -> (8,28) -> (8,26) -> (8,24) -- but wall at y=28!

# Try walk Down first to see if there's a gap below
for i, act in enumerate([GameAction.ACTION3, GameAction.ACTION3, GameAction.ACTION3,  # Left x3
                          GameAction.ACTION1, GameAction.ACTION1, GameAction.ACTION1]):  # Up x3
    obs = env.step(act)
    print(f"  Step {i}: act={act.name}, player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")

print(f"\nPlayer now at ({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")

# If we're on a tovemc sprite, clicking the matching buezna should teleport
for tov in game.jrxnntmty:
    if tov.x == game.qnnpcoyzd.x and tov.y == game.qnnpcoyzd.y:
        print(f"On tovemc: {tov.name} tags={tov.tags}")

# Try clicking buezna-b 
blrmbx = game.current_level.get_sprites_by_tag("sys_click")[0]  # blrmbx = b
print(f"\nClicking buezna-b at ({blrmbx.x+5},{blrmbx.y+2})")
obs = env.step(GameAction.ACTION6, {"x": blrmbx.x + 5, "y": blrmbx.y + 2})
print(f"After click b: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y}), lvl={obs.levels_completed}")

# Try clicking buezna-a
refgps = game.current_level.get_sprites_by_tag("sys_click")[1]  # refgps = a  
print(f"\nClicking buezna-a at ({refgps.x+5},{refgps.y+2})")
obs = env.step(GameAction.ACTION6, {"x": refgps.x + 5, "y": refgps.y + 2})
print(f"After click a: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y}), lvl={obs.levels_completed}")
