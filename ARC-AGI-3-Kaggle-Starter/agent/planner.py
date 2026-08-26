from collections import deque
from typing import List, Optional, Callable, Dict
import numpy as np
from .abstract_state import AbstractState
from .game_program import GameProgram


def goal_predicate(state: AbstractState) -> bool:
    """Avatar position overlaps any known goal entity bbox."""
    if state.avatar_id is None:
        return False
    avatar = state.entities.get(state.avatar_id)
    if avatar is None:
        return False
    ax, ay = avatar.position
    for gid in state.goal_ids:
        goal = state.entities.get(gid)
        if goal is None:
            continue
        xmin, ymin, xmax, ymax = goal.bbox
        if (xmin - 2) <= ax <= (xmax + 2) and (ymin - 2) <= ay <= (ymax + 2):
            return True
    return False


def plan_against_program(
    program: GameProgram,
    initial_state: AbstractState,
    goal_fn: Callable = goal_predicate,
    budget: int = 10_000_000,
    action_set: List[int] = None
) -> List[int]:
    if action_set is None:
        action_set = [1, 2, 3, 4] + list(program.active_special_actions or [])
    if goal_fn(initial_state):
        return []
    queue = deque([(initial_state, [])])
    visited = {initial_state.state_hash}
    nodes_expanded = 0
    while queue and nodes_expanded < budget:
        state, path = queue.popleft()
        nodes_expanded += 1
        for action in action_set:
            next_state = program.simulate(state, action)
            if next_state.state_hash in visited:
                continue
            visited.add(next_state.state_hash)
            new_path = path + [action]
            if goal_fn(next_state):
                print(f"BFS: plan_length={len(new_path)}, nodes_expanded={nodes_expanded}")
                return new_path
            queue.append((next_state, new_path))
    print(f"BFS: budget {budget} exhausted. Trying greedy fallback.")
    return _greedy_fallback(program, initial_state, goal_fn, action_set)


def _greedy_fallback(program, state, goal_fn, action_set, budget=100_000):
    best_path = []
    best_state = state
    steps = 0
    while not goal_fn(best_state) and steps < budget:
        best_action = None
        best_dist = float("inf")
        for action in action_set:
            next_s = program.simulate(best_state, action)
            if next_s.state_hash == best_state.state_hash:
                continue
            dist = _avatar_to_goal_distance(next_s)
            if dist < best_dist:
                best_dist = dist
                best_action = action
        if best_action is None:
            break
        best_state = program.simulate(best_state, best_action)
        best_path.append(best_action)
        steps += 1
    return best_path if goal_fn(best_state) else []


def _avatar_to_goal_distance(state: AbstractState) -> float:
    if state.avatar_id is None:
        return float("inf")
    avatar = state.entities.get(state.avatar_id)
    if avatar is None:
        return float("inf")
    ax, ay = avatar.position
    min_dist = float("inf")
    for gid in state.goal_ids:
        goal = state.entities.get(gid)
        if goal:
            gx, gy = goal.position
            min_dist = min(min_dist, abs(ax - gx) + abs(ay - gy))
    return min_dist
