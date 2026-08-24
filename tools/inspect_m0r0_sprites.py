"""
Inspect all sprites in m0r0 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("m0r0", seed=0)
obs = env.reset()
game = env._game

print("=== ALL SPRITES IN M0R0 LEVEL 0 ===")
for s in game.current_level._sprites:
    print(f"Sprite: name={s.name}, pos=(x={s.x}, y={s.y}), collidable={s.is_collidable}, tags={s.tags}, visible={s.is_visible}")
