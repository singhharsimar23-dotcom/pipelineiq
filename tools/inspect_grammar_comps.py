"""
Inspect _build_grammar_plan component extraction on tr87.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from my_agent import get_components, get_background_color, get_2d_grid
import numpy as np

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("tr87", seed=0)
obs = env.reset()
f = get_2d_grid(obs)
bg = get_background_color(f)

comps = get_components(f, bg, max_area=100)
print(f"Total comps (max_area=100): {len(comps)}")
for c in comps:
    print(f"Comp: pos=({c['cx']}, {c['cy']}), size=({c['w']}, {c['h']}), area={c['area']}, col={c['col']}")

tokens = [c for c in comps if 20 <= c['area'] <= 81 and abs(c['w'] - c['h']) <= 2 and c['cy'] < 55]
print(f"Filtered tokens (len={len(tokens)}): {tokens}")
