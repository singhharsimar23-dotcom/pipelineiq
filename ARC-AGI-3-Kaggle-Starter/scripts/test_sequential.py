import sys, os, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'vendor' / 'ARC-AGI-3-Agents'))

os.environ.setdefault('HOST', 'localhost')
os.environ.setdefault('PORT', '8001')
os.environ.setdefault('SCHEME', 'http')
os.environ.setdefault('ARC_API_KEY', 'test-key-123')

import arc_agi
from arc_agi import Arcade, OperationMode
from agent.my_agent import MyAgent

ROOT_URL = 'http://localhost:8001'
GAMES = ['ft09','vc33','tr87','tu93','ls20','lp85','m0r0',
         'ar25','sp80','cd82','sk48','dc22','lf52','s5i5',
         'sb26','sc25','tn36','wa30','bp35','cn04','g50t',
         'ka59','r11l','re86','su15']

arc = Arcade(operation_mode=OperationMode.NORMAL)
card_id = arc.open_scorecard(tags=['sequential-test'])

start = time.time()
for game_id in GAMES:
    env = arc.make(game_id, scorecard_id=card_id)
    agent = MyAgent(
        card_id=card_id,
        game_id=game_id,
        agent_name='myagent',
        ROOT_URL=ROOT_URL,
        record=False,
        arc_env=env,
        tags=[],
    )
    agent.main()
    print(f'{game_id}: done (levels={agent.last_levels_completed}, actions={agent.action_counter})', flush=True)

scorecard = arc.close_scorecard(card_id)
elapsed = time.time() - start
print(f'Total time: {elapsed:.1f}s')
print(f'Aggregate Score: {scorecard.score:.4f}%')
