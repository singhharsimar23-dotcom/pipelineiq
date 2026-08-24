"""
Pure numpy / matrix simulator for re86.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def simulate_re86_level(game):
    # Target sprite
    target = game.current_level.get_sprites_by_tag("0054xnsuqceejm")[0]
    sliders = game.current_level.get_sprites_by_tag("0031cppcuvqlbi")
    
    # Let's extract target non-(-1) and non-4 mask
    t_pix = target.pixels
    t_mask = (t_pix != -1) & (t_pix != 4)
    print(f"Target non-empty count: {np.sum(t_mask)}")
    
    # We want composite canvas tbzfoterqb to match target at all t_mask locations
    # tbzfoterqb is initialized to -1 (or transparent)
    # When slider 0 is placed at (x0, y0) with internal shift, and slider 1 at (x1, y1) with internal shift,
    # let's inspect the exact shift mechanism:
    # In re86.py:
    # A slider has a center line in X and center line in Y of color C.
    # When ACTION1 (UP) is applied: the horizontal line shifts by -3 in Y.
    # When ACTION2 (DOWN): horizontal line shifts by +3 in Y.
    # When ACTION3 (LEFT): vertical line shifts by -3 in X.
    # When ACTION4 (RIGHT): vertical line shifts by +3 in X.
    
    # Let's find the required horizontal line Y position and vertical line X position for each slider!
    # For slider 0 (color 11):
    t_c11_pts = np.argwhere((t_pix == 11) & t_mask)
    print(f"Target color 11 points:\n{t_c11_pts}")
    # A cross has 4 points: top, bottom, left, right (or horizontal line + vertical line intersecting)
    # Notice: t_c11_pts are (3, 15), (9, 6), (9, 24), (17, 15)
    # The vertical line is at X = 15!
    # The horizontal line is at Y = 9!
    # Let's verify:
    # Top point: (3, 15), Bottom point: (17, 15) -> vertical line at X=15!
    # Left point: (9, 6), Right point: (9, 24) -> horizontal line at Y=9!
    # Intersection center: (Y=9, X=15)!
    
    # For slider 1 (color 9):
    t_c9_pts = np.argwhere((t_pix == 9) & t_mask)
    print(f"Target color 9 points:\n{t_c9_pts}")
    # t_c9_pts are (16, 48), (24, 40), (24, 53), (35, 48)
    # The vertical line is at X = 48!
    # The horizontal line is at Y = 24!
    # Intersection center: (Y=24, X=48)!

    # Now let's find the INITIAL line positions for Slider 0 and Slider 1!
    # Slider 0: pos = (x=10, y=16), size = (23, 23).
    # Initial lines in Slider 0: horizontal at local Y=11, vertical at local X=11.
    # Global Y = 16 + 11 = 27. Global X = 10 + 11 = 21.
    # Desired Global Y = 9, Desired Global X = 15.
    # Delta Y0 = 9 - 27 = -18 -> (-18 / 3) = -6 steps (6 * ACTION1 - UP)!
    # Delta X0 = 15 - 21 = -6 -> (-6 / 3) = -2 steps (2 * ACTION3 - LEFT)!

    # Slider 1: pos = (x=23, y=32), size = (27, 27).
    # Initial lines in Slider 1: horizontal at local Y=13, vertical at local X=13.
    # Global Y = 32 + 13 = 45. Global X = 23 + 13 = 36.
    # Desired Global Y = 24, Desired Global X = 48.
    # Delta Y1 = 24 - 45 = -21 -> (-21 / 3) = -7 steps (7 * ACTION1 - UP)!
    # Delta X1 = 48 - 36 = +12 -> (+12 / 3) = +4 steps (4 * ACTION4 - RIGHT)!

    print(f"\nCalculated Analytical Actions:")
    print(f"Slider 1 (initially active): Y=-7 (7 UP), X=+4 (4 RIGHT)")
    print(f"Switch: ACTION5")
    print(f"Slider 0: Y=-6 (6 UP), X=-2 (2 LEFT)")

    # Build sequence
    actions = []
    # 1. Slider 1 moves
    actions.extend([GameAction.ACTION1] * 7) # 7 UP
    actions.extend([GameAction.ACTION4] * 4) # 4 RIGHT
    
    # 2. Switch to Slider 0
    actions.append(GameAction.ACTION5)
    
    # 3. Slider 0 moves
    actions.extend([GameAction.ACTION1] * 6) # 6 UP
    actions.extend([GameAction.ACTION3] * 2) # 2 LEFT

    return actions

def test_full_re86():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    game = env._game

    actions = simulate_re86_level(game)
    print(f"\nExecuting sequence of length {len(actions)}...")
    for i, a in enumerate(actions):
        obs = env.step(a)
        print(f"Step {i+1} ({a.name}): state={obs.state}, levels_completed={obs.levels_completed}")
        if obs.levels_completed > 0:
            print(f"*** LEVEL CLEARED AT STEP {i+1}! ***")
            break

if __name__ == "__main__":
    test_full_re86()
