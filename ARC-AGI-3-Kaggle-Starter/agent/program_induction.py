import numpy as np
from typing import List, Optional, Dict, Tuple
from .abstract_state import AbstractState
from .probe import Triple, ProbeResult
from .game_program import GameProgram, PrimitiveApplication
from .game_dsl import GAME_DSL


def codelength_null(triple: Triple) -> float:
    n_entities = triple.state_after.n_entities
    return max(10.0, n_entities * (2 * np.log2(64) + np.log2(16)))


def codelength_residual(residual: float) -> float:
    if residual == 0.0:
        return 0.0
    return float(np.log2(1.0 + residual))


def generate_candidates(probe_result: ProbeResult, all_entities: List[int], triples: Optional[List[Triple]] = None) -> List[GameProgram]:
    candidates = []
    dsl = GAME_DSL

    if probe_result.avatar_id is not None:
        eid = probe_result.avatar_id
        sz = probe_result.step_size or 1

        # Candidate set 1: Standard 4-way navigation
        pas = []
        bindings = {}
        for i, (action_id, (dx, dy)) in enumerate(
            {1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}.items()
        ):
            pas.append(
                PrimitiveApplication(
                    primitive=dsl["move"],
                    params={"entity_id": eid, "dx": dx, "dy": dy, "step_size": sz}
                )
            )
            bindings[action_id] = i
        candidates.append(GameProgram(primitives=pas, action_bindings=bindings))

        # Candidate set 2: Empirical action mappings directly extracted from probe transitions
        if triples:
            emp_pas = []
            emp_bindings = {}
            for t in triples:
                if eid in t.state_before.entities and eid in t.state_after.entities:
                    p0 = t.state_before.entities[eid].position
                    p1 = t.state_after.entities[eid].position
                    dx = p1[0] - p0[0]
                    dy = p1[1] - p0[1]
                    if t.action not in emp_bindings:
                        emp_pas.append(
                            PrimitiveApplication(
                                primitive=dsl["move"],
                                params={"entity_id": eid, "dx": dx, "dy": dy, "step_size": 1}
                            )
                        )
                        emp_bindings[t.action] = len(emp_pas) - 1
            if emp_pas:
                candidates.append(GameProgram(primitives=emp_pas, action_bindings=emp_bindings))

    # Toggle & interaction candidates
    for eid, k in probe_result.toggle_map.items():
        for action_n in probe_result.active_special_actions or [5, 6]:
            for prim_name in ["toggle_interaction", "toggle_display"]:
                if prim_name not in dsl:
                    continue
                pa = PrimitiveApplication(
                    primitive=dsl[prim_name],
                    params={"entity_id": eid, "k": k}
                )
                pas = [pa]
                bindings = {action_n: 0}

                if probe_result.avatar_id and probe_result.step_size:
                    sz = probe_result.step_size
                    av = probe_result.avatar_id
                    for i, (aid, (dx, dy)) in enumerate(
                        {1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}.items(),
                        start=1
                    ):
                        pas.append(
                            PrimitiveApplication(
                                primitive=dsl["move"],
                                params={"entity_id": av, "dx": dx, "dy": dy, "step_size": sz}
                            )
                        )
                        bindings[aid] = i
                candidates.append(GameProgram(primitives=pas, action_bindings=bindings))

    return candidates


def induce_program(triples: List[Triple], probe_result: ProbeResult) -> Optional[GameProgram]:
    if not triples:
        return None

    all_entities = list(
        set(
            eid
            for t in triples
            for eid in list(t.state_before.entities.keys()) + list(t.state_after.entities.keys())
        )
    )

    C_null = sum(codelength_null(t) for t in triples)
    candidates = generate_candidates(probe_result, all_entities, triples=triples)

    best_program = None
    best_delta = -np.inf

    for prog in candidates:
        residuals = [prog.residual(t.state_before, t.action, t.state_after) for t in triples]
        C_given_P = sum(codelength_residual(r) for r in residuals)
        len_P = prog.codelength()
        delta = C_null - C_given_P - len_P

        if delta >= 1.0 and delta > best_delta:
            best_delta = delta
            best_program = prog

    return best_program
