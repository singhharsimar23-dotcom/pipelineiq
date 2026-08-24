"""
Inspect Sprite.collides_with implementation and behavior.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import inspect

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("m0r0", seed=0)
obs = env.reset()
game = env._game

s1 = game.current_level.get_sprites_by_name("pikgci-toljda-leklkn")[0]
walls = game.current_level.get_sprites_by_tag("wahtyt")[0]

print("Sprite class:", s1.__class__)
print("collides_with source:\n", inspect.getsource(s1.collides_with))
