"""
Print token coordinates after each step in test_vc33_smart_valves.
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

def test_smart_valves_detailed():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    f = np.array(obs.frame[0])
    bg = get_background_color(f)
    comps = get_components(f, bg, max_area=600)
    
    valves = [c for c in comps if (c['cx'] >= 54 or c['cx'] <= 10 or c['cy'] <= 10 or c['cy'] >= 54) and 4 <= c['area'] <= 80 and abs(c['w'] - c['h']) <= 2]
    print(f"Valves: {valves}")
    
    v0, v1 = valves[0], valves[1]
    
    # In test_vc33_scaled.py:
    # 9 clicks on (60, 24) then 6 clicks on (60, 32)
    print("\nClicking Valve 0 (61, 25) 9 times...")
    for s in range(1, 10):
        a = GameAction.ACTION6
        a.set_data({"x": 60, "y": 24})
        obs = env.step(a)
        t = env._game.current_level.get_sprites_by_tag("0016uciqlhjlom")[0]
        print(f"  v0 click {s}: token pos=({t.x}, {t.y}), levels_completed={obs.levels_completed}")

    print("\nClicking Valve 1 (60, 32) 10 times...")
    for s in range(1, 11):
        a = GameAction.ACTION6
        a.set_data({"x": 60, "y": 32})
        obs = env.step(a)
        t = env._game.current_level.get_sprites_by_tag("0016uciqlhjlom")[0]
        print(f"  v1 click {s}: token pos=({t.x}, {t.y}), levels_completed={obs.levels_completed}")
        if obs.levels_completed > 0:
            print(f"*** CLEARED AT STEP {s}! ***")
            break

if __name__ == "__main__":
    test_smart_valves_detailed()
