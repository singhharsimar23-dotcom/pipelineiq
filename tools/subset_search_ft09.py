import sys
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState


def get_2d_grid(frame_data) -> np.ndarray:
    if frame_data is None:
        return np.zeros((64, 64), dtype=np.int16)
    f = getattr(frame_data, "frame", frame_data)
    if isinstance(f, list):
        if len(f) == 0:
            return np.zeros((64, 64), dtype=np.int16)
        f = np.array(f[-1])
    else:
        f = np.array(f)
    while f.ndim > 2:
        f = f[-1]
    if f.ndim == 3 and f.shape[-1] == 3:
        _, inverse = np.unique(f.reshape(-1, 3), axis=0, return_inverse=True)
        f = inverse.reshape(f.shape[0], f.shape[1])
    if f.shape != (64, 64):
        res = np.zeros((64, 64), dtype=np.int16)
        h, w = min(64, f.shape[0]), min(64, f.shape[1])
        res[:h, :w] = f[:h, :w]
        return res
    return f.astype(np.int16)


def main():
    RESPONSIVE_BUTTONS = [
        (38, 38), (46, 38), (54, 38),
        (38, 46),           (54, 46),
        (38, 54), (46, 54), (54, 54)
    ]

    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard(tags=["subset_search_ft09_seed0"])
    env = arc.make("ft09", seed=0, scorecard_id=sc_id)

    total_steps = 0

    # ── STEP A: COLOR OBSERVATION ──
    print("=== STEP A: COLOR OBSERVATION ===")
    obs_init = env.observation_space
    grid_before = get_2d_grid(obs_init)
    color_before = int(grid_before[38, 38])
    print(f"Position (38, 38) BEFORE click: color={color_before}")

    obs_click = env.step(GameAction.ACTION6, data={"x": 38, "y": 38})
    total_steps += 1
    grid_after = get_2d_grid(obs_click)
    color_after = int(grid_after[38, 38])
    print(f"Position (38, 38) AFTER click:  color={color_after}")

    env.step(GameAction.RESET, data={})
    total_steps += 1
    print("RESET issued.")

    # ── STEP B: REFERENCE PATTERN OBSERVATION ──
    print("\n=== STEP B: REFERENCE PATTERN OBSERVATION ===")
    obs_fresh = env.observation_space
    grid_fresh = get_2d_grid(obs_fresh)

    print("Colors at the 8 responsive button coordinates in initial frame:")
    for idx, (bx, by) in enumerate(RESPONSIVE_BUTTONS):
        print(f"  Button {idx} ({bx:2d}, {by:2d}): color={int(grid_fresh[by, bx]):2d}")

    print("\nGrid scan (steps of 8px from 4 to 60 in (cx, cy)):")
    # Header
    xs = list(range(4, 61, 8))
    ys = list(range(4, 61, 8))
    header = " cy\\cx | " + " ".join([f"{x:3d}" for x in xs])
    print(header)
    print("-" * len(header))
    for y in ys:
        row_str = f" {y:3d}   | "
        vals = []
        for x in xs:
            vals.append(f"{int(grid_fresh[y, x]):3d}")
        print(row_str + " ".join(vals))

    # ── STEP C: SUBSET SEARCH ──
    print("\n=== STEP C: SUBSET SEARCH ===")
    win_found = False
    winning_subset = None
    winning_subset_size = None
    steps_to_win = None

    # Subset sizes 1, 2, 3, 4
    for k in [1, 2, 3, 4]:
        print(f"\n--- Testing Subsets of Size {k} ({len(list(combinations(RESPONSIVE_BUTTONS, k)))} combinations) ---")
        for combo in combinations(RESPONSIVE_BUTTONS, k):
            # 1. RESET
            env.step(GameAction.RESET, data={})
            total_steps += 1

            # 2. Click subset buttons in sorted order
            sorted_combo = sorted(combo, key=lambda p: (p[1], p[0]))
            for (bx, by) in sorted_combo:
                obs = env.step(GameAction.ACTION6, data={"x": int(bx), "y": int(by)})
                total_steps += 1

            # 3. Check WIN
            is_win = (getattr(obs, "state", None) == GameState.WIN) or (getattr(obs, "levels_completed", 0) > 0)
            print(f"  subset_coords={sorted_combo}, win={is_win}")

            if is_win:
                win_found = True
                winning_subset = sorted_combo
                winning_subset_size = k
                steps_to_win = total_steps
                print(f"\nWIN DETECTED! Winning subset: {winning_subset}")
                break

        if win_found:
            break

    if not win_found:
        print(f"\nNO_WIN_IN_K4 (total steps used: {total_steps})")

    arc.close_scorecard(sc_id)

    # ── STEP D: RAW NUMBERS ──
    print("\n=== STEP D: RAW NUMBERS ===")
    print(f"winning_subset: {winning_subset}")
    print(f"winning_subset_size: {winning_subset_size}")
    print(f"steps_to_win: {steps_to_win}")
    print(f"color_before_click: {color_before}")
    print(f"color_after_click: {color_after}")


if __name__ == "__main__":
    main()
