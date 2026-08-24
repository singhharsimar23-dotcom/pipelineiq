"""
Test MyAgent on g50t across 5 seeds.
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

def test_agent_g50t():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    
    for seed in range(5):
        env = arcade.make("g50t", seed=seed)
        obs = env.reset()
        agent = MyAgent(card_id=None, game_id="g50t", agent_name="test", ROOT_URL="", record=False, arc_env=env)
        
        for _ in range(40):
            act = agent.choose_action([obs], obs)
            obs = env.step(act)
            if obs.levels_completed > 0:
                break
                
        print(f"Seed {seed}: levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"MY_AGENT G50T SCORES: {scores}")

if __name__ == "__main__":
    test_agent_g50t()
