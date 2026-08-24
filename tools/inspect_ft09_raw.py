import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

import numpy as np
import json
from tools.diagnose_ft09 import run_seed_diagnostic, get_2d_grid, get_background_color, get_components
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

for seed in range(5):
    res = run_seed_diagnostic(seed)
    print(f"\n==================== SEED {seed} REPORT ====================")
    print(f"seed_id: {res['seed_id']}")
    print(f"n_buttons: {res['n_buttons']}")
    print(f"matrix_rank_real: {res['matrix_rank_real']}")
    print(f"matrix_rank_gf2: {res['matrix_rank_gf2']}")
    print(f"win_achieved: {res['win_achieved']}")
    print(f"win_sequence: {res['win_sequence']}")
    print(f"steps_used: {res['steps_used']}")
