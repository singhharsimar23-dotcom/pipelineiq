"""
Test agent.main() on vc33 across 5 seeds.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from agent.my_agent import MyAgent

def test_vc33_main():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    for seed in range(5):
        env = arcade.make("vc33", seed=seed)
        obs = env.reset()
        agent = MyAgent(
            card_id="test",
            game_id="vc33",
            agent_name="agent",
            ROOT_URL="",
            record=False,
            arc_env=env,
        )
        agent.main()
        print(f"Seed {seed}: levels_completed={agent.levels_completed}, state={agent.state}, steps={agent.action_counter}")
        scores.append(agent.levels_completed)
    print(f"VC33 Agent.main() Scores (Seeds 0-4): {scores}")

if __name__ == "__main__":
    test_vc33_main()
