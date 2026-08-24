import sys
from pathlib import Path
from itertools import combinations
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


# ==============================================================================
# SHARED UTILITIES
# ==============================================================================

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


def avatar_pos(grid, avatar_color):
    """Return (cx, cy) of largest component with avatar_color, or None."""
    bg = get_background_color(grid)
    comps = [c for c in get_components(grid, bg) if c['color'] == avatar_color]
    if not comps:
        return None
    largest = max(comps, key=lambda c: c['area'])
    return largest['cx'], largest['cy']


def detect_avatar(env):
    """
    Identify avatar color by finding component that moves on ACTION1-4.
    Returns (avatar_color, start_cx, start_cy, pixels_per_step).
    """
    obs0 = env.step(GameAction.RESET, data={})
    f0 = get_2d_grid(obs0)
    bg = get_background_color(f0)
    comps0 = get_components(f0, bg)
    
    for act in [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]:
        env.step(GameAction.RESET, data={})
        obs1 = env.step(act, data={})
        f1 = get_2d_grid(obs1)
        comps1 = get_components(f1, bg)
        
        for c0 in comps0:
            color = c0['color']
            matching1 = [c for c in comps1 if c['color'] == color and abs(c['area'] - c0['area']) <= 2]
            if matching1:
                c1 = matching1[0]
                dcx = c1['cx'] - c0['cx']
                dcy = c1['cy'] - c0['cy']
                if abs(dcx) > 0 or abs(dcy) > 0:
                    step = int(max(abs(dcx), abs(dcy)))
                    env.step(GameAction.RESET, data={})
                    return color, c0['cx'], c0['cy'], step

    env.step(GameAction.RESET, data={})
    return None, None, None, None


def proper_bfs(env, avatar_color, bg_color, step_budget=12000):
    obs_init = env.step(GameAction.RESET, data={})
    steps = 1
    
    f_init = get_2d_grid(obs_init)
    start = avatar_pos(f_init, avatar_color)
    if start is None:
        print(f"BFS_ABORT: avatar_color={avatar_color} not found in initial frame")
        return {}, False, None, steps
    
    reachable = {start: []}
    frontier = [start]
    
    DIR_ACTIONS = [GameAction.ACTION1, GameAction.ACTION2,
                   GameAction.ACTION3, GameAction.ACTION4]
    
    while frontier and steps < step_budget:
        curr = frontier.pop(0)
        curr_path = reachable[curr]
        
        for action in DIR_ACTIONS:
            if steps >= step_budget:
                print(f"BFS_BUDGET_EXHAUSTED at steps={steps}")
                break
            
            env.step(GameAction.RESET, data={})
            steps += 1
            for a in curr_path:
                env.step(a, data={})
                steps += 1
            
            obs_new = env.step(action, data={})
            steps += 1
            
            f_new = get_2d_grid(obs_new)
            new_pos = avatar_pos(f_new, avatar_color)
            
            if new_pos is None or new_pos == curr:
                continue
            
            lc_new = getattr(obs_new, 'levels_completed', 0)
            st_new = getattr(obs_new, 'state', None)
            if st_new == GameState.WIN or lc_new > 0:
                win_path = curr_path + [action]
                print(f"WIN_FOUND | pos={new_pos} | path_len={len(win_path)} | steps={steps}")
                return reachable, True, win_path, steps
            
            if new_pos not in reachable:
                reachable[new_pos] = curr_path + [action]
                frontier.append(new_pos)
    
    return reachable, False, None, steps


