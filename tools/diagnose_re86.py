import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def instrument_re86():
    print("=== RE86 INSTRUMENTATION START ===")
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("re86", seed=0)
    obs = env.reset()
    f = np.array(obs.frame[0])
    print(f"Initial frame shape: {f.shape}, unique colors: {np.unique(f)}")

    # Check available actions
    actions = getattr(obs, "available_actions", [])
    print(f"Available actions: {actions}")

    # Inspect sprites from current level
    lvl = env._game.current_level
    print(f"Level name: {lvl.name}")

    target_sprites = lvl.get_sprites_by_tag("0054xnsuqceejm")
    slider_sprites = lvl.get_sprites_by_tag("0031cppcuvqlbi")
    well_sprites = lvl.get_sprites_by_tag("0007dtbisvazhv")

    print(f"Target templates count: {len(target_sprites)}")
    for i, s in enumerate(target_sprites):
        valid = s.pixels[s.pixels != -1]
        print(f"  Target {i}: shape={s.pixels.shape} pos=({s.x},{s.y}) non-empty pixels={len(valid)} colors={np.unique(valid)}")

    print(f"Sliders count: {len(slider_sprites)}")
    for i, s in enumerate(slider_sprites):
        valid = s.pixels[s.pixels != -1]
        print(f"  Slider {i}: name={s.name} shape={s.pixels.shape} pos=({s.x},{s.y}) colors={np.unique(valid)}")

    print(f"Color wells count: {len(well_sprites)}")
    for i, s in enumerate(well_sprites):
        valid = s.pixels[s.pixels != -1]
        print(f"  Well {i}: shape={s.pixels.shape} pos=({s.x},{s.y}) colors={np.unique(valid)}")

    # Test actions
    print("\n--- Testing Directional Actions on Active Slider ---")
    for act_id, name in [(GameAction.ACTION1, "UP"), (GameAction.ACTION2, "DOWN"), (GameAction.ACTION3, "LEFT"), (GameAction.ACTION4, "RIGHT"), (GameAction.ACTION5, "CYCLE_SLIDER")]:
        obs_init = env.reset()
        f_before = np.array(obs_init.frame[0])
        obs_after = env.step(act_id)
        f_after = np.array(obs_after.frame[0])
        delta = int(np.sum(f_after != f_before))
        print(f"Action {act_id.name} ({name}): frame delta = {delta}")

    print("=== RE86 INSTRUMENTATION END ===")

if __name__ == "__main__":
    instrument_re86()
