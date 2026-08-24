import os
import sys
from pathlib import Path

ROOT = Path("c:/Users/hprad/OneDrive/Desktop/pipelineiq/ARC-AGI-3-Kaggle-Starter")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor" / "ARC-AGI-3-Agents"))

import arc_agi
from arc_agi import OperationMode
import importlib.util

def run_eval():
    spec = importlib.util.spec_from_file_location("user_agent_module", ROOT / "agent" / "my_agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    MyAgentCls = module.MyAgent

    arc = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    all_envs = {e.game_id.split("-")[0]: e for e in arc.get_environments()}
    games = ["ft09", "tu93", "tn36", "vc33"]
    
    total_wins = 0
    total_levels = 0
    per_game_counts = {}

    for gid in games:
        env_info = all_envs.get(gid)
        num_levels = getattr(env_info, "num_levels", 6)
        if hasattr(env_info, "levels") and env_info.levels:
            num_levels = len(env_info.levels)

        env = arc.make(gid)
        if env is None:
            print(f"Error loading {gid}")
            continue

        agent = MyAgentCls(
            card_id="local-dev",
            game_id=gid,
            agent_name=f"MyAgent.{gid}",
            ROOT_URL="http://localhost",
            record=False,
            arc_env=env,
        )
        if hasattr(agent, "MAX_ACTIONS"):
            agent.MAX_ACTIONS = 600

        # Step-by-step level tracking
        steps_per_level = {}
        curr_lvl = 0
        lvl_start_step = 0

        agent.timer = 0
        while (
            not agent.is_done(agent.frames, agent.frames[-1])
            and agent.action_counter <= agent.MAX_ACTIONS
        ):
            action = agent.choose_action(
                agent.frames,
                agent._convert_raw_frame_data(
                    agent.arc_env.observation_space if agent.arc_env else None
                ),
            )
            frame = agent.take_action(action)
            if frame:
                agent.append_frame(frame)
                if frame.levels_completed != curr_lvl:
                    steps_per_level[curr_lvl] = (True, agent.action_counter - lvl_start_step + 1)
                    curr_lvl = frame.levels_completed
                    lvl_start_step = agent.action_counter + 1
            agent.action_counter += 1

        agent.cleanup()
        final_lvl = agent.frames[-1].levels_completed
        if curr_lvl not in steps_per_level:
            steps_per_level[curr_lvl] = (final_lvl > curr_lvl, agent.action_counter - lvl_start_step)

        # Print per level
        for l in range(num_levels):
            if l < final_lvl:
                st = steps_per_level.get(l, (True, 0))[1]
                print(f"{gid} L{l}: win=True  steps={st}")
            else:
                st = steps_per_level.get(l, (False, agent.action_counter))[1]
                print(f"{gid} L{l}: win=False steps={st}")

        per_game_counts[gid] = (final_lvl, num_levels)
        total_wins += final_lvl
        total_levels += num_levels

    print("--- SCORECARD ---")
    for gid in games:
        wins, tot = per_game_counts.get(gid, (0, 0))
        print(f"{gid}: {wins}/{tot}")
    pct = (total_wins / total_levels * 100) if total_levels > 0 else 0
    print(f"TOTAL: {total_wins}/{total_levels} = {pct:.2f}%")

if __name__ == "__main__":
    run_eval()
