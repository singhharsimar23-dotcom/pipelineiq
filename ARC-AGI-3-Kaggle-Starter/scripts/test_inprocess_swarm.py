import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'vendor' / 'ARC-AGI-3-Agents'))

import arc_agi
from arc_agi import OperationMode
from agent.my_agent import MyAgent

arc = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
envs = arc.get_environments()
game_ids = [e.game_id.split('-')[0] for e in envs]

agents = []
threads = []
results = {}

for gid in game_ids:
    env = arc.make(gid)
    agent = MyAgent(card_id='inprocess-swarm', game_id=gid, agent_name=f'MyAgent.{gid}', ROOT_URL='http://localhost', record=False, arc_env=env)
    agents.append((gid, agent))

def run_agent_in_thread(gid, agent):
    agent.main()
    final = agent.frames[-1]
    results[gid] = (final.state, final.levels_completed, agent.action_counter)

for gid, agent in agents:
    t = threading.Thread(target=run_agent_in_thread, args=(gid, agent))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

print("\n=== IN-PROCESS SWARM CONCURRENT RUN SUMMARY ===")
for gid in game_ids:
    state, levels, actions = results[gid]
    print(f"  {gid:6} -> levels={levels:2}  actions={actions:3}  state={state}")

sc = arc.get_scorecard()
print(f"\nIn-Process Swarm Scorecard Score: {sc.score:.4f}%")
