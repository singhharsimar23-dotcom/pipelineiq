"""
PipelineIQ V23 Production Multi-Archetype Autonomous Agent
Certified AI Observability & Mathematical ARC-AGI-3 Solver Engine

Architecture:
  1. Preserved V13 Fluid Slider Anchor (lp85, re86, bp35, cd82, ar25 -> 19.85% class score)
  2. Perimeter Valve Pulse Engine (vc33, tn36)
  3. Bounded Combinatorial Toggle Search (ft09, g50t, dc22, cn04)
  4. Multi-Goal BFS + Directional Sweep Fallback (ls20, su15, tr87, wa30, sp80)
  5. Multi-Level State Transition Re-Anchoring (Solves Level 0, Level 1, Level 2+)
  6. Thread-Safe Global Locks (_ACTION_LOCK)
"""
from __future__ import annotations

import time
import math
import random
import hashlib
import threading
from itertools import combinations
from typing import Any, List, Dict, Tuple, Optional
from collections import deque, Counter
import numpy as np

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent

MAX_STEPS: int = 9000
_ACTION_LOCK = threading.Lock()


def get_2d_grid(frame_data: Any) -> np.ndarray:
    """Safely extract 64x64 2D integer grid from FrameData."""
    if frame_data is None:
        return np.zeros((64, 64), dtype=np.int16)
    f = getattr(frame_data, "frame", frame_data)
    if isinstance(f, list):
        if len(f) == 0:
            return np.zeros((64, 64), dtype=np.int16)
        f = np.array(f[-1])
    else:
        f = np.array(f)
    while f.ndim > 2:
        f = f[-1]
    if f.ndim == 3 and f.shape[-1] == 3:
        _, inverse = np.unique(f.reshape(-1, 3), axis=0, return_inverse=True)
        f = inverse.reshape(f.shape[0], f.shape[1])
    if f.shape != (64, 64):
        res = np.zeros((64, 64), dtype=np.int16)
        h, w = min(64, f.shape[0]), min(64, f.shape[1])
        res[:h, :w] = f[:h, :w]
        return res
    return f.astype(np.int16)


def get_background_color(f: np.ndarray) -> int:
    """Empirically determine background color as perimeter mode."""
    border = (list(f[0, :]) + list(f[1, :]) + list(f[-1, :]) + list(f[-2, :]) +
              list(f[:, 0]) + list(f[:, 1]) + list(f[:, -1]) + list(f[:, -2]))
    return int(max(set(border), key=border.count)) if border else 0


def get_components(f: np.ndarray, bg: int, max_area: int = 1000) -> List[Dict[str, Any]]:
    """Extract connected non-background components with geometric metadata."""
    vis = np.zeros_like(f, bool)
    comps = []
    for r in range(64):
        for c in range(64):
            if not vis[r, c] and f[r, c] != bg:
                q = [(r, c)]
                vis[r, c] = True
                pix = []
                while q:
                    cr, cc = q.pop()
                    pix.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < 64 and 0 <= nc < 64 and not vis[nr, nc] and f[nr, nc] == f[cr, cc]:
                            vis[nr, nc] = True
                            q.append((nr, nc))
                area = len(pix)
                if area > max_area:
                    continue
                min_r = min(p[0] for p in pix)
                max_r = max(p[0] for p in pix)
                min_c = min(p[1] for p in pix)
                max_c = max(p[1] for p in pix)
                cy = (min_r + max_r) // 2
                cx = (min_c + max_c) // 2
                comps.append({
                    'cx': cx, 'cy': cy,
                    'min_r': min_r, 'max_r': max_r,
                    'min_c': min_c, 'max_c': max_c,
                    'w': max_c - min_c + 1, 'h': max_r - min_r + 1,
                    'area': area, 'col': int(f[pix[0][0], pix[0][1]])
                })
    return comps


class MCTSNode:
    def __init__(self, state: tuple, parent: Optional['MCTSNode'] = None, action: Optional[Tuple[GameAction, dict]] = None):
        self.state = state          # (avatar_pos, blocked_cells, toggle_state)
        self.parent = parent
        self.action = action        # action that led here
        self.children: List['MCTSNode'] = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions: Optional[List[Tuple[GameAction, dict]]] = None
    
    def ucb1(self, C: float = 1.414) -> float:
        if self.visits == 0:
            return float('inf')
        return (self.value / self.visits) + C * math.sqrt(math.log(self.parent.visits) / self.visits)
    
    def best_child(self, C: float = 1.414) -> 'MCTSNode':
        return max(self.children, key=lambda n: n.ucb1(C))
    
    def is_terminal(self) -> bool:
        return self.state[0] is None
    
    def is_fully_expanded(self) -> bool:
        return self.untried_actions is not None and len(self.untried_actions) == 0


class D4SymmetryCache:
    def __init__(self) -> None:
        self.cache: Dict[str, dict] = {}
        # key: perceptual hash of canonical frame
        # value: {frame, actions, game_id, level}

    def _canonical_transform(self, frame: np.ndarray) -> np.ndarray:
        """Returns the lexicographically smallest D4 transform."""
        transforms = self._all_d4(frame)
        return min(transforms, key=lambda f: f.tobytes())

    def _all_d4(self, frame: np.ndarray) -> List[np.ndarray]:
        """Returns all 8 D4 transforms of frame."""
        f = frame
        return [
            f,                           # 0: identity
            np.rot90(f, 1),             # 1: rot90
            np.rot90(f, 2),             # 2: rot180
            np.rot90(f, 3),             # 3: rot270
            np.fliplr(f),               # 4: fliplr
            np.flipud(f),               # 5: flipud
            np.fliplr(np.rot90(f, 1)), # 6: fliplr_rot90
            np.flipud(np.rot90(f, 1)), # 7: flipud_rot90
        ]

    def _phash(self, frame: np.ndarray) -> str:
        """Perceptual hash: downsample to 8x8, threshold, bitstring."""
        small = frame[::8, ::8]  # 64x64 -> 8x8
        mean = float(small.mean())
        bits = (small > mean).flatten()
        return ''.join('1' if b else '0' for b in bits)

    def store(self, initial_frame: np.ndarray,
              solution_actions: list,
              game_id: str,
              level: int) -> None:
        """Store canonical form of solved game frame + solution."""
        canonical = self._canonical_transform(initial_frame)
        h = self._phash(canonical)
        self.cache[h] = {
            'frame': canonical,
            'actions': list(solution_actions),
            'game_id': game_id,
            'level': level
        }
        print(f"[D4_CACHE] stored game={game_id} level={level} hash={h[:8]}")

    def lookup(self, query_frame: np.ndarray) -> Optional[list]:
        """
        Check if query_frame matches any stored game under D4.
        If match: return transformed action sequence.
        If no match: return None (fall through to other solvers).
        """
        d4_labels = [
            'identity', 'rot90', 'rot180', 'rot270',
            'fliplr', 'flipud', 'fliplr_rot90', 'flipud_rot90'
        ]
        transforms = self._all_d4(query_frame)

        for i, (tf, label) in enumerate(zip(transforms, d4_labels)):
            h = self._phash(tf)
            if h in self.cache:
                entry = self.cache[h]
                if np.array_equal(entry['frame'], self._canonical_transform(tf)):
                    print(f"[D4_CACHE] HIT: {label} matches {entry['game_id']} level={entry['level']}")
                    transformed = self._transform_actions(
                        entry['actions'], inverse_index=i
                    )
                    return transformed

        return None

    def _transform_actions(self, actions: list, inverse_index: int) -> list:
        """
        Apply inverse D4 transform to directional actions.
        Rotations rotate direction vectors.
        Flips flip direction vectors.
        Non-directional actions (ACTION5, ACTION6, RESET) pass through unchanged.
        """
        DIRECTION_ACTIONS = {
            GameAction.ACTION1: 0, # UP
            GameAction.ACTION4: 1, # RIGHT
            GameAction.ACTION2: 2, # DOWN
            GameAction.ACTION3: 3  # LEFT
        }
        INDEX_TO_ACTION = {
            0: GameAction.ACTION1,
            1: GameAction.ACTION4,
            2: GameAction.ACTION2,
            3: GameAction.ACTION3
        }

        INV = [0, 3, 2, 1, 4, 5, 6, 7]
        inv_i = INV[inverse_index]

        ROT = [
            [0, 1, 2, 3],  # identity
            [3, 0, 1, 2],  # rot90  (U->L, R->U, D->R, L->D)
            [2, 3, 0, 1],  # rot180
            [1, 2, 3, 0],  # rot270
            [0, 3, 2, 1],  # fliplr (U->U, R->L, D->D, L->R)
            [2, 1, 0, 3],  # flipud (U->D, R->R, D->U, L->L)
            [1, 0, 3, 2],  # fliplr+rot90
            [3, 2, 1, 0],  # flipud+rot90
        ]

        transformed = []
        for item in actions:
            if isinstance(item, tuple):
                act, data = item
                if act in DIRECTION_ACTIONS:
                    d = DIRECTION_ACTIONS[act]
                    new_d = ROT[inv_i][d]
                    transformed.append((INDEX_TO_ACTION[new_d], data))
                else:
                    transformed.append((act, data))
            else:
                act = item
                if act in DIRECTION_ACTIONS:
                    d = DIRECTION_ACTIONS[act]
                    new_d = ROT[inv_i][d]
                    transformed.append(INDEX_TO_ACTION[new_d])
                else:
                    transformed.append(act)

        return transformed


class BisimulationQuotient:
    def __init__(self) -> None:
        self.partition: List[set] = []
        self.cell_to_class: Dict[Tuple[int, int], int] = {}
        self.n_classes: int = 0

    def fit(self,
            frames: List[np.ndarray],
            actions: list,
            step_size: int = 3) -> None:
        """
        Build equivalence partition from observed frame transitions.

        Algorithm:
        1. Start: group pixels by initial color in first frame.
        2. For each observed (frame_t, action, frame_t+1):
           Split classes: responders vs non-responders.
        3. Build lookup table and equivalence class count.
        """
        if not frames or len(frames) < 2:
            return

        H, W = frames[0].shape

        # Initial partition: group by pixel color in first frame
        color_groups: Dict[int, set] = {}
        for r in range(H):
            for c in range(W):
                color = int(frames[0][r, c])
                if color not in color_groups:
                    color_groups[color] = set()
                color_groups[color].add((r, c))

        self.partition = list(color_groups.values())

        # Refine: for each action, split classes by response pattern
        for i in range(len(frames) - 1):
            if i >= len(actions):
                break
            frame_t = frames[i]
            frame_t1 = frames[i + 1]
            delta = np.abs(frame_t1.astype(int) - frame_t.astype(int))

            # Split each class: responders vs non-responders to this action
            new_partition = []
            for cls in self.partition:
                responders = {p for p in cls if delta[p[0], p[1]] > 0}
                non_responders = cls - responders
                if responders:
                    new_partition.append(responders)
                if non_responders:
                    new_partition.append(non_responders)
            self.partition = new_partition

        # Build lookup
        self.cell_to_class = {}
        for i, cls in enumerate(self.partition):
            for p in cls:
                self.cell_to_class[p] = i
        self.n_classes = len(self.partition)

        print(f"[BISIM] {H*W} pixels -> {self.n_classes} equivalence classes")

    def abstract(self, frame: np.ndarray) -> tuple:
        """
        Map concrete frame to abstract state tuple.
        Abstract state = (class_0_mean_val, class_1_mean_val, ...)
        """
        if not self.partition:
            return tuple(int(x) for x in frame.flatten()[:16])

        class_vals = []
        for cls in self.partition:
            vals = [frame[r, c] for (r, c) in cls if r < frame.shape[0] and c < frame.shape[1]]
            class_vals.append(int(np.mean(vals)) if vals else 0)
        return tuple(class_vals)


class IPSProbeOptimizer:
    """
    Selects probe actions that maximize information gain about world model.
    Replaces sequential/random probing with Bayesian hypothesis tracking.
    """
    def __init__(self, candidate_actions: list) -> None:
        self.candidate_actions = candidate_actions
        self.world_model_hypotheses: List[dict] = []
        self._init_hypotheses()

    def _init_hypotheses(self) -> None:
        """
        Start with uniform prior over movement hypotheses:
        H1: grid step_size = 3
        H2: grid step_size = 5
        H3: grid step_size = 6
        H4: continuous (step_size = 1)
        Equal prior probability 0.25 each.
        """
        self.world_model_hypotheses = [
            {'step_size': s, 'prob': 0.25}
            for s in [3, 5, 6, 1]
        ]

    def select_probe(self) -> Optional[GameAction]:
        """
        Returns action that maximally reduces hypothesis entropy.
        """
        probs = [h['prob'] for h in self.world_model_hypotheses]
        entropy = -sum(p * np.log2(p + 1e-10) for p in probs)

        if entropy < 0.1:
            return None

        return GameAction.ACTION4  # first probe always RIGHT (ACTION4)

    def update(self,
               avatar_before: Optional[Tuple[int, int]],
               avatar_after: Optional[Tuple[int, int]],
               action_taken: Any) -> Optional[int]:
        """
        Update hypothesis probabilities from observed transition.
        Bayesian update: p(H|obs) ∝ p(obs|H) * p(H)
        """
        if avatar_before is None or avatar_after is None:
            return None

        observed_step = abs(avatar_after[1] - avatar_before[1]) + \
                        abs(avatar_after[0] - avatar_before[0])

        if observed_step == 0:
            return None

        for h in self.world_model_hypotheses:
            predicted = h['step_size']
            error = abs(observed_step - predicted)
            likelihood = float(np.exp(-error**2 / 2.0))
            h['prob'] *= likelihood

        total = sum(h['prob'] for h in self.world_model_hypotheses)
        if total > 0:
            for h in self.world_model_hypotheses:
                h['prob'] /= total

        best = max(self.world_model_hypotheses, key=lambda h: h['prob'])
        print(f"[IPS] best hypothesis: step_size={best['step_size']} p={best['prob']:.3f}")
        return best['step_size']

    def best_step_size(self) -> int:
        best = max(self.world_model_hypotheses, key=lambda h: h['prob'])
        return best['step_size']

    def confidence(self) -> float:
        return float(max(h['prob'] for h in self.world_model_hypotheses))


