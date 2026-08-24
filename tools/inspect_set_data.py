"""
Inspect set_data implementation on GameAction.
"""
import inspect
from arcengine import GameAction, ActionInput

act = GameAction.ACTION6
print("set_data code / doc:", inspect.getsource(GameAction.set_data) if hasattr(GameAction, "set_data") else "No source")

ai = ActionInput(id=GameAction.ACTION6, data={"x": 10, "y": 20})
print("ActionInput:", ai, dir(ai))
if hasattr(ai, "data"):
    print("ai.data:", ai.data)
