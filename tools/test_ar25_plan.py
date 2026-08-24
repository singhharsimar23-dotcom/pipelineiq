"""
Verify exact dynamic mirror calculation for ar25.
"""
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from my_agent import get_2d_grid, get_background_color, get_components

def test_ar25(seed):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ar25", seed=seed)
    obs = env.reset()
    game = env._game
    
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    comps = get_components(f, bg, max_area=600)
    
    # 1. Mirror line is the tall vertical line (h >= 40, w <= 5)
    mirror_lines = [c for c in comps if c['h'] >= 40 and c['w'] <= 5]
    if not mirror_lines:
        return 0
    mirror = mirror_lines[0]
    
    # 2. Target dots (area <= 2, color matching targets)
    # 3. Movable piece (shape near mirror)
    # Let's find target dots
    dots = [c for c in comps if c['area'] == 1 and c['w'] == 1 and c['h'] == 1]
    
    # Movable shapes are the medium components (area 20-60)
    shapes = [c for c in comps if 20 <= c['area'] <= 60 and c != mirror]
    
    print(f"Seed {seed}: Mirror={mirror['cx']}, Dots={len(dots)}, Shapes={len(shapes)}")
    
    # If we apply dx=-10, dy=10 in level 0
    # In general, let's see why dx=-10, dy=10 works:
    # Initial shape is at cx=22, cy=19.
    # Target dots center is:
    dot_cx = int(np.mean([d['cx'] for d in dots]))
    dot_cy = int(np.mean([d['cy'] for d in dots]))
    print(f"Dot center: ({dot_cx}, {dot_cy})")
    
    # Reflected dot center across mirror['cx']:
    reflected_cx = 2 * mirror['cx'] - dot_cx
    print(f"Reflected center: ({reflected_cx}, {dot_cy})")
    
    # The left shape (cx=22, cy=19) needs to move so its center matches reflected center?
    # Wait, the shape is at cx=22, reflected_cx = 2*31 - 23 = 62 - 23 = 39 (the right shape is at cx=40).
    # Wait, the movable piece in the game engine was at (6, 5) in internal coords, which is (22, 19) in display coords!
    # Moving dx=-10 in internal coords moves it left by 10 pixels (or 3 grid cells).
    
    # Let's test the plan:
    actions = [GameAction.ACTION1] * 0 + [GameAction.ACTION2] * 10 + [GameAction.ACTION3] * 10
    for act in actions:
        obs = env.step(act)
    print(f"Seed {seed} result: levels={obs.levels_completed}")
    return obs.levels_completed

for s in range(5):
    test_ar25(s)
