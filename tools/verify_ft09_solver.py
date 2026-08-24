import sys
from pathlib import Path
from itertools import combinations
import traceback

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


def get_background_color(f: np.ndarray) -> int:
    border = (list(f[0, :]) + list(f[1, :]) + list(f[-1, :]) + list(f[-2, :]) +
              list(f[:, 0]) + list(f[:, 1]) + list(f[:, -1]) + list(f[:, -2]))
    return int(max(set(border), key=border.count)) if border else 0


def get_components(f: np.ndarray, bg: int) -> list:
    vis = np.zeros_like(f, bool)
    comps = []
    for r in range(64):
        for c in range(64):
            if not vis[r, c] and f[r, c] != bg:
                q = [(r, c)]
                vis[r, c] = True
                pix = []
                while q:
                    cr, cc = q.pop()
                    pix.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < 64 and 0 <= nc < 64 and not vis[nr, nc] and f[nr, nc] == f[cr, cc]:
                            vis[nr, nc] = True
                            q.append((nr, nc))
                min_r = min(p[0] for p in pix)
                max_r = max(p[0] for p in pix)
                min_c = min(p[1] for p in pix)
                max_c = max(p[1] for p in pix)
                cy = (min_r + max_r) // 2
                cx = (min_c + max_c) // 2
                w = max_c - min_c + 1
                h = max_r - min_r + 1
                area = len(pix)
                comps.append({
                    'cx': cx, 'cy': cy,
                    'min_r': min_r, 'max_r': max_r,
                    'min_c': min_c, 'max_c': max_c,
                    'w': w, 'h': h,
                    'area': area,
                    'color': int(f[pix[0][0], pix[0][1]])
                })
    return comps


def solve_ft09(env, max_steps: int = 2000) -> dict:
    """
    Isolated ft09 solver: Button Discovery, Response Verification, State Reading, and K-Subset Enumeration.
    """
    total_steps = 0
    obs_start = env.step(GameAction.RESET, data={})
    total_steps += 1

    grid = get_2d_grid(obs_start)
    bg = get_background_color(grid)
    initial_levels_completed = getattr(obs_start, "levels_completed", 0)

    # ── Step 1: BUTTON DISCOVERY ──
    all_comps = get_components(grid, bg)
    candidates = [
        c for c in all_comps
        if 25 <= c['area'] <= 49 and abs(c['w'] - c['h']) <= 1 and c['color'] != bg
    ]

    if not candidates:
        return {
            "win": False, "winning_subset": None, "k": None,
            "total_steps": total_steps, "n_responsive": 0,
            "color_off": None, "color_on": None
        }

    # Sort candidate buttons in raster order
    candidates.sort(key=lambda b: (b['cy'], b['cx']))

    # ── Step 2: RESPONSE VERIFICATION ──
    responsive_buttons = []
    color_off = None
    color_on = None

    for btn in candidates:
        bx, by = btn['cx'], btn['cy']
        obs_before = env.step(GameAction.RESET, data={})
        total_steps += 1
        f_before = get_2d_grid(obs_before)
        c_before = int(f_before[by, bx])

        obs_after = env.step(GameAction.ACTION6, data={"x": int(bx), "y": int(by)})
        total_steps += 1
        f_after = get_2d_grid(obs_after)
        c_after = int(f_after[by, bx])

        delta = int(np.sum(f_after != f_before))
        if delta > 0:
            responsive_buttons.append((bx, by))
            if color_off is None:
                color_off = c_before
            if color_on is None and c_after != c_before:
                color_on = c_after

    responsive_buttons.sort(key=lambda p: (p[1], p[0]))
    n_responsive = len(responsive_buttons)

    # ── Step 3: READ CURRENT STATE ──
    obs_clean = env.step(GameAction.RESET, data={})
    total_steps += 1
    f_current = get_2d_grid(obs_clean)

    state_vector = []
    for (bx, by) in responsive_buttons:
        col = int(f_current[by, bx])
        state_vector.append(1 if (color_on is not None and col == color_on) else 0)

    # ── Step 4: K-SUBSET ENUMERATION ──
    winning_subset = None
    winning_k = None
    win = False

    for k in range(0, n_responsive + 1):
        for combo in combinations(responsive_buttons, k):
            if total_steps >= max_steps:
                break

            env.step(GameAction.RESET, data={})
            total_steps += 1

            sorted_combo = sorted(combo, key=lambda p: (p[1], p[0]))
            last_obs = None
            for (bx, by) in sorted_combo:
                last_obs = env.step(GameAction.ACTION6, data={"x": int(bx), "y": int(by)})
                total_steps += 1

            is_win = False
            if last_obs is not None:
                st = getattr(last_obs, "state", None)
                lvl_done = getattr(last_obs, "levels_completed", 0)
                if st == GameState.WIN or lvl_done > initial_levels_completed:
                    is_win = True

            if is_win:
                win = True
                winning_subset = sorted_combo
                winning_k = k
                return {
                    "win": True,
                    "winning_subset": winning_subset,
                    "k": winning_k,
                    "total_steps": total_steps,
                    "n_responsive": n_responsive,
                    "color_off": color_off,
                    "color_on": color_on
                }

    return {
        "win": False,
        "winning_subset": None,
        "k": None,
        "total_steps": total_steps,
        "n_responsive": n_responsive,
        "color_off": color_off,
        "color_on": color_on
    }


