"""
Check if cd82 or bp35 have mirror reflection signatures.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from my_agent import get_2d_grid, get_background_color, get_components

for gid in ["cd82", "bp35", "sk48", "sc25", "tn36", "su15"]:
    try:
        arcade = Arcade(operation_mode=OperationMode.OFFLINE)
        env = arcade.make(gid, seed=0)
        obs = env.reset()
        game = env._game
        f = get_2d_grid(obs)
        bg = get_background_color(f)
        comps = get_components(f, bg, max_area=600)
        
        mirror_lines = [c for c in comps if (c['h'] >= 40 and c['w'] <= 5) or (c['w'] >= 40 and c['h'] <= 5)]
        dots = [c for c in comps if c['area'] == 1 and c['w'] == 1 and c['h'] == 1]
        
        print(f"\n{gid}: actions={obs.available_actions}, bg={bg}, mirror_lines={len(mirror_lines)}, dots={len(dots)}")
    except Exception as e:
        print(f"{gid}: error {e}")
