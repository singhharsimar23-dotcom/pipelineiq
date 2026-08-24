"""
Inspect _build_clone_shadow_plan component filters on g50t.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from my_agent import get_components, get_background_color, get_2d_grid

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("g50t", seed=0)
obs = env.reset()
f = get_2d_grid(obs)
bg = get_background_color(f)

comps = get_components(f, bg, max_area=600)
print(f"Total comps: {len(comps)}")
for c in comps:
    print(f"Comp: pos=({c['cx']}, {c['cy']}), size=({c['w']}, {c['h']}), area={c['area']}, col={c['col']}")

goals = [c for c in comps if 60 <= c['area'] <= 120 and abs(c['w'] - c['h']) <= 2 and c['cy'] > 40]
print(f"Goals: {goals}")
switches = [c for c in comps if 35 <= c['area'] <= 55 and abs(c['w'] - c['h']) <= 2 and c['cy'] < 20]
print(f"Switches: {switches}")
