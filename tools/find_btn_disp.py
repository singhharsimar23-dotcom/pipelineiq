"""
Test display_to_grid mapping in dc22.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

for dy in range(0, 64, 4):
    for dx in range(0, 64, 8):
        g = game.camera.display_to_grid(dx, dy)
        if g == (48, 9):
            print(f"*** FOUND DISPLAY FOR btn_a (48, 9): display=({dx}, {dy}) ***")
        if g == (48, 26):
            print(f"*** FOUND DISPLAY FOR btn_b (48, 26): display=({dx}, {dy}) ***")
