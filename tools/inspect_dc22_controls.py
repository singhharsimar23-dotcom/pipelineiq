"""
Inspect all sys_click controls in dc22.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

print("=== ALL SYS_CLICK CONTROLS ===")
for s in game.current_level.get_sprites():
    if "sys_click" in s.tags:
        print(f"Control: name={s.name}, grid_pos=({s.x}, {s.y}), size=({s.width}, {s.height}), tags={s.tags}")
