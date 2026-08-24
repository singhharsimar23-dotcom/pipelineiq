"""
Test ka59 Level 0 exact geometric solution across 5 seeds.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_ka59_exact():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    for seed in range(5):
        env = arcade.make("ka59", seed=seed)
        obs = env.reset()
        game = env._game

        # Block 0 starts at (9, 21). Target 0 needs (3, 24).
        # Move Left twice: (9, 21) -> (6, 21) -> (3, 21)
        env.step(GameAction.ACTION3)
        env.step(GameAction.ACTION3)
        # Move Down once: (3, 21) -> (3, 24) [EXACT MATCH FOR TARGET 0]
        env.step(GameAction.ACTION2)

        # Switch active block to Block 1 at (18, 21): display pos = (18 + 9, 21 + 9) = (27, 30)
        env.step(GameAction.ACTION6, data={"x": 27, "y": 30})

        # Target 1 needs (36, 18).
        # Move Block 1 Right x5: (18, 21) -> (33, 21)
        for _ in range(5):
            env.step(GameAction.ACTION4)
        # Move Block 1 Up once: (33, 21) -> (33, 18)
        env.step(GameAction.ACTION1)
        # Move Block 1 Right once: (33, 18) -> (36, 18) [EXACT MATCH FOR TARGET 1]
        obs = env.step(GameAction.ACTION4)
        
        print(f"Seed {seed}: win={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
        
    print(f"KA59 EXACT MULTI-SEED SCORES: {scores}")

if __name__ == "__main__":
    test_ka59_exact()
