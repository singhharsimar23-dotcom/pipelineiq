"""
DC22 - simpler approach: look at what sprites move/change on each click,
then trace the clickable map objects (plflho1, tovemc-plelvb) and 
understand the win condition properly.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
import numpy as np

def inspect_dc22_clicks():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=0)
    obs = env.reset()
    game = env._game
    
    from my_agent import get_2d_grid, get_background_color, get_components
    sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
    
    f0 = get_2d_grid(obs)
    
    # Check positions of all sprites
    print("=== ALL SPRITES ===")
    for s in game.current_level.get_sprites():
        print(f"  {s.name}: pos=({s.x},{s.y}), sz=({s.width}x{s.height}), tags={s.tags}")
    
    print(f"\nPlayer: ({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
    print(f"Goal: ({game.hfuqkxulm.x},{game.hfuqkxulm.y})")
    
    # Click button a
    sys_clicks = game.current_level.get_sprites_by_tag("sys_click")
    button_a = [s for s in sys_clicks if 'a' in s.tags][0]
    obs_a = env.step(GameAction.ACTION6, {"x": button_a.x + 5, "y": button_a.y + 2})
    f1 = get_2d_grid(obs_a)
    
    print("\n=== SPRITES AFTER CLICK A ===")
    for s in game.current_level.get_sprites():
        print(f"  {s.name}: pos=({s.x},{s.y}), interaction={s.interaction}")
    print(f"Player: ({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
    
    # Pixel diff
    diff = np.sum(f0 != f1)
    print(f"\nPixel diff after click A: {diff}")
    
    # Try moving now
    obs2 = env.step(GameAction.ACTION1)
    print(f"After Up: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
    obs2 = env.step(GameAction.ACTION1)
    print(f"After Up: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
    obs2 = env.step(GameAction.ACTION4)
    print(f"After Right: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
    obs2 = env.step(GameAction.ACTION4)
    print(f"After Right: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
    obs2 = env.step(GameAction.ACTION1)
    print(f"After Up: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
    obs2 = env.step(GameAction.ACTION1)
    print(f"After Up: player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent"))
    inspect_dc22_clicks()
