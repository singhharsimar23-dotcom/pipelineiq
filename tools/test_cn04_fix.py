"""
Test cn04 detection and solve.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from my_agent import MyAgent, get_2d_grid, get_background_color

for seed in range(5):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("cn04", seed=seed)
    obs = env.reset()
    agent = MyAgent(card_id=None, game_id="cn04", agent_name="test", ROOT_URL="", record=False, arc_env=env)
    
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    circuit_plan = agent._build_circuit_connector_plan(f, bg)
    print(f"Seed {seed}: circuit_plan len = {len(circuit_plan)}")
    
    for act, data in circuit_plan:
        obs = env.step(act)
        if obs.levels_completed > 0:
            print(f"  WIN! levels_completed={obs.levels_completed}")
            break
    print(f"  Final: levels={obs.levels_completed}")
