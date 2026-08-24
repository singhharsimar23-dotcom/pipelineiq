"""
sp80 - test with full 600-step budget across 5 seeds.
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
from my_agent import MyAgent

scores = []
for seed in range(5):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("sp80", seed=seed)
    obs = env.reset()
    agent = MyAgent(card_id=None, game_id="sp80", agent_name="test", ROOT_URL="", record=False, arc_env=env)
    
    for _ in range(600):
        act = agent.choose_action([obs], obs)
        obs = env.step(act)
    scores.append(obs.levels_completed)
    print(f"Seed {seed}: levels_completed={obs.levels_completed}")

print(f"SP80 SCORES: {scores}")
