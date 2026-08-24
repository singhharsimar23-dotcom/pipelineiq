"""
Inspect responsive buttons and actions in test_vc33_agent.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from agent.my_agent import MyAgent

def inspect_vc33_agent():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    agent = MyAgent(card_id="card", game_id="vc33", agent_name="agent", ROOT_URL="", record=False, arc_env=env)
    
    print(f"Probe positions ({len(agent.probe_positions)}): {agent.probe_positions}")
    for step in range(1, 50):
        action = agent.choose_action(None, obs)
        print(f"Step {step:2d}: phase={agent.phase}, act={action.id}, data={action.data}, queue_len={len(agent.action_queue)}, resp_buttons={agent.responsive_buttons}")
        obs = env.step(action)
        if obs.levels_completed > 0:
            print(f"*** LEVEL CLEARED AT STEP {step}! ***")
            break

if __name__ == "__main__":
    inspect_vc33_agent()
