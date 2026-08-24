"""
Print composite canvas vs target in re86 Level 1.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

def inspect_mismatch():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    
    # Solve Level 0:
    for _ in range(7): obs = env.step(GameAction.ACTION1)
    for _ in range(4): obs = env.step(GameAction.ACTION4)
    obs = env.step(GameAction.ACTION5)
    for _ in range(6): obs = env.step(GameAction.ACTION1)
    for _ in range(2): obs = env.step(GameAction.ACTION3)
    
    # Level 1 moves:
    for _ in range(10): obs = env.step(GameAction.ACTION2)
    for _ in range(6): obs = env.step(GameAction.ACTION3)
    obs = env.step(GameAction.ACTION5)
    for _ in range(7): obs = env.step(GameAction.ACTION1)
    for _ in range(6): obs = env.step(GameAction.ACTION3)
    obs = env.step(GameAction.ACTION5)
    for _ in range(2): obs = env.step(GameAction.ACTION2)
    for _ in range(7): obs = env.step(GameAction.ACTION3)

    game = env._game
    lvl = game.current_level
    target = lvl.get_sprites_by_tag("0054xnsuqceejm")[0]
    sliders = lvl.get_sprites_by_tag("0031cppcuvqlbi")

    # Build composite canvas like jeiavrvavi does:
    tbz = np.full((64, 64), -1, dtype=np.int16)
    for vm in sliders:
        gh, gw = vm.height, vm.width
        for r in range(gh):
            for c in range(gw):
                if vm.pixels[r, c] != -1:
                    gy = vm.y + r
                    gx = vm.x + c
                    if 0 <= gy < 64 and 0 <= gx < 64:
                        tbz[gy, gx] = vm.pixels[r, c]
                        
    # Check differences with target
    t_mask = (target.pixels != -1) & (target.pixels != 4)
    t_pts = np.argwhere(t_mask)
    print("Differences between target and composite canvas:")
    for r, c in t_pts:
        print(f"  Target at ({r}, {c}) = {target.pixels[r, c]} | Composite = {tbz[r, c]}")

if __name__ == "__main__":
    inspect_mismatch()
