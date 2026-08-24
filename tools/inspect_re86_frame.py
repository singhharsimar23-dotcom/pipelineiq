"""
Check how target template is rendered in the observation frame in re86.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode

def inspect_frame_template():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    f = np.array(obs.frame[0])

    print("Frame unique values:", np.unique(f))
    # Target points were:
    # Color 11 at (3, 15), (9, 6), (9, 24), (17, 15)
    # Color 9 at (16, 48), (24, 40), (24, 53), (35, 48)
    
    print("\nPixel values at target locations in initial frame:")
    for r, c in [(3, 15), (9, 6), (9, 24), (17, 15)]:
        print(f"  ({r}, {c}) in f = {f[r, c]}")
    for r, c in [(16, 48), (24, 40), (24, 53), (35, 48)]:
        print(f"  ({r}, {c}) in f = {f[r, c]}")

    # Let's inspect where color 11 and color 9 and color 4 (guide dots/brackets) are in f:
    for c in [4, 5, 9, 11, 15]:
        pts = np.argwhere(f == c)
        print(f"Color {c}: count = {len(pts)}")
        if len(pts) <= 10:
            print(f"  points = {pts.tolist()}")

if __name__ == "__main__":
    inspect_frame_template()
