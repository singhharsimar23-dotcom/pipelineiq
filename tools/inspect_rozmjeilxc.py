"""
Inspect rozmjeilxc in equnaohchtj.
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
env = arcade.make("lf52", seed=0)
obs = env.reset()
game = env._game
world = game.ikhhdzfmarl

print(inspect.getsource(world.rozmjeilxc))
