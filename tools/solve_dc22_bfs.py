"""
DC22 - full BFS state search: try all combinations of button clicks before navigation.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter"))
sys.path.insert(0, str(ROOT / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents"))

from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from collections import deque

def solve_dc22_seed0():
    arcade = Arcade(operation_mode=OperationMode.OFFLINE)
    env = arcade.make("dc22", seed=0)
    obs = env.reset()
    game = env._game
    
    sys_clicks = game.current_level.get_sprites_by_tag("sys_click")
    buttons = [(s.x + s.width // 2, s.y + s.height // 2, s.name) for s in sys_clicks]
    print(f"Buttons: {buttons}")

    # BFS: state = (player_x, player_y, tuple of actions taken)
    # Explore all combos of click(a), click(b), then nav
    # Try up to 3 clicks then nav sequences

    dir_actions = [
        (GameAction.ACTION1, 0, -2), (GameAction.ACTION2, 0, 2),
        (GameAction.ACTION3, -2, 0), (GameAction.ACTION4, 2, 0)
    ]

    click_actions = [
        (GameAction.ACTION6, {"x": bx, "y": by}, name) 
        for bx, by, name in buttons
    ]

    def try_sequence(actions):
        env = arcade.make("dc22", seed=0)
        obs = env.reset()
        game = env._game
        for act, data, _ in actions:
            if data:
                act.set_data(data)
            obs = env.step(act)
            if obs.levels_completed > 0 or game.smxyfelexa():
                return True, obs.levels_completed
        return False, obs.levels_completed

    # Try: k clicks (all combinations) then up to 20 dir moves BFS
    from itertools import product

    # Click combos: 0-3 clicks from the 2 buttons  
    click_combos = [()]
    for k in range(1, 4):
        for combo in product(range(len(click_actions)), repeat=k):
            click_combos.append(combo)

    best = 0
    for clicks in click_combos[:64]:
        env2 = arcade.make("dc22", seed=0)
        obs2 = env2.reset()
        game2 = env2._game
        
        # Apply clicks
        for ci in clicks:
            bx, by, name = buttons[ci]
            env2.step(GameAction.ACTION6, {"x": bx, "y": by})
        
        # Now BFS navigate
        px, py = game2.qnnpcoyzd.x, game2.qnnpcoyzd.y
        gx, gy = game2.hfuqkxulm.x, game2.hfuqkxulm.y
        
        q = deque([((px, py), [])])
        vis = {(px, py)}
        found = False
        while q:
            (cx, cy), path = q.popleft()
            if len(path) > 25:
                break
            if cx == gx and cy == gy:
                print(f"WIN with clicks={[buttons[i][2] for i in clicks]}, nav_steps={len(path)}")
                found = True
                best = 1
                break
            for act, dx, dy in dir_actions:
                env3 = arcade.make("dc22", seed=0)
                obs3 = env3.reset()
                g3 = env3._game
                for ci in clicks:
                    bx2, by2, _ = buttons[ci]
                    env3.step(GameAction.ACTION6, {"x": bx2, "y": by2})
                for pa in path:
                    env3.step(pa)
                obs3 = env3.step(act)
                nx, ny = g3.qnnpcoyzd.x, g3.qnnpcoyzd.y
                if (nx, ny) not in vis:
                    vis.add((nx, ny))
                    new_path = path + [act]
                    if nx == gx and ny == gy:
                        print(f"WIN with clicks={[buttons[i][2] for i in clicks]}, nav_steps={len(new_path)}")
                        print(f"Nav path: {[str(a) for a in new_path]}")
                        found = True
                        best = 1
                        break
                    q.append(((nx, ny), new_path))
            if found:
                break
        if found:
            break
    
    if best == 0:
        print("No solution found in search space")

if __name__ == "__main__":
    solve_dc22_seed0()
