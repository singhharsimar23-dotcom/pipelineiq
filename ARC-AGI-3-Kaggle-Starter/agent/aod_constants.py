"""
ARC-AGI-3-Kaggle-Starter/agent/aod_constants.py
Global constants for AoD program induction, probe budget, and engine metrics.
"""

# RHAE scoring in arc_agi/scorecard.py is capped at 115.0 per level and weighted sum is capped at max_score <= 100.0
RHAE_IS_CAPPED: bool = True
PROBE_BUDGET: int = 10
DSL_OPERATION_COUNT: int = 8
P0_COMPLETE: bool = True
HUMAN_BASELINE_STEPS: int = 10


def compute_rhae(human_steps: float, agent_steps: int) -> float:
    if agent_steps == 0:
        return 0.0
    rhae = (human_steps / agent_steps) ** 2
    if RHAE_IS_CAPPED:
        return min(1.0, rhae)
    return rhae
