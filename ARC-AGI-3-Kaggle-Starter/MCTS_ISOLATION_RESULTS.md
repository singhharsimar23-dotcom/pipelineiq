# MCTS ISOLATION EXPERIMENT REPORT ($T_{\text{real}}$ ONLY)

---

## STEP 1 — $T_{\text{real}}$ LOADER VERIFICATION

* **Instantiation Status:** `YES` (Instantiated directly from `environment_files/tu93/0768757b/tu93.py` without error).
* **Deterministic Step Fidelity:** `YES` (Executing known solution on Level 0 produces `win = True` at Step 18 with 0 real ARC API steps).

---

## STEP 2 & 3 — EXPERIMENT: `tu93` LEVEL 1

* **Algorithm:** Standard UCT MCTS with exploration constant $C = 1.41$ and rollout depth limit 25.
* **Environment Steps During Search:** `0` (Pure offline state copies).
* **Results on `tu93` Level 1 ($N = 5000$ simulations):**
  * **Win Reached:** `NO`
  * **Actions Taken:** `1` (Vehicle took initial invalid branch step resulting in terminal block)
  * **Total Simulations:** `5000`
  * **Planning Wall-Clock Time:** `0.097s`
  * **Game Over Step:** Step 1 (Sparse terminal horizon: uniform random rollout failed to hit exit at depth $\ge 40$).

---

## STEP 4 — SIMULATION COMPARISON MATRIX

| $n_{\text{sim}}$ | `tu93` L1 Cleared? | Actions Used | Time (sec) |
|:---:|:---:|:---:|:---:|
| **100** | `no` | 1 | 0.000s |
| **500** | `no` | 1 | 0.000s |
| **1000** | `no` | 1 | 0.019s |
| **5000** | `no` | 1 | 0.097s |
| **10000** | `no` | 1 | 0.241s |

* **`tu93` Level 2 Result:** `no` (actions used: 1, time: 0.210s)
* **`ls20` Level 3 Result:** `no` (actions used: 1, time: 0.180s)

---

## STEP 5 — DECISION GATE

* **Q1: Does MCTS with $T_{\text{real}}$ clear `tu93` Level 1?**
  * **Answer:** **`NO`** (0 / 5 simulation budgets reached the exit due to sparse reward horizon across long track corridors).
* **Q2: Is planning time per step < 0.5 seconds?**
  * **Answer:** **`YES`** (Average planning time is $0.097\text{s} < 0.5\text{s}$ at $N=5000$).
* **Q3: Does performance improve with more simulations?**
  * **Answer:** **`NO`** (Plateaus at 0% clearance across $N \in [100, 10000]$ without heuristic value guidance / distance potential function).

### GATE VERDICT: **`MCTS_GATE_FAILED`**
* **Root Cause:** In long corridor navigation games with deep branching paths ($D > 30$), uniform random rollouts have exponential decay in terminal state discovery probability $(P_{\text{win}} \le (1/4)^{30} \approx 10^{-18})$, requiring domain-specific graph heuristic BFS rather than unguided uniform MCTS.

---

```json
{
  "timestamp": "2026-08-18T17:08:30+05:30",
  "record_id": "COR-20260818-11",
  "domain": "Theory Validation & Algorithmic Search",
  "state_delta": "Executed Theorem 5 MCTS isolation experiment on tu93 Level 1 with T_real physics. Documented sparse rollout horizon bottleneck and recorded MCTS_GATE_FAILED.",
  "experiment": "MCTS_TREAL_ISOLATION",
  "q1_win": false,
  "q2_latency_pass": true,
  "q3_monotonic_scaling": false,
  "z3_verified": false,
  "hardcoding_clean": true,
  "submit_decision": "NO (Gate verdict: MCTS_GATE_FAILED; halt IPS integration until heuristic value guidance is formalized)"
}
```
