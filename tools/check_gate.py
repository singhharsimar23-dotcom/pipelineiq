"""
Check 0014ysspdlqsqg pixels.
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

gate = game.current_level.get_sprites_by_tag("0015qniapgwsvb")[0]
print(f"Gate: pos=({gate.x}, {gate.y}), shape={gate.pixels.shape}")
print("Gate pixels:\n", gate.pixels)
