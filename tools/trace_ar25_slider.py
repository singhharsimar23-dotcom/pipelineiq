"""
ar25 slider trace - what actions does the slider plan generate?
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from my_agent import MyAgent, get_2d_grid, get_background_color, get_components

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ar25", seed=0)
obs = env.reset()
agent = MyAgent(card_id=None, game_id="ar25", agent_name="test", ROOT_URL="", record=False, arc_env=env)
game = env._game

f = get_2d_grid(obs)
bg = get_background_color(f)

# Get the slider plan
plan = agent._build_slider_5act_plan(f, bg)
print(f"Slider plan ({len(plan)} actions):")
for i, (act, data) in enumerate(plan[:20]):
    print(f"  [{i}] {act.name}")

# Check what the sliders look like in ar25
comps = get_components(f, bg, max_area=600)
large = [c for c in comps if c['area'] > 30]
print(f"\nLarge components (area>30): {[(c['cx'],c['cy'],c['area'],c['col']) for c in large]}")

# Try running the plan
act = agent.choose_action([obs], obs)
print(f"\nFirst action: {act}, mode={agent.game_mode}")
for step in range(40):
    obs = env.step(act)
    act = agent.choose_action([obs], obs)
    if obs.levels_completed > 0:
        print(f"WIN at step {step}!")
        break
print(f"Final: levels={obs.levels_completed}")

# What does the game look like after running?
f2 = get_2d_grid(obs)
print("\nFrame comparison (column 31, rows 10-50):")
for r in range(10, 50):
    print(f"  r={r}: {f[r, 20:45]} -> {f2[r, 20:45]}")
