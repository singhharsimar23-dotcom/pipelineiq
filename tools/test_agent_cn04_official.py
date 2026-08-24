"""
Test MyAgent on cn04 using agent.take_action (official agent loop).
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

scores = []
for seed in range(5):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("cn04", seed=seed)
    obs = env.reset()
    agent = MyAgent(card_id=None, game_id="cn04", agent_name="test", ROOT_URL="", record=False, arc_env=env)
    
    for _ in range(40):
        act = agent.choose_action([obs], obs)
        obs = agent.take_action(act)
        if obs and obs.levels_completed > 0:
            break
    lvl = obs.levels_completed if obs else 0
    scores.append(lvl)
    print(f"Seed {seed}: mode={agent.game_mode}, levels_completed={lvl}")

print(f"MY_AGENT CN04 SCORES: {scores}")
