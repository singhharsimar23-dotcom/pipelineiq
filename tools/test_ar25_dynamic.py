"""
Develop dynamic coordinate-free mirror reflection solver for ar25.
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

def solve_ar25_seed(seed):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ar25", seed=seed)
    obs = env.reset()
    game = env._game
    
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    comps = get_components(f, bg, max_area=600)
    
    # Let's inspect all components
    print(f"\n--- Seed {seed} ---")
    for c in comps:
        print(f"  cx={c['cx']}, cy={c['cy']}, w={c['w']}, h={c['h']}, area={c['area']}, col={c['col']}")
        
    # The symmetry line: thin line spanning a large dimension (e.g. w=1 or h=1 with length > 20)
    # Or vertical divider
    mirror_lines = [c for c in comps if (c['w'] <= 2 and c['h'] >= 20) or (c['h'] <= 2 and c['w'] >= 20)]
    print(f"Mirror lines: {mirror_lines}")
    
    # Target dots: small area=1 dots of a specific target color
    # Movable shape: component that is not mirror line and not target dots
    
    # Let's verify what components exist
    target_dots = [c for c in comps if c['area'] == 1 and c['w'] == 1 and c['h'] == 1]
    print(f"Target dots: {len(target_dots)} dots at {[(c['cx'], c['cy']) for c in target_dots]}")
    
    movable = [c for c in comps if 4 <= c['area'] <= 25 and c['w'] <= 5 and c['h'] <= 5]
    print(f"Movable candidates: {movable}")
    
    if mirror_lines and target_dots and movable:
        m_line = mirror_lines[0]
        # Vertical mirror line at m_line['cx']
        mirror_x = m_line['cx']
        
        target_ys = [c['cy'] for c in target_dots]
        target_xs = [c['cx'] for c in target_dots]
        
        # Target bounding box
        min_ty, max_ty = min(target_ys), max(target_ys)
        min_tx, max_tx = min(target_xs), max(target_xs)
        
        shape = movable[0]
        # We need the reflected shape to match the target dots
        # Reflection across mirror_x: x_reflected = 2 * mirror_x - x_orig
        # So x_orig = 2 * mirror_x - x_reflected
        # The desired y is min_ty
        # The desired x: if targets are to the right of mirror line, x_target > mirror_x
        # x_orig will be < mirror_x
        # Specifically, min_tx reflects to max_sx: max_sx = 2 * mirror_x - min_tx
        # min_sx = 2 * mirror_x - max_tx
        desired_min_sx = 2 * mirror_x - max_tx
        desired_min_sy = min_ty
        
        curr_min_sx = shape['min_c']
        curr_min_sy = shape['min_r']
        
        dx = desired_min_sx - curr_min_sx
        dy = desired_min_sy - curr_min_sy
        
        print(f"Computed: dx={dx}, dy={dy} (mirror_x={mirror_x}, target_x_range=[{min_tx},{max_tx}], target_y_range=[{min_ty},{max_ty}])")
        
        # Execute actions
        actions = []
        if dy < 0:
            actions.extend([(GameAction.ACTION1, {})] * abs(dy))
        elif dy > 0:
            actions.extend([(GameAction.ACTION2, {})] * dy)
            
        if dx < 0:
            actions.extend([(GameAction.ACTION3, {})] * abs(dx))
        elif dx > 0:
            actions.extend([(GameAction.ACTION4, {})] * dx)
            
        for act, data in actions:
            obs = env.step(act)
            
        print(f"Result: levels_completed={obs.levels_completed}")
        return obs.levels_completed

for s in range(5):
    solve_ar25_seed(s)
