"""
DC22 - Try clicking aybe buttons (the navigation controls at pos 41,6 and 41,23)
to see if they move the bridge cursor, then try placing the bridge.
Also trace the win condition frame by frame.
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

def full_trace_dc22():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=0)
    obs = env.reset()
    game = env._game

    print(f"Initial: sjix={game.sjixewahg}, uxtz={game.uxtzlxsiq}, player=({game.qnnpcoyzd.x},{game.qnnpcoyzd.y})")
    
    # All clickable sprites
    all_sprites = game.current_level.get_sprites()
    print("Clickable sprites:")
    for s in all_sprites:
        if s.interaction.value != 0:  # Not removed
            print(f"  {s.name}: pos=({s.x},{s.y}), tags={s.tags}")

    # Try clicking every clickable sprite
    for s in list(all_sprites):
        if s.name.startswith("sprite") or s.name.startswith("buezna"):
            cx, cy = s.x + s.width // 2, s.y + s.height // 2
            # Reset
            env2 = arcade.make("dc22", seed=0)
            obs2 = env2.reset()
            g2 = env2._game
            obs2 = env2.step(GameAction.ACTION6, {"x": cx, "y": cy})
            print(f"Click {s.name}({cx},{cy}): sjix={g2.sjixewahg}, uxtz={g2.uxtzlxsiq}, player=({g2.qnnpcoyzd.x},{g2.qnnpcoyzd.y}), lvl={obs2.levels_completed}")

    # Now try: click buezna-refgps (a), then move player UP and RIGHT
    print("\n--- Trying click buezna-refgps then navigate ---")
    env3 = arcade.make("dc22", seed=0)
    obs3 = env3.reset()
    g3 = env3._game
    
    btn_a = g3.current_level.get_sprites_by_tag("sys_click")[1]  # refgps = a
    obs3 = env3.step(GameAction.ACTION6, {"x": btn_a.x + 5, "y": btn_a.y + 2})
    print(f"After click a: sjix={g3.sjixewahg}, uxtz={g3.uxtzlxsiq}, player=({g3.qnnpcoyzd.x},{g3.qnnpcoyzd.y})")
    
    # Try clicking the aybe button (actual bridge cursor)
    aybe = g3.current_level.get_sprites_by_tag("aybe")[0]  # upper button
    obs3 = env3.step(GameAction.ACTION6, {"x": aybe.x + 6, "y": aybe.y + 3})
    print(f"After click aybe upper: sjix={g3.sjixewahg}, uxtz={g3.uxtzlxsiq}")
    
    # Try nav
    obs3 = env3.step(GameAction.ACTION1)
    print(f"UP: player=({g3.qnnpcoyzd.x},{g3.qnnpcoyzd.y})")
    obs3 = env3.step(GameAction.ACTION1)
    print(f"UP: player=({g3.qnnpcoyzd.x},{g3.qnnpcoyzd.y})")
    obs3 = env3.step(GameAction.ACTION4)
    print(f"RIGHT: player=({g3.qnnpcoyzd.x},{g3.qnnpcoyzd.y})")

if __name__ == "__main__":
    full_trace_dc22()
