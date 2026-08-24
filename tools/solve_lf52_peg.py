"""
Solve lf52 Level 0 via Peg Solitaire search.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from collections import deque
import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def solve_lf52_level0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("lf52", seed=0)
    obs = env.reset()
    game = env._game
    world = game.ikhhdzfmarl

    # Peg Solitaire state: set of peg (x, y) coordinates
    # Valid board holes in Level 0:
    holes = set()
    initial_pegs = set()
    
    grid = world.hncnfaqaddg
    w, h = grid.grid_size
    for y in range(h):
        for x in range(w):
            items = [i.name for i in grid.ijpoqzvnjt(x, y)]
            if any("hupkpseyuim" in name for name in items):
                holes.add((x, y))
            if any("fozwvlovdui" in name for name in items):
                initial_pegs.add((x, y))

    print(f"Total holes: {len(holes)}, Total initial pegs: {len(initial_pegs)}")
    print(f"Initial pegs: {sorted(list(initial_pegs))}")

    # Peg Solitaire BFS
    # State: frozenset of peg coords
    # Move: (from_peg, jumped_peg, to_hole)
    # Valid jump: from_peg in state, jumped_peg in state, to_hole not in state and in holes
    # dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)] with distance 2
    
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    q = deque([(frozenset(initial_pegs), [])])
    visited = {frozenset(initial_pegs)}
    
    while q:
        pegs, path = q.popleft()
        if len(pegs) == 1:
            print(f"*** FOUND PEG SOLITAIRE SOLUTION! Path length: {len(path)} ***")
            for i, (p_from, p_to) in enumerate(path):
                print(f"  Move {i+1}: Jump peg from {p_from} to {p_to}")
            return path
            
        for px, py in pegs:
            for dx, dy in dirs:
                mid_x, mid_y = px + dx, py + dy
                dest_x, dest_y = px + 2*dx, py + 2*dy
                if (mid_x, mid_y) in pegs and (dest_x, dest_y) in holes and (dest_x, dest_y) not in pegs:
                    next_pegs = (pegs - {(px, py), (mid_x, mid_y)}) | {(dest_x, dest_y)}
                    if next_pegs not in visited:
                        visited.add(next_pegs)
                        q.append((next_pegs, path + [((px, py), (dest_x, dest_y))]))

    print("No peg solitaire solution found.")
    return None

if __name__ == "__main__":
    solve_lf52_level0()