def solve_ft09(env, max_steps: int = 2000) -> dict:
    total_steps = 0
    obs_start = env.step(GameAction.RESET, data={})
    total_steps += 1

    grid = get_2d_grid(obs_start)
    bg = get_background_color(grid)
    initial_levels_completed = getattr(obs_start, "levels_completed", 0)

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

    candidates.sort(key=lambda b: (b['cy'], b['cx']))

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
                return {
                    "win": True,
                    "winning_subset": sorted_combo,
                    "k": k,
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


# ==============================================================================
# SECTION EXECUTION
# ==============================================================================

def run_section_0():
    print("SECTION_0_START")
    arc = Arcade(operation_mode=OperationMode.COMPETITION)
    sc_id = arc.create_scorecard()
    env = arc.make('ft09', seed=0, scorecard_id=sc_id)
    result = solve_ft09(env, max_steps=2000)
    arc.close_scorecard(sc_id)

    print(f"ft09_competition | win={result['win']} | "
          f"steps={result['total_steps']} | "
          f"n_responsive={result['n_responsive']} | "
          f"color_off={result['color_off']} | color_on={result['color_on']}")

    if result['win']:
        print("FT09_COMPETITION_GATE: PASS")
    else:
        print("FT09_COMPETITION_GATE: FAIL — do NOT integrate ft09 into agent")

    print("SECTION_0_END")
    return result['win']


def run_section_1():
    print("SECTION_1_START")
    nav_games = ['ls20', 'su15', 'tr87', 'wa30', 'sp80']
    nav_summary = {}

    for GAME_ID in nav_games:
        print(f"\n--- SUBSECTION 1A: {GAME_ID} SETUP ---")
        arc = Arcade(operation_mode=OperationMode.OFFLINE)
        sc_id = arc.create_scorecard()
        env = arc.make(GAME_ID, seed=0, scorecard_id=sc_id)
        
        avatar_color, start_cx, start_cy, step_size = detect_avatar(env)
        
        obs_init = env.step(GameAction.RESET, data={})
        f_init = get_2d_grid(obs_init)
        bg = get_background_color(f_init)
        all_comps = get_components(f_init, bg)
        
        print(f"GAME={GAME_ID} | avatar_color={avatar_color} | "
              f"start=({start_cx},{start_cy}) | step_size={step_size}")
        print(f"ALL_COMPONENTS ({len(all_comps)} total):")
        for i, c in enumerate(all_comps):
            print(f"  [{i:2d}] cx={c['cx']:3d} cy={c['cy']:3d} "
                  f"area={c['area']:4d} color={c['color']:2d} "
                  f"w={c['w']:3d} h={c['h']:3d}")

        print(f"\n--- SUBSECTION 1B: {GAME_ID} PROPER BFS ---")
        reachable, win_bfs, win_path_bfs, steps_bfs = proper_bfs(
            env, avatar_color, bg, step_budget=12000
        )
        
        print(f"BFS_RESULT | game={GAME_ID} | "
              f"reachable_count={len(reachable)} | "
              f"win_found={win_bfs} | steps={steps_bfs}")
        
        if reachable:
            reach_cxs = [p[0] for p in reachable]
            reach_cys = [p[1] for p in reachable]
            comps_in_reach = [c for c in all_comps 
                              if min(reach_cxs) <= c['cx'] <= max(reach_cxs)
                              and min(reach_cys) <= c['cy'] <= max(reach_cys)
                              and c['color'] != avatar_color]
            print(f"COMPONENTS_IN_REACHABLE_ZONE ({len(comps_in_reach)}):")
            for c in comps_in_reach:
                print(f"  cx={c['cx']} cy={c['cy']} color={c['color']} area={c['area']}")

        interaction_win_found = False
        win_mechanism = "UNKNOWN"
        steps_total_game = steps_bfs

        if win_bfs:
            win_mechanism = "BFS_PATHFINDING"
        else:
            print(f"\n--- SUBSECTION 1C: {GAME_ID} ACTION5 & ACTION6 INTERACTION TEST ---")
            interactions_with_delta = []
            
            for pos in list(reachable.keys()):
                # Navigate to pos
                obs_nav = env.step(GameAction.RESET, data={})
                steps_total_game += 1
                for a in reachable[pos]:
                    obs_nav = env.step(a, data={})
                    steps_total_game += 1
                
                f_before = get_2d_grid(obs_nav)
                comps_before = get_components(f_before, bg)
                lc_before = getattr(obs_nav, 'levels_completed', 0)
                
                # ACTION5
                obs_a5 = env.step(GameAction.ACTION5, data={})
                steps_total_game += 1
                f_a5 = get_2d_grid(obs_a5)
                delta_a5 = int(np.sum(f_a5 != f_before))
                lc_a5 = getattr(obs_a5, 'levels_completed', 0)
                state_a5 = getattr(obs_a5, 'state', None)
                comps_a5 = get_components(f_a5, bg)
                colors_before = set(c['color'] for c in comps_before)
                colors_a5 = set(c['color'] for c in comps_a5)
                disappeared_a5 = colors_before - colors_a5
                
                if delta_a5 > 0:
                    interactions_with_delta.append((pos, GameAction.ACTION5, obs_a5))
                    print(f"ACTION5 at pos={pos} | delta={delta_a5} | "
                          f"disappeared={disappeared_a5} | lc={lc_a5} | state={state_a5}")
                
                if state_a5 == GameState.WIN or lc_a5 > lc_before:
                    print(f"WIN_EVENT | game={GAME_ID} | action=ACTION5 | "
                          f"pos={pos} | lc_before={lc_before} | lc_after={lc_a5}")
                    interaction_win_found = True
                    win_mechanism = "SWITCH_ACTIVATION"
                    break
                
                # ACTION6 at current pos
                obs_nav2 = env.step(GameAction.RESET, data={})
                steps_total_game += 1
                for a in reachable[pos]:
                    obs_nav2 = env.step(a, data={})
                    steps_total_game += 1
                f_before2 = get_2d_grid(obs_nav2)
                lc_before2 = getattr(obs_nav2, 'levels_completed', 0)
                
                obs_a6 = env.step(GameAction.ACTION6, data={'x': int(pos[0]), 'y': int(pos[1])})
                steps_total_game += 1
                f_a6 = get_2d_grid(obs_a6)
                delta_a6 = int(np.sum(f_a6 != f_before2))
                lc_a6 = getattr(obs_a6, 'levels_completed', 0)
                state_a6 = getattr(obs_a6, 'state', None)
                comps_a6 = get_components(f_a6, bg)
                disappeared_a6 = colors_before - set(c['color'] for c in comps_a6)
                
                if delta_a6 > 0:
                    interactions_with_delta.append((pos, GameAction.ACTION6, obs_a6))
                    print(f"ACTION6 at pos={pos} | delta={delta_a6} | "
                          f"disappeared={disappeared_a6} | lc={lc_a6} | state={state_a6}")
                
                if state_a6 == GameState.WIN or lc_a6 > lc_before2:
                    print(f"WIN_EVENT | game={GAME_ID} | action=ACTION6 | "
                          f"pos={pos} | lc_before={lc_before2} | lc_after={lc_a6}")
                    interaction_win_found = True
                    win_mechanism = "CLICK_INTERACTION"
                    break

            # Try clicking all components from nearest reachable pos
            if not interaction_win_found and reachable:
                for comp in all_comps:
                    if comp['color'] == avatar_color or comp['color'] == bg:
                        continue
                    cx_t, cy_t = comp['cx'], comp['cy']
                    nearest = min(reachable.keys(), key=lambda p: (p[0]-cx_t)**2 + (p[1]-cy_t)**2)
                    
                    obs_n3 = env.step(GameAction.RESET, data={})
                    steps_total_game += 1
                    for a in reachable[nearest]:
                        obs_n3 = env.step(a, data={})
                        steps_total_game += 1
                    f_before3 = get_2d_grid(obs_n3)
                    lc_before3 = getattr(obs_n3, 'levels_completed', 0)
                    
                    obs_click = env.step(GameAction.ACTION6, data={'x': int(cx_t), 'y': int(cy_t)})
                    steps_total_game += 1
                    f_click = get_2d_grid(obs_click)
                    delta_click = int(np.sum(f_click != f_before3))
                    lc_click = getattr(obs_click, 'levels_completed', 0)
                    state_click = getattr(obs_click, 'state', None)
                    
                    if delta_click > 0 or state_click == GameState.WIN or lc_click > lc_before3:
                        print(f"CLICK_COMPONENT | game={GAME_ID} | "
                              f"target=({cx_t},{cy_t}) color={comp['color']} area={comp['area']} | "
                              f"from={nearest} | delta={delta_click} | "
                              f"lc_before={lc_before3} | lc_after={lc_click} | state={state_click}")
                    
                    if state_click == GameState.WIN or lc_click > lc_before3:
                        print(f"WIN_EVENT | game={GAME_ID} | action=ACTION6_COMPONENT | "
                              f"target=({cx_t},{cy_t}) | lc_before={lc_before3} | lc_after={lc_click}")
                        interaction_win_found = True
                        win_mechanism = "CLICK_INTERACTION"
                        break

            if not interaction_win_found:
                print(f"\n--- SUBSECTION 1E: {GAME_ID} LEVEL 0 SUMMARY ---")
                print(f"LEVEL0_FRAME_SUMMARY | game={GAME_ID}")
                print(f"  bg_color={bg}")
                print(f"  total_components={len(all_comps)}")
                for c in sorted(all_comps, key=lambda x: x['area'], reverse=True)[:5]:
                    print(f"  largest: color={c['color']} area={c['area']} cx={c['cx']} cy={c['cy']}")

        print(f"\nSUBSECTION 1F: WIN_SUMMARY | game={GAME_ID} | "
              f"bfs_win={win_bfs} | "
              f"interaction_win={interaction_win_found} | "  
              f"win_mechanism={win_mechanism} | "
              f"total_steps_section1={steps_total_game}")
        
        nav_summary[GAME_ID] = {
            "win_found": win_bfs or interaction_win_found,
            "mechanism": win_mechanism
        }
        arc.close_scorecard(sc_id)

    print("\nNAVIGATION_SUMMARY:")
    for g, info in nav_summary.items():
        print(f"  {g}: win_found={info['win_found']} mechanism={info['mechanism']}")

    print("SECTION_1_END")
    return nav_summary


def run_section_2():
    print("SECTION_2_START")
    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard()
    env = arc.make('dc22', seed=0, scorecard_id=sc_id)

    obs_init = env.step(GameAction.RESET, data={})
    f_init = get_2d_grid(obs_init)
    bg = get_background_color(f_init)
    all_comps_dc22 = get_components(f_init, bg)

    print(f"dc22_FRAME_DUMP:")
    for i, c in enumerate(all_comps_dc22):
        print(f"  [{i:2d}] cx={c['cx']:3d} cy={c['cy']:3d} "
              f"area={c['area']:5d} color={c['color']:2d} "
              f"w={c['w']:3d} h={c['h']:3d}")

    # STEP 1: Try ALL 5 actions
    for action_name, action in [("ACTION1", GameAction.ACTION1),
                                ("ACTION2", GameAction.ACTION2),
                                ("ACTION3", GameAction.ACTION3),
                                ("ACTION4", GameAction.ACTION4),
                                ("ACTION5", GameAction.ACTION5)]:
        obs_b = env.step(GameAction.RESET, data={})
        f_before = get_2d_grid(obs_b)
        lc_before = getattr(obs_b, 'levels_completed', 0)
        
        obs_after = env.step(action, data={})
        f_after = get_2d_grid(obs_after)
        lc_after = getattr(obs_after, 'levels_completed', 0)
        
        diff_mask = f_after != f_before
        changed_pixels = list(zip(*np.where(diff_mask)))
        
        print(f"dc22_{action_name} | delta={len(changed_pixels)} | "
              f"lc_before={lc_before} lc_after={lc_after}")
        for (r, c_idx) in changed_pixels[:10]:
            print(f"  pixel ({c_idx},{r}): before={f_before[r,c_idx]} after={f_after[r,c_idx]}")

    # STEP 2: Clicks on (24,20) and (10,40)
    for bx, by in [(24, 20), (10, 40)]:
        obs_b = env.step(GameAction.RESET, data={})
        f_before = get_2d_grid(obs_b)
        
        obs_click = env.step(GameAction.ACTION6, data={'x': bx, 'y': by})
        f_click = get_2d_grid(obs_click)
        lc_click = getattr(obs_click, 'levels_completed', 0)
        state_click = getattr(obs_click, 'state', None)
        
        diff_mask = f_click != f_before
        changed_pixels = list(zip(*np.where(diff_mask)))
        
        print(f"dc22_CLICK ({bx},{by}) | delta={len(changed_pixels)} | "
              f"lc={lc_click} | state={state_click}")
        for (r, c_idx) in changed_pixels:
            print(f"  pixel ({c_idx},{r}): before={f_before[r,c_idx]} after={f_click[r,c_idx]}")

    # STEP 3: detect_avatar
    avatar_color_dc22, ax, ay, step_dc22 = detect_avatar(env)
    print(f"dc22_AVATAR: color={avatar_color_dc22} pos=({ax},{ay}) step={step_dc22}")

    # STEP 4: 200 random actions
    random.seed(42)
    obs_r_init = env.step(GameAction.RESET, data={})
    lc_start = getattr(obs_r_init, 'levels_completed', 0)
    actions_pool = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3,
                    GameAction.ACTION4, GameAction.ACTION5]
    win_dc22 = False
    for step_i in range(200):
        action = random.choice(actions_pool)
        obs_r = env.step(action, data={})
        lc_r = getattr(obs_r, 'levels_completed', 0)
        st_r = getattr(obs_r, 'state', None)
        if st_r == GameState.WIN or lc_r > lc_start:
            print(f"WIN_EVENT | game=dc22 | random_step={step_i} | "
                  f"action={action} | lc_before={lc_start} | lc_after={lc_r}")
            win_dc22 = True
            break

    if not win_dc22:
        print("dc22_RANDOM_WALK_200: WIN_NOT_FOUND")

    arc.close_scorecard(sc_id)
    print("SECTION_2_END")


