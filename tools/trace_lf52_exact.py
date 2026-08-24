"""
Trace lf52 step-by-step.
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
env = arcade.make("lf52", seed=0)
obs = env.reset()
game = env._game
world = game.ikhhdzfmarl

moves = [
    ((1, 2), (3, 2)),
    ((3, 2), (5, 2)),
    ((5, 2), (5, 4)),
    ((5, 4), (5, 6)),
]

for i, ((fx, fy), (tx, ty)) in enumerate(moves):
    print(f"\n--- Move {i+1}: from ({fx}, {fy}) to ({tx}, {ty}) ---")
    # Click peg
    obs1 = env.step(GameAction.ACTION6, data={"x": fx * 6 + 3, "y": fy * 6 + 3})
    selected = world.wpwvsglgmb.qoifrofmiu
    print(f"  After click peg: selected={getattr(selected, 'chahdtpdoz', None)}, arrows count={len(world.zpbguihjnf)}")
    
    # Click destination
    obs2 = env.step(GameAction.ACTION6, data={"x": tx * 6 + 3, "y": ty * 6 + 3})
    pegs_left = len(world.hncnfaqaddg.ndtvadsrqf("fozwvlovdui"))
    print(f"  After jump: pegs remaining={pegs_left}, win_flag={world.iajuzrgttrv}, levels_completed={obs2.levels_completed}")
