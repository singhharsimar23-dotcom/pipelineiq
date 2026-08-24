"""
1-to-1 Exact Kaggle ARC-AGI-3 Local Simulator
Replicates the exact Kaggle evaluation harness:
1. Multi-threaded Swarm orchestration across all 25 official competition games concurrently.
2. Exact connected component perception & black-box isolation.
3. Official ARC-AGI-3 scorecard efficiency formula with human baselines.
4. Level weighting: w_i = i, score capped by level fraction.
5. Aggregate score calculation and verification.
"""
from __future__ import annotations

import sys
import time
import threading
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor" / "ARC-AGI-3-Agents"))

import arc_agi
from arc_agi import Arcade, OperationMode
from arc_agi.scorecard import EnvironmentScoreCalculator
from agent.my_agent import MyAgent


def simulate_kaggle_eval():
    print("=" * 70)
    print("       PIPELINEIQ — 1-TO-1 EXACT KAGGLE EVALUATION SIMULATOR")
    print("=" * 70)

    # Initialize Arcade in normal offline mode matching local gateway behavior
    arc = Arcade(operation_mode=OperationMode.NORMAL)
    envs = arc.get_environments()
    game_ids = [e.game_id.split("-")[0] for e in envs]
    
    print(f"[*] Loaded {len(game_ids)} competition game environments.")
    print("[*] Spawning 25 concurrent agent threads (replicating Kaggle Swarm)...")

    agents = []
    threads = []
    results = {}
    lock = threading.Lock()

    start_time = time.time()

    # Instantiate all 25 agents concurrently
    for gid in game_ids:
        env = arc.make(gid)
        agent = MyAgent(
            card_id="simulated-kaggle-card",
            game_id=gid,
            agent_name=f"MyAgent.{gid}",
            ROOT_URL="http://gateway:8001",
            record=False,
            arc_env=env
        )
        agents.append((gid, agent))

    def worker(gid, agent):
        try:
            agent.main()
            final_frame = agent.frames[-1]
            with lock:
                results[gid] = {
                    "state": final_frame.state,
                    "levels_completed": final_frame.levels_completed,
                    "actions": agent.action_counter,
                    "error": None
                }
        except Exception as e:
            with lock:
                results[gid] = {
                    "state": "CRASH",
                    "levels_completed": 0,
                    "actions": agent.action_counter,
                    "error": str(e)
                }

    # Start all 25 parallel threads simultaneously
    for gid, agent in agents:
        t = threading.Thread(target=worker, args=(gid, agent))
        threads.append(t)
        t.start()

    # Join all threads
    for t in threads:
        t.join()

    elapsed = time.time() - start_time
    scorecard = arc.get_scorecard()

    print(f"[*] Concurrent evaluation finished in {elapsed:.2f}s.\n")
    print("-" * 75)
    print(f"{'GAME ID':<10} | {'LEVELS CLEARED':<15} | {'ACTIONS':<10} | {'STATE':<20} | {'ENV SCORE':<10}")
    print("-" * 75)

    env_score_map = {}
    for es_list in scorecard.environments:
        gid = es_list.id.split("-")[0]
        if es_list.runs:
            env_score_map[gid] = es_list.runs[-1].score

    for gid in sorted(game_ids):
        res = results.get(gid, {})
        lvl = res.get("levels_completed", 0)
        acts = res.get("actions", 0)
        state = str(res.get("state", "UNKNOWN")).replace("GameState.", "")
        score = env_score_map.get(gid, 0.0)
        print(f"{gid:<10} | {lvl:<15} | {acts:<10} | {state:<20} | {score:>6.2f}%")

    aggregate_score = scorecard.score

    print("-" * 75)
    print(f"AGGREGATE LEADERBOARD SCORE (25 Games Average): {aggregate_score:.4f}%\n")
    print("=" * 70)
    print(f" PREDICTED KAGGLE SUBMISSION SCORE: {aggregate_score:.2f}%")
    print("=" * 70)

    return aggregate_score


if __name__ == "__main__":
    simulate_kaggle_eval()
