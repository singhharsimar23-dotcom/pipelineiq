"""
Print components found in vc33 Level 0 frame.
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

def inspect_vc33_comps():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    f = np.array(obs.frame[0])
    bg = get_background_color(f)
    print(f"Frame shape={f.shape}, bg={bg}")
    
    comps = get_components(f, bg, max_area=600)
    print(f"Total non-bg components: {len(comps)}")
    for i, c in enumerate(comps):
        print(f"  Comp {i:2d}: area={c['area']:3d}, cx={c['cx']:2d}, cy={c['cy']:2d}, w={c['w']:2d}, h={c['h']:2d}")

if __name__ == "__main__":
    inspect_vc33_comps()