def run_section_3():
    print("SECTION_3_START")
    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard()
    env = arc.make('g50t', seed=0, scorecard_id=sc_id)

    obs_init = env.step(GameAction.RESET, data={})
    f_init = get_2d_grid(obs_init)

    bg_g50t = get_background_color(f_init)
    all_comps_g50t = get_components(f_init, bg_g50t)

    print(f"g50t_BACKGROUND_COLOR={bg_g50t}")
    print(f"g50t_ALL_COMPONENTS ({len(all_comps_g50t)}):")
    for i, c in enumerate(all_comps_g50t):
        print(f"  [{i:2d}] cx={c['cx']:3d} cy={c['cy']:3d} "
              f"area={c['area']:5d} color={c['color']:2d} "
              f"w={c['w']:3d} h={c['h']:3d}")

    print("g50t_FRAME_ROW_SUMMARY (dominant color per row):")
    for row in range(0, 64, 4):
        row_colors = list(f_init[row, :])
        dominant = max(set(row_colors), key=row_colors.count)
        unique = sorted(set(row_colors))
        print(f"  row={row:2d}: dominant={dominant} unique={unique}")

    print("g50t_ACTION_DELTAS:")
    for action_name, action in [("ACTION1", GameAction.ACTION1),
                                ("ACTION2", GameAction.ACTION2),
                                ("ACTION3", GameAction.ACTION3),
                                ("ACTION4", GameAction.ACTION4),
                                ("ACTION5", GameAction.ACTION5)]:
        obs_b = env.step(GameAction.RESET, data={})
        f_before = get_2d_grid(obs_b)
        obs_a = env.step(action, data={})
        f_after = get_2d_grid(obs_a)
        delta = int(np.sum(f_after != f_before))
        lc = getattr(obs_a, 'levels_completed', 0)
        st = getattr(obs_a, 'state', None)
        print(f"  {action_name}: delta={delta} lc={lc} state={st}")

    avatar_color_g50t, ax_g50t, ay_g50t, step_g50t = detect_avatar(env)
    print(f"g50t_AVATAR: color={avatar_color_g50t} pos=({ax_g50t},{ay_g50t}) step={step_g50t}")

    print("g50t_CLICK_ALL_COMPONENTS:")
    for comp in all_comps_g50t:
        obs_b = env.step(GameAction.RESET, data={})
        f_b = get_2d_grid(obs_b)
        lc_b = getattr(obs_b, 'levels_completed', 0)
        obs_c = env.step(GameAction.ACTION6, data={'x': int(comp['cx']), 'y': int(comp['cy'])})
        f_c = get_2d_grid(obs_c)
        delta_c = int(np.sum(f_c != f_b))
        lc_c = getattr(obs_c, 'levels_completed', 0)
        st_c = getattr(obs_c, 'state', None)
        if delta_c > 0 or st_c == GameState.WIN or lc_c > lc_b:
            print(f"  CLICK ({comp['cx']},{comp['cy']}) color={comp['color']} | "
                  f"delta={delta_c} lc_before={lc_b} lc_after={lc_c} state={st_c}")
        if st_c == GameState.WIN or lc_c > lc_b:
            print(f"WIN_EVENT | game=g50t | action=ACTION6 | target=({comp['cx']},{comp['cy']})")

    random.seed(42)
    obs_g_init = env.step(GameAction.RESET, data={})
    lc_g50t_start = getattr(obs_g_init, 'levels_completed', 0)
    all_actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3,
                   GameAction.ACTION4, GameAction.ACTION5]
    win_g50t = False
    for step_i in range(300):
        action = random.choice(all_actions)
        obs_r = env.step(action, data={})
        lc_r = getattr(obs_r, 'levels_completed', 0)
        st_r = getattr(obs_r, 'state', None)
        if st_r == GameState.WIN or lc_r > lc_g50t_start:
            print(f"WIN_EVENT | game=g50t | random_step={step_i} | "
                  f"lc_before={lc_g50t_start} | lc_after={lc_r}")
            win_g50t = True
            break

    if not win_g50t:
        print("g50t_RANDOM_WALK_300: WIN_NOT_FOUND")

    arc.close_scorecard(sc_id)
    print("SECTION_3_END")


