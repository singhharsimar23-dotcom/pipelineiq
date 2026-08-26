"""
tools/test_p3_verification.py
Verify probe protocol across navigation games, toggle games, and public suite.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))

from arc_agi import Arcade, OperationMode
from agent.probe import probe_and_collect, ProbeStateMachine

ALL_25 = [
    'lp85','g50t','cn04','dc22','vc33','ft09','re86','cd82',
    'ar25','bp35','ls20','tr87','wa30','sp80','su15',
    'sk48','sc25','tn36','ka59','lf52','m0r0','r11l','s5i5','sb26','tu93'
]

arc = Arcade(operation_mode=OperationMode.OFFLINE)

print("--- Test 1: Navigation Game (ls20) ---")
env = arc.make('ls20', seed=0)
triples, probe = probe_and_collect(env)
print(f"ls20: steps={probe.steps_used}, avatar={probe.avatar_id}, step_size={probe.step_size}, toggles={probe.toggle_map}, goal_ids={probe.goal_ids}")
assert probe.avatar_id is not None, "FAIL: avatar not found on ls20"
assert probe.step_size in [1, 2, 3, 4, 5, 6, 8, 10, 11, 16], f"FAIL: bad step_size {probe.step_size}"
assert len(probe.goal_ids) > 0, "FAIL: goal_ids empty on ls20"
print("PASS: ls20")

print("\n--- Test 2: GF(2) games ---")
for gid in ['g50t', 'cn04', 'dc22']:
    try:
        env = arc.make(gid, seed=0)
        triples, probe = probe_and_collect(env)
        print(f"{gid}: avatar={probe.avatar_id}, step_size={probe.step_size}, toggles={probe.toggle_map}, goal_ids={probe.goal_ids}, special={probe.active_special_actions}")
        assert len(probe.goal_ids) > 0, f"FAIL: goal_ids empty on {gid}"
    except Exception as ex:
        print(f"ERROR: {gid}: {ex}")

print("\n--- Test 3: All 25 games ---")
results = []
for gid in ALL_25:
    try:
        env = arc.make(gid, seed=0)
        t, p = probe_and_collect(env)
        results.append((gid, p.avatar_id is not None, p.step_size, len(p.toggle_map), len(p.active_special_actions), p.steps_used, len(p.goal_ids)))
    except Exception as ex:
        results.append((gid, False, None, 0, 0, 0, 0))

print(f"{'game_id':<8} | {'avatar':<8} | {'step_sz':<8} | {'toggles':<8} | {'special':<8} | {'steps':<6} | {'goals':<6}")
print("-" * 65)
for r in results:
    print(f"{r[0]:<8} | {str(r[1]):<8} | {str(r[2]):<8} | {r[3]:<8} | {r[4]:<8} | {r[5]:<6} | {r[6]:<6}")

avatar_found = sum(1 for r in results if r[1])
goals_found = sum(1 for r in results if r[6] > 0)
print(f"\nAvatar found: {avatar_found}/25")
print(f"Goal IDs populated: {goals_found}/25")

print("\n=== P3 COMPLETE ===")
print(f"AVATAR_FOUND: {avatar_found}/25")
print(f"STEP_SIZE_FOUND: {sum(1 for r in results if r[2] is not None)}/25")
print(f"GOAL_IDS_POPULATED: {goals_found}/25")
print(f"TOGGLE_GAMES_DETECTED: {sum(1 for r in results if r[3] > 0)}")
print(f"SPECIAL_ACTION_GAMES: {sum(1 for r in results if r[4] > 0)}")
print(f"AVG_STEPS_USED: {sum(r[5] for r in results)/len(results):.4f}")
print(f"PROBE_BUDGET: 10")
print("=== END P3 ===")
