import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction


def get_2d_grid(frame_data) -> np.ndarray:
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


def check_game(game_id: str):
    print(f"\n=======================================================")
    print(f"GAME: {game_id}")
    print(f"=======================================================")
    
    seeds = [0, 1, 2, 3, 4]
    values_by_seed = []
    
    arc = Arcade(operation_mode=OperationMode.OFFLINE)
    sc_id = arc.create_scorecard(tags=[f"check_seeds_{game_id}"])
    
    for s in seeds:
        env = arc.make(game_id, seed=s, scorecard_id=sc_id)
        obs = env.step(GameAction.RESET, data={})
        f = get_2d_grid(obs)
        
        # Pixel values at (38,38), (38,46), (46,38), (54,54)
        v_38_38 = int(f[38, 38])
        v_38_46 = int(f[38, 46])
        v_46_38 = int(f[46, 38])
        v_54_54 = int(f[54, 54])
        
        vals = (v_38_38, v_38_46, v_46_38, v_54_54)
        values_by_seed.append(vals)
        print(f"seed={s}, f[38,38]={v_38_38}, f[38,46]={v_38_46}, f[46,38]={v_46_38}, f[54,54]={v_54_54}")
    
    arc.close_scorecard(sc_id)
    
    # Check if identical across all 5 seeds
    all_identical = all(v == values_by_seed[0] for v in values_by_seed)
    if all_identical:
        print("\nSEED_VARIATION_ABSENT — OFFLINE mode serving fixed instance")


def main():
    games = ["cn04", "ft09", "dc22", "g50t"]
    for g in games:
        check_game(g)


if __name__ == "__main__":
    main()