def solve_cn04(env, max_steps=3000):
    total_steps = 0
    obs_init = env.step(GameAction.RESET, data={})
    total_steps += 1
    f_init = get_2d_grid(obs_init)
    bg = get_background_color(f_init)
    init_lc = getattr(obs_init, 'levels_completed', 0)
    
    all_comps = get_components(f_init, bg)
    
    movable_piece = None
    for comp in all_comps:
        if comp['color'] == bg:
            continue
        obs_res = env.step(GameAction.RESET, data={})
        total_steps += 1
        
        obs_sel = env.step(GameAction.ACTION6, data={'x': int(comp['cx']), 'y': int(comp['cy'])})
        total_steps += 1
        f_before = get_2d_grid(obs_sel)
        
        obs_move = env.step(GameAction.ACTION4, data={})
        total_steps += 1
        f_after = get_2d_grid(obs_move)
        
        delta = int(np.sum(f_after != f_before))
        if delta > 0:
            comps_after = get_components(f_after, bg)
            moved_comps = [c for c in comps_after if c['color'] == comp['color']]
            if moved_comps:
                new_cx = max(moved_comps, key=lambda x: x['area'])['cx']
                if new_cx != comp['cx']:
                    movable_piece = comp
                    print(f"MOVABLE_PIECE_FOUND: color={comp['color']} "
                          f"cx={comp['cx']} cy={comp['cy']} area={comp['area']}")
                    break
    
    if movable_piece is None:
        print("MOVABLE_PIECE_NOT_FOUND")
        return {'win': False, 'steps_used': total_steps, 
                'rotation': None, 'translation': None, 'total_attempts': 0}
    
    pin_comps = [c for c in all_comps if c['color'] in [8, 13]]
    print(f"PIN_MARKERS ({len(pin_comps)}):")
    for p in pin_comps:
        print(f"  color={p['color']} cx={p['cx']} cy={p['cy']} area={p['area']}")
    
    attempts = 0
    for rotation in range(4):
        for dx in range(-25, 26, 3):
            for dy in range(-25, 26, 3):
                if total_steps >= max_steps:
                    print(f"cn04_BUDGET_EXHAUSTED at steps={total_steps}")
                    return {'win': False, 'steps_used': total_steps,
                            'rotation': None, 'translation': None,
                            'total_attempts': attempts}
                
                env.step(GameAction.RESET, data={})
                total_steps += 1
                env.step(GameAction.ACTION6, 
                         data={'x': int(movable_piece['cx']),
                               'y': int(movable_piece['cy'])})
                total_steps += 1
                
                for _ in range(rotation):
                    env.step(GameAction.ACTION5, data={})
                    total_steps += 1
                
                h_action = GameAction.ACTION4 if dx > 0 else GameAction.ACTION3
                v_action = GameAction.ACTION2 if dy > 0 else GameAction.ACTION1
                
                for _ in range(abs(dx)):
                    env.step(h_action, data={})
                    total_steps += 1
                
                obs_final = None
                for _ in range(abs(dy)):
                    obs_final = env.step(v_action, data={})
                    total_steps += 1
                
                if obs_final is None:
                    obs_final = env.step(GameAction.ACTION5, data={})
                    total_steps += 1
                    # unrotate
                    for _ in range(3):
                        obs_final = env.step(GameAction.ACTION5, data={})
                        total_steps += 1
                
                lc_check = getattr(obs_final, 'levels_completed', 0)
                st_check = getattr(obs_final, 'state', None)
                attempts += 1
                
                if st_check == GameState.WIN or lc_check > init_lc:
                    print(f"WIN_EVENT | game=cn04 | "
                          f"rotation={rotation} | dx={dx} | dy={dy} | "
                          f"attempts={attempts} | steps={total_steps}")
                    return {'win': True, 'steps_used': total_steps,
                            'rotation': rotation, 'translation': (dx, dy),
                            'total_attempts': attempts}
    
    print(f"cn04_EXHAUSTED | attempts={attempts} | steps={total_steps} | win=False")
    return {'win': False, 'steps_used': total_steps,
            'rotation': None, 'translation': None,
            'total_attempts': attempts}


