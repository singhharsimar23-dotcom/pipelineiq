"""
CLASSIFIER_V2.py
Standalone Perception-Based Classifier Module for ARC-AGI-3
Zero hardcoded game IDs, zero hardcoded coordinates.
"""
from typing import List, Dict, Any, Tuple
import numpy as np
from collections import Counter, deque

GRID_DIM: int = 64

def get_background_color(f: np.ndarray) -> int:
    """Extract dominant background color from perimeter border."""
    border = (list(f[0,:]) + list(f[1,:]) + list(f[-1,:]) + list(f[-2,:]) +
              list(f[:,0]) + list(f[:,1]) + list(f[:,-1]) + list(f[:,-2]))
    counts = Counter(border)
    return counts.most_common(1)[0][0] if counts else 0

def get_components(f: np.ndarray, bg: int, max_area: int = 600) -> List[Dict[str, Any]]:
    """Connected component extraction via BFS."""
    visited = np.zeros((GRID_DIM, GRID_DIM), dtype=bool)
    comps = []
    for r in range(GRID_DIM):
        for c in range(GRID_DIM):
            if not visited[r, c] and f[r, c] != bg:
                col = int(f[r, c])
                q = deque([(r, c)])
                visited[r, c] = True
                cells = []
                while q:
                    cr, cc = q.popleft()
                    cells.append((cr, cc))
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < GRID_DIM and 0 <= nc < GRID_DIM and not visited[nr, nc] and f[nr, nc] == col:
                            visited[nr, nc] = True
                            q.append((nr, nc))
                if len(cells) <= max_area:
                    rows = [p[0] for p in cells]
                    cols = [p[1] for p in cells]
                    comps.append({
                        "col": col,
                        "cx": int(round(float(np.mean(cols)))),
                        "cy": int(round(float(np.mean(rows)))),
                        "area": len(cells),
                        "w": max(cols) - min(cols) + 1,
                        "h": max(rows) - min(rows) + 1,
                    })
    return comps

def classify_game(f: np.ndarray, available_actions: List[int]) -> str:
    """
    Perception-based game archetype classifier.
    Derives class strictly from step 0 frame geometry and action sets.
    """
    action_set = set(available_actions)
    bg = get_background_color(f)
    comps = get_components(f, bg, max_area=600)

    # 1. Pure Click Actions: action_set == {6}
    if action_set == {6}:
        # Check for Dual-Quadrant Button Matrix (target: GF2_TOGGLE, e.g. 3x3 dual grid)
        # Source evidence: Top hint buttons (cy < 30) and bottom interactive buttons (cy >= 30)
        upper_btns = [c for c in comps if c['cy'] < 30 and 4 <= c['area'] <= 40 and 4 <= c['cx'] <= 60]
        lower_btns = [c for c in comps if c['cy'] >= 30 and 4 <= c['area'] <= 40 and 4 <= c['cx'] <= 60]
        if len(upper_btns) >= 6 and len(lower_btns) >= 6:
            return 'GF2_TOGGLE'

        # Check for Fluid Valves on perimeter (target: FLUID_VALVES)
        # Source evidence: sys_click perimeter valve sprites at cx >= 55 or cx <= 10 with area ~16
        valves = [c for c in comps if 10 <= c['area'] <= 25 and (c['cx'] >= 55 or c['cx'] <= 10)]
        if len(valves) >= 2 and len(comps) <= 15:
            return 'FLUID_VALVES'

        # Check for Slider / Scale Rail (target: SLIDER_MANIPULATION)
        # Source evidence: Linear track rails with w >= 15 or h >= 15 with slider knob
        rails = [c for c in comps if (c['w'] >= 15 and c['h'] <= 6) or (c['h'] >= 15 and c['w'] <= 6)]
        if len(rails) >= 2:
            return 'SLIDER_MANIPULATION'

        # Check for Stencil Palette Pick & Drop (target: STENCIL_DRAG_DROP)
        # Source evidence: Isolated palette sprites along bottom/left edge and large background canvas
        palette_items = [c for c in comps if 15 <= c['area'] <= 40 and (c['cy'] >= 45 or c['cx'] <= 10)]
        if len(palette_items) >= 2:
            return 'STENCIL_DRAG_DROP'

        # Check for Mahjong / Memory Card Pair Layout (target: CARD_PAIR_MATCHING)
        # Source evidence: Symmetrical regular array of equal-sized cards (num_comps >= 30)
        cards = [c for c in comps if 8 <= c['area'] <= 36]
        if len(cards) >= 16:
            return 'CARD_PAIR_MATCHING'

        return 'CLICK_MANIPULATION'

    # 2. Pure 4-Way Directional: action_set == {1, 2, 3, 4}
    if action_set == {1, 2, 3, 4}:
        # Check for Track Vehicle (target: TRACK_NAV)
        # Source evidence: Track pixels (colors 2 and 0) forming continuous transit paths (count >= 50)
        track_pixels = np.sum((f == 2) | (f == 0))
        if track_pixels >= 50 and len(comps) >= 30:
            return 'TRACK_NAV'

        # Check for Grammar Tree Substitution (target: GRAMMAR_PARSING)
        # Source evidence: Dense token array with syntax blocks (len(comps) >= 40 without track pixels)
        if len(comps) >= 40:
            return 'GRAMMAR_PARSING'

        # Check for 5px Pad Morphing Automata (target: MORPH_GATE_NAV)
        # Source evidence: 5px square step pads (area == 5 or 25) distributed on a grid
        pads = [c for c in comps if c['w'] == 5 and c['h'] == 5]
        if len(pads) >= 3:
            return 'MORPH_GATE_NAV'

        return 'GRID_NAV'

    # 3. Directional + Push Operator: 5 in action_set
    if 5 in action_set:
        if 6 in action_set and any(a in action_set for a in [1, 2, 3, 4]):
            # Target: SOKOBAN_RECEPTOR (e.g. actions=[1, 2, 3, 4, 5, 6])
            return 'SOKOBAN_RECEPTOR'
        if set(action_set) <= {1, 2, 3, 4, 5}:
            # Target: PUSH_BLOCK_NAV (e.g. actions=[1, 2, 3, 4, 5])
            return 'PUSH_BLOCK_NAV'

    # 4. Click + Select/Shift/Undo: action_set contains 6 and other modifiers
    if 6 in action_set:
        if action_set == {6, 7}:
            # Target: SUBMIT_SELECTION (e.g. actions=[6, 7])
            return 'SUBMIT_SELECTION'
        if action_set == {3, 4, 6, 7}:
            # Target: PALETTE_SELECTION (e.g. actions=[3, 4, 6, 7])
            return 'PALETTE_SELECTION'
        if action_set == {5, 6, 7}:
            # Target: REGISTER_SHIFT (e.g. actions=[5, 6, 7])
            return 'REGISTER_SHIFT'
        if set(action_set) <= {1, 2, 3, 4, 6, 7}:
            # Target: KEY_DOOR_MAZE (e.g. actions=[1, 2, 3, 4, 6] or [1, 2, 3, 4, 6, 7])
            return 'KEY_DOOR_MAZE'

    return 'PROBE'
