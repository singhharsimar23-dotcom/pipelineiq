import sys
from pathlib import Path
import random
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
                    'pixels': pix,
                    'color': int(f[pix[0][0], pix[0][1]])
                })
    return comps


def run_ls20_diagnostic():
    print("=" * 70)
    print("DIAGNOSTIC INSTRUMENTATION: ls20 (Level 0, Seed 0)")
    print("=" * 70)

    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard(tags=["diag_ls20_seed0"])
    env = arc.make("ls20", seed=0, scorecard_id=sc_id)

    total_steps = 0
    obs_start = env.step(GameAction.RESET, data={})
    total_steps += 1
    f_start = get_2d_grid(obs_start)
    bg = get_background_color(f_start)
    comps = get_components(f_start, bg)

    # ── STEP 1: AVATAR DETECTION ──
    print("\n--- STEP 1: AVATAR DETECTION ---")
    print(f"Background color: {bg}")
    print(f"Found {len(comps)} non-background components.")

    # Test actions 1, 2, 3, 4 to locate avatar component
    avatar_color = 12
    ys0, xs0 = np.where(f_start == avatar_color)
    avatar_cx = int(round(np.mean(xs0)))
    avatar_cy = int(round(np.mean(ys0)))
    avatar_area = len(ys0)

    shifts = []
    for act_id, act_name in [
        (GameAction.ACTION1, "ACTION1 (UP)"),
        (GameAction.ACTION2, "ACTION2 (DOWN)"),
        (GameAction.ACTION3, "ACTION3 (LEFT)"),
        (GameAction.ACTION4, "ACTION4 (RIGHT)")
    ]:
        obs_before = env.step(GameAction.RESET, data={})
        total_steps += 1
        f_before = get_2d_grid(obs_before)

        obs_after = env.step(act_id, data={})
        total_steps += 1
        f_after = get_2d_grid(obs_after)

        delta = (f_after != f_before)
        px_changed = int(np.sum(delta))

        ys1, xs1 = np.where(f_after == avatar_color)
        if len(ys1) > 0 and len(ys0) > 0:
            dcx = int(round(np.mean(xs1) - np.mean(xs0)))
            dcy = int(round(np.mean(ys1) - np.mean(ys0)))
            if max(abs(dcx), abs(dcy)) > 0:
                shifts.append(max(abs(dcx), abs(dcy)))
            print(f"  {act_name:<16}: delta_pixels={px_changed:4d}, centroid_shift=(dcx={dcx:2d}, dcy={dcy:2d})")

    pixels_per_step = max(shifts) if shifts else 5

    print(f"\nAvatar Properties:")
    print(f"  avatar_color: {avatar_color}")
    print(f"  avatar_start: ({avatar_cx}, {avatar_cy})")
    print(f"  avatar_area: {avatar_area}")
    print(f"  pixels_per_step: {pixels_per_step}")

    # ── STEP 2: GOAL DETECTION ──
    print("\n--- STEP 2: GOAL DETECTION ---")
    other_comps = [
        c for c in comps
        if not (abs(c['cx'] - avatar_cx) <= 2 and abs(c['cy'] - avatar_cy) <= 2 and c['color'] == avatar_color)
    ]
    print(f"Found {len(other_comps)} non-avatar components:")
    for idx, c in enumerate(other_comps):
        print(f"  [{idx:2d}] (cx={c['cx']:2d}, cy={c['cy']:2d}), area={c['area']:3d}, color={c['color']:2d}, dims=({c['w']}x{c['h']})")

    goal_positions = [(c['cx'], c['cy']) for c in other_comps]
    goal_color = other_comps[0]['color'] if other_comps else None

    # Move avatar toward nearest non-bg component
    nearest_goal = min(other_comps, key=lambda c: (c['cx'] - avatar_cx)**2 + (c['cy'] - avatar_cy)**2)
    print(f"\nAttempting to move avatar toward nearest component at ({nearest_goal['cx']}, {nearest_goal['cy']})...")

    obs_mv = env.step(GameAction.RESET, data={})
    total_steps += 1
    cur_x, cur_y = avatar_cx, avatar_cy
    component_changed = False
    win_fired_goal = False

    for _ in range(20):
        dx = nearest_goal['cx'] - cur_x
        dy = nearest_goal['cy'] - cur_y
        if abs(dx) == 0 and abs(dy) == 0:
            break
        act = None
        if abs(dy) > 0:
            act = GameAction.ACTION1 if dy < 0 else GameAction.ACTION2
        else:
            act = GameAction.ACTION3 if dx < 0 else GameAction.ACTION4

        f_pre_step = get_2d_grid(obs_mv)
        obs_mv = env.step(act, data={})
        total_steps += 1
        f_post_step = get_2d_grid(obs_mv)

        av_pix = np.where(f_post_step == avatar_color)
        if len(av_pix[0]) > 0:
            cur_y = int(round(np.mean(av_pix[0])))
            cur_x = int(round(np.mean(av_pix[1])))

        g_box_pre = f_pre_step[nearest_goal['min_r']:nearest_goal['max_r']+1, nearest_goal['min_c']:nearest_goal['max_c']+1]
        g_box_post = f_post_step[nearest_goal['min_r']:nearest_goal['max_r']+1, nearest_goal['min_c']:nearest_goal['max_c']+1]
        if np.any(g_box_pre != g_box_post):
            component_changed = True

        if getattr(obs_mv, 'state', None) == GameState.WIN or getattr(obs_mv, 'levels_completed', 0) > 0:
            win_fired_goal = True
            break

    print(f"Did nearest component change? {component_changed}")
    print(f"Did WIN fire? {win_fired_goal}")
    print(f"goal_color: {goal_color}")
    print(f"goal_cx: {nearest_goal['cx']}, goal_cy: {nearest_goal['cy']}")

    # ── STEP 3: OBSTACLE DETECTION ──
    print("\n--- STEP 3: OBSTACLE DETECTION ---")
    obs_obs = env.step(GameAction.RESET, data={})
    total_steps += 1

    steps_before_block = 0
    blocked = False
    obstacle_color = None

    for step_i in range(1, 20):
        f_b = get_2d_grid(obs_obs)
        obs_obs = env.step(GameAction.ACTION1, data={})
        total_steps += 1
        f_a = get_2d_grid(obs_obs)
        delta_px = int(np.sum(f_a != f_b))
        if delta_px == 0:
            blocked = True
            steps_before_block = step_i - 1
            av_p = np.where(f_b == avatar_color)
            if len(av_p[0]) > 0:
                top_r = int(np.min(av_p[0]))
                c_m = int(np.mean(av_p[1]))
                if top_r > 0:
                    obstacle_color = int(f_b[top_r - 1, c_m])
            break

    print(f"Total steps before blocking: {steps_before_block}")
    print(f"Is movement blocked by walls/cells? {blocked}")
    print(f"Obstacle color: {obstacle_color}")

    # ── STEP 4: WIN CONDITION (50 Random Actions) ──
    print("\n--- STEP 4: WIN CONDITION (50 Random Actions) ---")
    obs_rand = env.step(GameAction.RESET, data={})
    total_steps += 1
    lvl_before = getattr(obs_rand, "levels_completed", 0)

    win_step = None
    last_act_name = None
    win_fired_rand = False

    random.seed(42)
    for step_idx in range(1, 51):
        act_choice = random.choice([
            (GameAction.ACTION1, "ACTION1"),
            (GameAction.ACTION2, "ACTION2"),
            (GameAction.ACTION3, "ACTION3"),
            (GameAction.ACTION4, "ACTION4"),
        ])
        obs_rand = env.step(act_choice[0], data={})
        total_steps += 1

        if getattr(obs_rand, "state", None) == GameState.WIN or getattr(obs_rand, "levels_completed", 0) > lvl_before:
            win_fired_rand = True
            win_step = step_idx
            last_act_name = act_choice[1]
            break

    lvl_after = getattr(obs_rand, "levels_completed", 0)
    print(f"Did WIN fire in 50 random actions? {win_fired_rand}")
    print(f"Win step: {win_step}, Last action: {last_act_name}")
    print(f"levels_completed before: {lvl_before}, after: {lvl_after}")

    arc.close_scorecard(sc_id)

    # ── STEP 5: RAW NUMBERS ──
    print("\n--- STEP 5: RAW NUMBERS ---")
    print(f"avatar_color: {avatar_color}")
    print(f"avatar_start: ({avatar_cx}, {avatar_cy})")
    print(f"goal_color: {goal_color}")
    print(f"goal_positions: {goal_positions}")
    print(f"obstacle_color: {obstacle_color}")
    print(f"grid_is_continuous: {pixels_per_step == 1}")
    print(f"pixels_per_step: {pixels_per_step}")
    print(f"win_achieved: {win_fired_goal or win_fired_rand}")
    print(f"steps_used: {total_steps}")

    return {
        "avatar_color": avatar_color,
        "avatar_cx": avatar_cx,
        "avatar_cy": avatar_cy,
        "pixels_per_step": pixels_per_step
    }


