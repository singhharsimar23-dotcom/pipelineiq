"""
Print pixel colors along the path in ls20.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from agent.my_agent import get_components, get_background_color

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ls20", seed=0)
obs = env.reset()
f = np.array(obs.frame[0])
bg = get_background_color(f)

print(f"bg = {bg}")
pts = [
    (45, 34), (45, 29), (45, 24), (45, 19),
    (40, 19), (35, 19), (30, 19),
    (25, 19), (25, 24), (25, 29), (25, 34),
    (20, 34), (15, 34), (10, 34)
]

for y, x in pts:
    print(f"Cell at (y={y}, x={x}): pixel color = {f[y, x]}")
