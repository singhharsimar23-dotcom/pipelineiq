"""
Print goals and path generated in my_agent on ls20.
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

def inspect_nav_goals():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ls20", seed=0)
    obs = env.reset()
    f = np.array(obs.frame[0])
    bg = get_background_color(f)
    print(f"bg={bg}")
    
    border = list(f[0, :]) + list(f[-1, :]) + list(f[:, 0]) + list(f[:, -1])
    non_bg = [c for c in border if c != bg]
    wall_col = int(max(set(non_bg), key=non_bg.count)) if non_bg else (bg + 1) % 16
    print(f"wall_col={wall_col}")
    
    comps = get_components(f, bg, max_area=300)
    print(f"Total non-bg comps: {len(comps)}")
    for i, c in enumerate(comps):
        print(f"  Comp {i}: area={c['area']}, cx={c['cx']}, cy={c['cy']}, w={c['w']}, h={c['h']}, color={f[c['cy'], c['cx']]}")

if __name__ == "__main__":
    inspect_nav_goals()
