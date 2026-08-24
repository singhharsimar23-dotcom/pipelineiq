"""
Print grid layout of lf52 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("lf52", seed=0)
obs = env.reset()
game = env._game
world = game.ikhhdzfmarl

grid = world.hncnfaqaddg
w, h = grid.grid_size
print(f"LF52 Level 0 Grid Size: ({w}, {h})")

for y in range(h):
    row_chars = []
    for x in range(w):
        items = [i.name for i in grid.ijpoqzvnjt(x, y)]
        if not items:
            row_chars.append(" ")
        elif any("wall" in name or "giyrmixbmt" in name for name in items):
            row_chars.append("#")
        elif any("fozwvlovdui" in name or "dgxfozncuiz" in name for name in items):
            row_chars.append("$") # Box
        elif any("avatar" in name or "hkadp" in name or "guy" in name for name in items):
            row_chars.append("@") # Avatar
        elif any("hupkpseyuim" in name for name in items):
            row_chars.append(".") # Target Goal
        else:
            row_chars.append(items[0][:1])
    print(f"Row {y:2d}: {''.join(row_chars)}")
