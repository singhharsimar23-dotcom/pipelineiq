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
                comps.append({
                    'cx': cx, 'cy': cy,
                    'min_r': min_r, 'max_r': max_r,
                    'min_c': min_c, 'max_c': max_c,
                    'w': max_c - min_c + 1, 'h': max_r - min_r + 1,
                    'area': len(pix),
                    'color': int(f[pix[0][0], pix[0][1]])
                })
    return comps


def run_game_instrumentation(game_id: str, seed: int = 0):
    print(f"\n{'='*70}")
    print(f"GAME: {game_id} | SEED: {seed} | LEVEL: 0")
    print(f"{'='*70}")

    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard(tags=[f"diag_{game_id}_seed_{seed}"])
    env = arc.make(game_id, seed=seed, scorecard_id=sc_id)

    total_steps = 0
    obs_start = env.step(GameAction.RESET, data={})
    total_steps += 1
    f_start = get_2d_grid(obs_start)
    bg = get_background_color(f_start)
    initial_levels_completed = getattr(obs_start, "levels_completed", 0)

    # ── STEP 1: BUTTON DISCOVERY (Standard Filter: 25 <= area <= 49) ──
    print("--- STEP 1: BUTTON DISCOVERY (25 <= area <= 49, abs(w-h) <= 1) ---")
    all_comps = get_components(f_start, bg)
    filter_used = "25<=area<=49"
    candidates = [
        c for c in all_comps
        if 25 <= c['area'] <= 49 and abs(c['w'] - c['h']) <= 1 and c['color'] != bg
    ]

    print(f"Candidates found ({filter_used}): count={len(candidates)}")
    for idx, c in enumerate(candidates):
        print(f"  [{idx:2d}] (cx={c['cx']:2d}, cy={c['cy']:2d}), area={c['area']:3d}, w={c['w']:2d}, h={c['h']:2d}, color={c['color']:2d}")

    # ── STEP 4 CHECK: Retry with 4 <= area <= 200 if 0 candidates found ──
    if len(candidates) == 0:
        print("\n--- STEP 4: RETRYING WITH WIDE FILTER (4 <= area <= 200, abs(w-h) <= 1) ---")
        filter_used = "4<=area<=200"
        candidates = [
            c for c in all_comps
            if 4 <= c['area'] <= 200 and abs(c['w'] - c['h']) <= 1 and c['color'] != bg
        ]
        print(f"Candidates found ({filter_used}): count={len(candidates)}")
        for idx, c in enumerate(candidates):
            print(f"  [{idx:2d}] (cx={c['cx']:2d}, cy={c['cy']:2d}), area={c['area']:3d}, w={c['w']:2d}, h={c['h']:2d}, color={c['color']:2d}")
    else:
        print(f"Filter succeeded: {filter_used}")

    candidates.sort(key=lambda b: (b['cy'], b['cx']))
    n_candidates = len(candidates)

    # ── STEP 2: RESPONSE VERIFICATION ──
    print("\n--- STEP 2: RESPONSE VERIFICATION ---")
    responsive_buttons = []
    color_off = None
    color_on = None
    delta_records = []

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

        delta = (f_after != f_before)
        px_changed = int(np.sum(delta))

        if px_changed > 0:
            responsive_buttons.append((bx, by))
            delta_records.append((bx, by, delta))
            if color_off is None:
                color_off = c_before
            if color_on is None and c_after != c_before:
                color_on = c_after
            print(f"  Candidate ({bx:2d}, {by:2d}) -> px_changed={px_changed:4d} (RESPONSIVE)")
        else:
            print(f"  Candidate ({bx:2d}, {by:2d}) -> px_changed=   0 (non-responsive)")

    responsive_buttons.sort(key=lambda p: (p[1], p[0]))
    n_responsive = len(responsive_buttons)
    print(f"Total responsive buttons: {n_responsive}")
    print(f"Responsive coordinates: {responsive_buttons}")

    # ── STEP 5: MATRIX A CONSTRUCTION & IDENTITY CHECK ──
    print("\n--- STEP 5: MATRIX A (n_responsive x n_responsive) ---")
    A = np.zeros((n_responsive, n_responsive), dtype=int)

    for i, (bx, by) in enumerate(responsive_buttons):
        # find matching delta
        match_delta = None
        for rbx, rby, d in delta_records:
            if rbx == bx and rby == by:
                match_delta = d
                break
        if match_delta is not None:
            for j, (ox, oy) in enumerate(responsive_buttons):
                r_min, r_max = max(0, oy - 4), min(64, oy + 5)
                c_min, c_max = max(0, ox - 4), min(64, ox + 5)
                if np.any(match_delta[r_min:r_max, c_min:c_max]):
                    A[j, i] = 1

    print("Influence Matrix A:")
    print(A)
    is_identity = bool(np.array_equal(A, np.eye(n_responsive, dtype=int))) if n_responsive > 0 else False
    print(f"matrix_is_identity: {is_identity}")

    # ── STEP 3: K-SUBSET SEARCH ──
    print("\n--- STEP 3: K-SUBSET SEARCH ---")
    win = False
    winning_subset = None
    winning_k = None

    if n_responsive > 0:
        for k in range(0, n_responsive + 1):
            for combo in combinations(responsive_buttons, k):
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
                    break
            if win:
                break

    print(f"win: {win}")
    print(f"winning_subset: {winning_subset}")
    print(f"k: {winning_k}")
    print(f"total_steps: {total_steps}")

    arc.close_scorecard(sc_id)

    # ── Summary Dictionary ──
    return {
        "game_id": game_id,
        "n_candidates": n_candidates,
        "n_responsive": n_responsive,
        "matrix_is_identity": is_identity,
        "win": win,
        "k": winning_k,
        "total_steps": total_steps,
        "color_off": color_off,
        "color_on": color_on,
        "filter_used": filter_used,
        "responsive_coords": responsive_buttons,
        "matrix_A": A.tolist(),
    }


def main():
    GAMES = ["cn04", "dc22", "g50t"]
    results = []

    for gid in GAMES:
        try:
            res = run_game_instrumentation(gid, seed=0)
            results.append(res)
        except Exception as e:
            print(f"EXCEPTION on game {gid}: {e}")
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("CONSOLIDATED SUMMARY TABLE")
    print("=" * 80)
    print(f"{'game_id':<8} | {'n_cand':<8} | {'n_resp':<8} | {'matrix_is_identity':<20} | {'win':<7} | {'k':<6} | {'steps':<8} | {'color_off':<10} | {'color_on':<10}")
    print("-" * 105)
    for r in results:
        print(f"{r['game_id']:<8} | {r['n_candidates']:<8} | {r['n_responsive']:<8} | {str(r['matrix_is_identity']):<20} | {str(r['win']):<7} | {str(r['k']):<6} | {r['total_steps']:<8} | {str(r['color_off']):<10} | {str(r['color_on']):<10}")


if __name__ == "__main__":
    main()
