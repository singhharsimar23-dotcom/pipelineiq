"""
Debug MyAgent on g50t with action traces.
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

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("g50t", seed=0)
obs = env.reset()
agent = MyAgent(card_id=None, game_id="g50t", agent_name="test", ROOT_URL="", record=False, arc_env=env)
game = env._game

for step in range(40):
    act = agent.choose_action([obs], obs)
    print(f"Step {step}: mode={agent.game_mode}, phase={agent.phase}, queue_len={len(agent.action_queue)}, act={act}, avatar=({game.vgwycxsxjz.dzxunlkwxt.x},{game.vgwycxsxjz.dzxunlkwxt.y})")
    obs = env.step(act)
    if obs.levels_completed > 0:
        print(f"WIN! levels_completed={obs.levels_completed}")
        break
