#!/usr/bin/env python3
"""
Diagnostic instrumentation agent for ft09 across 5 seeds.
Observer only. Raw data collection.
"""
import os
import sys
from pathlib import Path

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


def compute_gf2_rank(mat: np.ndarray) -> int:
    m = mat.copy().astype(int) % 2
    rows, cols = m.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if m[row, col] == 1:
                pivot = row
                break
        if pivot is not None:
            m[[rank, pivot]] = m[[pivot, rank]]
            for row in range(rows):
                if row != rank and m[row, col] == 1:
                    m[row] = (m[row] + m[rank]) % 2
            rank += 1
    return rank


def run_seed_diagnostic(seed: int):
    print(f"\n{'='*70}")
    print(f"DIAGNOSTIC RUN: ft09 | SEED: {seed} | LEVEL: 0")
    print(f"{'='*70}")

    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    scorecard_id = arc.create_scorecard(tags=[f"diag_ft09_seed_{seed}"])
    env = arc.make("ft09", seed=seed, scorecard_id=scorecard_id)

    steps_used = 0

    # Initial frame
    obs = env.observation_space
    grid = get_2d_grid(obs)
    bg = get_background_color(grid)

    # ── STEP 1: BUTTON DISCOVERY ──
    print("\n--- STEP 1: BUTTON DISCOVERY ---")
    all_comps = get_components(grid, bg)
    buttons = [
        c for c in all_comps
        if abs(c['w'] - c['h']) <= 1 and 4 <= c['area'] <= 200 and c['color'] != bg
    ]
    # Sort buttons in standard raster order (cy, cx)
    buttons.sort(key=lambda b: (b['cy'], b['cx']))

    n_buttons = len(buttons)
    areas = [b['area'] for b in buttons]
    side_lengths = [max(b['w'], b['h']) for b in buttons]
    grid_cell_size_estimate = float(np.mean(side_lengths)) if side_lengths else 0.0

    print(f"Number of buttons found: {n_buttons}")
    print(f"Grid cell size estimate: {grid_cell_size_estimate:.2f}px")
    print("Discovered Buttons:")
    for idx, b in enumerate(buttons):
        print(f"  Button {idx:2d}: cx={b['cx']:2d}, cy={b['cy']:2d}, area={b['area']:3d}, w={b['w']:2d}, h={b['h']:2d}, color={b['color']:2d}")

    # ── STEP 2: MATRIX OBSERVATION ──
    print("\n--- STEP 2: MATRIX OBSERVATION ---")
    A = np.zeros((n_buttons, n_buttons), dtype=int)

    for i, btn in enumerate(buttons):
        # Record baseline frame
        obs_baseline = env.observation_space
        f_base = get_2d_grid(obs_baseline)

        # Click button i
        act = GameAction.ACTION6
        obs_after = env.step(act, data={"x": int(btn['cx']), "y": int(btn['cy'])})
        steps_used += 1
        f_after = get_2d_grid(obs_after)

        delta = (f_after != f_base)
        pixels_changed = int(np.sum(delta))

        # Check which button positions changed (within 4px of centroid)
        changed_buttons = []
        for j, other_btn in enumerate(buttons):
            ox, oy = other_btn['cx'], other_btn['cy']
            # Neighborhood around other_btn centroid
            r_min, r_max = max(0, oy - 4), min(64, oy + 5)
            c_min, c_max = max(0, ox - 4), min(64, ox + 5)
            if np.any(delta[r_min:r_max, c_min:c_max]):
                changed_buttons.append(j)
                A[j, i] = 1

        print(f"  Button {i:2d} (cx={btn['cx']:2d}, cy={btn['cy']:2d}) clicked -> Pixels changed: {pixels_changed:4d} | Changed buttons: {changed_buttons}")

        # Issue RESET
        obs_reset = env.step(GameAction.RESET, data={})
        steps_used += 1

    print("\nInfluence Matrix A (n x n, A[j][i]=1 if clicking i alters j):")
    print(A)

    rank_real = int(np.linalg.matrix_rank(A))
    rank_gf2 = compute_gf2_rank(A)
    print(f"Matrix Rank (Real): {rank_real}/{n_buttons}")
    print(f"Matrix Rank (GF(2)): {rank_gf2}/{n_buttons}")

    # ── STEP 3: WIN STATE OBSERVATION ──
    print("\n--- STEP 3: WIN STATE OBSERVATION ---")
    win_achieved = False
    win_sequence = []
    pre_win_frame = None

    # Reset environment before sequential testing
    obs_seq = env.step(GameAction.RESET, data={})
    steps_used += 1

    seq_attempt = []
    # Try clicking buttons in order 0, 1, 2, ... n-1 cycling up to 150 steps
    for step_idx in range(150):
        btn_idx = step_idx % n_buttons
        btn = buttons[btn_idx]
        seq_attempt.append(btn_idx)

        f_pre = get_2d_grid(obs_seq)
        obs_seq = env.step(GameAction.ACTION6, data={"x": int(btn['cx']), "y": int(btn['cy'])})
        steps_used += 1

        if obs_seq is None:
            break

        is_win = (getattr(obs_seq, "state", None) == GameState.WIN) or (getattr(obs_seq, "levels_completed", 0) > 0)
        if is_win:
            win_achieved = True
            win_sequence = list(seq_attempt)
            pre_win_frame = f_pre
            print(f"WIN FIRED at step {step_idx + 1}!")
            print(f"Win Sequence (Button Indices): {win_sequence}")
            print(f"Pre-win Frame Non-zero Coordinates Count: {int(np.sum(pre_win_frame != bg))}")
            break

    if not win_achieved:
        print("WIN_NOT_FOUND")

    sc = arc.close_scorecard(scorecard_id)

    # ── STEP 4: PRINT RAW NUMBERS ──
    print("\n--- STEP 4: RAW NUMBERS SUMMARY ---")
    print(f"seed_id: {seed}")
    print(f"n_buttons: {n_buttons}")
    print(f"matrix_rank_real: {rank_real}")
    print(f"matrix_rank_gf2: {rank_gf2}")
    print(f"matrix_A: {A.tolist()}")
    print(f"win_achieved: {win_achieved}")
    print(f"win_sequence: {win_sequence if win_achieved else 'None'}")
    print(f"steps_used: {steps_used}")

    return {
        "seed_id": seed,
        "n_buttons": n_buttons,
        "matrix_rank_real": rank_real,
        "matrix_rank_gf2": rank_gf2,
        "matrix_A": A.tolist(),
        "win_achieved": win_achieved,
        "win_sequence": win_sequence if win_achieved else None,
        "steps_used": steps_used,
        "buttons": [(b['cx'], b['cy'], b['area']) for b in buttons],
    }


def main():
    seeds = [0, 1, 2, 3, 4]
    all_results = []
    for s in seeds:
        res = run_seed_diagnostic(s)
        all_results.append(res)

    print(f"\n{'='*70}")
    print("ALL 5 SEEDS RAW CONSOLIDATED DATA")
    print(f"{'='*70}")
    for r in all_results:
        print(f"Seed {r['seed_id']}: n_buttons={r['n_buttons']}, rank_real={r['matrix_rank_real']}, rank_gf2={r['matrix_rank_gf2']}, win_achieved={r['win_achieved']}, win_seq={r['win_sequence']}, steps={r['steps_used']}")


if __name__ == "__main__":
    main()
