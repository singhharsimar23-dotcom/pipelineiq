"""
Fast BFS state search on g50t Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from collections import deque
import numpy as np

def fast_solve_g50t():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    
    # In g50t:
    # Phase 1: Walk to pressure switch at (37, 7) -> 4x ACTION4 (Right)
    # Phase 2: Press ACTION5 (records clone timeline holding switch down while avatar rewinds to (13, 7))!
    # Phase 3: Now that switch is held down by clone shadow, gate is open!
    # Walk to Goal at (43, 49):
    # From (13, 7): Move Down: (13, 7) -> (13, 13) -> (13, 19) -> (13, 25) -> (13, 31) -> (13, 37) -> (13, 43) -> (13, 49) [7x ACTION2]
    # Move Right: (13, 49) -> (19, 49) -> (25, 49) -> (31, 49) -> (37, 49) -> (43, 49) [5x ACTION4]!
    
    scores = []
    for seed in range(5):
        env = arcade.make("g50t", seed=seed)
        obs = env.reset()
        game = env._game

        # 1. Walk Right to pressure plate at (37, 7) (4x ACTION4)
        for _ in range(4):
            env.step(GameAction.ACTION4)
            
        # 2. Press ACTION5 to rewind clone shadow on switch
        env.step(GameAction.ACTION5)
        # In g50t, rewind takes some animation steps (let's step until rewind is complete)
        while game.vgwycxsxjz.jqpwhiraaj:
            env.step(GameAction.ACTION5)
            
        # 3. Walk Down 7 steps (ACTION2)
        for _ in range(7):
            env.step(GameAction.ACTION2)
            while game.vgwycxsxjz.jqpwhiraaj:
                env.step(GameAction.ACTION5)
                
        # 4. Walk Right 5 steps (ACTION4)
        for _ in range(5):
            obs = env.step(GameAction.ACTION4)
            while game.vgwycxsxjz.jqpwhiraaj:
                obs = env.step(GameAction.ACTION5)
                
        print(f"Seed {seed}: avatar at ({game.vgwycxsxjz.dzxunlkwxt.x}, {game.vgwycxsxjz.dzxunlkwxt.y}), win_check={game.mrzduxdbbk()}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"G50T MULTI-SEED SCORES (Seeds 0-4): {scores}")

if __name__ == "__main__":
    fast_solve_g50t()
