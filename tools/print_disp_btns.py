"""
Print display coordinates for dc22 buttons.
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

btn_a = [s for s in game.current_level.get_sprites() if s.name == "buezna-refgps"][0]
btn_b = [s for s in game.current_level.get_sprites() if s.name == "buezna-blrmbx"][0]

print(f"btn_a grid pos: ({btn_a.x}, {btn_a.y}), center: ({btn_a.x + btn_a.width//2}, {btn_a.y + btn_a.height//2})")
print(f"btn_b grid pos: ({btn_b.x}, {btn_b.y}), center: ({btn_b.x + btn_b.width//2}, {btn_b.y + btn_b.height//2})")

disp_a = game.camera.grid_to_display(btn_a.x + btn_a.width//2, btn_a.y + btn_a.height//2)
disp_b = game.camera.grid_to_display(btn_b.x + btn_b.width//2, btn_b.y + btn_b.height//2)

print(f"Display coords: btn_a -> {disp_a}, btn_b -> {disp_b}")
