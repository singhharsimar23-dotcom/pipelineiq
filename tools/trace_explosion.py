"""
Print sprites after gate removal in ka59.
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

def trace_post_explosion():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    # Switch to Block 1 at (18, 21)
    env.step(GameAction.ACTION6, data={"x": 27, "y": 30})
    
    # Move Block 1 Right to (21, 21)
    obs = env.step(GameAction.ACTION4)
    print("Sprites after ACTION4:")
    for s in game.current_level.get_sprites():
        print(f"  Sprite: name={s.name}, pos=({s.x}, {s.y}), size=({s.width}, {s.height}), tags={s.tags}")

    # Now that explosion is underway or finished:
    # How many steps does explosion animation take?
    # In ka59.py: self.xrxdckwsth < 3 (3 explosion steps)
    for i in range(4):
        obs = env.step(GameAction.ACTION4)
        print(f"Post-step {i+1}: pos=({game.prkgpeyexo.x}, {game.prkgpeyexo.y}), win_check={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    trace_post_explosion()
