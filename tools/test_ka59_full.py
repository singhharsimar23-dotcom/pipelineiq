"""
Test moving both blocks to targets in ka59 Level 0.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

def test_ka59_full():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    scores = []
    for seed in range(5):
        env = arcade.make("ka59", seed=seed)
        obs = env.reset()
        game = env._game

        # Block 0 starts active at grid (9, 21).
        # Target 0 is at grid (2, 23).
        # Move Block 0 left twice: (9, 21) -> (3, 21)
        env.step(GameAction.ACTION3)
        env.step(GameAction.ACTION3)
        # Move Block 0 down once: (3, 21) -> (3, 24)
        env.step(GameAction.ACTION2)
        # Move Block 0 left once: (3, 24) -> (0, 24)
        env.step(GameAction.ACTION3)

        # Switch to Block 1 at grid (18, 21): display pos = (18 + 9, 21 + 9) = (27, 30)
        env.step(GameAction.ACTION6, data={"x": 27, "y": 30})

        # Target 1 is at grid (35, 17).
        # Move Block 1 right x5: (18, 21) -> (33, 21)
        for _ in range(5):
            env.step(GameAction.ACTION4)
        # Move Block 1 up once: (33, 21) -> (33, 18)
        for _ in range(2):
            env.step(GameAction.ACTION1)
        # Move Block 1 right: (33, 18) -> (36, 18)
        obs = env.step(GameAction.ACTION4)
        print(f"Seed {seed}: win={game.dbmlcqbquh()}, levels_completed={obs.levels_completed}")
        scores.append(obs.levels_completed)
    print(f"KA59 Multi-Seed Scores: {scores}")

if __name__ == "__main__":
    test_ka59_full()
