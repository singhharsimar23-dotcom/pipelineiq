"""
Quick diagnostic for sp80 — why is it scoring 0 now?
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
from my_agent import MyAgent, get_2d_grid, get_background_color, get_components

for seed in range(3):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("sp80", seed=seed)
    obs = env.reset()
    agent = MyAgent(card_id=None, game_id="sp80", agent_name="test", ROOT_URL="", record=False, arc_env=env)
    
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    
    # Get first action and mode
    act = agent.choose_action([obs], obs)
    print(f"Seed {seed}: game_mode={agent.game_mode}, phase={agent.phase}, act={act}, bg={bg}")
    
    # Run 80 steps
    for _ in range(80):
        obs = env.step(act)
        act = agent.choose_action([obs], obs)
    print(f"  Final: levels_completed={obs.levels_completed}")
