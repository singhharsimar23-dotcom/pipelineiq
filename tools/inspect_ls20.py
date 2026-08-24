"""
Diagnostic inspection of ls20 Level 0 entities and win requirements.
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

def inspect_ls20():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ls20", seed=0)
    obs = env.reset()
    game = env._game

    print("=== LS20 LEVEL 0 ENTITIES ===")
    avatar = game.gudziatsk
    print(f"Avatar: pos=(x={avatar.x}, y={avatar.y}) size=({avatar.width}, {avatar.height})")
    print(f"Target doors count: {len(game.plrpelhym)}")
    for i, door in enumerate(game.plrpelhym):
        print(f"  Door {i}: pos=(x={door.x}, y={door.y}) size=({door.width}, {door.height})")
        print(f"    Required shape={game.ldxlnycps[i]}, color={game.yjdexjsoa[i]}, rot={game.ehwheiwsk[i]}")
        print(f"    Current shape={game.fwckfzsyc}, color={game.hiaauhahz}, rot={game.cklxociuu}")
        print(f"    Door matching initially: {game.bejndxqqzf(i)}")

    # Check modifiers on grid
    for tag, name in [("ttfwljgohq", "Shape"), ("soyhouuebz", "Color"), ("rhsxkxzdjz", "Rotation"), ("npxgalaybz", "Energy/Key")]:
        items = game.current_level.get_sprites_by_tag(tag)
        print(f"  {name} modifiers ({len(items)}): {[(s.x, s.y) for s in items]}")

    # Check walls
    walls = game.current_level.get_sprites_by_tag("ihdgageizm")
    print(f"  Walls count: {len(walls)}")

if __name__ == "__main__":
    inspect_ls20()