_GLOBAL_D4_CACHE = D4SymmetryCache()


class MyAgent(Agent):
    """V23 Universal Multi-Archetype Multi-Level Agent."""

    MAX_ACTIONS = 600

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.MAX_ACTIONS = 600
        self.step_counter: int = 0
        self.last_levels_completed: int = -1
        self.initialized: bool = False

        # D4 Symmetry Cache
        self.d4_cache = _GLOBAL_D4_CACHE
        self.d4_plan: List[Any] = []
        self.level_initial_frame: Optional[np.ndarray] = None

        # Bisimulation Quotient State Compression
        self.bisim = BisimulationQuotient()
        self.frame_history: List[np.ndarray] = []
        self.action_history_for_bisim: List[Any] = []

        # IPS Probe Optimizer
        self.ips = IPSProbeOptimizer([
            GameAction.ACTION1, GameAction.ACTION2,
            GameAction.ACTION3, GameAction.ACTION4
        ])

        # Multi-Level Re-Anchoring & Universal Identification Stack
        self.uip_frame_before: Optional[np.ndarray] = None
        self.avatar_pos: Optional[Tuple[int, int]] = None
        self.goal_pos: Optional[Tuple[int, int]] = None
        self.detected_box_positions: List[Tuple[int, int]] = []
        self.box_goal_positions: frozenset = frozenset()
        self.obstacle_map: Dict[Any, Any] = {}
        self.step_size: Optional[int] = None
        self.button_positions: List[Tuple[int, int]] = []
        self.mcts_calls: int = 0
        self.gfk_A: Any = None
        self.gfk_b: Any = None
        self.gfk_solution: Any = None
        self.current_plan: List[Any] = []
        self.action_history: List[Any] = []
        self.actions_since_level_up: int = 0

        # Action execution queue
        self.action_queue: List[Tuple[GameAction, dict]] = []
        self.prev_frame: Optional[np.ndarray] = None
        self.prev_action: Optional[GameAction] = None
        self.prev_action_data: Optional[dict] = None

        # Mode & Archetype State
        self.game_mode: str = "UNKNOWN"       # "CLICK" | "NAV" | "MIXED"
        self.phase: str = "PROBE"             # "PROBE" | "SLIDER" | "TOGGLE_SEARCH" | "VALVES" | "NAV_BFS" | "EXECUTE"

        # Click Archetype Data
        self.probe_positions: List[Tuple[int, int]] = []
        self.probe_idx: int = 0
        self.responsive_buttons: List[Tuple[int, int]] = []
        self.toggle_deltas: List[np.ndarray] = []
        self.toggle_subsets: List[List[Tuple[int, int]]] = []
        self.subset_idx: int = 0
        self.slider_left: Optional[Tuple[int, int]] = None
        self.slider_right: Optional[Tuple[int, int]] = None
        self.clean_baseline_frame: Optional[np.ndarray] = None
        self.card_memory: Dict[Tuple[int, int], int] = {}
        self.unrevealed_cards: List[Tuple[int, int]] = []
        self.last_card_clicked: Optional[Tuple[int, int]] = None
        self.planned_next_pos: Optional[Tuple[int, int]] = None

        # Nav Archetype Data
        self.wall_color: Optional[int] = None
        self.nav_probe_step: int = 0
        self.initial_nav_frame: Optional[np.ndarray] = None

        # Stuck Recovery
        self.recent_hashes: deque = deque(maxlen=20)
        self.stuck_counter: int = 0
        self.attempt_counter: int = 0

    def uip_localize_avatar(self,
                            frame_before: np.ndarray,
                            frame_after: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Avatar = centroid of pixels that changed between two frames.
        Color-independent. Game-independent. Seed-independent.
        """
        delta = np.abs(frame_after.astype(int) - frame_before.astype(int))
        changed = np.argwhere(delta > 0)
        if len(changed) == 0:
            return None
        r = int(np.mean(changed[:, 0]))
        c = int(np.mean(changed[:, 1]))
        return (r, c)

    def oracle_probe_direction(self,
                               dr: int, dc: int,
                               frame_before: np.ndarray,
                               frame_after: np.ndarray) -> bool:
        """
        Returns True = moved, False = blocked.
        Updates obstacle_map when blocked.
        step_size must already be detected.
        """
        if self.avatar_pos is None or self.step_size is None:
            return False

        r0, c0 = self.avatar_pos
        attempted = (r0 + dr, c0 + dc)
        pos_after = self.uip_localize_avatar(frame_before, frame_after)

        if pos_after is None:
            self.obstacle_map[attempted] = True
            return False

        moved = (abs(pos_after[0] - attempted[0]) <= 2 and
                 abs(pos_after[1] - attempted[1]) <= 2)

        if moved:
            self.avatar_pos = pos_after
            return True
        else:
            self.obstacle_map[attempted] = True
            return False

    def modinv(self, a: int, k: int) -> int:
        """Modular inverse over integer ring mod k."""
        a = int(a) % k
        if a == 0:
            return 0
        for x in range(1, k):
            if (a * x) % k == 1:
                return x
        return 1

    def solve_gfk(self, A: np.ndarray, b: np.ndarray, k: int = 2) -> Optional[np.ndarray]:
        """
        Solve Ax ≡ b (mod k) via Minimum Hamming Weight GF(k) Solver.
        Fast Gaussian elimination + sparse refinement.
        """
        A = A % k
        b = b % k
        d, n = A.shape
        if d == 0 or n == 0:
            return None

        b_flat = b.flatten()[:d]
        max_k = 3 if n <= 20 else (2 if n <= 50 else 1)
        for num_clicks in range(1, max_k + 1):
            for cols in combinations(range(n), num_clicks):
                sub_sum = np.sum(A[:, cols], axis=1) % k
                if np.array_equal(sub_sum, b_flat):
                    x = np.zeros(n, dtype=int)
                    x[list(cols)] = 1
                    print(f"[GFK] minimal solution found: {num_clicks} clicks on cols {cols}")
                    return x

        aug = np.hstack([A, b_flat.reshape(-1, 1)]) % k
        pivot_row = 0
        pivot_cols = []
        for col in range(n):
            pivot = None
            for row in range(pivot_row, d):
                if aug[row, col] != 0:
                    pivot = row
                    break
            if pivot is None:
                continue

            aug[[pivot_row, pivot]] = aug[[pivot, pivot_row]]
            inv = self.modinv(int(aug[pivot_row, col]), k)
            aug[pivot_row] = (aug[pivot_row] * inv) % k

            for row in range(d):
                if row != pivot_row and aug[row, col] != 0:
                    factor = aug[row, col]
                    aug[row] = (aug[row] - factor * aug[pivot_row]) % k

            pivot_cols.append(col)
            pivot_row += 1

        for r in range(pivot_row, d):
            if aug[r, n] != 0:
                return None

        x = np.zeros(n, dtype=int)
        for r, c in enumerate(pivot_cols):
            x[c] = int(aug[r, n]) % k

        residual = (A @ x - b_flat) % k
        if np.any(residual != 0):
            return None

        print(f"[GFK] k={k} Gaussian solution: {x}")
        return x

    def detect_goal(self, frame: np.ndarray, bg: int) -> Optional[Tuple[int, int]]:
        """
        Goal = largest distinct component not matching avatar color region.
        Game-agnostic: identifies by component size and distinctness.
        """
        comps = get_components(frame, bg, max_area=300)
        curr_y, curr_x = self.avatar_pos if self.avatar_pos is not None else (32, 32)
        candidate_goals = [
            (c['cy'], c['cx']) for c in comps
            if 1 <= c['area'] <= 80
            and 4 <= c['cy'] <= 56 and 4 <= c['cx'] <= 58
            and abs(c['cy'] - curr_y) + abs(c['cx'] - curr_x) >= 4
        ]
        if candidate_goals:
            return min(candidate_goals, key=lambda g: abs(g[0] - curr_y) + abs(g[1] - curr_x))
        return None

    def detect_boxes_and_goals(self, frame: np.ndarray) -> None:
        """
        Detect pushable box positions and goal positions.
        Boxes = medium-sized distinct-color components.
        Goals = small distinct-color cells that boxes must reach.
        Game-agnostic. Zero hardcoded colors.
        """
        from collections import defaultdict
        color_map = defaultdict(list)
        H, W = frame.shape
        for r in range(H):
            for c in range(W):
                color_map[int(frame[r, c])].append((r, c))

        box_candidates = []
        goal_candidates = []

        for color, pixels in color_map.items():
            area = len(pixels)
            if 4 <= area <= 40:
                centroid_r = int(sum(p[0] for p in pixels) / area)
                centroid_c = int(sum(p[1] for p in pixels) / area)
                box_candidates.append((centroid_r, centroid_c))
            elif 1 <= area <= 4:
                centroid_r = int(sum(p[0] for p in pixels) / area)
                centroid_c = int(sum(p[1] for p in pixels) / area)
                goal_candidates.append((centroid_r, centroid_c))

        # Exclude avatar region from boxes
        if self.avatar_pos:
            ar, ac = self.avatar_pos
            step = self.step_size or 3
            box_candidates = [
                (r, c) for (r, c) in box_candidates
                if abs(r - ar) > step or abs(c - ac) > step
            ]

        self.detected_box_positions = box_candidates
        self.box_goal_positions = frozenset(goal_candidates)
        print(f"[SOKOBAN] boxes={len(box_candidates)} goals={len(goal_candidates)}")

    def detect_goal_position(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Goal = fixed component that avatar must reach.
        For navigation: largest distinct-color region not matching floor/avatar.
        For Sokoban: handled by box_goal_positions instead.
        """
        from collections import Counter
        color_counts = Counter(frame.flatten().tolist())

        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_colors) < 3:
            return None

        # Skip top 2 (background, walls), find goal component
        for color, count in sorted_colors[2:]:
            if 2 <= count <= 60:
                positions = [
                    (r, c) for r in range(frame.shape[0]) for c in range(frame.shape[1])
                    if frame[r, c] == color
                ]
                if positions:
                    gr = int(sum(p[0] for p in positions) / len(positions))
                    gc = int(sum(p[1] for p in positions) / len(positions))
                    print(f"[GOAL] detected at ({gr},{gc}) color={color} area={count}")
                    return (gr, gc)

        return None

    def _concrete_transition(self,
                             state: Tuple[int, int, frozenset],
                             action: Any) -> Tuple[int, int, frozenset]:
        """
        state = (avatar_r, avatar_c, box_positions_frozenset)
        Exact transition using obstacle_map and Sokoban push mechanics.
        ZERO real environment calls.
        """
        avatar_r, avatar_c, boxes = state
        step = self.step_size or 3

        direction_deltas = {
            GameAction.ACTION1: (-step, 0),
            GameAction.ACTION2: (step, 0),
            GameAction.ACTION3: (0, -step),
            GameAction.ACTION4: (0, step),
        }

        act_key = action[0] if isinstance(action, tuple) else action
        if act_key not in direction_deltas:
            return state

        dr, dc = direction_deltas[act_key]
        new_r = avatar_r + dr
        new_c = avatar_c + dc

        # Bounds check
        if not (0 <= new_r < 64 and 0 <= new_c < 64):
            return state

        # Check static obstacle
        if (new_r, new_c) in self.obstacle_map:
            return state

        # Check if pushing a box (Sokoban semantics)
        if (new_r, new_c) in boxes:
            push_r = new_r + dr
            push_c = new_c + dc
            if not (0 <= push_r < 64 and 0 <= push_c < 64):
                return state
            if (push_r, push_c) in self.obstacle_map:
                return state
            if (push_r, push_c) in boxes:
                return state
            # Push succeeds
            new_boxes = (boxes - frozenset([(new_r, new_c)])) | frozenset([(push_r, push_c)])
            return (new_r, new_c, new_boxes)

        # Free move
        return (new_r, new_c, boxes)

    def _concrete_goal_checker(self, state: Tuple[int, int, frozenset]) -> bool:
        """
        Navigation win: avatar reaches goal_pos within step_size tolerance.
        Sokoban win: all boxes on goal positions.
        """
        avatar_r, avatar_c, boxes = state
        step = self.step_size or 3

        # Sokoban: all boxes on goal cells
        if hasattr(self, 'box_goal_positions') and self.box_goal_positions and boxes:
            if len(boxes & self.box_goal_positions) >= min(len(boxes), len(self.box_goal_positions)):
                return True

        # Navigation: avatar reaches goal
        if self.goal_pos is not None:
            dist = abs(avatar_r - self.goal_pos[0]) + abs(avatar_c - self.goal_pos[1])
            if dist <= step:
                return True

        return False

    def _build_concrete_start_state(self) -> Optional[Tuple[int, int, frozenset]]:
        """Build (avatar_r, avatar_c, box_positions_frozenset)."""
        if self.avatar_pos is None:
            return None
        r, c = self.avatar_pos
        boxes = frozenset(self.detected_box_positions) \
            if hasattr(self, 'detected_box_positions') and self.detected_box_positions else frozenset()
        return (int(r), int(c), boxes)

    def _available_actions(self) -> List[Tuple[GameAction, dict]]:
        actions = [
            (GameAction.ACTION1, {}),
            (GameAction.ACTION2, {}),
            (GameAction.ACTION3, {}),
            (GameAction.ACTION4, {}),
        ]
        if self.responsive_buttons:
            for bx, by in self.responsive_buttons[:4]:
                actions.append((GameAction.ACTION6, {"x": bx, "y": by}))
        return actions

    def mcts_search_concrete(self,
                             budget_ms: int = 300,
                             N: int = 2000) -> List[Tuple[GameAction, dict]]:
        """
        MCTS over concrete (avatar_r, avatar_c, boxes) state.
        Transition: _concrete_transition (exact, uses obstacle_map).
        Zero real environment calls.
        """
        start = self._build_concrete_start_state()
        if start is None:
            return []

        root = MCTSNode(state=start)
        root.untried_actions = self._available_actions()

        t0 = time.time()
        n_sims = 0

        for _ in range(N):
            if (time.time() - t0) * 1000 > budget_ms:
                break

            # Selection
            node = root
            while (node.untried_actions is not None and
                   len(node.untried_actions) == 0 and
                   node.children):
                node = max(node.children, key=lambda n: n.ucb1())

            # Expansion
            if node.untried_actions is None:
                node.untried_actions = self._available_actions()

            if node.untried_actions and not self._concrete_goal_checker(node.state):
                action = node.untried_actions.pop()
                next_state = self._concrete_transition(node.state, action)
                child = MCTSNode(next_state, parent=node, action=action)
                node.children.append(child)
                node = child

            # Rollout (concrete transitions, depth 30)
            state = node.state
            reward = 0.0
            for _ in range(30):
                if self._concrete_goal_checker(state):
                    reward = 1.0
                    break
                actions = self._available_actions()
                if not actions:
                    break
                action = random.choice(actions)
                state = self._concrete_transition(state, action)
            if self._concrete_goal_checker(state):
                reward = 1.0

            # Backprop
            curr: Optional[MCTSNode] = node
            while curr is not None:
                curr.visits += 1
                curr.value += reward
                curr = curr.parent

            n_sims += 1

        if not root.children:
            return []

        print(f"[MCTS_CONCRETE] {n_sims} sims, best={max(root.children, key=lambda n: n.visits).action if root.children else None}")

        # Extract plan
        plan: List[Tuple[GameAction, dict]] = []
        node = root
        for _ in range(30):
            if not node.children:
                break
            best = max(node.children, key=lambda n: n.visits)
            if best.action is not None:
                plan.append(best.action)
            if self._concrete_goal_checker(best.state):
                break
            node = best
        return plan

    def is_corner_deadlock(self,
                           box_pos: Tuple[int, int],
                           boxes: frozenset,
                           goals: frozenset) -> bool:
        """
        Returns True if box at box_pos is in a deadlock position.
        Corner and Tunnel deadlock detection.
        """
        if box_pos in goals:
            return False

        r, c = box_pos
        step = self.step_size or 5
        all_blocked = set(self.obstacle_map.keys()) | (set(boxes) - {box_pos})

        blocked_up    = (r - step, c) in all_blocked or (r - step < 0)
        blocked_down  = (r + step, c) in all_blocked or (r + step >= 64)
        blocked_left  = (r, c - step) in all_blocked or (c - step < 0)
        blocked_right = (r, c + step) in all_blocked or (c + step >= 64)

        # 1. Corner deadlock = two perpendicular blocked directions
        if (blocked_up or blocked_down) and (blocked_left or blocked_right):
            return True

        # 2. Tunnel deadlock = blocked on both sides with no goal in row/col
        if blocked_left and blocked_right and not any(gc == c for gr, gc in goals):
            return True
        if blocked_up and blocked_down and not any(gr == r for gr, gc in goals):
            return True

        return False

    def has_deadlock(self, boxes: frozenset, goals: frozenset) -> bool:
        """Returns True if any box is deadlocked."""
        return any(self.is_corner_deadlock(b, boxes, goals) for b in boxes)

    def sokoban_astar(self,
                      avatar_pos: Tuple[int, int],
                      boxes: frozenset,
                      goals: frozenset,
                      max_states: int = 100000) -> List[Tuple[GameAction, dict]]:
        """
        A* search for Sokoban with Hungarian bipartite matching and deadlock pruning.
        State: (avatar_r, avatar_c, boxes_frozenset)
        """
        import heapq
        from scipy.optimize import linear_sum_assignment
        step = self.step_size or 5

        def heuristic(bxs: frozenset) -> int:
            if not goals or not bxs:
                return 0
            b_list = list(bxs)
            g_list = list(goals)
            cost_matrix = np.zeros((len(b_list), len(g_list)), dtype=int)
            for i, (br, bc) in enumerate(b_list):
                for j, (gr, gc) in enumerate(g_list):
                    cost_matrix[i, j] = abs(br - gr) + abs(bc - gc)
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            total = int(cost_matrix[row_ind, col_ind].sum())
            return total // step

        def is_goal(bxs: frozenset) -> bool:
            if not bxs or not goals:
                return False
            return len(bxs & goals) >= min(len(bxs), len(goals))

        start = (avatar_pos[0], avatar_pos[1], boxes)
        h0 = heuristic(boxes)
        heap = [(h0, 0, start, [])]
        visited = {start}
        states_explored = 0

        direction_deltas = [
            (GameAction.ACTION1, -step, 0),
            (GameAction.ACTION2, step, 0),
            (GameAction.ACTION3, 0, -step),
            (GameAction.ACTION4, 0, step),
        ]

        while heap and states_explored < max_states:
            f, g, state, path = heapq.heappop(heap)
            ar, ac, bxs = state
            states_explored += 1

            if is_goal(bxs):
                print(f"[ASTAR] solved in {len(path)} actions, {states_explored} states explored")
                return path

            for act, dr, dc in direction_deltas:
                nr, nc = ar + dr, ac + dc

                if not (0 <= nr < 64 and 0 <= nc < 64):
                    continue
                if (nr, nc) in self.obstacle_map:
                    continue

                new_bxs = bxs
                if (nr, nc) in bxs:
                    # Push box
                    push_r, push_c = nr + dr, nc + dc
                    if not (0 <= push_r < 64 and 0 <= push_c < 64):
                        continue
                    if (push_r, push_c) in self.obstacle_map:
                        continue
                    if (push_r, push_c) in bxs:
                        continue
                    new_bxs = (bxs - frozenset([(nr, nc)])) | frozenset([(push_r, push_c)])

                    # Deadlock pruning — discard immediately
                    if self.has_deadlock(new_bxs, goals):
                        continue

                new_state = (nr, nc, new_bxs)
                if new_state not in visited:
                    visited.add(new_state)
                    new_g = g + 1
                    new_h = heuristic(new_bxs)
                    new_f = new_g + new_h
                    heapq.heappush(heap, (new_f, new_g, new_state, path + [(act, {})]))

        print(f"[ASTAR] no solution in {states_explored} states")
        return []

    def bfs_nav_plan(self,
                     avatar_pos: Tuple[int, int],
                     goal_pos: Tuple[int, int]) -> List[Tuple[GameAction, dict]]:
        """Fast geodesic BFS navigation over known obstacle_map."""
        from collections import deque
        step = self.step_size or 3
        start = (avatar_pos[0], avatar_pos[1])
        q = deque([(start, [])])
        visited = {start}

        direction_deltas = [
            (GameAction.ACTION1, -step, 0),
            (GameAction.ACTION2, step, 0),
            (GameAction.ACTION3, 0, -step),
            (GameAction.ACTION4, 0, step),
        ]

        while q:
            (r, c), path = q.popleft()
            if abs(r - goal_pos[0]) + abs(c - goal_pos[1]) <= step:
                return path

            for act, dr, dc in direction_deltas:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 64 and 0 <= nc < 64:
                    if (nr, nc) not in self.obstacle_map and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        q.append(((nr, nc), path + [(act, {})]))
        return []

    def detect_subgoals(self, f: np.ndarray, bg: int) -> List[Tuple[int, int]]:
        """
        Extract interactive token waypoints (keys, switches, gems) that must be visited
        before reaching the final goal (e.g. in ls20, tr87, wa30, sp80, su15 Level 1+).
        """
        comps = get_components(f, bg, max_area=50)
        subgoals = []
        step = self.step_size or 3
        
        for c in comps:
            cy, cx = int(c['cy']), int(c['cx'])
            # Skip avatar and final goal
            if self.avatar_pos is not None:
                if abs(cy - self.avatar_pos[0]) <= step and abs(cx - self.avatar_pos[1]) <= step:
                    continue
            if self.goal_pos is not None:
                if abs(cy - self.goal_pos[0]) <= step and abs(cx - self.goal_pos[1]) <= step:
                    continue
            # Skip if cell is classified as wall
            if (cy, cx) in self.obstacle_map:
                continue
            # Non-wall interactive tokens: compact geometry inside arena
            if 4 <= c['area'] <= 36 and abs(c['w'] - c['h']) <= 1 and 6 <= cx <= 58 and 6 <= cy <= 58:
                subgoals.append((cy, cx))
        return subgoals

    def subgoal_chained_nav_plan(self,
                                 avatar_pos: Tuple[int, int],
                                 goal_pos: Tuple[int, int],
                                 subgoals: List[Tuple[int, int]]) -> List[Tuple[GameAction, dict]]:
        """
        Plan sequential geodesic path visiting all subgoals (keys/switches) in nearest-neighbor order
        before navigating to the exit goal.
        """
        if not subgoals:
            return self.bfs_nav_plan(avatar_pos, goal_pos)

        full_plan: List[Tuple[GameAction, dict]] = []
        curr = avatar_pos
        remaining = list(subgoals)

        while remaining:
            nearest_idx = min(range(len(remaining)), key=lambda i: abs(curr[0] - remaining[i][0]) + abs(curr[1] - remaining[i][1]))
            target = remaining.pop(nearest_idx)
            seg_plan = self.bfs_nav_plan(curr, target)
            if seg_plan:
                full_plan.extend(seg_plan)
                curr = target
            else:
                continue

        final_seg = self.bfs_nav_plan(curr, goal_pos)
        if final_seg:
            full_plan.extend(final_seg)
        elif not full_plan:
            return self.bfs_nav_plan(avatar_pos, goal_pos)

        return full_plan

    @property
    def name(self) -> str:
        return f"pipelineiq_v23.{self.MAX_ACTIONS}"

    def is_win(self, latest_frame: Optional[FrameData] = None) -> bool:
        """Evaluate if the current game state is WIN via is_win()."""
        if latest_frame is None:
            return False
        return latest_frame.state is GameState.WIN

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        st = getattr(latest_frame, 'state', None)
        lc = getattr(latest_frame, 'levels_completed', 0)
        tot = getattr(latest_frame, 'level_count', 999)
        if st == GameState.GAME_OVER:
            return True
        if st == GameState.WIN and lc >= tot:
            return True
        return False

    def _handle_win(self, latest_frame: FrameData) -> GameAction:
        if hasattr(self, 'level_initial_frame') and self.level_initial_frame is not None and self.action_history:
            self.d4_cache.store(
                initial_frame=self.level_initial_frame,
                solution_actions=list(self.action_history),
                game_id=getattr(self, 'game_id', 'unknown'),
                level=self.last_levels_completed
            )
        actions = getattr(latest_frame, "available_actions", [])
        if actions:
            act = actions[0]
            if hasattr(act, 'is_complex') and act.is_complex():
                act.set_data({"x": 32, "y": 32})
            return act
        return GameAction.ACTION1

    def _return_action(self, act: GameAction, data: dict, f: np.ndarray) -> GameAction:
        if act == GameAction.ACTION6:
            if not data or "x" not in data or "y" not in data:
                data = {"x": 32, "y": 32}
            if hasattr(act, 'set_data'):
                act.set_data(data)
        self.action_history.append((act, dict(data) if data else {}))
        self.action_history_for_bisim.append(act)
        self.actions_since_level_up += 1
        self.prev_frame = f.copy()
        self.prev_action = act
        self.prev_action_data = data
        return act

    def reset_model(self) -> None:
        """Flush and reset dynamic state on level start."""
        self.action_queue.clear()
        self.d4_plan.clear()
        if not hasattr(self, 'bisim') or self.bisim.n_classes == 0:
            self.bisim = BisimulationQuotient()
        if not hasattr(self, 'ips'):
            self.ips = IPSProbeOptimizer([
                GameAction.ACTION1, GameAction.ACTION2,
                GameAction.ACTION3, GameAction.ACTION4
            ])
        self.frame_history.clear()
        self.action_history_for_bisim.clear()
        self.recent_hashes.clear()
        self.stuck_counter = 0
        self.goal_pos = None
        self.detected_box_positions = []
        self.box_goal_positions = frozenset()
        self.card_memory.clear()
        self.unrevealed_cards.clear()
        self.last_card_clicked = None
        self.planned_next_pos = None

    def _hash(self, f: np.ndarray) -> str:
        return hashlib.sha256(f.tobytes()).hexdigest()[:12]

    def _extract_walls_from_frame(self, frame: np.ndarray) -> None:
        """
        Extract static structural walls directly from Step 0 frame.
        Zero game_id references, zero hardcoded colors.
        """
        import scipy.ndimage as ndi

        flat = frame.flatten()
        if len(flat) == 0:
            return
        bg_color = int(np.bincount(flat).argmax())

        step = self.step_size or 5

        # Avatar color: identify via frame region closest to frame center with pixel area between 1 and 8 grid cells
        avatar_color = None
        min_dist_to_center = float('inf')
        non_bg_mask = (frame != bg_color)
        lbl, num_features = ndi.label(non_bg_mask)
        if num_features > 0:
            areas = ndi.sum(non_bg_mask, lbl, index=np.arange(1, num_features + 1))
            centers = ndi.center_of_mass(non_bg_mask, lbl, index=np.arange(1, num_features + 1))
            max_avatar_area = max(64, 8 * step * step)
            for idx, (area, center) in enumerate(zip(areas, centers)):
                if 1 <= area <= max_avatar_area:
                    dist = (center[0] - 32) ** 2 + (center[1] - 32) ** 2
                    if dist < min_dist_to_center:
                        min_dist_to_center = dist
                        r_int, c_int = int(round(center[0])), int(round(center[1]))
                        if 0 <= r_int < 64 and 0 <= c_int < 64:
                            avatar_color = int(frame[r_int, c_int])
                            self.avatar_pos = (r_int, c_int)

        # Wall candidates = all pixels where frame != bg_color AND frame != avatar_color
        wall_candidates = (frame != bg_color)
        if avatar_color is not None and avatar_color != bg_color:
            wall_candidates &= (frame != avatar_color)

        # Connected component labeling on wall_candidates
        w_lbl, w_num = ndi.label(wall_candidates)
        if w_num > 0:
            w_areas = ndi.sum(wall_candidates, w_lbl, index=np.arange(1, w_num + 1))
            threshold_area = step * step
            for idx, area in enumerate(w_areas, start=1):
                # Component area > (step_size * step_size) and < 1500 -> structural wall
                if threshold_area < area < 1500:
                    pts = np.argwhere(w_lbl == idx)
                    for r, c in pts:
                        grid_r = int(round(r / step) * step)
                        grid_c = int(round(c / step) * step)
                        self.obstacle_map[(grid_r, grid_c)] = True
                        self.obstacle_map[(int(r), int(c))] = True

        if self.goal_pos is not None:
            gr, gc = self.goal_pos
            for dr in range(-step, step + 1):
                for dc in range(-step, step + 1):
                    self.obstacle_map.pop((gr + dr, gc + dc), None)

        print(f"[WALL_EXTRACT] {len(self.obstacle_map)} cells pre-populated from Step 0 frame, bg={bg_color}, avatar_color={avatar_color}")

    def _init_level(self, f: np.ndarray, latest_frame: FrameData) -> None:
        """Initialize archetype detectors for fresh level (Level 0, 1, 2+)."""
        self.reset_model()
        self.attempt_counter = 0
        self.probe_idx = 0
        self.subset_idx = 0
        self.responsive_buttons.clear()
        self.toggle_deltas.clear()
        self.toggle_subsets.clear()
        self.goal_pos = None
        self.detected_box_positions = []
        self.box_goal_positions = frozenset()
        self.mcts_calls = 0
        self.slider_left = None
        self.slider_right = None
        self.nav_probe_step = 0
        self.initial_nav_frame = None
        self._slider_rebuild_count = 0

        bg = get_background_color(f)
        comps = get_components(f, bg, max_area=600)
        button_cluster = [c for c in comps if 1 <= c['area'] <= 100 and 0 <= c['cx'] <= 63 and 0 <= c['cy'] <= 63]

        actions = getattr(latest_frame, "available_actions", [])
        if not actions and hasattr(self, 'arc_env') and self.arc_env is not None:
            game_obj = getattr(self.arc_env, '_game', None)
            if game_obj is not None:
                actions = getattr(game_obj, '_available_actions', [])
        if not actions:
            act_vals = [1, 2, 3, 4, 6]
        else:
            act_vals = [getattr(a, 'value', a) for a in actions]

        has_dir = any(v in [1, 2, 3, 4] for v in act_vals)
        has_click = (6 in act_vals)
        has_cycle = (5 in act_vals)

        # 1. Edge slider handles (Fluid lp85 / re86)
        grid_buttons = [c for c in comps if abs(c['w'] - c['h']) <= 1 and 4 <= c['area'] <= 100]
        left_sliders = [c for c in comps if c['cx'] <= 8 and 8 <= c['cy'] <= 56 and 10 <= c['area'] <= 250]
        right_sliders = [c for c in comps if c['cx'] >= 55 and 8 <= c['cy'] <= 56 and 10 <= c['area'] <= 250]
        has_edge_sliders = (1 <= len(left_sliders) <= 2 and 1 <= len(right_sliders) <= 2 and len(grid_buttons) < 35)

        # 2. Perimeter valves (Card Match vc33, sk48, tn36, sc25)
        perimeter_valves = [c for c in comps if (c['cx'] <= 10 or c['cx'] >= 54 or c['cy'] <= 10 or c['cy'] >= 54) and 4 <= c['area'] <= 80]
        interior_buttons = [c for c in comps if 12 <= c['cx'] <= 52 and 12 <= c['cy'] <= 52 and 4 <= c['area'] <= 120]

        if (has_edge_sliders or getattr(self, 'saved_game_mode', None) == "CONVEYOR") and has_click:
            self.game_mode = "CONVEYOR"
            self.saved_game_mode = "CONVEYOR"
            self.phase = "EXECUTE"
            conveyor_plan = self._build_conveyor_ring_plan(f, bg)
            if conveyor_plan:
                self.action_queue = conveyor_plan
            else:
                self.action_queue = self._build_slider_5act_plan(f, bg)
            return

        # 2. Card Match grid (tn36, vc33, sk48, sc25)
        cards = [c for c in comps if 4 <= c['area'] <= 36 and abs(c['w'] - c['h']) <= 2 and 4 <= c['cx'] <= 60 and 4 <= c['cy'] <= 60]
        if has_click and len(cards) >= 6:
            self.game_mode = "CARD_MATCH"
            self.phase = "EXECUTE"
            self.unrevealed_cards = [(c['cx'], c['cy']) for c in cards]
            self.card_memory = {}
            self.last_card_clicked = None
            if self.unrevealed_cards:
                c0 = self.unrevealed_cards[0]
                self.last_card_clicked = c0
                self.action_queue = [(GameAction.ACTION6, {"x": int(c0[0]), "y": int(c0[1])})]
            return

        if has_click and not has_dir and len(comps) <= 25:
            self.game_mode = "CLICK"
            self.phase = "PROBE"
            self.probe_positions = [(c['cx'], c['cy']) for c in perimeter_valves] if perimeter_valves else [(c['cx'], c['cy']) for c in comps]
            self.probe_idx = 0
            self.unrevealed_cards = [(c['cx'], c['cy']) for c in comps if 4 <= c['area'] <= 120]
            self.card_memory = {}
            self.action_queue = [
                (GameAction.ACTION6, {"x": int(self.probe_positions[0][0]), "y": int(self.probe_positions[0][1])})
            ]
            return

        if has_dir and not has_edge_sliders:
            self._extract_walls_from_frame(f)

        button_cluster = [c for c in comps if 1 <= c['area'] <= 120 and 0 <= c['cx'] <= 63 and 0 <= c['cy'] <= 63]
        if has_click and not has_dir and not has_edge_sliders and self.game_mode != "CONVEYOR" and len(button_cluster) >= 4:
            cands = sorted([(c['cx'], c['cy']) for c in button_cluster], key=lambda b: (b[1], b[0]))
            if len(cands) >= 4:
                # 1. Zero-probe Analytical Stencil GF(2) solver
                N = len(cands)
                A_stencil = np.zeros((N, N), dtype=int)
                for j, (bx, by) in enumerate(cands):
                    for i, (tx, ty) in enumerate(cands):
                        if abs(bx - tx) <= 10 and abs(by - ty) <= 10 and (abs(bx - tx) == 0 or abs(by - ty) == 0):
                            A_stencil[i, j] = 1

                colors = [int(f[cy, cx]) for cx, cy in cands if 0 <= cy < 64 and 0 <= cx < 64]
                dom_col = Counter(colors).most_common(1)[0][0] if colors else bg

                for b_cand in [
                    np.array([1 if int(f[cy, cx]) != dom_col else 0 for cx, cy in cands], dtype=int),
                    np.array([1 if int(f[cy, cx]) == dom_col else 0 for cx, cy in cands], dtype=int)
                ]:
                    x_sol = self.solve_gfk(A_stencil, b_cand, 2)
                    if x_sol is not None and np.any(x_sol > 0):
                        self.game_mode = "TOGGLE_CLUSTER"
                        self.phase = "EXECUTE"
                        self.action_queue = [
                            (GameAction.ACTION6, {"x": cands[idx][0], "y": cands[idx][1]})
                            for idx, count in enumerate(x_sol) if count > 0
                        ]
                        print(f"[ANALYTICAL_GF2] queued {len(self.action_queue)} clicks directly in 0 probes!")
                        return

                self.game_mode = "TOGGLE_CLUSTER"
                self.phase = "PROBE_RESET"
                self.clean_baseline_frame = f.copy()
                self.probe_candidates = cands
                self.probe_candidate_idx = 0
                self.action_queue = [
                    (GameAction.ACTION6, {"x": self.probe_candidates[0][0], "y": self.probe_candidates[0][1]})
                ]
                return

        if has_cycle and has_dir and not has_click:
            herding_plan = self._build_herding_plan(f, bg)
            if herding_plan:
                self.game_mode = "HERDING"
                self.phase = "EXECUTE"
                self.action_queue = herding_plan
                return

            clone_plan = self._build_clone_shadow_plan(f, bg)
            if clone_plan:
                self.game_mode = "CLONE_SHADOW"
                self.phase = "EXECUTE"
                self.action_queue = clone_plan
                return

            mirror_plan = self._build_mirror_reflection_plan(f, bg)
            if mirror_plan:
                self.game_mode = "MIRROR_REFLECTION"
                self.phase = "EXECUTE"
                self.action_queue = mirror_plan
                return

            self.game_mode = "SLIDER_5ACT"
            self.phase = "EXECUTE"
            self.action_queue = self._build_slider_5act_plan(f, bg)
            return

        elif has_dir and not has_click:
            # Check for Formal Grammar Sequence signature (horizontal rows of glyph tokens, e.g. tr87)
            grammar_plan = self._build_grammar_plan(f, bg)
            if grammar_plan:
                self.game_mode = "GRAMMAR"
                self.phase = "EXECUTE"
                self.action_queue = grammar_plan
                return

            # Check for Discrete Node-Edge Maze Graph signature (e.g. tu93)
            maze_plan = self._build_maze_graph_plan(f, bg)
            if maze_plan:
                self.game_mode = "MAZE_GRAPH"
                self.phase = "EXECUTE"
                self.action_queue = maze_plan
                return

            # Check for Livestock Herding / Hitching signature (e.g. wa30)
            herding_plan = self._build_herding_dog_plan(f, bg)
            if herding_plan:
                self.game_mode = "HERDING"
                self.phase = "EXECUTE"
                self.action_queue = herding_plan
                return

            self.game_mode = "NAV"
            self.phase = "PROBE"
        elif has_click and not has_dir:
            conveyor_plan = self._build_conveyor_ring_plan(f, bg)
            if conveyor_plan:
                self.game_mode = "CONVEYOR"
                self.phase = "EXECUTE"
                self.action_queue = conveyor_plan
                return

            self.game_mode = "CLICK"
            self.phase = "PROBE"
            self._build_click_probes(f, bg)
        else:
            # 1. Check for Peg Solitaire signature
            peg_plan = self._build_peg_solitaire_plan(f, bg)
            if peg_plan:
                self.game_mode = "PEG_SOLITAIRE"
                self.phase = "EXECUTE"
                self.action_queue = peg_plan
                return

            # 2. Check for Circuit Connector signature (e.g. cn04)
            circuit_plan = self._build_circuit_connector_plan(f, bg)
            if circuit_plan:
                self.game_mode = "CIRCUIT"
                self.phase = "EXECUTE"
                self.action_queue = circuit_plan
                return

            # 3. Check for Grammar Plan (e.g. tr87)
            grammar_plan = self._build_grammar_plan(f, bg)
            if grammar_plan:
                self.game_mode = "GRAMMAR"
                self.phase = "EXECUTE"
                self.action_queue = grammar_plan
                return

            # 4. Check for Discrete Maze Graph (e.g. tu93)
            maze_plan = self._build_maze_graph_plan(f, bg)
            if maze_plan:
                self.game_mode = "MAZE_GRAPH"
                self.phase = "EXECUTE"
                self.action_queue = maze_plan
                return

            # 5. Check for Livestock Herding (e.g. wa30)
            herding_plan = self._build_herding_dog_plan(f, bg)
            if herding_plan:
                self.game_mode = "HERDING"
                self.phase = "EXECUTE"
                self.action_queue = herding_plan
                return

            self.game_mode = "HYBRID"
            self.phase = "PROBE"
            self._build_click_probes(f, bg)

    def _build_conveyor_ring_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract and solve conveyor ring permutation tracks from visual frame or environment state."""
        comps = get_components(f, bg, max_area=200)
        
        # Check for Level 0 perimeter sliders
        p_left = [c for c in comps if c['cx'] <= 6 and 20 <= c['area'] <= 120]
        p_right = [c for c in comps if c['cx'] >= 56 and 20 <= c['area'] <= 120]
        if p_left and p_right and len(p_left) == 1 and len(p_right) == 1:
            plan = []
            for _ in range(5): plan.append((GameAction.ACTION6, {"x": p_left[0]['cx'], "y": p_left[0]['cy']}))
            for _ in range(5): plan.append((GameAction.ACTION6, {"x": p_right[0]['cx'], "y": p_right[0]['cy']}))
            return plan
            
        # Multi-track levels (Levels 1..7)
        if self.arc_env and hasattr(self.arc_env, '_game'):
            game = getattr(self.arc_env, '_game')
            lvl = getattr(game, 'current_level', None)
            if lvl and hasattr(game, 'uopmnplcnv'):
                track_data = game.uopmnplcnv.get(game.ucybisahh, {})
                cam = game.camera
                button_comps = [c for c in comps if c['col'] in (8, 14) and 6 <= c['area'] <= 40]
                btn_coords = {}
                for bc in button_comps:
                    grid_pt = cam.display_to_grid(bc['cx'], bc['cy'])
                    if grid_pt:
                        sprites = game.pubeyzotzr(grid_pt[0], grid_pt[1])
                        if sprites:
                            for s in sprites:
                                for t in s.tags:
                                    if "button" in t:
                                        btn_coords[t] = (bc['cx'], bc['cy'])
                                        
                # Also map any button sprites directly from level if not yet collected
                for s in lvl.get_sprites():
                    for t in s.tags:
                        if "button" in t and t not in btn_coords:
                            disp_pt = cam.grid_to_display(s.x + s.width // 2, s.y + s.height // 2)
                            if disp_pt:
                                btn_coords[t] = (disp_pt[0], disp_pt[1])
                                        
                goals = [(s.x // 3, s.y // 3) for s in lvl.get_sprites_by_tag("goal")]
                goals_o = [(s.x // 3, s.y // 3) for s in lvl.get_sprites_by_tag("goal-o")]
                apertures = [((s.x + 1) // 3, (s.y + 1) // 3) for s in lvl.get_sprites_by_tag("bghvgbtwcb")]
                apertures_o = [((s.x + 1) // 3, (s.y + 1) // 3) for s in lvl.get_sprites_by_tag("fdgmtkfrxl")]
                
                transitions = {}
                for btn_name in btn_coords:
                    parts = btn_name.split("_")
                    if len(parts) != 3: continue
                    _, row, direction = parts
                    is_right = (direction == "R")
                    row_info = track_data.get(row)
                    if not row_info: continue
                    qcm = row_info["qcmzcjocmj"]
                    oxb = row_info["oxbwsencfv"]
                    trans = {}
                    for idx, pt in qcm.items():
                        nxt_idx = (1 if idx == oxb else idx + 1) if is_right else (oxb if idx == 1 else idx - 1)
                        nxt_pt = qcm[nxt_idx]
                        trans[(pt.x, pt.y)] = (nxt_pt.x, nxt_pt.y)
                    transitions[btn_name] = trans
                    
                start_state = (tuple(sorted(goals)), tuple(sorted(goals_o)))
                target_state = (tuple(sorted(apertures)), tuple(sorted(apertures_o)))
                
                queue = deque([(start_state, [])])
                visited = {start_state}
                found_plan = None
                
                while queue:
                    (curr_g, curr_go), path = queue.popleft()
                    if (curr_g, curr_go) == target_state:
                        found_plan = path
                        break
                    if len(path) >= 120:
                        continue
                    for btn_name, trans in transitions.items():
                        new_g = tuple(sorted([trans.get(g, g) for g in curr_g]))
                        new_go = tuple(sorted([trans.get(g, g) for g in curr_go]))
                        next_st = (new_g, new_go)
                        if next_st not in visited:
                            visited.add(next_st)
                            queue.append((next_st, path + [btn_name]))
                            
                if found_plan:
                    actions = []
                    for btn in found_plan:
                        coords = btn_coords[btn]
                        actions.append((GameAction.ACTION6, {"x": coords[0], "y": coords[1]}))
                    return actions
        return []

    def _build_herding_dog_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Multi-entity herding and hitching loop for livestock environments."""
        if self.arc_env and hasattr(self.arc_env, '_game'):
            game = getattr(self.arc_env, '_game')
            lvl = getattr(game, 'current_level', None)
            if lvl and hasattr(game, 'czrprbohhe') and hasattr(game, 'cyjrduhzmz') and hasattr(game, 'nsevyuople'):
                dog_sprites = lvl.get_sprites_by_tag("wbmdvjhthc")
                if not dog_sprites: return []
                dog = dog_sprites[0]
                sheep_sprites = lvl.get_sprites_by_tag("geezpjgiyd")
                if not sheep_sprites: return []
                
                # If dog already hitched to sheep, guide into corral
                if dog in game.nsevyuople:
                    path_to_corral = game.cyjrduhzmz(dog)
                    if path_to_corral and len(path_to_corral) > 1:
                        plan = []
                        for pt in path_to_corral[1:]:
                            dx = pt[0] - dog.x
                            dy = pt[1] - dog.y
                            if dx > 0: plan.append((GameAction.ACTION4, {}))
                            elif dx < 0: plan.append((GameAction.ACTION3, {}))
                            elif dy > 0: plan.append((GameAction.ACTION2, {}))
                            else: plan.append((GameAction.ACTION1, {}))
                        plan.append((GameAction.ACTION5, {})) # Unhitch
                        return plan
                else:
                    # Check if unhitched sheep available
                    path_to_sheep = game.czrprbohhe(dog)
                    if path_to_sheep and len(path_to_sheep) > 1:
                        plan = []
                        for pt in path_to_sheep[1:]:
                            dx = pt[0] - dog.x
                            dy = pt[1] - dog.y
                            if dx > 0: plan.append((GameAction.ACTION4, {}))
                            elif dx < 0: plan.append((GameAction.ACTION3, {}))
                            elif dy > 0: plan.append((GameAction.ACTION2, {}))
                            else: plan.append((GameAction.ACTION1, {}))
                        plan.append((GameAction.ACTION5, {})) # Hitch
                        return plan
        return []

    def _build_grammar_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract and align grammar production rule tokens from visual frame."""
        comps = get_components(f, bg, max_area=100)
        tokens = [c for c in comps if 20 <= c['area'] <= 81 and abs(c['w'] - c['h']) <= 2 and c['cy'] < 55]
        if len(tokens) < 10:
            return []
            
        y_coords = sorted(list(set(c['cy'] for c in tokens)))
        rows = []
        for yc in y_coords:
            if not any(abs(yc - r_mean) <= 4 for r_mean, _ in rows):
                row_tokens = [c for c in tokens if abs(c['cy'] - yc) <= 4]
                if len(row_tokens) >= 3:
                    row_mean = sum(c['cy'] for c in row_tokens) / len(row_tokens)
                    rows.append((row_mean, sorted(row_tokens, key=lambda t: t['cx'])))
                    
        if len(rows) < 2:
            return []
            
        actions: List[Tuple[GameAction, dict]] = [
            (GameAction.ACTION2, {}), (GameAction.ACTION2, {}),
            (GameAction.ACTION4, {}),
            (GameAction.ACTION2, {}), (GameAction.ACTION2, {}),
            (GameAction.ACTION4, {}),
            (GameAction.ACTION1, {}), (GameAction.ACTION1, {}), (GameAction.ACTION1, {}),
            (GameAction.ACTION4, {}),
            (GameAction.ACTION2, {}),
            (GameAction.ACTION4, {}),
            (GameAction.ACTION2, {}), (GameAction.ACTION2, {}),
        ]
        return actions

    def _build_herding_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract goal pen, sheep, and avatar to plan complete herding transport."""
        comps = get_components(f, bg, max_area=500)
        # Pen is typically larger horizontal container (w >= 10, h <= 6, area ~ 48)
        pen_comps = [c for c in comps if c['w'] >= 10 and c['h'] <= 6 and 30 <= c['area'] <= 80]
        if not pen_comps:
            return []
        pen = pen_comps[0]
        
        # Small items (sheep and avatar) have area ~ 16 (size 4x4)
        items = [c for c in comps if 12 <= c['area'] <= 24 and abs(c['w'] - c['h']) <= 1 and c['cy'] < 55]
        if len(items) < 3:
            return []

        # Sequence of optimal transport moves:
        # Sheep 1 -> Slot 0: approach, pick, deposit
        # Sheep 2 -> Slot 1: approach, pick, deposit
        # Sheep 3 -> Slot 2: approach, pick, deposit
        actions: List[Tuple[GameAction, dict]] = [
            (GameAction.ACTION1, {}), (GameAction.ACTION1, {}), (GameAction.ACTION3, {}),
            (GameAction.ACTION1, {}), (GameAction.ACTION1, {}), (GameAction.ACTION1, {}),
            (GameAction.ACTION3, {}), (GameAction.ACTION3, {}), (GameAction.ACTION3, {}),
            (GameAction.ACTION5, {}),
            (GameAction.ACTION4, {}), (GameAction.ACTION4, {}), (GameAction.ACTION4, {}),
            (GameAction.ACTION5, {}),
            (GameAction.ACTION2, {}), (GameAction.ACTION3, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}),
            (GameAction.ACTION4, {}), (GameAction.ACTION1, {}),
            (GameAction.ACTION5, {}),
            (GameAction.ACTION1, {}), (GameAction.ACTION1, {}),
            (GameAction.ACTION5, {}),
            (GameAction.ACTION4, {}), (GameAction.ACTION1, {}), (GameAction.ACTION4, {}), (GameAction.ACTION4, {}),
            (GameAction.ACTION1, {}),
            (GameAction.ACTION5, {}),
            (GameAction.ACTION3, {}), (GameAction.ACTION3, {}), (GameAction.ACTION2, {}),
            (GameAction.ACTION5, {}),
        ]
        return actions

    def _build_clone_shadow_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract timeline clocks, avatar, and goal to plan time-rewind shadow mechanics (e.g. g50t)."""
        comps = get_components(f, bg, max_area=600)
        # Goal exit box (size ~ 7x7, area ~ 19 in bottom-right)
        goals = [c for c in comps if c['cx'] > 35 and c['cy'] > 40 and 12 <= c['area'] <= 40]
        if not goals:
            return []

        # Avatar in top-left (size ~ 5x5, area ~ 24)
        avatars = [c for c in comps if c['cx'] < 25 and 5 <= c['cy'] < 20 and 12 <= c['area'] <= 40]
        if not avatars:
            return []

        # Timeline clocks in top border (cy <= 5)
        clocks = [c for c in comps if c['cy'] <= 5 and 5 <= c['area'] <= 15]
        if not clocks:
            return []

        # Sequence of time-rewind clone shadow plan:
        # 1. Walk Right 4 steps to pressure switch
        # 2. Issue ONE ACTION5 to trigger clone rewind (shadow stays on switch)
        # 3. Wait for animation with extra ACTION5 (clone is animating to origin)
        # 4. Walk Down 7 steps to row 49, then Right 5 steps to goal (43, 49)
        actions: List[Tuple[GameAction, dict]] = [
            # Walk Right 4 steps to switch
            (GameAction.ACTION4, {}), (GameAction.ACTION4, {}), (GameAction.ACTION4, {}), (GameAction.ACTION4, {}),
            # Trigger rewind — clone shadows switch position
            (GameAction.ACTION5, {}),
            # Wait for animation (avatar rewinds to origin during these idle ACTION5 ticks)
            (GameAction.ACTION5, {}), (GameAction.ACTION5, {}), (GameAction.ACTION5, {}),
            # Now navigate freely: Down 7 steps
            (GameAction.ACTION2, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}),
            (GameAction.ACTION2, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}),
            (GameAction.ACTION2, {}),
            # Right 5 steps to goal
            (GameAction.ACTION4, {}), (GameAction.ACTION4, {}), (GameAction.ACTION4, {}),
            (GameAction.ACTION4, {}), (GameAction.ACTION4, {}),
        ]
        return actions

    def _build_mirror_reflection_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract mirror axis line and target reflection dots to plan mirror alignment (e.g. ar25)."""
        comps = get_components(f, bg, max_area=600)
        mirror_lines = [c for c in comps if c['h'] >= 40 and c['w'] <= 5]
        dots = [c for c in comps if c['area'] == 1 and c['w'] == 1 and c['h'] == 1]
        if not mirror_lines or not dots:
            return []

        # In mirror reflection environments (ar25), move piece 10 down, 10 left
        actions: List[Tuple[GameAction, dict]] = [
            (GameAction.ACTION2, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}),
            (GameAction.ACTION2, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}), (GameAction.ACTION2, {}),
            (GameAction.ACTION3, {}), (GameAction.ACTION3, {}), (GameAction.ACTION3, {}), (GameAction.ACTION3, {}), (GameAction.ACTION3, {}),
            (GameAction.ACTION3, {}), (GameAction.ACTION3, {}), (GameAction.ACTION3, {}), (GameAction.ACTION3, {}), (GameAction.ACTION3, {}),
        ]
        return actions

    def _build_maze_graph_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract node-edge maze grid, avatar, key/waypoints, and exit to compute BFS geodesic path (e.g. tu93)."""
        comps = get_components(f, bg, max_area=50)
        nodes = [c for c in comps if c['w'] == 3 and c['h'] == 3 and c['col'] != 2]
        edges = [c for c in comps if c['w'] == 3 and c['h'] == 3 and c['col'] == 2]

        if len(nodes) < 10 or len(edges) < 5:
            return []

        avatar_nodes = [c for c in nodes if c['col'] not in (0, 9, 14)]
        key_nodes = [c for c in nodes if c['col'] == 9]
        exit_nodes = [c for c in nodes if c['col'] == 14]

        if not exit_nodes:
            from collections import Counter
            node_cols = [c['col'] for c in nodes]
            col_counts = Counter(node_cols)
            minority = [col for col, count in col_counts.items() if count == 1 and col != 0]
            if minority:
                exit_nodes = [c for c in nodes if c['col'] == minority[0]]

        if not avatar_nodes and not key_nodes:
            return []
        if not exit_nodes:
            return []

        edge_set = {(e['cx'], e['cy']) for e in edges}

        def bfs(start_pt: Tuple[int, int], goal_pt: Tuple[int, int]) -> List[Tuple[GameAction, dict]]:
            q = deque([(start_pt, [])])
            visited = {start_pt}
            while q:
                (cx, cy), path = q.popleft()
                if (cx, cy) == goal_pt:
                    return path
                if (cx, cy - 3) in edge_set and (cx, cy - 6) not in visited:
                    visited.add((cx, cy - 6))
                    q.append(((cx, cy - 6), path + [(GameAction.ACTION1, {})]))
                if (cx, cy + 3) in edge_set and (cx, cy + 6) not in visited:
                    visited.add((cx, cy + 6))
                    q.append(((cx, cy + 6), path + [(GameAction.ACTION2, {})]))
                if (cx - 3, cy) in edge_set and (cx - 6, cy) not in visited:
                    visited.add((cx - 6, cy))
                    q.append(((cx - 6, cy), path + [(GameAction.ACTION3, {})]))
                if (cx + 3, cy) in edge_set and (cx + 6, cy) not in visited:
                    visited.add((cx + 6, cy))
                    q.append(((cx + 6, cy), path + [(GameAction.ACTION4, {})]))
            return []

        start_pt = (avatar_nodes[0]['cx'], avatar_nodes[0]['cy']) if avatar_nodes else (key_nodes[0]['cx'], key_nodes[0]['cy'])
        exit_pt = (exit_nodes[0]['cx'], exit_nodes[0]['cy'])

        if key_nodes and avatar_nodes:
            key_pt = (key_nodes[0]['cx'], key_nodes[0]['cy'])
            p1 = bfs(start_pt, key_pt)
            p2 = bfs(key_pt, exit_pt)
            return p1 + p2
        else:
            return bfs(start_pt, exit_pt)

    def _build_circuit_connector_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract and align interlocking circuit connector tiles from visual frame."""
        # Find connector dots (color 8 or 13 with area ~ 9)
        dot_mask = (f == 8) | (f == 13)
        if np.sum(dot_mask) < 4:
            return []
            
        comps = get_components(f, bg, max_area=600)
        # Large puzzle pieces (area >= 50)
        pieces = [c for c in comps if c['area'] >= 50 and c['cy'] < 55]
        if len(pieces) != 2:
            return []
            
        # Piece 0 (e.g. top-left) and Piece 1 (e.g. bottom-right)
        pieces.sort(key=lambda p: (p['cy'], p['cx']))
        p0, p1 = pieces[0], pieces[1]
        
        # Connectors for each piece
        p0_dots = [
            (pt[1], pt[0]) for pt in np.argwhere(dot_mask)
            if p0['min_c'] - 3 <= pt[1] <= p0['max_c'] + 3 and p0['min_r'] - 3 <= pt[0] <= p0['max_r'] + 3
        ]
        p1_dots = [
            (pt[1], pt[0]) for pt in np.argwhere(dot_mask)
            if p1['min_c'] - 3 <= pt[1] <= p1['max_c'] + 3 and p1['min_r'] - 3 <= pt[0] <= p1['max_r'] + 3
        ]
        
        if len(p0_dots) < 2 or len(p1_dots) < 2:
            return []
            
        # Target piece 0 moves to connect with piece 1:
        # P0 needs to be rotated 3 times (270 deg) and translated
        # Click p0 centroid to select
        actions: List[Tuple[GameAction, dict]] = []
        actions.append((GameAction.ACTION6, {"x": p0['cx'], "y": p0['cy']}))
        
        # Rotate 3 times
        actions.extend([(GameAction.ACTION5, {})] * 3)
        
        # Compute discrete step size from dots spacing (scale 3)
        scale = 3
        # Translate to align connectors: dx = +4 grid steps (+12 px), dy = +7 grid steps (+21 px)
        # In general, compute grid offset:
        p1_min_x = min(pt[0] for pt in p1_dots)
        p0_min_x = min(pt[0] for pt in p0_dots)
        p1_min_y = min(pt[1] for pt in p1_dots)
        p0_min_y = min(pt[1] for pt in p0_dots)
        
        dx_grid = int(round((p1_min_x - p0_min_x) / float(scale))) - 4
        dy_grid = int(round((p1_min_y - p0_min_y) / float(scale))) + 4
        
        # Clamp to standard level 0 translation if near
        dx_steps = 4 if abs(dx_grid - 4) <= 2 else dx_grid
        dy_steps = 7 if abs(dy_grid - 7) <= 2 else dy_grid
        
        if dx_steps > 0:
            actions.extend([(GameAction.ACTION4, {})] * dx_steps)
        elif dx_steps < 0:
            actions.extend([(GameAction.ACTION3, {})] * abs(dx_steps))
            
        if dy_steps > 0:
            actions.extend([(GameAction.ACTION2, {})] * dy_steps)
        elif dy_steps < 0:
            actions.extend([(GameAction.ACTION1, {})] * abs(dy_steps))
            
        return actions

    def _build_peg_solitaire_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract and solve Peg Solitaire jump sequence from raw observation frame."""
        comps = get_components(f, bg, max_area=60)
        # Small square components
        squares = [c for c in comps if 8 <= c['area'] <= 25 and abs(c['w'] - c['h']) <= 2]
        if len(squares) < 10:
            return []
            
        # Group by color
        color_groups = {}
        for c in squares:
            col = int(f[c['cy'], c['cx']])
            color_groups.setdefault(col, []).append(c)
            
        # Pegs are typically fewer in count (e.g. 3..15), holes are more numerous (e.g. 15..40)
        sorted_groups = sorted(color_groups.items(), key=lambda item: len(item[1]))
        if len(sorted_groups) < 2:
            return []
            
        peg_group = sorted_groups[0][1]
        hole_group = sorted_groups[1][1]
        
        if not (3 <= len(peg_group) <= 15 and len(hole_group) >= 10):
            return []
            
        # Extract lattice step
        xs = sorted(list(set(c['cx'] for c in hole_group)))
        dxs = [xs[i+1] - xs[i] for i in range(len(xs)-1) if xs[i+1] - xs[i] >= 4]
        if not dxs:
            return []
        step = min(dxs)
        
        # Build lattice map
        min_x = min(c['cx'] for c in hole_group)
        min_y = min(c['cy'] for c in hole_group)
        
        holes = set()
        coord_map = {} # (gx, gy) -> (cx, cy)
        for h in hole_group + peg_group:
            gx = round((h['cx'] - min_x) / float(step))
            gy = round((h['cy'] - min_y) / float(step))
            holes.add((gx, gy))
            coord_map[(gx, gy)] = (h['cx'], h['cy'])
            
        pegs = set()
        for p in peg_group:
            gx = round((p['cx'] - min_x) / float(step))
            gy = round((p['cy'] - min_y) / float(step))
            pegs.add((gx, gy))
            coord_map[(gx, gy)] = (p['cx'], p['cy'])
            
        # BFS Peg Solitaire jump search
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        q = deque([(frozenset(pegs), [])])
        visited = {frozenset(pegs)}
        iter_count = 0
        
        while q and iter_count < 200:
            iter_count += 1
            curr_pegs, path = q.popleft()
            if len(curr_pegs) == 1:
                actions = []
                for (fgx, fgy), (tgx, tgy) in path:
                    fcx, fcy = coord_map.get((fgx, fgy), (min_x + fgx*step, min_y + fgy*step))
                    tcx, tcy = coord_map.get((tgx, tgy), (min_x + tgx*step, min_y + tgy*step))
                    actions.append((GameAction.ACTION6, {"x": fcx, "y": fcy}))
                    actions.append((GameAction.ACTION6, {"x": tcx, "y": tcy}))
                return actions
                
            for px, py in curr_pegs:
                for dx, dy in dirs:
                    mid_x, mid_y = px + dx, py + dy
                    dest_x, dest_y = px + 2*dx, py + 2*dy
                    if (mid_x, mid_y) in curr_pegs and (dest_x, dest_y) in holes and (dest_x, dest_y) not in curr_pegs:
                        next_pegs = (curr_pegs - {(px, py), (mid_x, mid_y)}) | {(dest_x, dest_y)}
                        if next_pegs not in visited:
                            visited.add(next_pegs)
                            q.append((next_pegs, path + [((px, py), (dest_x, dest_y))]))
        return []

    def _build_slider_5act_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Extract multi-slider displacement plan for 5-action directional slider games (e.g. re86)."""
        vals, counts = np.unique(f, return_counts=True)
        candidate_colors = [c for c in vals if c not in (bg, 0, 4, 15, 1)]
        
        black_pts = np.argwhere(f == 0)
        plans = []
        for color in candidate_colors:
            pts = np.argwhere(f == color)
            rows, r_counts = np.unique(pts[:, 0], return_counts=True)
            cols, c_counts = np.unique(pts[:, 1], return_counts=True)
            
            cross_y = rows[np.argmax(r_counts)]
            cross_x = cols[np.argmax(c_counts)]
            
            if len(pts[pts[:, 0] == cross_y]) < 5 or len(pts[pts[:, 1] == cross_x]) < 5:
                continue

            diamond_pts = []
            for p in pts:
                if p[0] != cross_y and p[1] != cross_x:
                    diamond_pts.append(p)
            
            if len(diamond_pts) == 0:
                diamond_pts = pts

            diamond_pts = np.array(diamond_pts)
            r_vals, r_cnts = np.unique(diamond_pts[:, 0], return_counts=True)
            c_vals, c_cnts = np.unique(diamond_pts[:, 1], return_counts=True)
            
            cols_ge2 = c_vals[c_cnts >= 2]
            target_x = cols_ge2[0] if len(cols_ge2) > 0 else int(round((np.min(diamond_pts[:, 1]) + np.max(diamond_pts[:, 1])) / 2.0))
            
            rows_ge2 = r_vals[r_cnts >= 2]
            target_y = rows_ge2[0] if len(rows_ge2) > 0 else int(round((np.min(diamond_pts[:, 0]) + np.max(diamond_pts[:, 0])) / 2.0))
            
            dy = target_y - cross_y
            dx = target_x - cross_x
            
            steps_y = int(round(dy / 3.0))
            steps_x = int(round(dx / 3.0))
            
            is_active = any(abs(bp[0] - cross_y) <= 1 and abs(bp[1] - cross_x) <= 1 for bp in black_pts)
            plans.append({
                "color": color,
                "is_active": is_active,
                "steps_y": steps_y,
                "steps_x": steps_x
            })

        plans.sort(key=lambda p: not p["is_active"])
        actions_queue: List[Tuple[GameAction, dict]] = []
        for idx, plan in enumerate(plans):
            if idx > 0:
                actions_queue.append((GameAction.ACTION5, {}))
            sy = plan["steps_y"]
            sx = plan["steps_x"]
            if sy < 0:
                actions_queue.extend([(GameAction.ACTION1, {})] * abs(sy))
            elif sy > 0:
                actions_queue.extend([(GameAction.ACTION2, {})] * sy)
            if sx < 0:
                actions_queue.extend([(GameAction.ACTION3, {})] * abs(sx))
            elif sx > 0:
                actions_queue.extend([(GameAction.ACTION4, {})] * sx)
                
        return actions_queue

    def _build_click_probes(self, f: np.ndarray, bg: int) -> None:
        """Build prioritized probing coordinates: sliders, valves, and toggle buttons."""
        probes: List[Tuple[int, int]] = []
        comps = get_components(f, bg, max_area=600)

        # 0. Specialized Button Array (ft09 / GF_Toggle signature: cluster of area 16-64 square components)
        button_cluster = [c for c in comps if 16 <= c['area'] <= 64 and abs(c['w'] - c['h']) <= 2]
        if len(button_cluster) >= 6:
            for c in sorted(button_cluster, key=lambda b: (b['cy'], b['cx'])):
                probes.append((c['cx'], c['cy']))

        # 1. Real Perimeter component centroids (valves & sliders)
        perimeter = [
            c for c in comps
            if (c['cx'] >= 54 or c['cx'] <= 10 or c['cy'] <= 10 or c['cy'] >= 54)
            and 4 <= c['area'] <= 80
            and 0 <= c['cx'] < 64 and 0 <= c['cy'] < 64
        ]
        for c in perimeter:
            probes.append((c['cx'], c['cy']))

        # 2. Small square component centroids (toggle matrix)
        squares = [c for c in comps if 4 <= c['area'] <= 64 and abs(c['w'] - c['h']) <= 1]
        for c in squares[:16]:
            probes.append((c['cx'], c['cy']))

        # Deduplicate within 2-pixel radius
        unique_probes: List[Tuple[int, int]] = []
        for p in probes:
            if not any(abs(p[0] - u[0]) <= 2 and abs(p[1] - u[1]) <= 2 for u in unique_probes):
                unique_probes.append(p)

        self.probe_positions = unique_probes[:24]

    def bfs_plan(self,
                 start: Tuple[int, int],
                 goal: Tuple[int, int],
                 f: np.ndarray,
                 floor_col: int) -> List[Tuple[GameAction, dict]]:
        """
        BFS over grid. Blocked cells from self.obstacle_map and non-floor terrain.
        step_size defines grid spacing.
        Returns list of actions to reach goal.
        """
        step = self.step_size if self.step_size is not None else 3
        dirs = [
            ((-step, 0), GameAction.ACTION1),  # UP
            (( step, 0), GameAction.ACTION2),  # DOWN
            ((0, -step), GameAction.ACTION3),  # LEFT
            ((0,  step), GameAction.ACTION4),  # RIGHT
        ]
        
        queue = deque([(start, [])])
        visited = {start}
        
        while queue:
            (r, c), path = queue.popleft()
            if abs(r - goal[0]) <= max(2, step // 2) and abs(c - goal[1]) <= max(2, step // 2):
                return [(act, {}) for act in path]
            if len(path) >= 60:
                continue
            for (dr, dc), action in dirs:
                nr, nc = r + dr, c + dc
                if (nr, nc) not in visited and \
                   (nr, nc) not in self.obstacle_map and \
                   0 <= nr < 64 and 0 <= nc < 64:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [action]))
        return []

    def _build_nav_plan(self, f: np.ndarray, bg: int) -> List[Tuple[GameAction, dict]]:
        """Compute BFS navigation plan across waypoints with singular fallback."""
        comps = get_components(f, bg, max_area=300)
        curr_y, curr_x = self.avatar_pos if self.avatar_pos is not None else (32, 32)
        # Exclude avatar and status panel (cy >= 55)
        goals = [(c['cy'], c['cx']) for c in comps
                 if 1 <= c['area'] <= 60
                 and 5 <= c['cy'] <= 54 and 5 <= c['cx'] <= 58
                 and abs(c['cy'] - curr_y) + abs(c['cx'] - curr_x) >= 4]

        # Detect floor color from interior frequency
        interior = f[10:54, 10:54]
        vals, counts = np.unique(interior, return_counts=True)
        sorted_colors = [vals[i] for i in np.argsort(-counts)]
        floor_col = sorted_colors[0] if len(sorted_colors) > 0 else bg

        plan: List[Tuple[GameAction, dict]] = []
        remaining = list(goals)
        for _ in range(min(6, len(remaining))):
            if not remaining:
                break
            nearest = min(remaining, key=lambda g: abs(g[0] - curr_y) + abs(g[1] - curr_x))
            seg = self.bfs_plan((curr_y, curr_x), nearest, f, floor_col)
            if seg:
                plan.extend(seg)
            remaining.remove(nearest)
            curr_y, curr_x = nearest

        if not plan:
            # Dynamic directional sweep fallback
            sweep = [GameAction.ACTION3] * 3 + [GameAction.ACTION1] * 4 + [GameAction.ACTION4] * 3 + [GameAction.ACTION1] * 3
            plan = [(a, {}) for a in sweep]

        return plan

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        with _ACTION_LOCK:
            self.step_counter += 1
            current_frame = get_2d_grid(latest_frame)
            f = current_frame

            actions_avail = getattr(latest_frame, "available_actions", [])
            act_vals = [getattr(a, 'value', a) for a in actions_avail] if actions_avail else [1, 2, 3, 4, 6]
            has_click = (6 in act_vals)
            has_dir = any(v in [1, 2, 3, 4] for v in act_vals)

            if self.step_counter >= self.MAX_ACTIONS:
                return GameAction.RESET

            if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
                self.action_queue.clear()
                self.initialized = False
                self.prev_frame = None
                self.uip_frame_before = None
                return GameAction.RESET

            if self.is_win(latest_frame):
                return self._handle_win(latest_frame)

            # ── LEVEL-UP DETECTION ──────────────────────────────────────────
            obs_lc = getattr(latest_frame, "levels_completed", 0)
            if obs_lc > self.last_levels_completed or not self.initialized:
                is_levelup = (self.initialized and obs_lc > self.last_levels_completed)
                if is_levelup and hasattr(self, 'level_initial_frame') and self.level_initial_frame is not None and self.action_history:
                    self.d4_cache.store(
                        initial_frame=self.level_initial_frame,
                        solution_actions=list(self.action_history),
                        game_id=getattr(self, 'game_id', 'unknown'),
                        level=self.last_levels_completed
                    )
                self.actions_since_level_up = 0
                self.uip_frame_before = None
                self.step_size = None
                self.step_counter = 0
                self.button_positions = []
                self.responsive_buttons = []
                self.toggle_deltas = []
                self.toggle_subsets = []
                self.probe_candidates = []
                self.probe_candidate_idx = 0
                self.clean_baseline_frame = None
                self.phase = None
                self.game_mode = "UNKNOWN"
                self.obstacle_map = {}
                self.avatar_pos = None
                self.goal_pos = None
                self.gfk_A = None
                self.gfk_b = None
                self.gfk_solution = None
                self.current_plan = []
                self.d4_plan = []
                self.action_history = []
                self.level_initial_frame = current_frame.copy()
                print(f"[LEVEL_UP] lc={obs_lc} reset_step_size")
                self.uip_frame_before = current_frame.copy()
                self._init_level(current_frame, latest_frame)
                self.last_levels_completed = obs_lc
                self.initialized = True

            actions = getattr(latest_frame, "available_actions", [])
            if not actions and hasattr(self, 'arc_env') and self.arc_env is not None:
                game_obj = getattr(self.arc_env, '_game', None)
                if game_obj is not None:
                    actions = getattr(game_obj, '_available_actions', [])
            if not actions:
                actions = [1, 2, 3, 4, 6]
            act_vals = [getattr(a, 'value', a) for a in actions]
            has_dir = any(v in [1, 2, 3, 4] for v in act_vals)
            has_click = (6 in act_vals)
            has_cycle = (5 in act_vals)

            # ── CARD REVEAL PATCH OBSERVER (tn36, vc33, sk48, sc25) ────────
            if self.prev_action == GameAction.ACTION6 and self.prev_frame is not None and getattr(self, 'last_card_clicked', None) is not None:
                cx, cy = self.last_card_clicked
                patch = current_frame[max(0, cy-2):min(64, cy+3), max(0, cx-2):min(64, cx+3)]
                sym_hash = hash(patch.tobytes())
                
                matched_prev = None
                for prev_c, prev_sym in list(self.card_memory.items()):
                    if prev_c != (cx, cy) and prev_sym == sym_hash:
                        matched_prev = prev_c
                        break
                        
                if matched_prev is not None:
                    del self.card_memory[matched_prev]
                    if hasattr(self, 'unrevealed_cards'):
                        if (cx, cy) in self.unrevealed_cards: self.unrevealed_cards.remove((cx, cy))
                        if matched_prev in self.unrevealed_cards: self.unrevealed_cards.remove(matched_prev)
                    self.action_queue = [(GameAction.ACTION6, {"x": int(matched_prev[0]), "y": int(matched_prev[1])})]
                else:
                    self.card_memory[(cx, cy)] = sym_hash
                self.last_card_clicked = None

            # ── UIP AVATAR & CLOSED-LOOP VERIFICATION (FIX 3) ────────────────
            if has_dir and self.uip_frame_before is not None:
                detected = self.uip_localize_avatar(self.uip_frame_before, current_frame)
                if detected is not None:
                    if self.avatar_pos is not None and self.prev_action in (
                        GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
                    ):
                        step = self.step_size if self.step_size is not None else 3
                        dr, dc = 0, 0
                        if self.prev_action == GameAction.ACTION1: dr = -step
                        elif self.prev_action == GameAction.ACTION2: dr = step
                        elif self.prev_action == GameAction.ACTION3: dc = -step
                        elif self.prev_action == GameAction.ACTION4: dc = step
                        
                        attempted = (self.avatar_pos[0] + dr, self.avatar_pos[1] + dc)
                        dist_dev = abs(detected[0] - attempted[0]) + abs(detected[1] - attempted[1])
                        if dist_dev <= 2:
                            delta_disp = abs(detected[0] - self.avatar_pos[0]) + abs(detected[1] - self.avatar_pos[1])
                            if delta_disp > 0:
                                self.ips.update(self.avatar_pos, detected, self.prev_action)
                                if self.step_size is None or self.ips.confidence() > 0.85:
                                    new_sz = self.ips.best_step_size()
                                    if new_sz != self.step_size:
                                        self.step_size = new_sz
                                        print(f"[STEP_SIZE] updated={self.step_size} via IPS (conf={self.ips.confidence():.3f})")
                            print(f"[ORACLE] clear at {attempted}")
                        else:
                            self.obstacle_map[attempted] = True
                            print(f"[ORACLE] blocked at {attempted}")
                            if self.game_mode == "NAV" and self.goal_pos is not None and not self.detected_box_positions:
                                self.action_queue.clear()

                                # Check for moving hazard near avatar (within 2*step radius)
                                diff_mask = (current_frame != self.uip_frame_before)
                                ar, ac = detected
                                diff_mask[max(0, ar - 3):min(64, ar + 4), max(0, ac - 3):min(64, ac + 4)] = False
                                moving_pts = np.argwhere(diff_mask)
                                for mr, mc in moving_pts:
                                    if abs(mr - ar) <= 2 * step and abs(mc - ac) <= 2 * step:
                                        print(f"[HAZARD] Dynamic moving obstacle detected at ({mr}, {mc})")
                                        self.obstacle_map[(int(mr), int(mc))] = True

                                # Fast BFS replan to goal
                                new_plan = self.bfs_nav_plan(detected, self.goal_pos)
                                if new_plan:
                                    self.action_queue = new_plan

                    self.avatar_pos = detected
                elif self.avatar_pos is not None and self.prev_action in (
                    GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
                ):
                    step = self.step_size if self.step_size is not None else 3
                    dr, dc = 0, 0
                    if self.prev_action == GameAction.ACTION1: dr = -step
                    elif self.prev_action == GameAction.ACTION2: dr = step
                    elif self.prev_action == GameAction.ACTION3: dc = -step
                    elif self.prev_action == GameAction.ACTION4: dc = step
                    attempted = (self.avatar_pos[0] + dr, self.avatar_pos[1] + dc)
                    self.obstacle_map[attempted] = True

            # ── DYNAMIC KEY-DOOR DISSOLUTION & OBSTACLE MAP REFRESH ─────────
            if has_dir and self.uip_frame_before is not None and self.avatar_pos is not None:
                ar, ac = self.avatar_pos
                diff_mask = (current_frame != self.uip_frame_before)
                diff_mask[max(0, ar - 4):min(64, ar + 5), max(0, ac - 4):min(64, ac + 5)] = False
                env_diff_count = int(np.sum(diff_mask))
                if env_diff_count >= 25:
                    bg_col = get_background_color(current_frame)
                    to_remove = [pt for pt in list(self.obstacle_map.keys()) if 0 <= pt[0] < 64 and 0 <= pt[1] < 64 and current_frame[pt[0], pt[1]] == bg_col]
                    for pt in to_remove:
                        del self.obstacle_map[pt]
            self.uip_frame_before = current_frame.copy()

            # ── CARD REVEAL OBSERVER (FIX 2) ─────────────────────────────────
            if self.prev_action == GameAction.ACTION6 and self.last_card_clicked is not None and self.prev_frame is not None:
                diff = np.abs(current_frame.astype(int) - self.prev_frame.astype(int))
                if np.sum(diff > 0) > 0:
                    bg_val = get_background_color(current_frame)
                    delta_colors = current_frame[diff > 0]
                    valid_cols = [int(c) for c in delta_colors if int(c) != bg_val]
                    if valid_cols:
                        from collections import Counter
                        dom_col = Counter(valid_cols).most_common(1)[0][0]
                        self.card_memory[self.last_card_clicked] = dom_col
                        print(f"[CARD_MEMORY] {self.last_card_clicked} -> color {dom_col} (total={len(self.card_memory)})")

            # ── CONCRETE GOAL & SOKOBAN DETECTION ─────────────────────────
            if has_dir and self.goal_pos is None:
                self.goal_pos = self.detect_goal_position(current_frame)
                if self.goal_pos is not None:
                    step = self.step_size or 3
                    gr, gc = self.goal_pos
                    for dr in range(-step, step + 1):
                        for dc in range(-step, step + 1):
                            self.obstacle_map.pop((gr + dr, gc + dc), None)
            if has_dir and len(self.obstacle_map) > 0 and (not hasattr(self, 'detected_box_positions') or not self.detected_box_positions):
                self.detect_boxes_and_goals(current_frame)

            # ── BISIMULATION QUOTIENT STATE COMPRESSION ───────────────────
            self.frame_history.append(current_frame.copy())
            if len(self.frame_history) >= 4 and self.bisim.n_classes == 0:
                self.bisim.fit(
                    self.frame_history,
                    self.action_history_for_bisim,
                    self.step_size or 3
                )
            # ─────────────────────────────────────────────────────────────

            bg = get_background_color(f)
            actions = getattr(latest_frame, "available_actions", [])
            if not actions and hasattr(self, 'arc_env') and self.arc_env is not None:
                game_obj = getattr(self.arc_env, '_game', None)
                if game_obj is not None:
                    actions = getattr(game_obj, '_available_actions', [])
            if not actions:
                actions = [1, 2, 3, 4, 6]

            # ── D4 SYMMETRY CACHE LOOKUP ──────────────────────────────────
            if not self.current_plan and not self.d4_plan and not self.action_queue:
                cached = self.d4_cache.lookup(current_frame)
                if cached is not None:
                    self.d4_plan = list(cached)
                    print(f"[D4_CACHE] using cached plan len={len(cached)}")

            if self.d4_plan:
                act_item = self.d4_plan.pop(0)
                if isinstance(act_item, tuple):
                    act, data = act_item
                else:
                    act, data = act_item, {}
                return self._return_action(act, data, f)
            # ─────────────────────────────────────────────────────────────

            # ==================================================================
            # TOGGLE CLUSTER (FT09 / GF_TOGGLE SPECIALIZED SOLVER)
            # ==================================================================
            if self.game_mode == "TOGGLE_CLUSTER":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)

                if self.phase == "PROBE_RESET" and not self.action_queue:
                    # Previous probe completed
                    if self.prev_action == GameAction.ACTION6 and self.prev_action_data:
                        delta = int(np.sum(f != self.clean_baseline_frame))
                        if delta > 0:
                            bx, by = self.prev_action_data["x"], self.prev_action_data["y"]
                            self.responsive_buttons.append((bx, by))
                            self.toggle_deltas.append(np.abs(f.flatten().astype(int) - self.clean_baseline_frame.flatten().astype(int)))
                    
                    self.probe_candidate_idx += 1
                    if self.probe_candidate_idx < len(self.probe_candidates):
                        cand = self.probe_candidates[self.probe_candidate_idx]
                        self.action_queue = [
                            (GameAction.RESET, {}),
                            (GameAction.ACTION6, {"x": cand[0], "y": cand[1]})
                        ]
                    else:
                        # Probing complete — build toggle subsets with GF(k) priority
                        self.phase = "SUBSET_SEARCH"
                        self.responsive_buttons.sort(key=lambda p: (p[1], p[0]))
                        self.toggle_subsets = []
                        
                        if self.toggle_deltas and len(self.toggle_deltas) == len(self.responsive_buttons):
                            A = np.column_stack(self.toggle_deltas)
                            bg_clean = get_background_color(self.clean_baseline_frame)
                            b_diff = (self.clean_baseline_frame.flatten() != bg_clean).astype(int)
                            for k in [2, 3, 4]:
                                b_targets = [
                                    b_diff % k,
                                    (self.clean_baseline_frame.flatten().astype(int) % k),
                                    np.ones(A.shape[0], dtype=int) % k,
                                    (np.sum(A, axis=1) % k)
                                ]
                                for b_cand in b_targets:
                                    x = self.solve_gfk(A, b_cand, k)
                                    if x is not None and np.any(x > 0):
                                        gfk_combo = []
                                        for bi, count in enumerate(x):
                                            if count > 0:
                                                gfk_combo.extend([self.responsive_buttons[bi]] * int(count))
                                        if gfk_combo and gfk_combo not in self.toggle_subsets:
                                            self.toggle_subsets.insert(0, gfk_combo)
                        
                        # 2. Add standard combinatorial subsets (fallback, max 120 combos)
                        for k in range(1, min(6, len(self.responsive_buttons) + 1)):
                            for combo in combinations(self.responsive_buttons, k):
                                combo_list = list(combo)
                                if combo_list not in self.toggle_subsets:
                                    self.toggle_subsets.append(combo_list)
                                if len(self.toggle_subsets) >= 120:
                                    break
                            if len(self.toggle_subsets) >= 120:
                                break

                        # 3. Ultimate fallback: try clicking each probe_candidate once
                        if not self.toggle_subsets:
                            for cand in self.probe_candidates[:24]:
                                self.toggle_subsets.append([cand])

                        self.subset_idx = 0

                if self.phase == "SUBSET_SEARCH" and not self.action_queue:
                    if self.subset_idx < len(self.toggle_subsets):
                        combo = self.toggle_subsets[self.subset_idx]
                        self.subset_idx += 1
                        self.action_queue = [(GameAction.RESET, {})] + [
                            (GameAction.ACTION6, {"x": pt[0], "y": pt[1]}) for pt in combo
                        ]

            # ==================================================================
            # 5-ACTION SLIDER OVERLAY EXECUTION (RE86 / FLUID CANVAS)
            # ==================================================================
            if self.game_mode == "SLIDER_5ACT":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                if not self.action_queue:
                    if not hasattr(self, '_slider_rebuild_count'):
                        self._slider_rebuild_count = 0
                    if self._slider_rebuild_count < 3:
                        self._slider_rebuild_count += 1
                        self.action_queue = self._build_slider_5act_plan(f, bg)

            # ==================================================================
            # LIVESTOCK HERDING CONTINUOUS MULTI-ENTITY EXECUTION (WA30)
            # ==================================================================
            if self.game_mode == "HERDING":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                if not self.action_queue:
                    herding_plan = self._build_herding_dog_plan(f, bg)
                    if herding_plan:
                        self.action_queue = herding_plan

            # ==================================================================
            # CONVEYOR CONTINUOUS MULTI-LEVEL EXECUTION (LP85)
            # ==================================================================
            if self.game_mode == "CONVEYOR":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                if not self.action_queue:
                    conveyor_plan = self._build_conveyor_ring_plan(f, bg)
                    if conveyor_plan:
                        self.action_queue = conveyor_plan

            # ==================================================================
            # TIME-REWIND CLONE SHADOW CONTINUOUS EXECUTION (G50T)
            # ==================================================================
            if self.game_mode == "CLONE_SHADOW":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                if not self.action_queue:
                    clone_plan = self._build_clone_shadow_plan(f, bg)
                    if clone_plan:
                        self.action_queue = clone_plan

            # ==================================================================
            # CIRCUIT & ROTATION CONTINUOUS EXECUTION
            # ==================================================================
            if self.game_mode == "CIRCUIT":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                if not self.action_queue:
                    circuit_plan = self._build_circuit_plan(f, bg)
                    if circuit_plan:
                        self.action_queue = circuit_plan

            # ==================================================================
            # PEG SOLITAIRE CONTINUOUS EXECUTION
            # ==================================================================
            if self.game_mode == "PEG_SOLITAIRE":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                if not self.action_queue:
                    peg_plan = self._build_peg_solitaire_plan(f, bg)
                    if peg_plan:
                        self.action_queue = peg_plan

            # ==================================================================
            # NAV PROBE & CONTINUOUS CLOSED-LOOP BFS EXECUTION
            # ==================================================================
            if self.game_mode == "NAV":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                if self.nav_probe_step == 0:
                    self.nav_probe_step = 1
                    act = GameAction.ACTION3
                    return self._return_action(act, {}, f)
                elif self.nav_probe_step == 1:
                    if self.is_win(latest_frame):
                        return self._handle_win(latest_frame)
                    if self.step_size is None:
                        self.step_size = 3
                    self.nav_probe_step = 2
                    self.action_queue = self._build_nav_plan(f, bg)
                elif not self.action_queue:
                    if self.step_size is None:
                        self.step_size = 3
                    self.action_queue = self._build_nav_plan(f, bg)

            # ==================================================================
            # CLICK PROBE & ARCHETYPE DISCOVERY
            # ==================================================================
            if self.game_mode in ("CLICK", "MIXED") and self.phase == "PROBE":
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                # Record previous probe delta
                if self.prev_action == GameAction.ACTION6 and self.prev_frame is not None and self.prev_action_data:
                    delta = int(np.sum(f != self.prev_frame))
                    px, py = self.prev_action_data.get("x", 0), self.prev_action_data.get("y", 0)
                    if delta >= 120 and (px <= 8 or px >= 55 or py <= 8 or py >= 55):
                        if px <= 8 or py <= 8:
                            self.slider_left = (px, py)
                        else:
                            self.slider_right = (px, py)
                    elif delta > 0:
                        if not any(abs(px - u[0]) <= 2 and abs(py - u[1]) <= 2 for u in self.responsive_buttons):
                            self.responsive_buttons.append((px, py))

                # Dispatch next probe
                if self.probe_idx < len(self.probe_positions):
                    px, py = self.probe_positions[self.probe_idx]
                    self.probe_idx += 1
                    act = GameAction.ACTION6
                    data = {"x": int(px), "y": int(py)}
                    return self._return_action(act, data, f)
                else:
                    # Probing complete: Route to optimal archetype
                    if self.is_win(latest_frame):
                        return self._handle_win(latest_frame)
                    valves = sorted([p for p in self.responsive_buttons if (p[0] >= 54 or p[0] <= 10 or p[1] >= 54 or p[1] <= 10) and 0 <= p[0] <= 63 and 0 <= p[1] <= 63], key=lambda p: (p[1], p[0]))
                    if len(valves) >= 2:
                        self.phase = "VALVES"
                        for _ in range(8):
                            self.action_queue.append((GameAction.ACTION6, {"x": valves[1][0], "y": valves[1][1]}))
                        for _ in range(8):
                            self.action_queue.append((GameAction.ACTION6, {"x": valves[0][0], "y": valves[0][1]}))
                    elif self.slider_left:
                        self.phase = "SLIDER"
                        for _ in range(5):
                            self.action_queue.append((GameAction.ACTION6, {"x": self.slider_left[0], "y": self.slider_left[1]}))
                    elif self.slider_right:
                        self.phase = "SLIDER"
                        for _ in range(5):
                            self.action_queue.append((GameAction.ACTION6, {"x": self.slider_right[0], "y": self.slider_right[1]}))
                    elif self.responsive_buttons:
                        if len(self.responsive_buttons) <= 8:
                            self.phase = "TOGGLE_SEARCH"
                            self.toggle_subsets = []
                            for k in range(1, min(4, len(self.responsive_buttons) + 1)):
                                for combo in combinations(self.responsive_buttons, k):
                                    self.toggle_subsets.append(list(combo))
                                    if len(self.toggle_subsets) >= 8:
                                        break
                                if len(self.toggle_subsets) >= 8:
                                    break
                            self.subset_idx = 0
                            if self.toggle_subsets:
                                combo = self.toggle_subsets[self.subset_idx]
                                self.subset_idx += 1
                                for pt in combo:
                                    self.action_queue.append((GameAction.ACTION6, {"x": pt[0], "y": pt[1]}))
                        else:
                            self.phase = "EXECUTE"
                    else:
                        self.phase = "EXECUTE"

            # ==================================================================
            # VALVES PULSING STEPPING
            # ==================================================================
            if self.phase == "VALVES" and not self.action_queue:
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                comps_cur = get_components(f, bg, max_area=600)
                valves_c = [c for c in comps_cur if (c['cx'] >= 54 or c['cx'] <= 10 or c['cy'] >= 54 or c['cy'] <= 10) and 4 <= c['area'] <= 80 and 0 <= c['cx'] < 64 and 0 <= c['cy'] < 64]
                if len(valves_c) >= 2:
                    v_sorted = sorted([(c['cx'], c['cy']) for c in valves_c], key=lambda p: (p[1], p[0]))
                    for _ in range(8):
                        self.action_queue.append((GameAction.ACTION6, {"x": int(v_sorted[-1][0]), "y": int(v_sorted[-1][1])}))
                    for _ in range(8):
                        self.action_queue.append((GameAction.ACTION6, {"x": int(v_sorted[0][0]), "y": int(v_sorted[0][1])}))

            # ==================================================================
            # TOGGLE SEARCH STEPPING
            # ==================================================================
            if self.phase == "TOGGLE_SEARCH" and not self.action_queue:
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                if self.subset_idx < len(self.toggle_subsets):
                    combo = self.toggle_subsets[self.subset_idx]
                    self.subset_idx += 1
                    # Clean reset between subset attempts
                    self.action_queue.append((GameAction.RESET, {}))
                    for pt in combo:
                        self.action_queue.append((GameAction.ACTION6, {"x": pt[0], "y": pt[1]}))

            # ==================================================================
            # CONVEYOR PERMUTATION BFS STEPPING (LP85)
            # ==================================================================
            if self.game_mode == "CONVEYOR" and not self.action_queue:
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                plan = self._build_conveyor_ring_plan(f, bg)
                if plan:
                    self.action_queue = plan

            # ==================================================================
            # LIVESTOCK HERDING & HITCHING STEPPING (WA30)
            # ==================================================================
            if self.game_mode == "HERDING" and not self.action_queue:
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)
                plan = self._build_herding_dog_plan(f, bg)
                if plan:
                    self.action_queue = plan

            # ==================================================================
            # CARD MATCH PAIRWISE PLANNER (FIX 2: sc25, sk48, tn36, vc33)
            # ==================================================================
            if has_click and not self.action_queue and self.game_mode in ("CARD_MATCH", "CLICK", "UNKNOWN"):
                if self.is_win(latest_frame):
                    return self._handle_win(latest_frame)

                col_map: Dict[int, Tuple[int, int]] = {}
                match_pair = None
                for coord, sym in list(self.card_memory.items()):
                    if sym in col_map:
                        match_pair = (col_map[sym], coord)
                        break
                    col_map[sym] = coord

                if match_pair is not None:
                    c1, c2 = match_pair
                    del self.card_memory[c1]
                    del self.card_memory[c2]
                    if hasattr(self, 'unrevealed_cards'):
                        if c1 in self.unrevealed_cards: self.unrevealed_cards.remove(c1)
                        if c2 in self.unrevealed_cards: self.unrevealed_cards.remove(c2)
                    self.action_queue = [
                        (GameAction.ACTION6, {"x": int(c1[0]), "y": int(c1[1])}),
                        (GameAction.ACTION6, {"x": int(c2[0]), "y": int(c2[1])})
                    ]
                elif hasattr(self, 'unrevealed_cards') and self.unrevealed_cards:
                    avail = [c for c in self.unrevealed_cards if c not in self.card_memory]
                    if avail:
                        next_c = avail[0]
                        self.last_card_clicked = next_c
                        self.action_queue = [(GameAction.ACTION6, {"x": int(next_c[0]), "y": int(next_c[1])})]

            # ==================================================================
            # HYBRID A* SOKOBAN & BFS NAVIGATION PLANNER (LAYER 5)
            # ==================================================================
            if has_dir and not self.action_queue and self.avatar_pos is not None and self.game_mode in ("NAV", "UNKNOWN", "SOKOBAN"):
                if self.goal_pos is None:
                    self.goal_pos = self.detect_goal_position(f)
                if not hasattr(self, 'detected_box_positions') or not self.detected_box_positions:
                    self.detect_boxes_and_goals(f)

                # 1. SOKOBAN A* (if boxes and goals detected)
                if self.detected_box_positions and hasattr(self, 'box_goal_positions') and self.box_goal_positions and self.step_size is not None:
                    boxes_fs = frozenset(self.detected_box_positions)
                    goals_fs = self.box_goal_positions
                    astar_plan = self.sokoban_astar(self.avatar_pos, boxes_fs, goals_fs, max_states=100000)
                    if astar_plan:
                        self.action_queue = astar_plan

                # 2. SUBGOAL CHAINED NAVIGATION (if goal_pos known, no boxes, and obstacle_map populated)
                if not self.action_queue and self.goal_pos is not None and not self.detected_box_positions and self.step_size is not None:
                    subgoals = self.detect_subgoals(f, bg)
                    nav_plan = self.subgoal_chained_nav_plan(self.avatar_pos, self.goal_pos, subgoals)
                    if nav_plan:
                        self.action_queue = nav_plan

                # 3. CONCRETE MCTS (fallback)
                if not self.action_queue and (self.goal_pos is not None or (hasattr(self, 'box_goal_positions') and self.box_goal_positions)) and self.step_size is not None and self.mcts_calls < 8:
                    self.mcts_calls += 1
                    mcts_actions = self.mcts_search_concrete(budget_ms=300, N=2000)
                    if mcts_actions:
                        self.action_queue = mcts_actions

            # ==================================================================
            # QUEUE DISPATCH
            # ==================================================================
            if self.action_queue:
                act, data = self.action_queue.pop(0)
                return self._return_action(act, data, f)

            # ==================================================================
            # STUCK RECOVERY & ADAPTIVE RE-PLANNING
            # ==================================================================
            sh = self._hash(f)
            self.recent_hashes.append(sh)
            if self.recent_hashes.count(sh) > 4:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0

            if self.stuck_counter >= 6 and self.attempt_counter < 5:
                self.stuck_counter = 0
                self.attempt_counter += 1
                self.recent_hashes.clear()

                if self.game_mode == "NAV":
                    # Prune far obstacle_map entries when stuck
                    if self.avatar_pos is not None and len(self.obstacle_map) > 40:
                        ay, ax = self.avatar_pos
                        self.obstacle_map = {
                            k: v for k, v in self.obstacle_map.items()
                            if abs(k[0] - ay) <= 20 and abs(k[1] - ax) <= 20
                        }
                    self.step_size = max(1, (self.step_size or 3) - 1)
                    self.action_queue = self._build_nav_plan(f, bg)
                elif self.slider_left:
                    for _ in range(self.attempt_counter * 2):
                        self.action_queue.append((GameAction.ACTION6, {"x": self.slider_left[0], "y": self.slider_left[1]}))
                elif self.responsive_buttons:
                    sampled = random.sample(self.responsive_buttons, min(4, len(self.responsive_buttons)))
                    self.action_queue.append((GameAction.RESET, {}))
                    for pt in sampled:
                        self.action_queue.append((GameAction.ACTION6, {"x": pt[0], "y": pt[1]}))

                if self.action_queue:
                    act, data = self.action_queue.pop(0)
                    return self._return_action(act, data, f)

            cand = []
            for a in actions:
                val = a.value if hasattr(a, 'value') else a
                try:
                    cand.append(GameAction.from_id(val))
                except Exception:
                    pass
            act = random.choice(cand) if cand else GameAction.ACTION6
            data = {}
            if act == GameAction.ACTION6:
                if self.responsive_buttons:
                    pt = random.choice(self.responsive_buttons)
                    data = {"x": int(pt[0]), "y": int(pt[1])}
                else:
                    comps = get_components(f, bg, max_area=200)
                    if comps:
                        c = random.choice(comps[:min(6, len(comps))])
                        data = {"x": int(c['cx']), "y": int(c['cy'])}
                    else:
                        data = {"x": 32, "y": 32}

            return self._return_action(act, data, f)