def run_section_4():
    print("SECTION_4_START")
    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard()
    env = arc.make('cn04', seed=0, scorecard_id=sc_id)

    results = []
    for level in range(6):
        res = solve_cn04(env, max_steps=3000)
        results.append(res)
        print(f"cn04 level={level} | win={res['win']} | "
              f"steps={res['steps_used']} | "
              f"rotation={res['rotation']} | "
              f"translation={res['translation']} | "
              f"attempts={res['total_attempts']}")

    arc.close_scorecard(sc_id)
    print("SECTION_4_END")
    return results


def main():
    ft09_gate_pass = False
    nav_summary = {}
    cn04_solved = False

    try:
        ft09_gate_pass = run_section_0()
    except Exception as e:
        print(f"EXCEPTION_SECTION_0 | {e}")
        traceback.print_exc()

    try:
        nav_summary = run_section_1()
    except Exception as e:
        print(f"EXCEPTION_SECTION_1 | {e}")
        traceback.print_exc()

    try:
        run_section_2()
    except Exception as e:
        print(f"EXCEPTION_SECTION_2 | {e}")
        traceback.print_exc()

    try:
        run_section_3()
    except Exception as e:
        print(f"EXCEPTION_SECTION_3 | {e}")
        traceback.print_exc()

    try:
        cn04_res = run_section_4()
        cn04_solved = any(r['win'] for r in cn04_res)
    except Exception as e:
        print(f"EXCEPTION_SECTION_4 | {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
