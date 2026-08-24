"""
DC22 - discover what the maze layout looks like by reading the frame.
Also trace what sjixewahg and uxtzlxsiq are (cursor position for bridge placement).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from my_agent import get_2d_grid, get_background_color
import numpy as np

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

f = get_2d_grid(obs)
print("Frame (left half, rows 0-63, cols 0-32):")
print(f[0:64, 0:32])

# Print the actual maze as characters
print("\nMaze map (0=bg, other=wall):")
bg_col = int(f[0, 0])
print(f"BG color: {bg_col}")
for row in range(64):
    rowstr = ""
    for col in range(32):
        px = f[row, col]
        if px == bg_col:
            rowstr += "."
        else:
            rowstr += str(int(px) % 10)
    print(f"{row:2d}: {rowstr}")

print(f"\nGame cursor: sjixewahg={game.sjixewahg}, uxtzlxsiq={game.uxtzlxsiq}")
print(f"cuvqxkfop={game.cuvqxkfop}")
