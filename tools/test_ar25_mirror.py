"""
Analyze ar25 mirror reflection puzzle mechanics.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("ar25", seed=0)
obs = env.reset()
game = env._game

print("Active object (yvifanjrcyu):", game.yvifanjrcyu.name if game.yvifanjrcyu else None, "pos:", (game.yvifanjrcyu.x, game.yvifanjrcyu.y) if game.yvifanjrcyu else None)
print("All selectable objects (ayyvxqrhnzw):", [(s.name, s.x, s.y, s.tags) for s in game.ayyvxqrhnzw])
print("Targets (fswikrcrdmx):", [(s.name, s.x, s.y) for s in game.fswikrcrdmx])
print("Initial win check:", game.vplrhaovhr())

# Test moving the active object left/right/up/down
for dx in range(-15, 15):
    env.reset()
    # Move active object
    act = GameAction.ACTION4 if dx > 0 else GameAction.ACTION3
    for _ in range(abs(dx)):
        obs = env.step(act)
    if game.vplrhaovhr() or obs.levels_completed > 0:
        print(f"WIN found by moving dx={dx}! levels_completed={obs.levels_completed}")
        break

# Try with switching active object (ACTION5)
for sel in range(len(game.ayyvxqrhnzw)):
    for dx in range(-25, 25):
        env.reset()
        for _ in range(sel):
            env.step(GameAction.ACTION5)
        act = GameAction.ACTION4 if dx > 0 else GameAction.ACTION3
        for _ in range(abs(dx)):
            obs = env.step(act)
        if game.vplrhaovhr() or obs.levels_completed > 0:
            print(f"WIN with sel={sel}, dx={dx}! levels_completed={obs.levels_completed}")