def main():
    SEEDS = [0, 1, 2, 3, 4]
    LEVELS = [0, 1, 2, 3, 4, 5]

    results_by_level_seed = {lvl: {} for lvl in LEVELS}

    print("================================================================================")
    print("PART 2: VERIFICATION RUN (ft09, Levels 0-5, Seeds 0-4)")
    print("================================================================================\n")

    for seed in SEEDS:
        arc = Arcade(operation_mode=OperationMode.OFFLINE)
        sc_id = arc.create_scorecard(tags=[f"ft09_full_verif_seed_{seed}"])
        env = arc.make("ft09", seed=seed, scorecard_id=sc_id)

        for lvl in LEVELS:
            try:
                res = solve_ft09(env)
                results_by_level_seed[lvl][seed] = res
                print(f"level={lvl}, seed={seed}, win={res['win']}, winning_subset={res['winning_subset']}, k={res['k']}, total_steps={res['total_steps']}, n_responsive={res['n_responsive']}, color_off={res['color_off']}, color_on={res['color_on']}")
            except Exception as e:
                print(f"EXCEPTION at level={lvl}, seed={seed}: {e}")
                traceback.print_exc()
                results_by_level_seed[lvl][seed] = {
                    "win": False, "winning_subset": None, "k": None,
                    "total_steps": -1, "n_responsive": 0,
                    "color_off": None, "color_on": None
                }

        arc.close_scorecard(sc_id)

    # ── Cross-Seed Table ──
    print("\n================================================================================")
    print("CROSS-SEED SUBSET TABLE")
    print("================================================================================")
    print(f"{'level':<5} | {'seed0_subset':<42} | {'seed1_subset':<42} | {'seed2_subset':<42} | {'seed3_subset':<42} | {'seed4_subset':<42} | {'subsets_identical':<17}")
    print("-" * 240)

    for lvl in LEVELS:
        subsets = [results_by_level_seed[lvl][s]["winning_subset"] for s in SEEDS]
        subsets_identical = all(sub == subsets[0] for sub in subsets)
        sub_strs = [str(sub) if sub is not None else "None" for sub in subsets]
        print(f"{lvl:<5} | {sub_strs[0]:<42} | {sub_strs[1]:<42} | {sub_strs[2]:<42} | {sub_strs[3]:<42} | {sub_strs[4]:<42} | {str(subsets_identical):<17}")

    # ── Cross-Level Summary ──
    print("\n================================================================================")
    print("CROSS-LEVEL SUMMARY (Seed 0)")
    print("================================================================================")
    print(f"{'level':<5} | {'k_value':<8} | {'steps_used':<10}")
    print("-" * 30)
    for lvl in LEVELS:
        r0 = results_by_level_seed[lvl][0]
        k_val = str(r0["k"]) if r0["k"] is not None else "None"
        steps_val = str(r0["total_steps"])
        print(f"{lvl:<5} | {k_val:<8} | {steps_val:<10}")


if __name__ == "__main__":
    main()
