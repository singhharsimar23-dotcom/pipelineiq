"""
Test Card Match / Token Sorting across all Card Match games: vc33, tn36, sk48, sc25.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_card_match(game_id):
    print(f"\n================ TESTING {game_id.upper()} ================")
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make(game_id, seed=0)
    obs = env.reset()
    game = env._game

    valves = game.current_level.get_sprites_by_tag("0022jvmlspyigc")
    tokens = game.current_level.get_sprites_by_tag("0016uciqlhjlom")
    targets = game.current_level.get_sprites_by_tag("0010gnulkywfpz")
    gates = game.current_level.get_sprites_by_tag("0004sttgkofqwb")

    print(f"{game_id}: {len(valves)} valves, {len(tokens)} tokens, {len(targets)} targets, {len(gates)} gates")
    
    # Let's test valve click sequences
    # Try clicking each valve up to 8 times
    for v_idx, v in enumerate(valves):
        # Display coordinate
        disp_x = v.x * 2 + v.width
        disp_y = v.y * 2 + v.height
        print(f"Testing Valve {v_idx} at disp ({disp_x}, {disp_y})...")
        for step in range(1, 10):
            obs = env.step(GameAction.ACTION6, data={"x": disp_x, "y": disp_y})
            if obs.levels_completed > 0:
                print(f"*** {game_id} LEVEL 0 CLEARED on Valve {v_idx} Step {step}! ***")
                return True
    return False

if __name__ == "__main__":
    for gid in ["vc33", "tn36", "sk48", "sc25"]:
        test_card_match(gid)
