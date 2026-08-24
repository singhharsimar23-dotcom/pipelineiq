"""
Diagnostic probe for m0r0 (Mirror Sokoban / Avatar Merging Engine).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from collections import deque
import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def diagnose_m0r0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("m0r0", seed=0)
    obs = env.reset()
    game = env._game

    print("=== M0R0 LEVEL 0 ENTITIES ===")
    print("Available actions:", getattr(obs, "available_actions", []))
    
    for name in ["pikgci-toljda-leklkn", "pikgci-toljda-rivmdg", "pikgci-boweok-leklkn", "pikgci-boweok-rivmdg"]:
        s = game.current_level.get_sprites_by_name(name)
        if s:
            print(f"  Avatar '{name}': pos=(x={s[0].x}, y={s[0].y}) color={s[0].pixels[0,0]}")

    walls = game.current_level.get_sprites_by_tag("wahtyt")
    print(f"  Walls sprite count: {len(walls)}")
    if walls:
        w = walls[0]
        print(f"  Walls bounding box: pos=(x={w.x}, y={w.y}) shape={w.pixels.shape}")

    # Test directional movements from initial state
    print("\n--- Testing BFS on 4-mirror avatar state ---")
    # State is tuple of (p1, p2, p3, p4) coords
    # We want to find shortest action sequence that reaches a win (all merged)
    
if __name__ == "__main__":
    diagnose_m0r0()
