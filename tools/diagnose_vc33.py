"""
Diagnostic probe for vc33 (Card Match / Token Sorting Engine).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

def diagnose_vc33():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("vc33", seed=0)
    obs = env.reset()
    
    lvl = env._game.current_level
    print(f"=== VC33 DIAGNOSTIC START ===")
    print(f"Level name: {lvl.name}")
    
    valves = lvl.get_sprites_by_tag("0022jvmlspyigc")
    gates = lvl.get_sprites_by_tag("0004sttgkofqwb")
    tokens = lvl.get_sprites_by_tag("0016uciqlhjlom")
    targets = lvl.get_sprites_by_tag("0010gnulkywfpz")
    
    print(f"Valves count: {len(valves)}")
    for i, v in enumerate(valves):
        print(f"  Valve {i}: pos=(x={v.x}, y={v.y}) size={v.pixels.shape} click_center=(x={v.x + v.width//2}, y={v.y + v.height//2})")

    print(f"Gates count: {len(gates)}")
    for i, g in enumerate(gates):
        print(f"  Gate {i}: pos=(x={g.x}, y={g.y}) size={g.pixels.shape} click_center=(x={g.x + g.width//2}, y={g.y + g.height//2})")

    print(f"Tokens count: {len(tokens)}")
    for i, t in enumerate(tokens):
        color = t.pixels[-1, -1]
        print(f"  Token {i}: pos=(x={t.x}, y={t.y}) color={color}")

    print(f"Target Indicators count: {len(targets)}")
    for i, tg in enumerate(targets):
        valid = tg.pixels[tg.pixels != -2]
        print(f"  Target Indicator {i}: pos=(x={tg.x}, y={tg.y}) colors={np.unique(valid)}")

    # Let's test clicking Valve 0 and see how tokens shift
    print("\n--- Testing Valve 0 click ---")
    f_before = np.array(obs.frame[0])
    v0 = valves[0]
    click_x = v0.x + v0.width // 2
    click_y = v0.y + v0.height // 2
    obs_after = env.step(GameAction.ACTION6, data={"x": click_x, "y": click_y})
    f_after = np.array(obs_after.frame[0])
    delta = int(np.sum(f_after != f_before))
    print(f"Clicked Valve 0 at ({click_x}, {click_y}) -> frame delta = {delta}")
    
    # Check tokens after click
    for i, t in enumerate(tokens):
        print(f"  Token {i} after click: pos=(x={t.x}, y={t.y})")

if __name__ == "__main__":
    diagnose_vc33()
