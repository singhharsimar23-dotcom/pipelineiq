"""
DC22: The game is a SLIDING BRIDGE PUZZLE on the RIGHT side (cols 32-63).
The left half we've been looking at is just the background (coorbs-bg).
Need to look at right half and understand the puzzle.

The puzzle: 
- A 4x4 grid of bridge placeholders (sjixewahg = X cursor, uxtzlxsiq = Y cursor)
- Click sys_click buttons 'a' and 'b' to move cursor or place bridges
- The bridge blocks let player cross gaps from start to goal

Let's map the right side (cols 32-63).
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
from my_agent import get_2d_grid

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

f = get_2d_grid(obs)
print("RIGHT half frame (cols 32-63):")
for row in range(0, 64):
    rowstr = ""
    for col in range(32, 64):
        px = int(f[row, col])
        if px == 3:
            rowstr += "."
        elif px == 4:
            rowstr += " "
        else:
            rowstr += str(px % 10)
    print(f"{row:2d}: {rowstr}")

print(f"\nsjixewahg={game.sjixewahg}, uxtzlxsiq={game.uxtzlxsiq}")

# Now click button 'up' (aybe tag) to see what moves
# Look at the aybe button
aybe_sprites = game.current_level.get_sprites_by_tag("aybe")
print(f"\naybe sprites: {[(s.name, s.x, s.y, s.width, s.height) for s in aybe_sprites]}")

# Click the up button (higher y = lower on screen, but for sprite coord sys y=small is up)
# The sprite at (41,6) is ABOVE (41,23)
# Click the up button at (41, 6)
up_btn = aybe_sprites[0]  # pos=(41,6)
print(f"\nClicking aybe button 0 at ({up_btn.x + 6},{up_btn.y + 3})")
obs = env.step(GameAction.ACTION6, {"x": up_btn.x + 6, "y": up_btn.y + 3})
f1 = get_2d_grid(obs)
print(f"sjixewahg={game.sjixewahg}, uxtzlxsiq={game.uxtzlxsiq}")
print("RIGHT half after click:")
for row in range(0, 64):
    rowstr = ""
    for col in range(32, 64):
        px = int(f1[row, col])
        if px == 3:
            rowstr += "."
        elif px == 4:
            rowstr += " "
        else:
            rowstr += str(px % 10)
    print(f"{row:2d}: {rowstr}")
