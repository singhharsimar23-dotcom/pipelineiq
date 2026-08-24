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
                comps.append({
                    'cx': cx, 'cy': cy,
                    'min_r': min_r, 'max_r': max_r,
                    'min_c': min_c, 'max_c': max_c,
                    'w': max_c - min_c + 1, 'h': max_r - min_r + 1,
                    'area': len(pix),
                    'color': int(f[pix[0][0], pix[0][1]])
                })
    return comps


def main():
    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard(tags=["diagnose_cn04_seed0"])
    env = arc.make("cn04", seed=0, scorecard_id=sc_id)

    obs = env.step(GameAction.RESET, data={})
    grid = get_2d_grid(obs)
    bg = get_background_color(grid)

    print("=== CN04 ENVIRONMENT DIAGNOSTIC (Seed 0, Level 0) ===")
    print(f"Background Color: {bg}")
    print(f"Available Actions: {getattr(obs, 'available_actions', None)}")
    print(f"Action Space: {getattr(env, 'action_space', None)}")
    print(f"Level Count: {getattr(env, 'level_count', None)}")

    comps = get_components(grid, bg)
    print(f"\nTotal Non-Background Components: {len(comps)}")
    comps.sort(key=lambda c: (c['cy'], c['cx']))
    for idx, c in enumerate(comps):
        print(f"  [{idx:2d}] (cx={c['cx']:2d}, cy={c['cy']:2d}) area={c['area']:4d}, w={c['w']:2d}, h={c['h']:2d}, color={c['color']:2d}, bounds=[{c['min_r']}:{c['max_r']}, {c['min_c']}:{c['max_c']}]")

    print("\n--- GRID SPATIAL OVERVIEW (ASCII / Coarse Map) ---")
    for r in range(0, 64, 4):
        row_str = f"r={r:2d} | "
        for c in range(0, 64, 4):
            val = int(grid[r, c])
            char = "." if val == bg else f"{val:X}"
            row_str += char + " "
        print(row_str)

    print("\n--- SYSTEMATIC CLICK RESPONSE PROBE ON ALL COMPONENTS ---")
    responsive = []
    for idx, c in enumerate(comps):
        f_before = get_2d_grid(env.step(GameAction.RESET, data={}))
        obs_after = env.step(GameAction.ACTION6, data={"x": int(c['cx']), "y": int(c['cy'])})
        f_after = get_2d_grid(obs_after)
        delta = (f_after != f_before)
        px_changed = int(np.sum(delta))
        if px_changed > 0:
            # Analyze where pixels changed
            changed_rows, changed_cols = np.where(delta)
            r_span = (int(np.min(changed_rows)), int(np.max(changed_rows)))
            c_span = (int(np.min(changed_cols)), int(np.max(changed_cols)))
            colors_before = np.unique(f_before[delta])
            colors_after = np.unique(f_after[delta])
            responsive.append({
                "idx": idx, "cx": c['cx'], "cy": c['cy'],
                "area": c['area'], "color": c['color'],
                "px_changed": px_changed,
                "r_span": r_span, "c_span": c_span,
                "col_before": colors_before.tolist(),
                "col_after": colors_after.tolist(),
                "delta_mask": delta
            })
            print(f"  Component [{idx:2d}] at (cx={c['cx']:2d}, cy={c['cy']:2d}) -> px_changed={px_changed:4d} | r_span={r_span}, c_span={c_span} | colors: {colors_before.tolist()} -> {colors_after.tolist()}")

    print(f"\nTotal Responsive Components: {len(responsive)}")

    arc.close_scorecard(sc_id)


if __name__ == "__main__":
    main()
