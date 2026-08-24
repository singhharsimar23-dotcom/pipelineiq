"""
Debug what game mode MyAgent detects for g50t.
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
from my_agent import MyAgent, get_components, get_background_color, get_2d_grid
import numpy as np

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("g50t", seed=0)
obs = env.reset()
agent = MyAgent(card_id=None, game_id="g50t", agent_name="test", ROOT_URL="", record=False, arc_env=env)

f = get_2d_grid(obs)
bg = get_background_color(f)

print(f"Available actions: {obs.available_actions}")
print(f"Background: {bg}")
print(f"has_dir: {any(a in obs.available_actions for a in [1,2,3,4])}")
print(f"has_click: {6 in obs.available_actions}")
print(f"has_cycle: {5 in obs.available_actions}")
print(f"Game mode: {agent.game_mode}")

# What does _build_clone_shadow_plan return?
clone_result = agent._build_clone_shadow_plan(f, bg)
print(f"clone_plan length: {len(clone_result)}")

# What does _build_herding_plan return?
herd_result = agent._build_herding_plan(f, bg)
print(f"herd_plan length: {len(herd_result)}")

comps = get_components(f, bg, max_area=600)
print("\nAll components:")
for c in comps:
    print(f"  cx={c['cx']}, cy={c['cy']}, w={c['w']}, h={c['h']}, area={c['area']}, col={c['col']}")

# Check conditions specifically
goals = [c for c in comps if c['cx'] > 35 and c['cy'] > 40 and 12 <= c['area'] <= 40]
avatars = [c for c in comps if c['cx'] < 25 and 5 <= c['cy'] < 20 and 12 <= c['area'] <= 40]
clocks = [c for c in comps if c['cy'] <= 5 and 5 <= c['area'] <= 15]
print(f"\nGoals found: {goals}")
print(f"Avatars found: {avatars}")
print(f"Clocks found: {clocks}")
