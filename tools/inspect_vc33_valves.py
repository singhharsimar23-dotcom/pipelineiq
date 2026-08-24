"""
Print valve connections and channel states in vc33.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

def inspect_valves():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    game = env._game

    print(f"Gravity data: {game.dwwmpxqsza}")
    print(f"Valves mapping count: {len(game.wrcxjliglr)}")
    for valve, (s1, s2) in game.wrcxjliglr.items():
        print(f"Valve at ({valve.x}, {valve.y}):")
        print(f"  Channel 1: name={s1.name}, pos=({s1.x},{s1.y}), size=({s1.width},{s1.height}), len={game.pjfzvvjgud(s1)}")
        print(f"  Channel 2: name={s2.name}, pos=({s2.x},{s2.y}), size=({s2.width},{s2.height}), len={game.pjfzvvjgud(s2)}")
        print(f"  Tokens in Ch1: {[t.pixels[-1,-1] for t in game.usqfmpzewf(s1)]}")
        print(f"  Tokens in Ch2: {[t.pixels[-1,-1] for t in game.usqfmpzewf(s2)]}")

if __name__ == "__main__":
    inspect_valves()
