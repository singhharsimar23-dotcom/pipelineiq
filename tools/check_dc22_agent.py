"""
Check what game mode and detection fires for dc22.
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

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
agent = MyAgent(card_id=None, game_id="dc22", agent_name="test", ROOT_URL="", record=False, arc_env=env)
game = env._game

f = get_2d_grid(obs)
bg = get_background_color(f)

print(f"bg={bg}, actions={obs.available_actions}")
comps = get_components(f, bg, max_area=600)
print(f"\nAll components ({len(comps)} total):")
for c in comps:
    print(f"  cx={c['cx']}, cy={c['cy']}, w={c['w']}, h={c['h']}, area={c['area']}, col={c['col']}")

# What does TOGGLE_CLUSTER detect?
button_cluster = [c for c in comps if 25 <= c['area'] <= 49 and abs(c['w'] - c['h']) <= 1]
print(f"\nButton cluster (area 25-49, square): {len(button_cluster)} found")

# Run first action to see what mode it picks
act = agent.choose_action([obs], obs)
print(f"\nAgent game_mode={agent.game_mode}, phase={agent.phase}, queue_len={len(agent.action_queue)}")
print(f"First action: {act}")
