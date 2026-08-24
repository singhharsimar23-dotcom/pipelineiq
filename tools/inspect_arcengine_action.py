"""
Inspect GameAction and ActionInput in arcengine.
"""
import arcengine
from arcengine import GameAction

print("dir(GameAction):", dir(GameAction))
print("GameAction.ACTION6:", type(GameAction.ACTION6), repr(GameAction.ACTION6))

act = GameAction.ACTION6
print("Has set_data:", hasattr(act, "set_data"))
if hasattr(act, "set_data"):
    act.set_data({"x": 10, "y": 20})
    print("act.data:", getattr(act, "data", None))

try:
    from arcengine import ActionInput
    print("ActionInput exists:", ActionInput)
except Exception as e:
    print("ActionInput import error:", e)
