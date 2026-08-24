"""
DC22 - Try clicking directly on tovemc sprites (bridge pieces) 
and try different window/camera coordinate computations.
Also try clicking on the sprite objects in left vs right panel.
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
from my_agent import get_2d_grid
import numpy as np

arcade = Arcade(operation_mode=OperationMode.OFFLINE)
env = arcade.make("dc22", seed=0)
obs = env.reset()
game = env._game

f0 = get_2d_grid(obs)

# Check the camera to understand display -> grid mapping
print(f"Camera: {game.camera}")
print(f"Camera bg: {game.camera.background}")

# Click at various specific grid coords to see what happens
test_clicks = [
    (42, 7, "buezna-refgps center"),
    (42, 24, "buezna-blrmbx center"),
    (48, 9, "buezna-refgps center+offset"),
    (48, 26, "buezna-blrmbx center+offset"),
    (8, 24, "tovemc-plelvb1"),
    (18, 10, "tovemc-plelvb2"),
    (10, 30, "player pos"),
    (24, 10, "goal pos"),
    # Try clicking in different regions
    (32, 32, "center"),
    (41, 9, "aybe-upper inner"),
    (56, 9, "right of buezna-refgps"),
]

for cx, cy, label in test_clicks:
    env2 = arcade.make("dc22", seed=0)
    obs2 = env2.reset()
    g2 = env2._game
    f1_pre = get_2d_grid(obs2)
    obs2 = env2.step(GameAction.ACTION6, {"x": cx, "y": cy})
    f1 = get_2d_grid(obs2)
    diff = int(np.sum(f1_pre != f1))
    print(f"Click ({cx},{cy}) [{label}]: sjix={g2.sjixewahg}, uxtz={g2.uxtzlxsiq}, player=({g2.qnnpcoyzd.x},{g2.qnnpcoyzd.y}), pixel_diff={diff}, lvl={obs2.levels_completed}")
