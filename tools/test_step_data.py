"""
Check how env.step in Arcade handles action data.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("vc33", seed=0)
obs = env.reset()

# Test 1: env.step(GameAction.ACTION6, data={"x": 60, "y": 24})
obs = env.step(GameAction.ACTION6, data={"x": 60, "y": 24})
t1 = env._game.current_level.get_sprites_by_tag("0016uciqlhjlom")[0]
print(f"After env.step(ACTION6, data=...): token pos = ({t1.x}, {t1.y})")

obs = env.reset()
# Test 2: a = GameAction.ACTION6; a.set_data({"x": 60, "y": 24}); env.step(a)
a = GameAction.ACTION6
a.set_data({"x": 60, "y": 24})
obs = env.step(a)
t2 = env._game.current_level.get_sprites_by_tag("0016uciqlhjlom")[0]
print(f"After env.step(a with set_data): token pos = ({t2.x}, {t2.y})")
