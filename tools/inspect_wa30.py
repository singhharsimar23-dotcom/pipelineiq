"""
Inspect wa30 Level 0 sprites, sheep, pen, and avatar.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
import numpy as np

def inspect_wa30():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("wa30", seed=0)
    obs = env.reset()
    game = env._game

    print("=== WA30 LEVEL 0 HERDING / TRANSPORT ===")
    print("Available actions:", getattr(obs, "available_actions", []))
    for s in game.current_level.get_sprites():
        print(f"Sprite: name={s.name}, pos=({s.x}, {s.y}), size=({s.width}, {s.height}), tags={s.tags}")
        
    avatar = game.current_level.get_sprites_by_tag("wbmdvjhthc")[0]
    sheep = game.current_level.get_sprites_by_tag("geezpjgiyd")
    print(f"Avatar: pos=({avatar.x}, {avatar.y})")
    print(f"Sheep ({len(sheep)}): {[ (s.x, s.y) for s in sheep ]}")
    print(f"Step size celomdfhbh: {getattr(game, 'celomdfhbh', 'N/A')}")
    print(f"Initial win check: {game.ymzfopzgbq()}")

if __name__ == "__main__":
    inspect_wa30()
