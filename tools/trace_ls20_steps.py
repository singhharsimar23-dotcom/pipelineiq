"""
Trace choose_action step-by-step for ls20.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from agent.my_agent import MyAgent
from arcengine import GameAction

def trace_ls20():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ls20", seed=0)
    obs = env.reset()
    agent = MyAgent(card_id="test", game_id="ls20", agent_name="agent", ROOT_URL="", record=False, arc_env=env)

    for step in range(1, 25):
        action = agent.choose_action(None, obs)
        print(f"Step {step:2d}: nav_probe_step={agent.nav_probe_step}, act={action.name}, avatar_pos={agent.avatar_pos}, avatar_color={agent.avatar_color}, queue_len={len(agent.action_queue)}")
        obs = env.step(action)
        if obs.levels_completed > 0:
            print(f"*** LEVEL CLEARED AT STEP {step}! ***")
            break

if __name__ == "__main__":
    trace_ls20()
