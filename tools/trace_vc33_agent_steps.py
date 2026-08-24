"""
Trace exact agent actions on vc33.
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

def trace():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    agent = MyAgent(card_id="card", game_id="vc33", agent_name="agent", ROOT_URL="", record=False, arc_env=env)

    for step in range(1, 35):
        action = agent.choose_action(None, obs)
        data = getattr(action, "data", None)
        print(f"Step {step:2d}: phase={agent.phase}, act={action.name}, data={data}, resp_buttons={agent.responsive_buttons}")
        obs = env.step(action)
        if obs.levels_completed > 0:
            print(f"*** LEVEL CLEARED AT STEP {step}! ***")
            break

if __name__ == "__main__":
    trace()
