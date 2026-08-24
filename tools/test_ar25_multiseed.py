"""
Multi-seed analysis of ar25 level 0.
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

arcade = Arcade(operation_mode=OperationMode.OFFLINE)

for seed in range(5):
    env = arcade.make("ar25", seed=seed)
    obs = env.reset()
    game = env._game
    
    f = get_2d_grid(obs)
    bg = get_background_color(f)
    comps = get_components(f, bg, max_area=600)
    
    print(f"\n--- Seed {seed} ---")
    print("Movable:", game.yvifanjrcyu.name if game.yvifanjrcyu else None, "at", (game.yvifanjrcyu.x, game.yvifanjrcyu.y) if game.yvifanjrcyu else None)
    print("Targets:", [(s.x, s.y) for s in game.fswikrcrdmx])
    print("All sprites:")
    for s in game.current_level.get_sprites():
        if s.is_visible:
            print(f"  {s.name}: ({s.x},{s.y}) {s.width}x{s.height} tags={s.tags}")
    
    # Try searching for dx, dy
    found = False
    for dy in range(-20, 25):
        for dx in range(-20, 25):
            env.reset()
            act_y = GameAction.ACTION1 if dy < 0 else GameAction.ACTION2
            for _ in range(abs(dy)):
                env.step(act_y)
            act_x = GameAction.ACTION3 if dx < 0 else GameAction.ACTION4
            for _ in range(abs(dx)):
                obs = env.step(act_x)
            if game.vplrhaovhr() or obs.levels_completed > 0:
                print(f"  WIN on seed {seed} with dx={dx}, dy={dy}! levels_completed={obs.levels_completed}")
                found = True
                break
        if found:
            break
