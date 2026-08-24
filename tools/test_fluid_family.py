"""
Test universal slider solver on remaining Fluid games: bp35, cd82, ar25.
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

def test_fluid_game(game_id):
    print(f"\n================ TESTING {game_id.upper()} ================")
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make(game_id, seed=0)
    obs = env.reset()
    
    # Inspect actions and sprites
    actions = getattr(obs, "available_actions", [])
    print(f"Available actions: {actions}")
    
    lvl = env._game.current_level
    print(f"Level name in {game_id}: {lvl.name}")
    print(f"Total sprites: {len(lvl._sprites)}")

if __name__ == "__main__":
    for gid in ["bp35", "cd82", "ar25"]:
        test_fluid_game(gid)
