from typing import List, Optional, Any
import numpy as np
from .abstract_state import AbstractState, abstract_state, reset_extractor
from .probe import ProbeStateMachine, ProbeResult, Triple
from .program_induction import induce_program
from .game_program import GameProgram
from .planner import plan_against_program, goal_predicate
from .aod_constants import PROBE_BUDGET


class UniversalAgent:
    """
    BUG-FIX-1: choose_action() is a proper step-by-step state machine.
    The probe runs one action per choose_action() call via ProbeStateMachine.
    Induction and BFS run synchronously (no env.step()) when probe completes.
    """

    def __init__(self):
        self._probe_sm: Optional[ProbeStateMachine] = None
        self._probe_complete: bool = False
        self.program: Optional[GameProgram] = None
        self.plan: List[int] = []
        self.probe_result: Optional[ProbeResult] = None
        self.frame_prev: Optional[np.ndarray] = None
        self.level_count: int = 0
        self.induction_failed: bool = False
        self.steps_this_level: int = 0
        self._first_frame_processed: bool = False

    def reset(self, initial_frame=None):
        """Call at the start of each new game."""
        reset_extractor()
        self._probe_sm = ProbeStateMachine(budget=PROBE_BUDGET)
        self._probe_complete = False
        self.program = None
        self.plan = []
        self.probe_result = None
        self.frame_prev = None
        self.level_count = 0
        self.induction_failed = False
        self.steps_this_level = 0
        self._first_frame_processed = False

        if initial_frame is not None:
            frame = self._extract_frame(initial_frame)
            state = abstract_state(frame)
            self._probe_sm.process_observation(state)
            self._first_frame_processed = True
            self.frame_prev = frame

    def choose_action(self, obs) -> int:
        """
        Main entry point. Called once per environment step.
        Returns one action ID.
        """
        frame = self._extract_frame(obs)
        current_state = abstract_state(frame, self.frame_prev)

        # ── PHASE 1: PROBE — step-by-step state machine ──
        if not self._probe_complete and not self.induction_failed:
            if not self._first_frame_processed:
                self._probe_sm.process_observation(current_state)
                self._first_frame_processed = True
            else:
                self._probe_sm.process_observation(current_state)

            next_action = self._probe_sm.get_next_action(current_state)

            if next_action is None or self._probe_sm.is_done():
                self._probe_complete = True
                self.probe_result = self._probe_sm.result
                self._run_induction_and_plan(frame, current_state)
                self.frame_prev = frame
                if self.plan:
                    return self.plan.pop(0)
                return 1

            self.frame_prev = frame
            return next_action

        # ── PHASE 2: FALLBACK ──
        if self.induction_failed:
            self.frame_prev = frame
            return 1

        # ── PHASE 3: EXECUTE PLAN ──
        return self._execute_or_replan(frame, current_state)

    def _run_induction_and_plan(self, frame: np.ndarray, current_state: AbstractState):
        try:
            print("UNIVERSAL_AGENT: Running program induction...")
            self.program = induce_program(self._probe_sm.triples, self.probe_result)

            if self.program is None:
                print("UNIVERSAL_AGENT: Induction failed. Activating fallback.")
                self.induction_failed = True
            else:
                print(f"UNIVERSAL_AGENT: Program found. Primitives: {[pa.primitive.name for pa in self.program.primitives]}")
                self._replan(frame, current_state)
        except Exception as ex:
            print(f"UNIVERSAL_AGENT: Induction error: {ex}. Using fallback.")
            self.induction_failed = True

    def _execute_or_replan(self, frame: np.ndarray, current_state: AbstractState) -> int:
        if self.plan:
            action = self.plan.pop(0)
            self.steps_this_level += 1
            self.frame_prev = frame
            return action

        self._replan(frame, current_state)
        self.frame_prev = frame

        if self.plan:
            action = self.plan.pop(0)
            self.steps_this_level += 1
            return action

        return 1

    def _replan(self, frame: np.ndarray, current_state: Optional[AbstractState] = None):
        if self.program is None:
            return
        if current_state is None:
            current_state = abstract_state(frame, self.frame_prev)
        if self.probe_result and self.probe_result.goal_ids:
            current_state.goal_ids = self.probe_result.goal_ids
        self.plan = plan_against_program(self.program, current_state, goal_predicate)
        self.level_count += 1
        self.steps_this_level = 0
        print(f"UNIVERSAL_AGENT: Planned level {self.level_count}. Plan length: {len(self.plan)}")

    def on_level_up(self, new_frame: np.ndarray):
        from .abstract_state import _extractor
        new_state = _extractor.reset_for_new_level(new_frame)
        self.plan = []
        self._replan(new_frame, new_state)
        self.frame_prev = new_frame
        print(f"UNIVERSAL_AGENT: LEVEL_UP. Re-planned level {self.level_count}.")

    def _extract_frame(self, obs) -> np.ndarray:
        if isinstance(obs, np.ndarray):
            return obs
        if isinstance(obs, dict):
            return np.array(obs.get("frame", obs.get("image", np.zeros((64, 64)))))
        if hasattr(obs, "frame") and obs.frame:
            f = obs.frame[0] if isinstance(obs.frame, list) else obs.frame
            return np.array(f)
        return np.array(obs)
