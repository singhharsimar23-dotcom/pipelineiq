"""
Inspect GameAction behavior in arcengine.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arcengine import GameAction

def test_game_action():
    a = GameAction.ACTION6
    print(f"Type of a: {type(a)}")
    print(f"Dir of a: {dir(a)}")
    
    # Try set_data
    if hasattr(a, "set_data"):
        a.set_data({"x": 10, "y": 20})
        print(f"After set_data: a.data = {getattr(a, 'data', None)}")
    else:
        print("No set_data method!")

if __name__ == "__main__":
    test_game_action()
