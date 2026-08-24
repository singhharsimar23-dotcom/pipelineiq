"""
Test BFS on tu93 Level 0 across seeds.
"""
import sys
from pathlib import Path
from collections import deque

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from my_agent import get_2d_grid, get_background_color

def solve_tu93_seed(seed):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("tu93", seed=seed)
    obs = env.reset()
    game = env._game
    
    # BFS in env state
    # Move directions: 1=UP, 2=DOWN, 3=LEFT, 4=RIGHT
    actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
    
    # Let's explore with BFS
    # To avoid cloning env, we can explore actions using a tree or shortest path
    # Or find avatar position in frame
    f0 = get_2d_grid(obs)
    bg0 = get_background_color(f0)
    
    # Test random walks or BFS
    # In tu93, let's see how many steps to goal
    q = deque([([], (3, 3))])
    visited = {(3, 3)}
    
    # Let's test step actions from start
    for act in [GameAction.ACTION4, GameAction.ACTION2, GameAction.ACTION4, GameAction.ACTION2]:
        obs = env.step(act)
        print(f"Action {act.name}: levels={obs.levels_completed}")
        
solve_tu93_seed(0)
