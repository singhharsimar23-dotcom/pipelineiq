"""
ar25 vs re86 comparison - understand why ar25 fails.
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
from my_agent import get_2d_grid, get_background_color, get_components

def inspect_game(game_id):
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make(game_id, seed=0)
    obs = env.reset()
    game = env._game
    
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    comps = get_components(f, bg, max_area=600)
    
    print(f"\n=== {game_id} ===")
    print(f"bg={bg}, actions={obs.available_actions}")
    print(f"Sprites:")
    for s in game.current_level.get_sprites():
        print(f"  {s.name}: ({s.x},{s.y}) {s.width}x{s.height} {s.interaction.name} tags={s.tags}")
    print(f"Components ({len(comps)}):")
    for c in comps[:10]:
        print(f"  cx={c['cx']}, cy={c['cy']}, w={c['w']}, h={c['h']}, area={c['area']}, col={c['col']}")
    
    # Test each action
    for act_id, name in [(1,"UP"),(2,"DOWN"),(3,"LEFT"),(4,"RIGHT"),(5,"ACTION5")]:
        env2 = arcade.make(game_id, seed=0)
        obs2 = env2.reset()
        g2 = env2._game
        obs2 = env2.step(GameAction.from_id(act_id))
        f2 = get_2d_grid(obs2)
        import numpy as np
        diff = int(np.sum(f != f2))
        print(f"  ACT{act_id}({name}): pixel_diff={diff}, lvl={obs2.levels_completed}")

inspect_game("ar25")
inspect_game("re86")
