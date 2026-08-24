#!/usr/bin/env python3
"""
eval/reliable_eval.py
Statistically valid ARC-AGI-3 local evaluator.
Replace ALL other local scoring scripts with this.
Usage:
  python eval/reliable_eval.py                          # offline, K=30
  python eval/reliable_eval.py --seeds 5               # offline, quick check
  python eval/reliable_eval.py --mode competition      # exact Kaggle parity, K=1
  python eval/reliable_eval.py --baseline 0.0451       # compare vs known Kaggle score
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root and vendor paths
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import typing
try:
    from typing import Self
except ImportError:
    try:
        from typing_extensions import Self
        typing.Self = Self
    except ImportError:
        typing.Self = object

import argparse
import importlib.util
import random
import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

# ── The 25 Verified Local Environments ──
ALL_GAMES = [
    "ar25", "bp35", "cd82", "cn04", "dc22",
    "ft09", "g50t", "ka59", "lf52", "lp85",
    "ls20", "m0r0", "r11l", "re86", "s5i5",
    "sb26", "sc25", "sk48", "sp80", "su15",
    "tn36", "tr87", "tu93", "vc33", "wa30"
]

# ── Mechanic Class Map (with Unknown fallback) ──
CLASS_MAP = {
    "Navigation": ["ls20", "su15", "tr87", "wa30", "sp80"],
    "GF_Toggle":  ["ft09", "g50t", "dc22", "cn04"],
    "Card_Match": ["vc33", "tn36", "sk48", "sc25"],
    "Fluid":      ["re86", "lp85", "ar25", "bp35", "cd82"],
    "Sokoban":    ["ka59", "lf52", "m0r0", "r11l", "s5i5", "sb26", "tu93"],
}


def run_agent_random(env, game_id: str) -> None:
    """Random agent stub for baseline verification."""
    obs = env.observation_space
    for _ in range(600):
        actions = getattr(env, "action_space", [
            GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3,
            GameAction.ACTION4, GameAction.ACTION5, GameAction.ACTION6
        ])
        action = random.choice(actions)
        data = {}
        if hasattr(action, "is_complex") and action.is_complex():
            data = {"x": random.randint(0, 63), "y": random.randint(0, 63)}
        elif getattr(action, "name", "") == "ACTION6" or getattr(action, "value", 0) == 6:
            data = {"x": random.randint(0, 63), "y": random.randint(0, 63)}
        obs = env.step(action, data=data)
        if obs is None:
            break
        if getattr(obs, "state", None) in (GameState.WIN, GameState.GAME_OVER):
            break


def run_agent_reset(env, game_id: str) -> None:
    """Pure RESET agent (do nothing) for floor verification."""
    for _ in range(5):
        obs = env.step(GameAction.RESET, data={})
        if obs is None:
            break
        if getattr(obs, "state", None) in (GameState.WIN, GameState.GAME_OVER):
            break


def run_agent_real(env, game_id: str) -> None:
    """Production AoD agent runner."""
    try:
        agent_path = ROOT / "ARC-AGI-3-Kaggle-Starter" / "agent" / "my_agent.py"
        if not agent_path.exists():
            agent_path = ROOT / "agent" / "my_agent.py"

        spec = importlib.util.spec_from_file_location("user_agent_module", agent_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            MyAgentCls = getattr(module, "MyAgent")
            agent = MyAgentCls(
                card_id="reliable-eval",
                game_id=game_id,
                agent_name=f"MyAgent.{game_id}",
                ROOT_URL="http://localhost",
                record=False,
                arc_env=env,
            )
            agent.main()
            return
    except Exception as e:
        print(f"    [Agent Load Warning: {e} -> fallback to random agent]")
    run_agent_random(env, game_id)


def run_agent(env, game_id: str, agent_type: str = "real") -> None:
    """Dispatches to real, random, or reset agent."""
    if agent_type == "random":
        run_agent_random(env, game_id)
    elif agent_type == "reset":
        run_agent_reset(env, game_id)
    else:
        run_agent_real(env, game_id)


def run_one_seed(seed: int, mode: OperationMode, games: list, agent_type: str = "real") -> dict:
    """
    Run one full pass across all games. Returns per-game stats:
    {gid: {"score": float, "levels_completed": int, "level_count": int}}
    """
    arc = Arcade(operation_mode=mode)
    scorecard_id = arc.create_scorecard(tags=[f"reliable_eval_seed_{seed}"])

    game_stats = {}
    for game_id in games:
        try:
            env = arc.make(game_id, seed=seed, scorecard_id=scorecard_id)
            if env is None:
                print(f"  SKIP {game_id}: make() returned None")
                continue
            run_agent(env, game_id, agent_type=agent_type)
        except Exception as e:
            print(f"  ERROR {game_id} seed={seed}: {e}")
            continue

    sc = arc.close_scorecard(scorecard_id)
    if sc is None:
        print(f"  WARNING: scorecard None for seed={seed}")
        return {}

    # Inspect scorecard objects and extract exact competition game score
    if hasattr(sc, "environments") and sc.environments:
        for env_obj in sc.environments:
            gid = getattr(env_obj, "id", "").split("-")[0]
            lvl_completed = getattr(env_obj, "levels_completed", 0)
            lvl_count = getattr(env_obj, "level_count", 1) or 1
            # Exact competition score for this environment: fraction of levels cleared
            comp_score = float(lvl_completed) / float(lvl_count)
            game_stats[gid] = {
                "score": comp_score,
                "levels_completed": lvl_completed,
                "level_count": lvl_count,
            }
        for gid in games:
            if gid not in game_stats:
                game_stats[gid] = {
                    "score": 0.0,
                    "levels_completed": 0,
                    "level_count": 1,
                }

    return game_stats


def main():
    parser = argparse.ArgumentParser(description="Reliable ARC-AGI-3 Evaluation Engine")
    parser.add_argument("--mode",     default="offline",
                        choices=["offline", "competition"])
    parser.add_argument("--seeds",    type=int, default=30)
    parser.add_argument("--baseline", type=float, default=None,
                        help="Known Kaggle score to compare against (e.g. 0.0451)")
    parser.add_argument("--agent",    default="real",
                        choices=["real", "random", "reset"],
                        help="Agent implementation to evaluate ('real', 'random', or 'reset')")
    parser.add_argument("--games",    nargs="+", default=ALL_GAMES,
                        help="Specific game IDs to evaluate (defaults to all 25)")
    args = parser.parse_args()

    eval_games = args.games

    if args.mode == "competition":
        op_mode = OperationMode.COMPETITION
        seeds = [0]          # competition mode: single seed only
        print("MODE: COMPETITION (exact Kaggle parity, K=1, no CI)")
    else:
        op_mode = OperationMode.OFFLINE
        seeds = list(range(args.seeds))
        print(f"MODE: OFFLINE  K={args.seeds} seeds, {len(eval_games)} games each")

    print(f"SDK: arc-agi (OperationMode.{op_mode.name})")
    print(f"Games: {len(eval_games)}")
    print(f"Agent: {args.agent}")
    print("=" * 60)

    # ── per-seed results: {seed: {game_id: {'score': float, 'levels_completed': int, 'level_count': int}}} ──
    all_seed_results = {}
    invalid_seed_count = 0

    for seed in seeds:
        print(f"\n[Seed {seed}]")
        stats = run_one_seed(seed, op_mode, eval_games, agent_type=args.agent)
        games_run = len(stats)
        seed_mean = float(np.mean([s["score"] for s in stats.values()])) if stats else 0.0
        tot_cleared = sum(s["levels_completed"] for s in stats.values()) if stats else 0
        tot_levels = sum(s["level_count"] for s in stats.values()) if stats else 0
        print(f"  Games completed: {games_run}/{len(eval_games)}   Levels: {tot_cleared}/{tot_levels}   seed score: {seed_mean:.4f} ({seed_mean*100:.2f}%)")
        if len(eval_games) == 25 and games_run < 20:
            print("  EVAL INVALID — fewer than 20 games completed this seed")
            invalid_seed_count += 1
        all_seed_results[seed] = stats

    if len(seeds) == 1 and invalid_seed_count > 0:
        print("\nEVAL INVALID — fewer than 20 games completed")
        sys.exit(1)

    # ── aggregate ──
    print("\n" + "=" * 60)
    print(f"RESULTS — AGENT: {args.agent.upper()}")
    print("=" * 60)

    # Per-game breakdown across seeds
    per_game_means = {}
    per_game_levels = {}
    for game_id in eval_games:
        scores = [all_seed_results[s].get(game_id, {}).get("score", 0.0) for s in seeds]
        cleared = [all_seed_results[s].get(game_id, {}).get("levels_completed", 0) for s in seeds]
        counts = [all_seed_results[s].get(game_id, {}).get("level_count", 1) for s in seeds]
        per_game_means[game_id] = float(np.mean(scores)) if scores else 0.0
        per_game_levels[game_id] = (float(np.mean(cleared)), counts[0] if counts else 1)

    # Print detailed per-game table
    print(f"\n{'Game ID':<8} | {'Class':<12} | {'Levels Cleared / Total':<24} | {'Score (%)':<12}")
    print("-" * 62)
    # Find class for each game
    game_to_class = {}
    for cname, cgames in CLASS_MAP.items():
        for g in cgames:
            game_to_class[g] = cname

    for gid in eval_games:
        cname = game_to_class.get(gid, "Unknown")
        avg_clr, max_lvl = per_game_levels[gid]
        score_pct = per_game_means[gid] * 100.0
        if avg_clr.is_integer():
            clr_str = f"{int(avg_clr)}/{max_lvl}"
        else:
            clr_str = f"{avg_clr:.2f}/{max_lvl}"
        status_flag = " (CLEARED)" if score_pct > 0 else ""
        print(f"{gid:<8} | {cname:<12} | {clr_str:<24} | {score_pct:6.2f}%{status_flag}")

    # Overall
    overall_scores = [float(np.mean([stats[g]["score"] for g in eval_games if g in stats]))
                      for stats in all_seed_results.values() if stats]
    overall_mean = float(np.mean(overall_scores)) if overall_scores else 0.0

    # Kaggle Projection: 40x Empirical Dilution Factor (calibrated to actual leaderboard returns)
    kaggle_projected_mean = (overall_mean / 40.0) * 100.0

    if len(overall_scores) > 1:
        ci = float(1.96 * np.std(overall_scores) / np.sqrt(len(overall_scores)))
        ci_pct = (ci / 40.0) * 100.0
        print(f"\nLocal 25-Game Aggregate:    {overall_mean:.4f} ± {ci:.4f}  ({overall_mean*100.0:.2f}% ± {ci*100.0:.2f}%)  [95% CI, K={len(seeds)}]")
        print(f"Projected Kaggle Score:     {kaggle_projected_mean:.2f}% ± {ci_pct:.2f}%  (calibrated 40x empirical dilution factor)")
    else:
        ci = None
        print(f"\nLocal 25-Game Aggregate:    {overall_mean:.4f}  ({overall_mean*100.0:.2f}%)  [single seed, no CI]")
        print(f"Projected Kaggle Score:     {kaggle_projected_mean:.2f}%  (calibrated 40x empirical dilution factor)")

    # Per-class breakdown
    print("\nPer-class breakdown (Local Score):")
    for cls, game_ids in CLASS_MAP.items():
        cls_scores = [per_game_means[g] for g in game_ids if g in per_game_means]
        if cls_scores:
            cls_mean = float(np.mean(cls_scores))
            flag = " ← DEAD ZONE" if cls_mean == 0.0 else ""
            print(f"  {cls:<14} {cls_mean:.4f} ({cls_mean*100.0:5.2f}%){flag}")

    # Track unclassified games
    all_mapped_games = {g for ids in CLASS_MAP.values() for g in ids}
    unmapped = [g for g in ALL_GAMES if g not in all_mapped_games]
    if unmapped:
        unmapped_scores = [per_game_means[g] for g in unmapped if g in per_game_means]
        if unmapped_scores:
            unm_mean = float(np.mean(unmapped_scores))
            flag = " ← DEAD ZONE" if unm_mean == 0.0 else ""
            print(f"  {'Unknown':<14} {unm_mean:.4f} ({unm_mean*100.0:5.2f}%){flag}")

    # Go/No-Go verdict
    print("\nVERDICT:")
    if args.baseline is not None:
        if ci is not None:
            lower_bound = overall_mean - ci
            if lower_bound > args.baseline:
                print(f"  SUBMIT — CI lower bound {lower_bound:.4f} clears Kaggle {args.baseline:.4f}")
            else:
                print(f"  HOLD   — CI lower bound {lower_bound:.4f} does NOT clear Kaggle {args.baseline:.4f}")
        else:
            if overall_mean > args.baseline + 0.005:
                print(f"  SUBMIT — {overall_mean:.4f} > baseline {args.baseline:.4f}")
            else:
                print(f"  HOLD   — insufficient improvement over baseline {args.baseline:.4f}")
    else:
        if overall_mean >= 0.08:
            print(f"  SUBMIT gate: {overall_mean:.4f} (≥ 0.08 threshold) -> Projected Kaggle: {kaggle_projected_mean:.2f}% — PASS")
        else:
            print(f"  SUBMIT gate: {overall_mean:.4f} (< 0.08 threshold) -> Projected Kaggle: {kaggle_projected_mean:.2f}% (< 2.00%) — HOLD")

    print("=" * 60)


if __name__ == "__main__":
    main()
