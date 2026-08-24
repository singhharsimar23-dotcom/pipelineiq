"""
Test lf52 solve with exact grid offset (10, 5).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_lf52_exact():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    
    # Moves: (from_gx, from_gy), (to_gx, to_gy)
    moves = [
        ((1, 2), (3, 2)),
        ((3, 2), (5, 2)),
        ((5, 2), (5, 4)),
        ((5, 4), (5, 6)),
    ]
    
    ox, oy = 10, 5
    
    for seed in range(5):
        env = arcade.make("lf52", seed=seed)
        obs = env.reset()
        game = env._game
        world = game.ikhhdzfmarl
        
        for (fx, fy), (tx, ty) in moves:
            # Click from peg
            env.step(GameAction.ACTION6, data={"x": fx * 6 + ox + 3, "y": fy * 6 + oy + 3})
            # Click to destination arrow
            obs = env.step(GameAction.ACTION6, data={"x": tx * 6 + ox + 3, "y": ty * 6 + oy + 3})
            
        print(f"Seed {seed}: win_flag={world.iajuzrgttrv}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"LF52 EXACT MULTI-SEED SCORES: {scores}")

if __name__ == "__main__":
    test_lf52_exact()
