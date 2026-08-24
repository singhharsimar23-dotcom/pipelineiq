"""
Print avatar coordinates and states step by step in m0r0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def trace_m0r0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("m0r0", seed=0)
    obs = env.reset()
    game = env._game

    def print_state(label, obs):
        s1 = game.current_level.get_sprites_by_name("pikgci-toljda-leklkn")[0]
        s2 = game.current_level.get_sprites_by_name("pikgci-toljda-rivmdg")[0]
        print(f"{label}: s1=({s1.x}, {s1.y}), s2=({s2.x}, {s2.y}), mode={game.pyhtlpzlmnr}, okpvc={game.okpvcjupabr}, levels_completed={obs.levels_completed}")

    print_state("Initial", obs)
    
    # Step 1: ACTION6
    obs = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
    print_state("After ACTION6", obs)

    # Step 2: ACTION4
    obs = env.step(GameAction.ACTION4)
    print_state("After 1st ACTION4", obs)

    # Step 3: ACTION4
    obs = env.step(GameAction.ACTION4)
    print_state("After 2nd ACTION4", obs)

if __name__ == "__main__":
    trace_m0r0()
