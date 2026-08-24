import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
from tools.diagnose_ft09 import get_2d_grid, get_background_color, get_components, compute_gf2_rank
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

for seed in range(5):
    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard()
    env = arc.make("ft09", seed=seed, scorecard_id=sc_id)
    grid = get_2d_grid(env.observation_space)
    bg = get_background_color(grid)

    comps = [c for c in get_components(grid, bg) if abs(c['w'] - c['h']) <= 1 and 4 <= c['area'] <= 200 and c['color'] != bg]
    comps.sort(key=lambda b: (b['cy'], b['cx']))

    n_buttons = len(comps)
    areas = [c['area'] for c in comps]
    side_lengths = [max(c['w'], c['h']) for c in comps]
    grid_cell_size_estimate = float(np.mean(side_lengths)) if side_lengths else 0.0

    print(f"\n=======================================================")
    print(f"SEED {seed} RAW DATA")
    print(f"=======================================================")
    print(f"STEP 1: BUTTON DISCOVERY")
    print(f"Number of buttons found: {n_buttons}")
    print(f"Grid cell size estimate: {grid_cell_size_estimate:.2f}px")
    print("Coordinates & Areas:")
    for idx, c in enumerate(comps):
        print(f"  [{idx:2d}] (cx={c['cx']:2d}, cy={c['cy']:2d}) area={c['area']:3d} w={c['w']:2d} h={c['h']:2d} color={c['color']:2d}")

    # STEP 2: Matrix Observation
    A = np.zeros((n_buttons, n_buttons), dtype=int)
    pixels_changed_list = []
    changed_map = {}
    steps = 0

    for i, btn in enumerate(comps):
        f_base = get_2d_grid(env.observation_space)
        obs_after = env.step(GameAction.ACTION6, data={"x": int(btn['cx']), "y": int(btn['cy'])})
        steps += 1
        f_after = get_2d_grid(obs_after)
        delta = (f_after != f_base)
        px_ch = int(np.sum(delta))
        pixels_changed_list.append(px_ch)

        changed_btns = []
        for j, ob in enumerate(comps):
            ox, oy = ob['cx'], ob['cy']
            r_min, r_max = max(0, oy - 4), min(64, oy + 5)
            c_min, c_max = max(0, ox - 4), min(64, ox + 5)
            if np.any(delta[r_min:r_max, c_min:c_max]):
                changed_btns.append(j)
                A[j, i] = 1
        changed_map[i] = (px_ch, changed_btns)
        env.step(GameAction.RESET, data={})
        steps += 1

    print(f"\nSTEP 2: MATRIX OBSERVATION")
    for i in range(n_buttons):
        px_ch, c_btns = changed_map[i]
        if px_ch > 0:
            print(f"  Button {i:2d} (cx={comps[i]['cx']:2d}, cy={comps[i]['cy']:2d}) -> px_changed={px_ch:4d}, changed_buttons={c_btns}")

    rank_real = int(np.linalg.matrix_rank(A))
    rank_gf2 = compute_gf2_rank(A)

    # STEP 3: Win State Observation
    env.step(GameAction.RESET, data={})
    steps += 1
    win_achieved = False
    win_seq = []
    seq_attempt = []
    for step_idx in range(150):
        b_idx = step_idx % n_buttons
        btn = comps[b_idx]
        seq_attempt.append(b_idx)
        obs_seq = env.step(GameAction.ACTION6, data={"x": int(btn['cx']), "y": int(btn['cy'])})
        steps += 1
        if obs_seq is None:
            break
        if (getattr(obs_seq, "state", None) == GameState.WIN) or (getattr(obs_seq, "levels_completed", 0) > 0):
            win_achieved = True
            win_seq = list(seq_attempt)
            break

    print(f"\nSTEP 3: WIN STATE OBSERVATION")
    print(f"Win Achieved: {win_achieved}")
    print(f"Win Sequence: {win_seq if win_achieved else 'WIN_NOT_FOUND'}")

    print(f"\nSTEP 4: RAW NUMBERS")
    print(f"seed_id: {seed}")
    print(f"n_buttons: {n_buttons}")
    print(f"matrix_rank_real: {rank_real}")
    print(f"matrix_rank_gf2: {rank_gf2}")
    print(f"matrix_A: {A.tolist()}")
    print(f"win_achieved: {win_achieved}")
    print(f"win_sequence: {win_seq if win_achieved else None}")
    print(f"steps_used: {steps}")

    arc.close_scorecard(sc_id)
