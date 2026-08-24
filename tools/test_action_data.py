"""
Check a.action_data after set_data.
"""
from arcengine import GameAction

a = GameAction.ACTION6
a.set_data({"x": 10, "y": 20})
print("a.action_data:", a.action_data)
print("a.is_complex:", a.is_complex)
