"""
Print detailed grid between y=12 and y=32.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import numpy as np

def print_detail():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game
    
    for y in range(12, 33):
        row = []
        for x in range(45):
            s = game.current_level.get_sprite_at(x, y)
            if s is None:
                row.append(".")
            elif "xzmuziohuf" in s.tags:
                row.append("T")
            elif "vrxelxosfy" in s.tags:
                row.append("B")
            elif "qniapgwsvb" in s.tags:
                row.append("G")
            elif "ifoxxfvvvs" in s.tags:
                row.append("#")
            else:
                row.append("?")
        print(f"{y:2d}: " + "".join(row))

if __name__ == "__main__":
    print_detail()
