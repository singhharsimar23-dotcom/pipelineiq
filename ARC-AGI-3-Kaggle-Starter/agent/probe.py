from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import numpy as np
from .abstract_state import AbstractState, abstract_state, reset_extractor, Entity
from .aod_constants import PROBE_BUDGET


@dataclass
class Triple:
    state_before: AbstractState
    action: int
    state_after: AbstractState


@dataclass
class ProbeResult:
    avatar_id: Optional[int] = None
    step_size: Optional[int] = None
    push_entities: Set[int] = field(default_factory=set)
    wall_entities: Set[int] = field(default_factory=set)
    toggle_map: Dict[int, int] = field(default_factory=dict)  # entity_id -> k
    active_special_actions: Set[int] = field(default_factory=set)
    goal_ids: List[int] = field(default_factory=list)
    dead_signatures: Set[int] = field(default_factory=set)
    steps_used: int = 0


class ProbeStateMachine:
    def __init__(self, budget: int = PROBE_BUDGET):
        self.budget = budget
        self.result = ProbeResult()
        self.triples: List[Triple] = []
        self._done = False
        self._steps = 0

        # Internal state
        self._last_state: Optional[AbstractState] = None
        self._last_action: Optional[int] = None
        self._initialized = False

        # EXP0 state
        self._all_initial_entity_ids: List[int] = []

        # EXP1 state (directional probing)
        self._exp1_directions = [1, 2, 3, 4]  # ACTION1-4
        self._exp1_idx = 0
        self._exp1_done = False

        # EXP2 state (interactive entity probing)
        self._exp2_entities: List[int] = []
        self._exp2_idx = 0
        self._exp2_done = False

        # EXP3 state (toggle detection)
        self._exp3_candidates: List[int] = []
        self._exp3_idx = 0
        self._exp3_press_count = 0
        self._exp3_state0_hash: Optional[int] = None
        self._exp3_first_hash: Optional[int] = None
        self._exp3_current_eid: Optional[int] = None
        self._exp3_done = False

        # EXP4 state (special actions)
        self._exp4_actions = [5, 6, 7]
        self._exp4_idx = 0
        self._exp4_done = False

    def is_done(self) -> bool:
        return self._done

    def process_observation(self, state: AbstractState):
        if not self._initialized:
            self._all_initial_entity_ids = list(state.entities.keys())
            self._initialized = True
            self._last_state = state
            return

        if self._last_action is not None and self._last_state is not None:
            triple = Triple(self._last_state, self._last_action, state)
            self.triples.append(triple)
            self._process_triple(triple)
            self._last_state = state

    def _process_triple(self, triple: Triple):
        s0, action, s1 = triple.state_before, triple.action, triple.state_after

        # EXP1: Avatar detection from position changes
        if not self._exp1_done and action in [1, 2, 3, 4]:
            for eid in s0.entities:
                if eid not in s1.entities:
                    continue
                p0 = s0.entities[eid].position
                p1 = s1.entities[eid].position
                disp = max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))
                if disp > 0:
                    self.result.avatar_id = eid
                    self.result.step_size = disp
                    try:
                        from .abstract_state import _extractor
                        _extractor.mark_avatar(eid)
                    except Exception:
                        pass
                    break

        # EXP2: Entity classification
        if self._exp1_done and not self._exp2_done and action in [1, 2, 3, 4]:
            if self.result.avatar_id is not None:
                av = self.result.avatar_id
                avatar_moved = (
                    av in s0.entities
                    and av in s1.entities
                    and s0.entities[av].position != s1.entities[av].position
                )
                for eid in self._exp2_entities:
                    if eid == av:
                        continue
                    if eid in s0.entities and eid in s1.entities:
                        if s0.entities[eid].position != s1.entities[eid].position:
                            self.result.push_entities.add(eid)
                        elif not avatar_moved:
                            self.result.wall_entities.add(eid)

        # EXP3 & EXP4: Toggle detection and special action tracking
        if action in [5, 6, 7]:
            if s1.state_hash != s0.state_hash:
                self.result.active_special_actions.add(action)
                # Check for color/state toggle on entities
                for eid in s0.entities:
                    if eid in s1.entities and s0.entities[eid].color != s1.entities[eid].color:
                        self.result.toggle_map[eid] = 2

    def get_next_action(self, state: AbstractState) -> Optional[int]:
        if self._done or self._steps >= self.budget:
            self._finalize(state)
            return None

        # EXP1: find avatar
        if not self._exp1_done:
            if self._exp1_idx >= len(self._exp1_directions):
                self._exp1_done = True
                self._exp2_entities = [eid for eid in state.entities if eid != self.result.avatar_id]
            else:
                action = self._exp1_directions[self._exp1_idx]
                self._exp1_idx += 1
                self._last_action = action
                self._steps += 1
                return action

        # EXP2: classify entities
        if self._exp1_done and not self._exp2_done:
            if self._exp2_idx >= min(3, len(self._exp2_entities)) or self._steps >= self.budget - 4:
                self._exp2_done = True
                self._exp3_candidates = list(self.result.wall_entities)[:3]
            else:
                eid = self._exp2_entities[self._exp2_idx]
                self._exp2_idx += 1
                entity = state.entities.get(eid)
                avatar = state.entities.get(self.result.avatar_id) if self.result.avatar_id else None
                if entity and avatar:
                    dx = entity.position[0] - avatar.position[0]
                    dy = entity.position[1] - avatar.position[1]
                    action = (4 if dx > 0 else 3) if abs(dx) > abs(dy) else (2 if dy > 0 else 1)
                    self._last_action = action
                    self._steps += 1
                    return action
                else:
                    return self.get_next_action(state)

        # EXP3 / EXP4: special action vocabulary
        if not self._exp4_done:
            if self._exp4_idx >= len(self._exp4_actions) or self._steps >= self.budget:
                self._exp4_done = True
            else:
                action = self._exp4_actions[self._exp4_idx]
                self._exp4_idx += 1
                self._last_action = action
                self._steps += 1
                return action

        self._finalize(state)
        return None

    def _finalize(self, state: Optional[AbstractState] = None):
        if self._done:
            return
        self._done = True
        self.result.steps_used = self._steps

        classified = set()
        if self.result.avatar_id:
            classified.add(self.result.avatar_id)
        classified |= self.result.push_entities
        classified |= self.result.wall_entities

        # Goals = entities present on frame 0, not classified as avatar/push/wall
        self.result.goal_ids = [
            eid for eid in self._all_initial_entity_ids if eid not in classified
        ][:5]
        if not self.result.goal_ids and self._all_initial_entity_ids:
            self.result.goal_ids = self._all_initial_entity_ids[:3]


def probe_and_collect(env, budget: int = None) -> Tuple[List[Triple], ProbeResult]:
    """TEST-ONLY wrapper around ProbeStateMachine."""
    if budget is None:
        budget = PROBE_BUDGET
    sm = ProbeStateMachine(budget=budget)
    fd0 = env.reset()
    f0 = np.array(fd0.frame[0]) if hasattr(fd0, "frame") and fd0.frame else np.zeros((64, 64), dtype=int)
    reset_extractor()
    state = abstract_state(f0)
    sm.process_observation(state)
    frame_prev = f0
    while not sm.is_done():
        action = sm.get_next_action(state)
        if action is None:
            break
        from arcengine import GameAction
        data = {}
        if action == 6:
            data = {"x": 32, "y": 32}
        game_act = GameAction.from_id(action)
        fd_new = env.step(game_act, data=data)
        new_frame = np.array(fd_new.frame[0]) if hasattr(fd_new, "frame") and fd_new.frame else frame_prev
        new_state = abstract_state(new_frame, frame_prev)
        sm.process_observation(new_state)
        state = new_state
        frame_prev = new_frame
        if getattr(fd_new, "state", None) in ["WIN", "GAME_OVER"]:
            break
    sm._finalize(state)
    return sm.triples, sm.result
