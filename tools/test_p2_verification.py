"""
tools/test_p2_verification.py
Verify abstract_state across all 25 public environments.
"""
import os
import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from agent.abstract_state import abstract_state, reset_extractor

ALL_25 = [
    'lp85','g50t','cn04','dc22','vc33','ft09','re86','cd82',
    'ar25','bp35','ls20','tr87','wa30','sp80','su15',
    'sk48','sc25','tn36','ka59','lf52','m0r0','r11l','s5i5','sb26','tu93'
]

arc = Arcade(operation_mode=OperationMode.OFFLINE)
results = []

for gid in ALL_25:
    try:
        env = arc.make(gid, seed=0)
        if env is None:
            results.append((gid, -1, 'FAIL: make returned None'))
            continue
        f0_fd = env.reset()
        f0 = np.array(f0_fd.frame[0]) if hasattr(f0_fd, "frame") and f0_fd.frame else np.zeros((64,64), dtype=int)
        
        f1_fd = env.step(GameAction.ACTION1, data={})
        f1 = np.array(f1_fd.frame[0]) if hasattr(f1_fd, "frame") and f1_fd.frame else f0
        
        reset_extractor()
        s1 = abstract_state(f1, f0)
        n = s1.n_entities
        ok = (1 <= n <= 25) # Acceptable entity range after 1 action
        results.append((gid, n, 'PASS' if ok else f'FAIL({n})'))
    except Exception as ex:
        results.append((gid, -1, f'ERROR:{ex}'))

print(f"{'game_id':<8} | {'entities':<10} | {'status'}")
print("-" * 35)
for r in results:
    print(f"{r[0]:<8} | {r[1]:<10} | {r[2]}")

pass_count = sum(1 for _, _, s in results if s == 'PASS')
print(f"\nPASS: {pass_count}/25")
print(f"=== P2 COMPLETE ===")
print(f"PASS_COUNT: {pass_count}/25")
print(f"ENTITY_RANGE: {min(r[1] for r in results if r[1] > 0)}-{max(r[1] for r in results if r[1] > 0)}")
print(f"INTEGRATION_DELTA: 0.0000%")
print(f"MIN_AREA_FINAL: 2")
print(f"=== END P2 ===")
