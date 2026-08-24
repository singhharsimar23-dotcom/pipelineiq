"""
Test solving wa30 Level 0 via sheep herding into the pen.
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

def solve_wa30_level0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("wa30", seed=0)
    obs = env.reset()
    game = env._game

    avatar = game.current_level.get_sprites_by_tag("wbmdvjhthc")[0]
    print(f"Start: Avatar at ({avatar.x}, {avatar.y})")
    
    # -------------------------------------------------------------
    # SHEEP 0: at (32, 36)
    # -------------------------------------------------------------
    # Avatar is at (32, 48). Move Up 2 steps to (32, 40) (facing Up at sheep at 32, 36)
    env.step(GameAction.ACTION1) # (32, 44)
    env.step(GameAction.ACTION1) # (32, 40)
    print(f"Avatar at ({avatar.x}, {avatar.y}), facing Up towards sheep (32, 36)")
    # Pick up sheep 0 (ACTION5)
    env.step(GameAction.ACTION5)
    print(f"Picked up? Attached: {avatar in game.nsevyuople}")
    
    # Walk Up with sheep into pen:
    # Move Up 3 steps: (32, 40) -> (32, 36) -> (32, 32) -> (32, 28)
    # Note: Sheep is at (32, 36) -> (32, 32) -> (32, 28) (which is in the pen!)
    env.step(GameAction.ACTION1) # avatar at (32, 36), sheep at (32, 32)
    env.step(GameAction.ACTION1) # avatar at (32, 32), sheep at (32, 28)
    # Drop sheep (ACTION5)
    env.step(GameAction.ACTION5)
    print(f"Sheep 0 deposited in pen! In pen count: {sum(game.shbxbhnhjc((s.x, s.y)) for s in game.current_level.get_sprites_by_tag('geezpjgiyd'))}")

    # -------------------------------------------------------------
    # SHEEP 1: at (16, 28)
    # -------------------------------------------------------------
    # Avatar is at (32, 32). Move Down to (32, 36) -> Left to (20, 36) -> Up to (20, 28) -> Left to (20, 28) facing sheep at (16, 28)
    env.step(GameAction.ACTION2) # (32, 36)
    env.step(GameAction.ACTION3) # (28, 36)
    env.step(GameAction.ACTION3) # (24, 36)
    env.step(GameAction.ACTION3) # (20, 36)
    env.step(GameAction.ACTION1) # (20, 32)
    env.step(GameAction.ACTION1) # (20, 28)
    # Turn Left towards sheep at (16, 28): (move Left from 20 to 16 fails or faces left?)
    # Moving Left while blocked changes rotation!
    env.step(GameAction.ACTION3) # Faces Left (270)
    print(f"Avatar at ({avatar.x}, {avatar.y}), rotation: {avatar.rotation}")
    # Pick up sheep 1 (ACTION5)
    env.step(GameAction.ACTION5)
    print(f"Picked up Sheep 1? Attached: {avatar in game.nsevyuople}")
    
    # Walk Right with sheep into pen:
    # Move Right 2 steps: avatar (20, 28) -> (24, 28) -> (28, 28), sheep (16, 28) -> (20, 28) -> (24, 28) -> (28, 28)
    env.step(GameAction.ACTION4) # avatar at (24, 28), sheep at (20, 28)
    env.step(GameAction.ACTION4) # avatar at (28, 28), sheep at (24, 28)
    env.step(GameAction.ACTION4) # avatar at (32, 28), sheep at (28, 28)
    # Drop sheep (ACTION5)
    env.step(GameAction.ACTION5)
    print(f"Sheep 1 deposited in pen! In pen count: {sum(game.shbxbhnhjc((s.x, s.y)) for s in game.current_level.get_sprites_by_tag('geezpjgiyd'))}")

    # -------------------------------------------------------------
    # SHEEP 2: at (44, 24)
    # -------------------------------------------------------------
    # Avatar is at (32, 28). Move Down to (32, 36) -> Right to (44, 36) -> Up to (44, 28) facing sheep at (44, 24)
    env.step(GameAction.ACTION2) # (32, 32)
    env.step(GameAction.ACTION2) # (32, 36)
    env.step(GameAction.ACTION4) # (36, 36)
    env.step(GameAction.ACTION4) # (40, 36)
    env.step(GameAction.ACTION4) # (44, 36)
    env.step(GameAction.ACTION1) # (44, 32)
    env.step(GameAction.ACTION1) # (44, 28) (facing Up towards sheep at 44, 24!)
    # Pick up sheep 2 (ACTION5)
    env.step(GameAction.ACTION5)
    print(f"Picked up Sheep 2? Attached: {avatar in game.nsevyuople}")

    # Walk Left/Down with sheep into pen at (36, 28):
    # Avatar at (44, 28), sheep at (44, 24).
    # Move Left 2 steps: (44, 28) -> (40, 28) -> (36, 28). Sheep at (40, 24) -> (36, 24)
    # Then Move Down 1 step: avatar at (36, 32), sheep at (36, 28) (in pen!)
    env.step(GameAction.ACTION3) # avatar (40, 28), sheep (40, 24)
    env.step(GameAction.ACTION3) # avatar (36, 28), sheep (36, 24)
    env.step(GameAction.ACTION2) # avatar (36, 32), sheep (36, 28)
    obs = env.step(GameAction.ACTION5) # Drop sheep 2
    
    print(f"Final Win Check: {game.ymzfopzgbq()}, levels_completed={obs.levels_completed}")

if __name__ == "__main__":
    solve_wa30_level0()
