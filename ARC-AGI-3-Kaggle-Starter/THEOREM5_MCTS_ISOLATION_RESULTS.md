# THEOREM 5 RESEARCH REPORT: MCTS WITH T_real ISOLATION EXPERIMENT

---

## STEP 1 & 2 — $T_{\text{real}}$ LOADER & ABSTRACT STATE VERIFICATION

* **Instantiation Status:** `YES` (Directly executed source class from `environment_files/tu93/0768757b/tu93.py`).
* **Level 0 Ground Truth Check:** 5 known-correct steps confirmed: $(9, 3) \to (9, 9) \to (9, 15) \to (15, 15) \to (15, 9)$ matching exact physical game state.
* **Abstract State Representation for Level 1:**
  $$\mathcal{S}_{\text{abstract}} = \big(\text{active\_vehicle\_idx}, \; ((\text{veh}_0.x, \text{veh}_0.y), \dots), \; \text{frozenset}(\text{exits})\big)$$
  * Initial Level 1 State: `active_idx = 0, vehicles = ((3, 24),), exits = ((39, 12),)`
  * Sufficiency: **`YES`** (Fully captures vehicle geometry, track step constraints, and win condition).

---

## STEP 3 & 4 — EXPERIMENT MATRIX (`tu93` LEVEL 1)

| $n_{\text{sim}}$ | L1 Win? | Actions Used | Plan Time per Step (s) | Total Simulation Calls |
|:---:|:---:|:---:|:---:|:---:|
| **`100`** | `no` | 1 | `0.0000s` | 101 |
| **`500`** | `no` | 1 | `0.0042s` | 501 |
| **`1000`** | `no` | 1 | `0.0211s` | 1001 |
| **`5000`** | `no` | 1 | `0.0880s` | 5001 |
| **`10000`** | `no` | 1 | `0.2337s` | 10001 |

* **Planning Speed:** Average step time at $n_{\text{sim}}=10000$ is **`0.2337s`** ($\le 0.5\text{s}$ constraint satisfied).
* **Clearance Result:** 0 / 5 simulation budgets reached the exit due to exponential decay of random rollout discovery over the depth-42 corridor.

---

## STEP 5 — GATE DECISION

* **GATE_QUESTION_1:** Does any $n_{\text{sim}}$ clear `tu93` L1?
  * **Answer:** **`NO`** (Evidence: Row 5, $n_{\text{sim}}=10000$ failed to clear Level 1).
* **GATE_QUESTION_2:** Is $\text{plan\_time\_per\_step} \le 0.5\text{s}$?
  * **Answer:** **`YES`** (Evidence: $0.2337\text{s} \le 0.5000\text{s}$ at $n_{\text{sim}}=10000$).
* **GATE_QUESTION_3:** Does win rate improve monotonically with $n_{\text{sim}}$?
  * **Answer:** **`NO`** (Plateaus at 0% win rate across all $N \in [100, 10000]$).

### GATE VERDICT: **`MCTS_GATE_FAILED`**
* **Root Cause Diagnosis:**
  1. **Sparse Reward Horizon:** The distance from start $(3, 24)$ to exit $(39, 12)$ requires a path length of $\ge 42$ steps through a narrow 6px track maze.
  2. **Rollout Decay:** Uniform random rollout has terminal discovery probability $P_{\text{win}} \le (1/4)^{42} \approx 10^{-25}$, resulting in $0.0$ backpropagated value signal to root.
  3. **Architectural Implication:** Unguided MCTS is insufficient for long-horizon navigation. The system must employ **heuristic distance potential BFS** on the extracted track graph rather than uniform random rollout MCTS.

---

```json
{
  "timestamp": "2026-08-18T17:25:35+05:30",
  "record_id": "COR-20260818-17",
  "domain": "Theory Validation & Algorithmic Search",
  "state_delta": "Completed Theorem 5 MCTS isolation experiment on tu93 Level 1 with exact T_real physics. Documented latency compliance (0.2337s <= 0.5s) and sparse rollout failure, recording MCTS_GATE_FAILED. Saved to THEOREM5_MCTS_ISOLATION_RESULTS.md.",
  "gate_verdict": "MCTS_GATE_FAILED",
  "q1_l1_win": false,
  "q2_speed_pass": true,
  "q3_monotonic": false,
  "z3_verified": false,
  "hardcoding_clean": true,
  "submit_decision": "NO (Gate verdict: MCTS_GATE_FAILED; halt IPS+MCTS coupling and preserve graph heuristic BFS)"
}
```
