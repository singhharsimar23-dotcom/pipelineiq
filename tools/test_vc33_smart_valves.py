"""
Test smart valve pair selection in vc33.
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

def test_smart_valves():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    for seed in range(5):
        env = arcade.make("vc33", seed=seed)
        obs = env.reset()
        f = np.array(obs.frame[0])
        bg = get_background_color(f)
        comps = get_components(f, bg, max_area=600)
        
        # Real valve pairs: components on same perimeter edge with similar small area
        valves = [c for c in comps if (c['cx'] >= 54 or c['cx'] <= 10 or c['cy'] <= 10 or c['cy'] >= 54) and 4 <= c['area'] <= 80 and abs(c['w'] - c['h']) <= 2]
        print(f"\nSeed {seed}: Found {len(valves)} valve candidates: {[(v['cx'], v['cy']) for v in valves]}")
        
        # Click Valve 0 8 times (moves token to right end), then Valve 1 8 times (moves token to target indicator)
        v0 = valves[0]
        v1 = valves[1]
        
        for step in range(1, 17):
            v = v0 if step <= 6 else v1
            a = GameAction.ACTION6
            a.set_data({"x": v['cx'], "y": v['cy']})
            obs = env.step(a)
            if obs.levels_completed > 0:
                print(f"*** SEED {seed} LEVEL 0 CLEARED AT STEP {step}! ***")
                break

if __name__ == "__main__":
    test_smart_valves()
