import numpy as np
import copy
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable, Any
from .abstract_state import AbstractState, Entity
from .game_dsl import GAME_DSL, Primitive


@dataclass
class PrimitiveApplication:
    primitive: Primitive
    params: Dict[str, Any]  # e.g. {'entity_id': 3, 'dx': 2, 'dy': 0}


class GameProgram:
    def __init__(self, primitives: List[PrimitiveApplication], action_bindings: Dict[int, int]):
        self.primitives = primitives
        self.action_bindings = action_bindings
        self.active_special_actions: set = set()

    def simulate(self, state: AbstractState, action: int) -> AbstractState:
        new_entities = {eid: copy.deepcopy(e) for eid, e in state.entities.items()}
        primitive_indices = self.action_bindings.get(action, [])
        if isinstance(primitive_indices, int):
            primitive_indices = [primitive_indices]
        for idx in primitive_indices:
            if idx >= len(self.primitives):
                continue
            new_entities = self._apply_primitive(self.primitives[idx], new_entities, action)
        h = hash(tuple((i, e.position, e.color) for i, e in sorted(new_entities.items())))
        return AbstractState(
            entities=new_entities,
            avatar_id=state.avatar_id,
            goal_ids=state.goal_ids,
            state_hash=h
        )

    def _apply_primitive(self, pa: PrimitiveApplication, entities: Dict, action: int) -> Dict:
        name = pa.primitive.name
        p = pa.params
        if name == "move":
            eid = p["entity_id"]
            dx, dy = p.get("dx", 0), p.get("dy", 0)
            step = p.get("step_size", 1)
            if eid in entities:
                old_x, old_y = entities[eid].position
                new_x = max(0, min(63, old_x + dx * step))
                new_y = max(0, min(63, old_y + dy * step))
                entities[eid].prev_position = entities[eid].position
                entities[eid].position = (new_x, new_y)
                w = entities[eid].bbox[2] - entities[eid].bbox[0]
                h_b = entities[eid].bbox[3] - entities[eid].bbox[1]
                entities[eid].bbox = (new_x - w // 2, new_y - h_b // 2, new_x + w // 2, new_y + h_b // 2)
        elif name in ["toggle_interaction", "toggle_display"]:
            eid = p["entity_id"]
            k = p.get("k", 2)
            if eid in entities:
                entities[eid].color = (entities[eid].color + 1) % k
        elif name == "set_position":
            eid = p["entity_id"]
            if eid in entities:
                entities[eid].position = (p["x"], p["y"])
        elif name == "rotate":
            eid = p["entity_id"]
            degrees = p.get("degrees", 90)
            if eid in entities:
                entities[eid].color = (entities[eid].color + degrees // 90) % 4
        elif name == "scale":
            eid = p["entity_id"]
            factor = p.get("factor", 2)
            if eid in entities:
                entities[eid].area = int(entities[eid].area * factor)
        return entities

    def codelength(self) -> float:
        total = 0.0
        for pa in self.primitives:
            total += pa.primitive.cost
            for k, v in pa.params.items():
                if k in ["dx", "dy", "x", "y"]:
                    total += np.log2(64)
                elif k == "k":
                    total += np.log2(8)
                elif k == "step_size":
                    total += np.log2(8)
                elif k == "entity_id":
                    total += np.log2(max(8, len(pa.params)))
        return total

    def residual(self, state: AbstractState, action: int, observed_next: AbstractState) -> float:
        predicted = self.simulate(state, action)
        if predicted.state_hash == observed_next.state_hash:
            return 0.0
        total = 0.0
        # Measure error on entities governed by the program
        target_eids = set(pa.params.get("entity_id") for pa in self.primitives if "entity_id" in pa.params)
        if not target_eids:
            target_eids = set(observed_next.entities.keys())
        for eid in target_eids:
            if eid in observed_next.entities and eid in predicted.entities:
                obs_pos = observed_next.entities[eid].position
                pred_pos = predicted.entities[eid].position
                obs_col = observed_next.entities[eid].color
                pred_col = predicted.entities[eid].color
                total += abs(obs_pos[0] - pred_pos[0]) + abs(obs_pos[1] - pred_pos[1]) + (10.0 if obs_col != pred_col else 0.0)
            elif eid in observed_next.entities or eid in predicted.entities:
                total += 32.0
        return total
