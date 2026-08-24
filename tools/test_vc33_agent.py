"""
Test my_agent on vc33 across 5 seeds.
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

def test_vc33_agent():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    for seed in range(5):
        env = arcade.make("vc33", seed=seed)
        obs = env.reset()
        agent = MyAgent(card_id="card", game_id="vc33", agent_name="agent", ROOT_URL="", record=False, arc_env=env)
        
        while True:
            action = agent.choose_action(None, obs)
            obs = env.step(action)
            if obs.levels_completed > 0 or getattr(obs, "state", None) in (1, 2) or agent.step_counter > 500:
                break
        print(f"Seed {seed}: levels_completed={obs.levels_completed}, steps={agent.step_counter}, game_mode={agent.game_mode}, phase={agent.phase}")
        scores.append(obs.levels_completed)
    print(f"VC33 Scores: {scores}")

if __name__ == "__main__":
    test_vc33_agent()
