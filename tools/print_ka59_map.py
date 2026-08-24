"""
Print 2D collision map of ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import numpy as np

def print_ka59_map():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game
    
    # 45x45 grid
    grid = np.full((45, 45), ".", dtype=str)
    
    # Add sprites
    for s in game.current_level.get_sprites():
        char = s.name[:1]
        if "xzmuziohuf" in s.tags:
            char = "T" # Target
        elif "vrxelxosfy" in s.tags:
            char = "B" # Block
        elif "qniapgwsvb" in s.tags:
            char = "G" # Gate
        elif "ifoxxfvvvs" in s.tags:
            char = "#" # Wall
            
        p = s.pixels
        for r in range(s.height):
            for c in range(s.width):
                if p[r, c] != -1:
                    gy = s.y + r
                    gx = s.x + c
                    if 0 <= gy < 45 and 0 <= gx < 45:
                        grid[gy, gx] = char
                        
    for y in range(45):
        if y % 3 == 0:
            print(f"{y:2d}: " + "".join(grid[y]))

if __name__ == "__main__":
    print_ka59_map()
