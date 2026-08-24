"""
Trace gate collision and pushing in ka59.
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

def trace_gate_push():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    # Switch to Block 1 at (18, 21)
    env.step(GameAction.ACTION6, data={"x": 27, "y": 30})
    
    # Move Block 1 Right to (21, 21)
    env.step(GameAction.ACTION4)
    print(f"Block 1 pos: ({game.prkgpeyexo.x}, {game.prkgpeyexo.y})")

    # Inspect loydmqkgjw when moving right
    gate = [s for s in game.current_level.get_sprites() if "qniapgwsvb" in s.tags][0]
    print(f"Gate pos: ({gate.x}, {gate.y}), size: ({gate.width}, {gate.height})")
    
    # Call loydmqkgjw
    res = game.loydmqkgjw(game.prkgpeyexo, 3, 0)
    print(f"loydmqkgjw(3, 0) returned: {res}")
    
    # What did it collide with?
    game.prkgpeyexo.move(3, 0)
    for s in game.current_level.get_sprites():
        if game.prkgpeyexo.collides_with(s) and s != game.prkgpeyexo:
            print(f"  Collides with: name={s.name}, tags={s.tags}")
    game.prkgpeyexo.move(-3, 0)

if __name__ == "__main__":
    trace_gate_push()
