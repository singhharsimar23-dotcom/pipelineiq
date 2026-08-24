"""
Inspect cn04 frame colors and components.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from agent.my_agent import get_components, get_background_color
import numpy as np

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("cn04", seed=0)
obs = env.reset()
f = np.array(obs.frame[0])
bg = get_background_color(f)

print(f"cn04 Frame bg: {bg}")
print(f"Unique colors in cn04 frame: {np.unique(f)}")

comps = get_components(f, bg, max_area=600)
print(f"Components ({len(comps)}):")
for i, c in enumerate(comps):
    print(f"  Comp {i}: area={c['area']}, cx={c['cx']}, cy={c['cy']}, w={c['w']}, h={c['h']}, color={f[c['cy'], c['cx']]}")
