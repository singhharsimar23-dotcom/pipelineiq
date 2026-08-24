"""
Print all collision obstacles in ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ka59", seed=0)
obs = env.reset()
game = env._game

print("=== ALL SPRITES IN KA59 LEVEL 0 ===")
for s in game.current_level._sprites:
    print(f"Sprite: name={s.name}, pos=(x={s.x}, y={s.y}), size=({s.width}, {s.height}), tags={s.tags}")
