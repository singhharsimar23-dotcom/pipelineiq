"""
Inspect tu93 frame components.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from my_agent import get_2d_grid, get_background_color, get_components

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("tu93", seed=0)
obs = env.reset()
f = get_2d_grid(obs)
bg = get_background_color(f)

comps = get_components(f, bg, max_area=10000)
print(f"Background: {bg}, Total comps: {len(comps)}")
for c in comps:
    print(f"  cx={c['cx']}, cy={c['cy']}, w={c['w']}, h={c['h']}, area={c['area']}, col={c['col']}")
