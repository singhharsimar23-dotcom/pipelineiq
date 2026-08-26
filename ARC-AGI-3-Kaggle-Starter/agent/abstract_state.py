import numpy as np
import scipy.ndimage
import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from scipy.optimize import linear_sum_assignment


@dataclass
class Entity:
    id: int
    position: Tuple[int, int]  # (x, y) centroid in pixels
    color: int  # dominant pixel value (0-15)
    area: int  # pixel count
    bbox: Tuple[int, int, int, int]  # xmin, ymin, xmax, ymax
    entity_type: str  # avatar|object|goal|wall|unknown
    prev_position: Optional[Tuple[int, int]] = None

    def clone(self) -> "Entity":
        return Entity(
            id=self.id,
            position=self.position,
            color=self.color,
            area=self.area,
            bbox=self.bbox,
            entity_type=self.entity_type,
            prev_position=self.prev_position
        )


@dataclass
class AbstractState:
    entities: Dict[int, Entity]
    avatar_id: Optional[int]
    goal_ids: List[int]
    state_hash: int
    n_entities: int = 0

    def __post_init__(self):
        self.n_entities = len(self.entities)


class AbstractStateExtractor:
    def __init__(self):
        self.known_avatar_id: Optional[int] = None
        self.known_goal_ids: List[int] = []
        self.entity_registry: Dict[int, Entity] = {}
        self.next_id: int = 1
        self.frame_0: Optional[np.ndarray] = None
        self._min_area: int = 2

    def extract(self, frame_t, frame_prev=None) -> AbstractState:
        frame_t = self._norm(frame_t)
        H, W = frame_t.shape
        if frame_prev is None or self.frame_0 is None:
            self.frame_0 = frame_t.copy()
            return self._from_full(frame_t, H, W)
        frame_prev = self._norm(frame_prev)
        return self._from_delta(frame_t, frame_prev, H, W)

    def _norm(self, f):
        if hasattr(f, "ndim") and f.ndim == 3:
            f = (f[:, :, 0] * 0.299 + f[:, :, 1] * 0.587 + f[:, :, 2] * 0.114).astype(int)
        elif not isinstance(f, np.ndarray):
            f = np.array(f, dtype=int)
            if f.ndim == 3:
                f = (f[:, :, 0] * 0.299 + f[:, :, 1] * 0.587 + f[:, :, 2] * 0.114).astype(int)
        return f.astype(int)

    def _from_delta(self, ft, fp, H, W):
        delta = (ft != fp)
        if delta.sum() == 0:
            return self._from_registry()
        if delta.sum() > 0.8 * H * W:
            return self._from_full(ft, H, W)
        struct = scipy.ndimage.generate_binary_structure(2, 2)
        labeled, n = scipy.ndimage.label(delta, structure=struct)
        new_ents = [e for i in range(1, n + 1) for e in [self._comp_to_entity((labeled == i), ft, i)] if e is not None]
        self._hungarian_update(new_ents, ft)
        return self._from_registry()

    def _from_full(self, f, H, W):
        bg = np.bincount(f.flatten()).argmax()
        fg = (f != bg)
        struct = scipy.ndimage.generate_binary_structure(2, 2)
        labeled, n = scipy.ndimage.label(fg, structure=struct)
        self.entity_registry.clear()
        self.next_id = 1
        for i in range(1, n + 1):
            e = self._comp_to_entity((labeled == i), f, i)
            if e:
                e.id = self.next_id
                self.entity_registry[e.id] = e
                self.next_id += 1
        return self._from_registry()

    def _comp_to_entity(self, mask, f, raw_id):
        area = mask.sum()
        if area < self._min_area:
            return None
        ys, xs = np.where(mask)
        pixels = f[mask].flatten()
        color = int(np.bincount(pixels, minlength=16).argmax())
        return Entity(
            id=raw_id,
            position=(int(xs.mean()), int(ys.mean())),
            color=color,
            area=int(area),
            bbox=(int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())),
            entity_type="unknown"
        )

    def _hungarian_update(self, new_ents, ft):
        if not self.entity_registry or not new_ents:
            self.entity_registry.clear()
            self.next_id = 1
            for e in new_ents:
                e.id = self.next_id
                self.entity_registry[e.id] = e
                self.next_id += 1
            return
        eids = list(self.entity_registry.keys())
        ep = np.array([self.entity_registry[i].position for i in eids], dtype=float)
        np_ = np.array([e.position for e in new_ents], dtype=float)
        n_e, n_n = len(eids), len(new_ents)
        sz = max(n_e, n_n)
        C = np.full((sz, sz), 1e9)
        for i, p in enumerate(ep):
            for j, q in enumerate(np_):
                C[i, j] = np.linalg.norm(p - q)
        ri, ci = linear_sum_assignment(C)
        for r, c in zip(ri, ci):
            if r < n_e and c < n_n:
                eid = eids[r]
                ne = new_ents[c]
                reg = self.entity_registry[eid]
                reg.prev_position = reg.position
                reg.position = ne.position
                reg.color = ne.color
                reg.area = ne.area
                reg.bbox = ne.bbox

    def _from_registry(self):
        h = hash(tuple((i, e.position, e.color) for i, e in sorted(self.entity_registry.items())))
        # Return deep copy of entities so AbstractState snapshots are immutable
        entities_copy = {i: e.clone() for i, e in self.entity_registry.items()}
        return AbstractState(
            entities=entities_copy,
            avatar_id=self.known_avatar_id,
            goal_ids=list(self.known_goal_ids),
            state_hash=h
        )

    def mark_avatar(self, eid):
        self.known_avatar_id = eid
        if eid in self.entity_registry:
            self.entity_registry[eid].entity_type = "avatar"

    def mark_goal(self, eid):
        if eid not in self.known_goal_ids:
            self.known_goal_ids.append(eid)
        if eid in self.entity_registry:
            self.entity_registry[eid].entity_type = "goal"

    def reset_for_new_level(self, new_frame):
        f = self._norm(new_frame)
        return self._from_full(f, *f.shape)


_extractor = AbstractStateExtractor()


def abstract_state(frame_t, frame_prev=None) -> AbstractState:
    return _extractor.extract(frame_t, frame_prev)


def reset_extractor():
    global _extractor
    _extractor = AbstractStateExtractor()
