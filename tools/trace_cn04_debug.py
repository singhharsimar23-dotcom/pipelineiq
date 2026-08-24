"""
Debug step-by-step actions in cn04 with MyAgent.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from my_agent import MyAgent

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("cn04", seed=0)
obs = env.reset()
agent = MyAgent(card_id=None, game_id="cn04", agent_name="test", ROOT_URL="", record=False, arc_env=env)

for step in range(20):
    act = agent.choose_action([obs], obs)
    print(f"Step {step}: act={act.name}, data={getattr(act, 'data', None)}, queue_len={len(agent.action_queue)}, mode={agent.game_mode}")
    obs = env.step(act)
    if obs.levels_completed > 0:
        print(f"WIN at step {step}!")
        break
