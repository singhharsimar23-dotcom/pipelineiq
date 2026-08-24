"""
Quick ar25 diagnostic - check what game mode fires and what's happening.
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

for game_id in ["ar25", "bp35", "cd82"]:
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make(game_id, seed=0)
    obs = env.reset()
    agent = MyAgent(card_id=None, game_id=game_id, agent_name="test", ROOT_URL="", record=False, arc_env=env)
    
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    comps = get_components(f, bg, max_area=600)
    
    act = agent.choose_action([obs], obs)
    print(f"{game_id}: game_mode={agent.game_mode}, bg={bg}, actions={obs.available_actions}")
    
    # Run 600 steps
    for _ in range(600):
        obs = env.step(act)
        act = agent.choose_action([obs], obs)
    print(f"  Final: levels_completed={obs.levels_completed}")
