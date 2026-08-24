"""
Test precise avatar detection from directional shift in ls20.
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
from arcengine import GameAction

def test_avatar_detect():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ls20", seed=0)
    obs = env.reset()
    f0 = np.array(obs.frame[0])
    bg = get_background_color(f0)
    
    # Try ACTION3 (Left) where avatar moves left:
    obs = env.step(GameAction.ACTION3)
    f1 = np.array(obs.frame[0])
    
    diff = (f0 != f1) & (f0 != bg) & (f1 != bg)
    print(f"Diff non-bg pixels: {np.sum(diff)}")
    
    # Compare components before and after
    comps0 = get_components(f0, bg, max_area=100)
    comps1 = get_components(f1, bg, max_area=100)
    
    for c0 in comps0:
        for c1 in comps1:
            if c0['area'] == c1['area'] and abs(c0['w'] - c1['w']) <= 1 and abs(c0['h'] - c1['h']) <= 1:
                dx = c1['cx'] - c0['cx']
                dy = c1['cy'] - c0['cy']
                if abs(dx) > 0 or abs(dy) > 0:
                    print(f"Avatar detected: color={f0[c0['cy'], c0['cx']]}, old_pos=({c0['cx']}, {c0['cy']}), new_pos=({c1['cx']}, {c1['cy']}), shift=({dx}, {dy}), area={c0['area']}")

if __name__ == "__main__":
    test_avatar_detect()
