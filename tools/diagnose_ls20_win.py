import sys
from pathlib import Path
from collections import deque
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


def get_avatar_pos(f: np.ndarray, avatar_color: int = 12):
    ys, xs = np.where(f == avatar_color)
    if len(ys) == 0:
        return None
    return int(round(np.mean(xs))), int(round(np.mean(ys)))


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


def main():
    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard(tags=["ls20_win_diag_seed0"])
    env = arc.make("ls20", seed=0, scorecard_id=sc_id)

    total_steps = 0
    bg = 4
    avatar_color = 12
    step_size = 5

    # ── EXPERIMENT 1: Test component [2] (36, 12) ──
    print("================================================================================")
    print("EXPERIMENT 1 — Test component [2] as goal: (cx=36, cy=12), color=5, area=43")
    print("================================================================================\n")

    obs_exp1 = env.step(GameAction.RESET, data={})
    total_steps += 1
    f_exp1 = get_2d_grid(obs_exp1)
    av_pos = get_avatar_pos(f_exp1, avatar_color)
    print(f"Initial Avatar position: {av_pos}")

    target_x, target_y = 36, 12
    closest_dist = float('inf')
    closest_pos = av_pos
    exp1_won = False
    exp1_trigger_act = None

    for step_i in range(1, 31):
        cur_pos = get_avatar_pos(f_exp1, avatar_color)
        if cur_pos is None:
            break
        cx, cy = cur_pos
        dist = (cx - target_x)**2 + (cy - target_y)**2
        if dist < closest_dist:
            closest_dist = dist
            closest_pos = cur_pos

        # Choose greedy directional action toward target
        dx = target_x - cx
        dy = target_y - cy
        
        # Priority: move vertically first, then horizontally
        act = None
        act_name = None
        if dy < 0:
            act, act_name = GameAction.ACTION1, "ACTION1 (UP)"
        elif dy > 0:
            act, act_name = GameAction.ACTION2, "ACTION2 (DOWN)"
        elif dx < 0:
            act, act_name = GameAction.ACTION3, "ACTION3 (LEFT)"
        elif dx > 0:
            act, act_name = GameAction.ACTION4, "ACTION4 (RIGHT)"
        else:
            act, act_name = GameAction.ACTION1, "ACTION1 (UP)"

        f_before = f_exp1
        obs_exp1 = env.step(act, data={})
        total_steps += 1
        f_exp1 = get_2d_grid(obs_exp1)

        new_av_pos = get_avatar_pos(f_exp1, avatar_color)
        lvl_comp = getattr(obs_exp1, "levels_completed", 0)
        is_win_st = getattr(obs_exp1, "state", None) == GameState.WIN
        frame_ch = bool(np.any(f_exp1 != f_before))
        
        # Check target component area
        target_pix_before = np.sum(f_before[9:16, 33:40] != bg)
        target_pix_after = np.sum(f_exp1[9:16, 33:40] != bg)
        comp_disappeared = bool(target_pix_after < target_pix_before)

        print(f"  Step {step_i:2d}: action={act_name:<16} | avatar_new_pos={str(new_av_pos):<10} | levels_completed={lvl_comp} | frame_changed={str(frame_ch):<5} | comp_disappeared={comp_disappeared}")

        if lvl_comp > 0 or is_win_st:
            exp1_won = True
            exp1_trigger_act = act_name
            print(f"\nWIN_CONDITION_FOUND | triggering_action={exp1_trigger_act} | final_avatar_pos={new_av_pos} | steps_used={step_i}")
            break

    if not exp1_won:
        print(f"\nTARGET_UNREACHABLE | closest_pos_reached={closest_pos}")

    # ── EXPERIMENT 2: Test each small component as goal ──
    print("\n================================================================================")
    print("EXPERIMENT 2 — Test each small component as goal (area < 50, non-avatar, non-bg)")
    print("================================================================================\n")

    obs_e2 = env.step(GameAction.RESET, data={})
    total_steps += 1
    f_e2 = get_2d_grid(obs_e2)
    comps_e2 = get_components(f_e2, bg)
    small_comps = [
        c for c in comps_e2
        if c['area'] < 50 and c['color'] != avatar_color
    ]
    print(f"Found {len(small_comps)} small candidate components to test:")
    for idx, c in enumerate(small_comps):
        print(f"  Candidate [{idx}]: (cx={c['cx']:2d}, cy={c['cy']:2d}), color={c['color']:2d}, area={c['area']:2d}")

    exp2_win = False
    goal_found = None

    for idx, c in enumerate(small_comps):
        obs_test = env.step(GameAction.RESET, data={})
        total_steps += 1
        f_curr = get_2d_grid(obs_test)
        gx, gy = c['cx'], c['cy']

        reached = False
        win_fired = False
        disappeared = False

        # Budget: 40 actions
        for _ in range(40):
            cur_p = get_avatar_pos(f_curr, avatar_color)
            if cur_p is None:
                break
            ax, ay = cur_p
            if abs(ax - gx) <= 2 and abs(ay - gy) <= 2:
                reached = True

            dx = gx - ax
            dy = gy - ay
            if dx == 0 and dy == 0:
                break

            act = None
            if abs(dy) > 0:
                act = GameAction.ACTION1 if dy < 0 else GameAction.ACTION2
            else:
                act = GameAction.ACTION3 if dx < 0 else GameAction.ACTION4

            f_prev = f_curr
            obs_test = env.step(act, data={})
            total_steps += 1
            f_curr = get_2d_grid(obs_test)

            if getattr(obs_test, "state", None) == GameState.WIN or getattr(obs_test, "levels_completed", 0) > 0:
                win_fired = True
                reached = True
                break

        # Check if component disappeared
        orig_area = np.sum(f_curr[c['min_r']:c['max_r']+1, c['min_c']:c['max_c']+1] == c['color'])
        if orig_area == 0:
            disappeared = True

        print(f"  Component [{idx}] (cx={c['cx']:2d}, cy={c['cy']:2d}, color={c['color']:2d}, area={c['area']:2d}) -> reached={str(reached):<5} | WIN_fired={str(win_fired):<5} | comp_disappeared={disappeared}")

        if win_fired:
            exp2_win = True
            goal_found = (c['cx'], c['cy'], c['color'])
            print(f"\nGOAL DETECTED! goal_found = {goal_found}")
            break

    # ── EXPERIMENT 3: Maze Structure (Reachable Set BFS) ──
    print("\n================================================================================")
    print("EXPERIMENT 3 — Maze structure: Reachable Set via BFS Simulation")
    print("================================================================================\n")

    obs_e3 = env.step(GameAction.RESET, data={})
    total_steps += 1
    f_e3 = get_2d_grid(obs_e3)
    start_pos = get_avatar_pos(f_e3, avatar_color)

    # We will discover reachable positions by executing path sequences from start
    # Queue stores (position, path_of_actions)
    queue = deque([(start_pos, [])])
    visited = {start_pos}
    bfs_action_budget = 200
    bfs_actions_used = 0

    while queue and bfs_actions_used < bfs_action_budget:
        pos, path = queue.popleft()
        
        for act in [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]:
            if bfs_actions_used >= bfs_action_budget:
                break
            
            # Reset to start and replay path + new action
            env.step(GameAction.RESET, data={})
            bfs_actions_used += 1
            total_steps += 1

            for p_act in path:
                env.step(p_act, data={})
                bfs_actions_used += 1
                total_steps += 1

            obs_new = env.step(act, data={})
            bfs_actions_used += 1
            total_steps += 1
            f_new = get_2d_grid(obs_new)
            new_pos = get_avatar_pos(f_new, avatar_color)

            if new_pos is not None and new_pos not in visited:
                visited.add(new_pos)
                queue.append((new_pos, path + [act]))

    reachable_positions = list(visited)
    cxs = [p[0] for p in reachable_positions]
    cys = [p[1] for p in reachable_positions]
    min_cx, max_cx = min(cxs), max(cxs)
    min_cy, max_cy = min(cys), max(cys)

    can_reach_36_12 = (36, 12) in visited or any(abs(p[0]-36) <= 2 and abs(p[1]-12) <= 2 for p in visited)
    can_reach_36_48 = (36, 48) in visited or any(abs(p[0]-36) <= 2 and abs(p[1]-48) <= 2 for p in visited)

    print(f"total_reachable_positions: {len(reachable_positions)}")
    print(f"min_cx: {min_cx}, max_cx: {max_cx}")
    print(f"min_cy: {min_cy}, max_cy: {max_cy}")
    print(f"Reachable set positions sample: {reachable_positions[:15]}")
    print(f"can_avatar_reach (36, 12)? {can_reach_36_12}")
    print(f"can_avatar_reach (36, 48)? {can_reach_36_48}")

    arc.close_scorecard(sc_id)

    # ── STEP 5: RAW NUMBERS ──
    print("\n================================================================================")
    print("STEP 5 — RAW NUMBERS")
    print("================================================================================")
    print(f"win_condition_found: {exp1_won or exp2_win}")
    print(f"goal_coordinates: {goal_found[:2] if goal_found else None}")
    print(f"goal_color: {goal_found[2] if goal_found else None}")
    print(f"reachable_cell_count: {len(reachable_positions)}")
    print(f"maze_is_solvable: {can_reach_36_12 or (goal_found is not None)}")
    print(f"steps_used_total: {total_steps}")


if __name__ == "__main__":
    main()
