"""
Diagnostic probe for ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def inspect_ka59():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("ka59", seed=0)
    obs = env.reset()
    game = env._game

    print("=== KA59 LEVEL 0 ENTITIES ===")
    print("Available actions:", getattr(obs, "available_actions", []))
    print(f"Avatar: name={game.prkgpeyexo.name}, pos=(x={game.prkgpeyexo.x}, y={game.prkgpeyexo.y}), size=({game.prkgpeyexo.width}, {game.prkgpeyexo.height})")
    
    # Check all other sprites
    for s in game.current_level._sprites:
        if s != game.prkgpeyexo:
            print(f"Sprite: name={s.name}, pos=(x={s.x}, y={s.y}), size=({s.width}, {s.height}), tags={s.tags}")

if __name__ == "__main__":
    inspect_ka59()
