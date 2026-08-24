"""
Pure analytical connector-matching solver for cn04 Level 0.
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

def solve_cn04_math():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("cn04", seed=0)
    obs = env.reset()
    game = env._game

    s1 = game.current_level.get_sprites()[0]
    s2 = game.current_level.get_sprites()[1]

    # Original s1 pixels: shape=(5, 6), 8s at: (1, 5), (3, 5)
    # Original s2 pixels: shape=(7, 4), 8s at: (2, 0), (4, 0)
    # s2 position: (12, 9), rotation: 0
    # So s2 connectors in world grid are: (12 + 0, 9 + 2) = (12, 11) and (12 + 0, 9 + 4) = (12, 13)
    
    # We want s1 rotated such that its connectors are at (12, 11) and (12, 13)
    # Let's check rotation of s1:
    # If s1 is rotated by angle rot in {0, 90, 180, 270}:
    for rot in [0, 90, 180, 270]:
        # Copy s1 pixels and rotate
        p = s1.pixels.copy()
        k = rot // 90
        p_rot = np.rot90(p, -k) # arcengine rotate
        c_pts = np.argwhere(p_rot == 8)
        # We need relative spacing to match (12, 11) and (12, 13) which has dy=2, dx=0
        if len(c_pts) == 2:
            dy = c_pts[1][0] - c_pts[0][0]
            dx = c_pts[1][1] - c_pts[0][1]
            if (dx == 0 and dy == 2) or (dx == 0 and dy == -2):
                # Matching orientation!
                # Target grid pos:
                # c_pts[0] should be at world (12, 11) -> s1.x + c_pts[0][1] == 12, s1.y + c_pts[0][0] == 11
                target_x = 12 - c_pts[0][1]
                target_y = 11 - c_pts[0][0]
                print(f"Matched rotation: {rot}, target_pos: ({target_x}, {target_y})")
                
                # S1 starts at (3, 3) with rotation 90
                # Rotations needed:
                rot_actions = ((rot - 90) % 360) // 90
                dx_steps = target_x - 3
                dy_steps = target_y - 3
                print(f"Actions needed: rot_actions={rot_actions}, dx={dx_steps}, dy={dy_steps}")
                
                # Execute in env!
                env.step(GameAction.ACTION6, data={"x": 18, "y": 18})
                for _ in range(rot_actions):
                    env.step(GameAction.ACTION5)
                if dx_steps < 0:
                    for _ in range(abs(dx_steps)):
                        env.step(GameAction.ACTION3)
                elif dx_steps > 0:
                    for _ in range(dx_steps):
                        env.step(GameAction.ACTION4)
                if dy_steps < 0:
                    for _ in range(abs(dy_steps)):
                        env.step(GameAction.ACTION1)
                elif dy_steps > 0:
                    for _ in range(dy_steps):
                        obs = env.step(GameAction.ACTION2)
                        
                print(f"Env win result: win_check={game.sjwqloivve()}, levels_completed={obs.levels_completed}")
                return

if __name__ == "__main__":
    solve_cn04_math()
