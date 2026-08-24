"""
Solve dc22 Level 0 via button clicks and BFS navigation.
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

def solve_dc22_level0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    
    # Try clicking buttons a and b
    btn_a = (48, 9)
    btn_b = (48, 26)
    
    for click_seq in [[btn_a], [btn_b], [btn_a, btn_b], [btn_b, btn_a], [btn_a, btn_a], [btn_b, btn_b], []]:
        env = arcade.make("dc22", seed=0)
        obs = env.reset()
        game = env._game
        
        for cx, cy in click_seq:
            env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            
        # Now try BFS navigation
        # Avatar is at (game.qnnpcoyzd.x, game.qnnpcoyzd.y)
        # Goal is at (game.hfuqkxulm.x, game.hfuqkxulm.y)
        # Action map: 1: Up (0, -2), 2: Down (0, 2), 3: Left (-2, 0), 4: Right (2, 0)
        # Let's test moving along path:
        # Initial pos: (10, 30), goal pos: (24, 10)
        # Let's try simple directions: Up, Down, Left, Right
        
        # BFS over avatar movement in env
        # State: (x, y)
        actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
        
        # Test path to goal
        path = []
        for _ in range(50):
            if game.smxyfelexa():
                print(f"*** FOUND DC22 WIN! Clicks: {click_seq}, Path: {path} ***")
                print(f"Levels completed: {obs.levels_completed}")
                return click_seq, path
                
            ax, ay = game.qnnpcoyzd.x, game.qnnpcoyzd.y
            gx, gy = game.hfuqkxulm.x, game.hfuqkxulm.y
            
            # Greedy step towards goal
            moved = False
            # Prefer Up or Right
            cand_moves = []
            if ay > gy: cand_moves.append(GameAction.ACTION1)
            if ax < gx: cand_moves.append(GameAction.ACTION4)
            if ay < gy: cand_moves.append(GameAction.ACTION2)
            if ax > gx: cand_moves.append(GameAction.ACTION3)
            
            for act in cand_moves:
                obs = env.step(act)
                if (game.qnnpcoyzd.x, game.qnnpcoyzd.y) != (ax, ay):
                    path.append(act)
                    moved = True
                    break
            if not moved:
                break

if __name__ == "__main__":
    solve_dc22_level0()