def run_sp80_avatar_check():
    print("\n" + "=" * 70)
    print("STEP 1 ONLY ON sp80 (Level 0, Seed 0)")
    print("=" * 70)

    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard(tags=["diag_sp80_seed0"])
    env = arc.make("sp80", seed=0, scorecard_id=sc_id)

    obs_start = env.step(GameAction.RESET, data={})
    f_start = get_2d_grid(obs_start)
    bg = get_background_color(f_start)

    # Identify avatar color from directional action displacement
    # Test ACTION1, 2, 3, 4
    all_shifts = []
    av_col = None
    av_cx, av_cy = None, None

    for act_id, act_name in [
        (GameAction.ACTION1, "ACTION1 (UP)"),
        (GameAction.ACTION2, "ACTION2 (DOWN)"),
        (GameAction.ACTION3, "ACTION3 (LEFT)"),
        (GameAction.ACTION4, "ACTION4 (RIGHT)")
    ]:
        obs_before = env.step(GameAction.RESET, data={})
        f_before = get_2d_grid(obs_before)

        obs_after = env.step(act_id, data={})
        f_after = get_2d_grid(obs_after)

        delta = (f_after != f_before)
        px_changed = int(np.sum(delta))

        # Check which color appeared in f_after on new pixels
        colors_after = np.unique(f_after[delta & (f_after != bg)])
        colors_before = np.unique(f_before[delta & (f_before != bg)])
        
        common_moving = set(colors_after).intersection(set(colors_before))
        dcx, dcy = 0, 0
        if common_moving:
            av_col = list(common_moving)[0]
            ys0, xs0 = np.where(f_before == av_col)
            ys1, xs1 = np.where(f_after == av_col)
            if len(ys0) > 0 and len(ys1) > 0:
                dcx = int(round(np.mean(xs1) - np.mean(xs0)))
                dcy = int(round(np.mean(ys1) - np.mean(ys0)))
                if max(abs(dcx), abs(dcy)) > 0:
                    all_shifts.append(max(abs(dcx), abs(dcy)))
                av_cx = int(round(np.mean(xs0)))
                av_cy = int(round(np.mean(ys0)))

        print(f"  {act_name:<16}: delta_pixels={px_changed:4d}, centroid_shift=(dcx={dcx:2d}, dcy={dcy:2d})")

    arc.close_scorecard(sc_id)

    step_sz = max(all_shifts) if all_shifts else 1
    print(f"\nsp80 Avatar Properties:")
    print(f"  avatar_color: {av_col}")
    print(f"  avatar_start: ({av_cx}, {av_cy})")
    print(f"  pixels_per_step: {step_sz}")

    return {
        "avatar_color": av_col,
        "avatar_cx": av_cx,
        "avatar_cy": av_cy,
        "pixels_per_step": step_sz
    }


def main():
    try:
        ls20_res = run_ls20_diagnostic()
        sp80_res = run_sp80_avatar_check()

        print("\n" + "=" * 70)
        print("COMPARISON: ls20 vs sp80")
        print("=" * 70)
        same_color = (ls20_res["avatar_color"] == sp80_res["avatar_color"])
        same_step = (ls20_res["pixels_per_step"] == sp80_res["pixels_per_step"])
        print(f"avatar_color: ls20={ls20_res['avatar_color']}, sp80={sp80_res['avatar_color']} -> {'SAME' if same_color else 'DIFFERENT'}")
        print(f"pixels_per_step: ls20={ls20_res['pixels_per_step']}, sp80={sp80_res['pixels_per_step']} -> {'SAME' if same_step else 'DIFFERENT'}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
